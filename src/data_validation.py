
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
GROUND_TRUTH_DIR = Path("data/ground_truth")


def validate_data():
    print("Starting comprehensive data validation...\n")

    errors = []
    warnings = []

    def load_csv(path, name):
        if not path.exists():
            errors.append(f"{name}: File not found - {path}")
            return None

        return pd.read_csv(path)

    # Load raw datasets
    claimants = load_csv(RAW_DIR / "claimants.csv", "Claimants")
    policies = load_csv(RAW_DIR / "policies.csv", "Policies")
    providers = load_csv(RAW_DIR / "providers.csv", "Providers")
    incidents = load_csv(RAW_DIR / "incidents.csv", "Incidents")
    claims = load_csv(RAW_DIR / "claims.csv", "Claims")
    invoices = load_csv(RAW_DIR / "invoices.csv", "Invoices")
    payments = load_csv(RAW_DIR / "payments.csv", "Payments")

    # Load processed datasets
    investigations = load_csv(
        PROCESSED_DIR / "investigations.csv", "Investigations"
    )
    fraud_results = load_csv(
        PROCESSED_DIR / "fraud_results.csv", "Fraud Results"
    )
    financial_exceptions = load_csv(
        PROCESSED_DIR / "financial_exceptions.csv",
        "Financial Exceptions"
    )
    relationship_edges = load_csv(
        PROCESSED_DIR / "relationship_edges.csv",
        "Relationship Edges"
    )

    ground_truth = load_csv(
        GROUND_TRUTH_DIR / "ground_truth.csv", "Ground Truth"
    )

    history_path = PROCESSED_DIR / "investigation_status_history.csv"
    history = (
        pd.read_csv(history_path)
        if history_path.exists()
        else None
    )

    datasets = {
        "claimants": (claimants, "claimant_id"),
        "policies": (policies, "policy_id"),
        "providers": (providers, "provider_id"),
        "incidents": (incidents, "incident_id"),
        "claims": (claims, "claim_id"),
        "invoices": (invoices, "invoice_id"),
        "payments": (payments, "payment_id"),
        "investigations": (investigations, "investigation_id"),
        "fraud_results": (fraud_results, "claim_id"),
        "ground_truth": (ground_truth, "claim_id"),
        "financial_exceptions": (
            financial_exceptions, "investigation_id"
        )
    }

    # Stop further checks if required files are missing
    if errors:
        print("\nVALIDATION ERRORS")
        for error in errors:
            print("ERROR:", error)
        return False

    # 1. Check required columns and primary-key uniqueness
    for name, (df, key) in datasets.items():

        if key not in df.columns:
            errors.append(f"{name}: Missing identifier column {key}")
            continue

        if df[key].isna().any():
            errors.append(f"{name}: Missing {key} values")

        # Duplicate invoice IDs are intentional test anomalies.
        if name == "invoices":
            duplicate_count = df[key].duplicated().sum()
            if duplicate_count:
                warnings.append(
                    f"Invoices: {duplicate_count} duplicate invoice IDs "
                    "require anomaly investigation"
                )
            continue

        duplicate_count = df[key].duplicated().sum()

        if duplicate_count:
            errors.append(
                f"{name}: {duplicate_count} duplicate {key} values"
            )
        else:
            print(f"PASS: {name} identifiers are unique")

    # 2. Check missing values in core datasets
    core_datasets = {
        "claimants": claimants,
        "policies": policies,
        "providers": providers,
        "incidents": incidents,
        "claims": claims,
        "invoices": invoices,
        "payments": payments
    }

    for name, df in core_datasets.items():
        missing = df.isnull().sum().sum()

        if missing:
            errors.append(
                f"{name}: {missing} missing values"
            )
        else:
            print(f"PASS: {name} has no missing values")

    # 3. Check foreign-key references
    def check_fk(child, child_column, parent, parent_column, label):
        invalid = ~child[child_column].isin(parent[parent_column])
        count = invalid.sum()

        if count:
            errors.append(
                f"{label}: {count} invalid references"
            )
        else:
            print(f"PASS: {label} references are valid")

    check_fk(
        policies, "claimant_id",
        claimants, "claimant_id",
        "Policy -> Claimant"
    )

    check_fk(
        claims, "claimant_id",
        claimants, "claimant_id",
        "Claim -> Claimant"
    )

    check_fk(
        claims, "policy_id",
        policies, "policy_id",
        "Claim -> Policy"
    )

    check_fk(
        claims, "incident_id",
        incidents, "incident_id",
        "Claim -> Incident"
    )

    check_fk(
        claims, "provider_id",
        providers, "provider_id",
        "Claim -> Provider"
    )

    check_fk(
        invoices, "claim_id",
        claims, "claim_id",
        "Invoice -> Claim"
    )

    check_fk(
        invoices, "provider_id",
        providers, "provider_id",
        "Invoice -> Provider"
    )

    check_fk(
        payments, "claim_id",
        claims, "claim_id",
        "Payment -> Claim"
    )

    check_fk(
        investigations, "claim_id",
        claims, "claim_id",
        "Investigation -> Claim"
    )

    check_fk(
        fraud_results, "claim_id",
        claims, "claim_id",
        "Fraud Results -> Claim"
    )

    check_fk(
        ground_truth, "claim_id",
        claims, "claim_id",
        "Ground Truth -> Claim"
    )

    check_fk(
        financial_exceptions, "claim_id",
        claims, "claim_id",
        "Financial Exception -> Claim"
    )

    # 4. Verify claimant-policy ownership consistency
    ownership = claims.merge(
        policies[["policy_id", "claimant_id"]],
        on="policy_id",
        suffixes=("_claim", "_policy"),
        validate="many_to_one"
    )

    mismatches = ownership[
        ownership["claimant_id_claim"]
        != ownership["claimant_id_policy"]
    ]

    if len(mismatches):
        errors.append(
            f"{len(mismatches)} claims reference policies "
            "owned by different claimants"
        )
    else:
        print("PASS: Claimant-policy ownership is consistent")

    # 5. Validate financial amounts
    for name, df, amount_column in [
        ("Claims", claims, "claim_amount"),
        ("Approved claims", claims, "approved_amount"),
        ("Invoices", invoices, "invoice_amount"),
        ("Payments", payments, "payment_amount")
    ]:
        amounts = pd.to_numeric(
            df[amount_column], errors="coerce"
        )

        if amounts.isna().any():
            errors.append(
                f"{name}: Invalid or missing {amount_column}"
            )
        elif (amounts < 0).any():
            errors.append(
                f"{name}: Negative {amount_column} values found"
            )

    if not errors:
        print("PASS: Financial amounts are valid")

    if (claims["approved_amount"] > claims["claim_amount"]).any():
        errors.append(
            "Approved amounts exceed requested claim amounts"
        )
    else:
        print("PASS: Approved amounts do not exceed claim amounts")

    # 6. Validate investigation history references
    if history is not None and not history.empty:
        check_fk(
            history,
            "investigation_id",
            investigations,
            "investigation_id",
            "Investigation History -> Investigation"
        )

    # 7. Validate relationship edge endpoints
    if not relationship_edges.empty:
        valid_ids = set()

        for df, key in [
            (claimants, "claimant_id"),
            (policies, "policy_id"),
            (providers, "provider_id"),
            (incidents, "incident_id"),
            (claims, "claim_id"),
            (invoices, "invoice_id"),
            (payments, "payment_id")
        ]:
            valid_ids.update(df[key].dropna().astype(str))

        invalid_edges = (
            ~relationship_edges["source"].astype(str).isin(valid_ids)
            | ~relationship_edges["target"].astype(str).isin(valid_ids)
        )

        if invalid_edges.any():
            errors.append(
                f"{invalid_edges.sum()} relationship edges "
                "contain unknown entity IDs"
            )
        else:
            print("PASS: Relationship edge endpoints are valid")

    # 8. Display validation summary
    print("\nVALIDATION SUMMARY")
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))

    for warning in warnings:
        print("WARNING:", warning)

    for error in errors:
        print("ERROR:", error)

    if errors:
        print("\nValidation completed with errors.")
        return False

    print("\nAll implemented validation checks passed!")
    return True


if __name__ == "__main__":
    validate_data()
