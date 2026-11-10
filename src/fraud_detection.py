
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def detect_fraud():
    print("Starting fraud detection...\n")

    # Load datasets
    claims = pd.read_csv(DATA_DIR / "claims.csv")
    claimants = pd.read_csv(DATA_DIR / "claimants.csv")

    # Validate required columns
    required_claim_columns = {
        "claim_id", "claimant_id", "provider_id",
        "claim_amount", "approved_amount"
    }

    required_claimant_columns = {
        "claimant_id", "phone"
    }

    if not required_claim_columns.issubset(claims.columns):
        raise ValueError("Claims dataset is missing required columns.")

    if not required_claimant_columns.issubset(claimants.columns):
        raise ValueError("Claimants dataset is missing required columns.")

    # Convert financial values to numeric
    claims["claim_amount"] = pd.to_numeric(
        claims["claim_amount"], errors="coerce"
    )
    claims["approved_amount"] = pd.to_numeric(
        claims["approved_amount"], errors="coerce"
    )

    if claims[
        ["claim_amount", "approved_amount"]
    ].isna().any().any():
        raise ValueError("Claim amounts contain missing or invalid values.")

    if claims["claimant_id"].isna().any():
        raise ValueError("Claims contain missing claimant IDs.")

    if claims["provider_id"].isna().any():
        raise ValueError("Claims contain missing provider IDs.")

    # Initialize risk fields
    claims["risk_score"] = 0
    claims["risk_reasons"] = ""

    def apply_rule(condition, points, reason):
        """Apply a risk rule and record its explanation."""
        condition = condition.fillna(False)

        claims.loc[condition, "risk_score"] += points

        claims.loc[condition, "risk_reasons"] += (
            reason + "; "
        )

    # Rule 1: Multiple claims from the same claimant
    claimant_counts = claims["claimant_id"].value_counts()

    claims["claimant_claim_count"] = (
        claims["claimant_id"].map(claimant_counts)
    )

    apply_rule(
        claims["claimant_claim_count"] >= 4,
        30,
        "Multiple claims by claimant"
    )

    # Rule 2: High claim amount
    apply_rule(
        claims["claim_amount"] >= 350000,
        30,
        "Unusually high claim amount"
    )

    # Rule 3: Large difference between requested and approved amounts
    claims["amount_difference"] = (
        claims["claim_amount"] - claims["approved_amount"]
    )

    apply_rule(
        claims["amount_difference"] >= 200000,
        20,
        "Large difference between requested and approved amount"
    )

    # Rule 4: Shared phone numbers
    # Ignore missing and blank phone numbers.
    claimants["phone"] = (
        claimants["phone"]
        .astype("string")
        .str.strip()
    )

    valid_phones = claimants[
        claimants["phone"].notna()
        & (claimants["phone"] != "")
    ].copy()

    phone_counts = valid_phones["phone"].value_counts()

    valid_phones["shared_phone_count"] = (
        valid_phones["phone"].map(phone_counts)
    )

    shared_claimants = set(
        valid_phones.loc[
            valid_phones["shared_phone_count"] > 1,
            "claimant_id"
        ]
    )

    apply_rule(
        claims["claimant_id"].isin(shared_claimants),
        20,
        "Shared phone number - requires verification"
    )

    # Rule 5: Providers handling many claims
    provider_counts = claims["provider_id"].value_counts()

    claims["provider_claim_count"] = (
        claims["provider_id"].map(provider_counts)
    )

    apply_rule(
        claims["provider_claim_count"] >= 12,
        20,
        "Provider handles unusually many claims"
    )

    # Rule 6: Providers connected to many distinct claimants
    provider_claimant_counts = (
        claims.groupby("provider_id")["claimant_id"].nunique()
    )

    claims["provider_claimant_count"] = (
        claims["provider_id"].map(provider_claimant_counts)
    )

    apply_rule(
        claims["provider_claimant_count"] >= 8,
        40,
        "Provider connected to many claimants"
    )

    # Cap risk scores at 100
    claims["risk_score"] = claims["risk_score"].clip(
        lower=0,
        upper=100
    )

    # Assign risk categories
    claims["risk_level"] = pd.cut(
        claims["risk_score"],
        bins=[-1, 29, 59, 100],
        labels=["Low", "Medium", "High"]
    )

    # Save results
    output_file = OUTPUT_DIR / "fraud_results.csv"

    claims.to_csv(output_file, index=False)

    print("Fraud detection completed!")

    print("\nRisk level summary:")
    print(
        claims["risk_level"]
        .value_counts()
        .reindex(["Low", "Medium", "High"], fill_value=0)
    )

    print(
        "\nTotal suspicious claims:",
        (claims["risk_score"] >= 30).sum()
    )

    print("\nResults saved to:", output_file)

    return claims


if __name__ == "__main__":
    detect_fraud()
