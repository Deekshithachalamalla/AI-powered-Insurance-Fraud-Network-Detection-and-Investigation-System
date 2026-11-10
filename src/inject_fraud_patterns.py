
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
GT_DIR = Path("data/ground_truth")

GT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 20261022


def inject_fraud_patterns():
    print("Injecting controlled fraud patterns...\n")

    claimants = pd.read_csv(RAW_DIR / "claimants.csv")
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    if len(claimants) < 2:
        raise ValueError("At least two claimants are required.")

    if len(claims) < 3:
        raise ValueError("At least three claims are required.")

    if claimants["claimant_id"].isna().any():
        raise ValueError("Claimant IDs contain missing values.")

    if claims["claim_id"].isna().any():
        raise ValueError("Claim IDs contain missing values.")

    if claims["provider_id"].isna().any():
        raise ValueError("Provider IDs contain missing values.")

    ground_truth_records = {}

    # Pattern 1: Shared phone number
    claimant_a = claimants.iloc[0]["claimant_id"]
    claimant_b = claimants.iloc[1]["claimant_id"]

    shared_phone = claimants.iloc[0]["phone"]

    claimants.loc[
        claimants["claimant_id"] == claimant_b,
        "phone"
    ] = shared_phone

    # Label claims belonging to these two claimants
    shared_phone_claims = claims[
        claims["claimant_id"].isin([claimant_a, claimant_b])
    ]

    for claim_id in shared_phone_claims["claim_id"]:
        ground_truth_records[claim_id] = {
            "claim_id": claim_id,
            "is_fraud": 1,
            "fraud_pattern": "Shared claimant phone number"
        }

    # Pattern 2: Suspicious provider network
    suspicious_provider = claims.iloc[0]["provider_id"]

    # Select claims from distinct claimants.
    # Aim for 12 claims to trigger both provider rules.
    provider_candidates = (
        claims.drop_duplicates(
            subset="claimant_id",
            keep="first"
        )
        .head(12)
    )

    suspicious_claim_ids = provider_candidates["claim_id"].tolist()

    claims.loc[
        claims["claim_id"].isin(suspicious_claim_ids),
        "provider_id"
    ] = suspicious_provider

    for claim_id in suspicious_claim_ids:
        existing = ground_truth_records.get(claim_id)

        if existing:
            existing["fraud_pattern"] += " + Shared provider network"
        else:
            ground_truth_records[claim_id] = {
                "claim_id": claim_id,
                "is_fraud": 1,
                "fraud_pattern": "Shared provider network"
            }

    # Save modified datasets
    claimants.to_csv(
        RAW_DIR / "claimants.csv",
        index=False
    )

    claims.to_csv(
        RAW_DIR / "claims.csv",
        index=False
    )

    # Create ground-truth dataset
    ground_truth = pd.DataFrame(
        list(ground_truth_records.values()),
        columns=["claim_id", "is_fraud", "fraud_pattern"]
    )

    ground_truth = ground_truth.sort_values(
        "claim_id"
    ).reset_index(drop=True)

    ground_truth.to_csv(
        GT_DIR / "ground_truth.csv",
        index=False
    )

    print("Fraud patterns injected successfully!")

    print("\nShared phone claimants:")
    print(claimant_a, claimant_b)

    print("\nSuspicious provider:", suspicious_provider)
    print("Claims connected to provider:", len(suspicious_claim_ids))

    print("\nGround-truth positive labels:", len(ground_truth))
    print("Ground-truth file:", GT_DIR / "ground_truth.csv")

    return ground_truth


if __name__ == "__main__":
    inject_fraud_patterns()
