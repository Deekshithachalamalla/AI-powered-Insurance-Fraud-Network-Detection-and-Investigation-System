
import pandas as pd
import numpy as np
from pathlib import Path

# Reproducible random data
SEED = 20261022

# Project folders
RAW_DIR = Path("data/raw")
GROUND_TRUTH_DIR = Path("data/ground_truth")


def generate_data(
    num_claimants=100,
    num_policies=150,
    num_providers=30,
    num_claims=200,
    seed=SEED
):
    # Use a local random generator for reproducibility
    rng = np.random.default_rng(seed)

    # Validate dataset sizes
    if min(num_claimants, num_policies, num_providers) <= 0:
        raise ValueError("Claimants, policies and providers must be greater than zero.")

    if num_claims < 0:
        raise ValueError("Number of claims cannot be negative.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating insurance data...")

    cities = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai"]

    # 1. Claimants
    claimants = pd.DataFrame({
        "claimant_id": [
            f"CLT-{i:06d}" for i in range(1, num_claimants + 1)
        ],
        "name": [
            f"Claimant_{i}" for i in range(1, num_claimants + 1)
        ],
        "phone": [
            f"9{rng.integers(100000000, 999999999)}"
            for _ in range(num_claimants)
        ],
        "city": rng.choice(cities, num_claimants)
    })

    # 2. Policies
    policies = pd.DataFrame({
        "policy_id": [
            f"POL-{i:06d}" for i in range(1, num_policies + 1)
        ],
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
        "provider_id": [
            f"PRV-{i:06d}" for i in range(1, num_providers + 1)
        ],
        "provider_name": [
            f"Provider_{i}" for i in range(1, num_providers + 1)
        ],
        "provider_type": rng.choice(
            ["Hospital", "Repair Shop", "Clinic"], num_providers
        ),
        "city": rng.choice(cities, num_providers)
    })

    # 4. Incidents
    incidents = pd.DataFrame({
        "incident_id": [
            f"INC-{i:06d}" for i in range(1, num_claims + 1)
        ],
        "incident_type": rng.choice(
            ["Accident", "Medical", "Property Damage"], num_claims
        ),
        "incident_city": rng.choice(cities, num_claims),
        "incident_date": pd.date_range(
            start="2026-01-01", periods=num_claims, freq="D"
        )
    })

    # 5. Claims
    # First select policies, then derive their actual owners.
    selected_policy_ids = rng.choice(
        policies["policy_id"], num_claims
    )

    policy_owner_mapping = policies.set_index(
        "policy_id"
    )["claimant_id"].to_dict()

    selected_claimant_ids = [
        policy_owner_mapping[policy_id]
        for policy_id in selected_policy_ids
    ]

    # Generate requested amounts first.
    claim_amounts = rng.integers(
        10000, 500000, num_claims
    )

    # Approved amounts are always less than or equal to claim amounts.
    approval_percentages = rng.uniform(
        0.1, 1.0, num_claims
    )

    approved_amounts = (
        claim_amounts * approval_percentages
    ).astype(int)

    claims = pd.DataFrame({
        "claim_id": [
            f"CLM-2026-{i:06d}" for i in range(1, num_claims + 1)
        ],
        "claimant_id": selected_claimant_ids,
        "policy_id": selected_policy_ids,
        "incident_id": incidents["incident_id"],
        "provider_id": rng.choice(
            providers["provider_id"], num_claims
        ),
        "claim_amount": claim_amounts,
        "approved_amount": approved_amounts,
        "claim_status": rng.choice(
            ["Submitted", "Approved", "Rejected", "Under Review"],
            num_claims
        )
    })

    # Save master and transaction datasets
    datasets = {
        "claimants": claimants,
        "policies": policies,
        "providers": providers,
        "incidents": incidents,
        "claims": claims
    }

    for name, dataframe in datasets.items():
        dataframe.to_csv(
            RAW_DIR / f"{name}.csv",
            index=False
        )

    # Initialize ground truth for a fresh generation run.
    ground_truth = pd.DataFrame(
        columns=["claim_id", "is_fraud", "fraud_pattern"]
    )

    ground_truth.to_csv(
        GROUND_TRUTH_DIR / "ground_truth.csv",
        index=False
    )

    print("\nData generation completed!")

    for name, dataframe in datasets.items():
        print(f"{name}: {len(dataframe)} records")

    print("\nData integrity checks:")
    print(
        "Claims with mismatched policy owners:",
        (
            claims.merge(
                policies[["policy_id", "claimant_id"]],
                on="policy_id",
                suffixes=("_claim", "_policy")
            )["claimant_id_claim"]
            != claims.merge(
                policies[["policy_id", "claimant_id"]],
                on="policy_id",
                suffixes=("_claim", "_policy")
            )["claimant_id_policy"]
        ).sum()
    )

    print(
        "Approved amounts exceeding claim amounts:",
        (claims["approved_amount"] > claims["claim_amount"]).sum()
    )

    return datasets


if __name__ == "__main__":
    generate_data()
