
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
GT_DIR = Path("data/ground_truth")

SEED = 20261022


def inject_anomalies():
    print("Injecting financial anomalies...\n")

    invoices = pd.read_csv(RAW_DIR / "invoices.csv")
    payments = pd.read_csv(RAW_DIR / "payments.csv")
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    # Check minimum records
    if len(invoices) < 2:
        raise ValueError("At least two invoices are required.")

    if len(payments) < 1:
        raise ValueError("At least one payment is required.")

    required_claim_columns = {
        "claim_id", "claimant_id", "approved_amount"
    }

    if not required_claim_columns.issubset(claims.columns):
        raise ValueError("Claims dataset is missing required columns.")

    # Load existing ground truth and preserve previous labels
    gt_path = GT_DIR / "ground_truth.csv"

    if gt_path.exists():
        ground_truth = pd.read_csv(gt_path)
    else:
        ground_truth = pd.DataFrame(
            columns=["claim_id", "is_fraud", "fraud_pattern"]
        )

    records = {}

    for _, row in ground_truth.iterrows():
        records[row["claim_id"]] = {
            "claim_id": row["claim_id"],
            "is_fraud": int(row["is_fraud"]),
            "fraud_pattern": str(row["fraud_pattern"])
        }

    def add_ground_truth(claim_id, pattern):
        if claim_id in records:
            existing = records[claim_id]["fraud_pattern"]

            if pattern not in existing:
                records[claim_id]["fraud_pattern"] = (
                    existing + " + " + pattern
                )
        else:
            records[claim_id] = {
                "claim_id": claim_id,
                "is_fraud": 1,
                "fraud_pattern": pattern
            }

    # Anomaly 1: Duplicate invoice ID across different claimants
    invoice_claims = invoices.merge(
        claims[["claim_id", "claimant_id"]],
        on="claim_id",
        how="inner",
        validate="many_to_one"
    )

    duplicate_pair = None

    for i in range(len(invoice_claims)):
        for j in range(i + 1, len(invoice_claims)):
            first = invoice_claims.iloc[i]
            second = invoice_claims.iloc[j]

            if first["claimant_id"] != second["claimant_id"]:
                duplicate_pair = (i, j)
                break

        if duplicate_pair:
            break

    if duplicate_pair is None:
        raise ValueError(
            "Could not find invoices belonging to two different claimants."
        )

    first_index, second_index = duplicate_pair

    first_invoice = invoice_claims.iloc[first_index]
    second_invoice = invoice_claims.iloc[second_index]

    duplicate_invoice_id = first_invoice["invoice_id"]

    invoices.loc[
        invoices["claim_id"] == second_invoice["claim_id"],
        "invoice_id"
    ] = duplicate_invoice_id

    add_ground_truth(
        first_invoice["claim_id"],
        "Duplicate invoice across claimants"
    )

    add_ground_truth(
        second_invoice["claim_id"],
        "Duplicate invoice across claimants"
    )

    # Anomaly 2: Payment exceeds approved amount
    payment_claim_id = payments.iloc[0]["claim_id"]

    matching_claim = claims[
        claims["claim_id"] == payment_claim_id
    ]

    if matching_claim.empty:
        raise ValueError("Payment references a nonexistent claim.")

    approved_amount = pd.to_numeric(
        matching_claim.iloc[0]["approved_amount"],
        errors="raise"
    )

    if pd.isna(approved_amount):
        raise ValueError("Approved amount is missing.")

    payments.loc[0, "payment_amount"] = approved_amount + 100000

    add_ground_truth(
        payment_claim_id,
        "Payment exceeds approved amount"
    )

    # Save modified datasets
    invoices.to_csv(RAW_DIR / "invoices.csv", index=False)
    payments.to_csv(RAW_DIR / "payments.csv", index=False)

    # Save merged ground truth without deleting previous labels
    updated_ground_truth = pd.DataFrame(
        list(records.values()),
        columns=["claim_id", "is_fraud", "fraud_pattern"]
    )

    updated_ground_truth = updated_ground_truth.sort_values(
        "claim_id"
    ).reset_index(drop=True)

    updated_ground_truth.to_csv(gt_path, index=False)

    print("Financial anomalies injected successfully!")
    print("1. Duplicate invoice across different claimants")
    print("2. Payment exceeding approved amount")
    print("Ground-truth labels:", len(updated_ground_truth))


if __name__ == "__main__":
    inject_anomalies()
