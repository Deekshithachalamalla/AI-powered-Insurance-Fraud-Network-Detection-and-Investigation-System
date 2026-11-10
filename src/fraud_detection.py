
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def detect_fraud():
    print("Starting fraud detection...\n")

    claims = pd.read_csv(DATA_DIR / "claims.csv")
    claimants = pd.read_csv(DATA_DIR / "claimants.csv")
    providers = pd.read_csv(DATA_DIR / "providers.csv")

    # Start with zero risk points
    claims["risk_score"] = 0
    claims["risk_reasons"] = ""

    # Rule 1: Multiple claims from the same claimant
    claimant_counts = claims["claimant_id"].value_counts()

    claims["claimant_claim_count"] = (
        claims["claimant_id"].map(claimant_counts)
    )

    claims.loc[
        claims["claimant_claim_count"] >= 4, "risk_score"
    ] += 30

    claims.loc[
        claims["claimant_claim_count"] >= 4, "risk_reasons"
    ] += "Multiple claims by claimant; "

    # Rule 2: High claim amount
    claims.loc[
        claims["claim_amount"] >= 350000, "risk_score"
    ] += 30

    claims.loc[
        claims["claim_amount"] >= 350000, "risk_reasons"
    ] += "Unusually high claim amount; "

    # Rule 3: Requested amount exceeds approved amount significantly
    claims["amount_difference"] = (
        claims["claim_amount"] - claims["approved_amount"]
    )

    claims.loc[
        claims["amount_difference"] >= 200000, "risk_score"
    ] += 20

    claims.loc[
        claims["amount_difference"] >= 200000, "risk_reasons"
    ] += "Large difference between requested and approved amount; "

    # Rule 4: Shared phone numbers between claimants
    phone_counts = claimants["phone"].value_counts()

    claimants["shared_phone_count"] = (
        claimants["phone"].map(phone_counts)
    )

    shared_claimants = set(
        claimants.loc[
            claimants["shared_phone_count"] > 1, "claimant_id"
        ]
    )

    claims.loc[
        claims["claimant_id"].isin(shared_claimants), "risk_score"
    ] += 20

    claims.loc[
        claims["claimant_id"].isin(shared_claimants), "risk_reasons"
    ] += "Shared phone number; "

    
    # Rule 5: Providers handling many claims
    provider_counts = claims["provider_id"].value_counts()

    claims["provider_claim_count"] = (
    claims["provider_id"].map(provider_counts)
)

    claims.loc[
    claims["provider_claim_count"] >= 12, "risk_score"
] += 20

    claims.loc[
    claims["provider_claim_count"] >= 12, "risk_reasons"
] += "Provider handles unusually many claims; "


    
    # Rule 6: Highly concentrated provider network
    provider_claimant_counts = (
        claims.groupby("provider_id")["claimant_id"].nunique()
    )

    claims["provider_claimant_count"] = (
        claims["provider_id"].map(provider_claimant_counts)
    )

    # Flag providers connected to at least 8 distinct claimants
    claims.loc[
        claims["provider_claimant_count"] >= 8, "risk_score"
    ] += 40

    claims.loc[
        claims["provider_claimant_count"] >= 8, "risk_reasons"
    ] += "Provider connected to many claimants; "


    
    # Cap risk score at 100
    claims["risk_score"] = claims["risk_score"].clip(upper=100)

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
    print(claims["risk_level"].value_counts())

    print("\nTotal suspicious claims:",
          (claims["risk_score"] >= 30).sum())

    print("\nResults saved to:", output_file)

    return claims


if __name__ == "__main__":
    detect_fraud()
