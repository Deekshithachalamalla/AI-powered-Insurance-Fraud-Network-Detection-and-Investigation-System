
import pandas as pd
import numpy as np
from pathlib import Path

# Reproducible random data
SEED = 20261022
rng = np.random.default_rng(SEED)

# Project folders
RAW_DIR = Path("data/raw")
GROUND_TRUTH_DIR = Path("data/ground_truth")

RAW_DIR.mkdir(parents=True, exist_ok=True)
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)


def generate_data(
    num_claimants=100,
    num_policies=150,
    num_providers=30,
    num_claims=200
):
    print("Generating insurance data...")

    # 1. Claimants
    claimants = pd.DataFrame({
        "claimant_id": [f"CLT-{i:06d}" for i in range(1, num_claimants + 1)],
        "name": [f"Claimant_{i}" for i in range(1, num_claimants + 1)],
        "phone": [
            f"9{rng.integers(100000000, 999999999)}"
            for _ in range(num_claimants)
        ],
        "city": rng.choice(
            ["Hyderabad", "Bengaluru", "Chennai", "Mumbai"],
            num_claimants
        )
    })

    # 2. Policies
    policies = pd.DataFrame({
        "policy_id": [f"POL-{i:06d}" for i in range(1, num_policies + 1)],
        "claimant_id": rng.choice(
            claimants["claimant_id"], num_policies
        ),
        "policy_type": rng.choice(
            ["Health", "Vehicle", "Property"], num_policies
        ),
        "premium": rng.integers(5000, 50000, num_policies),
        "policy_status": rng.choice(
            ["Active", "Expired"], num_policies, p=[0.9, 0.1]
        )
    })

    # 3. Providers
    providers = pd.DataFrame({
        "provider_id": [f"PRV-{i:06d}" for i in range(1, num_providers + 1)],
        "provider_name": [
            f"Provider_{i}" for i in range(1, num_providers + 1)
        ],
        "provider_type": rng.choice(
            ["Hospital", "Repair Shop", "Clinic"], num_providers
        ),
        "city": rng.choice(
            ["Hyderabad", "Bengaluru", "Chennai", "Mumbai"],
            num_providers
        )
    })

    # 4. Incidents
    incidents = pd.DataFrame({
        "incident_id": [f"INC-{i:06d}" for i in range(1, num_claims + 1)],
        "incident_type": rng.choice(
            ["Accident", "Medical", "Property Damage"], num_claims
        ),
        "incident_city": rng.choice(
            ["Hyderabad", "Bengaluru", "Chennai", "Mumbai"],
            num_claims
        ),
        "incident_date": pd.date_range(
            start="2026-01-01", periods=num_claims, freq="D"
        )
    })

    # 5. Claims
    claims = pd.DataFrame({
        "claim_id": [f"CLM-2026-{i:06d}" for i in range(1, num_claims + 1)],
        "claimant_id": rng.choice(
            claimants["claimant_id"], num_claims
        ),
        "policy_id": rng.choice(
            policies["policy_id"], num_claims
        ),
        "incident_id": incidents["incident_id"],
        "provider_id": rng.choice(
            providers["provider_id"], num_claims
        ),
        "claim_amount": rng.integers(10000, 500000, num_claims),
        "approved_amount": rng.integers(5000, 300000, num_claims),
        "claim_status": rng.choice(
            ["Submitted", "Approved", "Rejected", "Under Review"],
            num_claims
        )
    })

    # Save master and transaction data
    datasets = {
        "claimants": claimants,
        "policies": policies,
        "providers": providers,
        "incidents": incidents,
        "claims": claims
    }

    for name, dataframe in datasets.items():
        dataframe.to_csv(RAW_DIR / f"{name}.csv", index=False)

    # Separate ground-truth file (initially empty)
    ground_truth = pd.DataFrame(
        columns=["claim_id", "is_fraud", "fraud_pattern"]
    )
    ground_truth.to_csv(
        GROUND_TRUTH_DIR / "ground_truth.csv", index=False
    )

    print("\nData generation completed!")
    for name, dataframe in datasets.items():
        print(f"{name}: {len(dataframe)} records")

    return datasets


if __name__ == "__main__":
    generate_data()
