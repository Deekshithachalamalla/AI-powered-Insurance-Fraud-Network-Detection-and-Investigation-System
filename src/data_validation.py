
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")


def validate_data():
    print("Starting data validation...\n")

    # Load datasets
    claimants = pd.read_csv(DATA_DIR / "claimants.csv")
    policies = pd.read_csv(DATA_DIR / "policies.csv")
    providers = pd.read_csv(DATA_DIR / "providers.csv")
    incidents = pd.read_csv(DATA_DIR / "incidents.csv")
    claims = pd.read_csv(DATA_DIR / "claims.csv")

    errors = []

    # Check primary key uniqueness
    datasets = {
        "claimants": (claimants, "claimant_id"),
        "policies": (policies, "policy_id"),
        "providers": (providers, "provider_id"),
        "incidents": (incidents, "incident_id"),
        "claims": (claims, "claim_id")
    }

    for name, (df, key) in datasets.items():
        duplicates = df[key].duplicated().sum()

        if duplicates > 0:
            errors.append(f"{name}: {duplicates} duplicate IDs")
        else:
            print(f"PASS: {name} IDs are unique")

    # Check foreign keys
    checks = [
        ("claimant_id", claimants, "claimant_id"),
        ("policy_id", policies, "policy_id"),
        ("incident_id", incidents, "incident_id"),
        ("provider_id", providers, "provider_id")
    ]

    for claim_column, parent_df, parent_column in checks:
        invalid = ~claims[claim_column].isin(parent_df[parent_column])
        count = invalid.sum()

        if count > 0:
            errors.append(
                f"Claims contain {count} invalid {claim_column} references"
            )
        else:
            print(f"PASS: All {claim_column} references are valid")

    # Check missing values
    for name, (df, _) in datasets.items():
        missing = df.isnull().sum().sum()

        if missing > 0:
            errors.append(f"{name}: {missing} missing values")
        else:
            print(f"PASS: {name} has no missing values")

    # Display results
    print("\nVALIDATION SUMMARY")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print("\nValidation completed with errors.")
    else:
        print("All validation checks passed!")
        print("Data is ready for the next stage.")


if __name__ == "__main__":
    validate_data()
