
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
GT_DIR = Path("data/ground_truth")

GT_DIR.mkdir(parents=True, exist_ok=True)


def inject_fraud_patterns():
    print("Injecting controlled fraud patterns...")

    claimants = pd.read_csv(RAW_DIR / "claimants.csv")
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    # Pattern 1: Make two claimants share a phone number
    claimant_a = claimants.loc[0, "claimant_id"]
    claimant_b = claimants.loc[1, "claimant_id"]

    shared_phone = claimants.loc[0, "phone"]
    claimants.loc[
        claimants["claimant_id"] == claimant_b, "phone"
    ] = shared_phone

    # Pattern 2: Connect several claims to one provider
    suspicious_provider = "PRV-000001"

    suspicious_claim_ids = claims["claim_id"].head(3).tolist()

    claims.loc[
        claims["claim_id"].isin(suspicious_claim_ids),
        "provider_id"
    ] = suspicious_provider

    # Save updated raw datasets
    claimants.to_csv(RAW_DIR / "claimants.csv", index=False)
    claims.to_csv(RAW_DIR / "claims.csv", index=False)

    # Create separate ground-truth labels
    ground_truth = pd.DataFrame([
        {
            "claim_id": suspicious_claim_ids[0],
            "is_fraud": 1,
            "fraud_pattern": "Shared provider network"
        },
        {
            "claim_id": suspicious_claim_ids[1],
            "is_fraud": 1,
            "fraud_pattern": "Shared phone and provider"
        },
        {
            "claim_id": suspicious_claim_ids[2],
            "is_fraud": 1,
            "fraud_pattern": "Shared provider network"
        }
    ])

    ground_truth.to_csv(
        GT_DIR / "ground_truth.csv",
        index=False
    )

    print("Fraud patterns injected successfully!")
    print("Planted suspicious claims:", len(ground_truth))
    print("Ground-truth labels saved separately.")


if __name__ == "__main__":
    inject_fraud_patterns()
