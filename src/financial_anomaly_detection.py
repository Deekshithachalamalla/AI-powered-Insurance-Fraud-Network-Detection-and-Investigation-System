
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EXCEPTION_COLUMNS = [
    "investigation_id",
    "exception_type",
    "record_id",
    "claim_id",
    "description",
    "status"
]


def detect_financial_anomalies():
    print("Checking financial transactions...\n")

    invoices = pd.read_csv(RAW_DIR / "invoices.csv")
    payments = pd.read_csv(RAW_DIR / "payments.csv")
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    exceptions = []

    # Validate required columns
    required_invoice_columns = {
        "invoice_id", "claim_id", "provider_id", "invoice_amount"
    }

    required_payment_columns = {
        "payment_id", "claim_id", "payment_amount"
    }

    required_claim_columns = {
        "claim_id", "approved_amount"
    }

    if not required_invoice_columns.issubset(invoices.columns):
        raise ValueError("Invoices dataset is missing required columns.")

    if not required_payment_columns.issubset(payments.columns):
        raise ValueError("Payments dataset is missing required columns.")

    if not required_claim_columns.issubset(claims.columns):
        raise ValueError("Claims dataset is missing required columns.")

    claim_ids = set(claims["claim_id"].dropna())

    # 1. Duplicate invoice IDs across different claims
    invoice_claim_counts = (
        invoices.groupby("invoice_id")["claim_id"].nunique()
    )

    cross_claim_duplicate_ids = invoice_claim_counts[
        invoice_claim_counts > 1
    ].index

    duplicate_invoices = invoices[
        invoices["invoice_id"].isin(cross_claim_duplicate_ids)
    ]

    for _, row in duplicate_invoices.iterrows():
        exceptions.append({
            "exception_type": "Duplicate Invoice",
            "record_id": row["invoice_id"],
            "claim_id": row["claim_id"],
            "description": (
                "Invoice ID is reused across different claims"
            ),
            "status": "Open"
        })

    # 2. Invoice references to nonexistent claims
    invalid_invoices = invoices[
        ~invoices["claim_id"].isin(claim_ids)
    ]

    for _, row in invalid_invoices.iterrows():
        exceptions.append({
            "exception_type": "Invalid Invoice Claim Reference",
            "record_id": row["invoice_id"],
            "claim_id": row["claim_id"],
            "description": (
                "Invoice references a claim that does not exist"
            ),
            "status": "Open"
        })

    # 3. Validate payment amounts
    payments["payment_amount"] = pd.to_numeric(
        payments["payment_amount"],
        errors="coerce"
    )

    if payments["payment_amount"].isna().any():
        raise ValueError(
            "Payments contain missing or invalid payment amounts."
        )

    # 4. Payment references to nonexistent claims
    invalid_payments = payments[
        ~payments["claim_id"].isin(claim_ids)
    ]

    for _, row in invalid_payments.iterrows():
        exceptions.append({
            "exception_type": "Invalid Payment Claim Reference",
            "record_id": row["payment_id"],
            "claim_id": row["claim_id"],
            "description": (
                "Payment references a claim that does not exist"
            ),
            "status": "Open"
        })

    # 5. Payment exceeds approved claim amount
    payment_check = payments.merge(
        claims[["claim_id", "approved_amount"]],
        on="claim_id",
        how="inner",
        validate="many_to_one"
    )

    payment_check["approved_amount"] = pd.to_numeric(
        payment_check["approved_amount"],
        errors="coerce"
    )

    if payment_check["approved_amount"].isna().any():
        raise ValueError(
            "Claims contain missing or invalid approved amounts."
        )

    excessive_payments = payment_check[
        payment_check["payment_amount"]
        > payment_check["approved_amount"]
    ]

    for _, row in excessive_payments.iterrows():
        exceptions.append({
            "exception_type": "Excess Payment",
            "record_id": row["payment_id"],
            "claim_id": row["claim_id"],
            "description": (
                f"Payment {row['payment_amount']} exceeds "
                f"approved amount {row['approved_amount']}"
            ),
            "status": "Open"
        })

    # Generate unique financial investigation IDs
    exception_df = pd.DataFrame(
        exceptions,
        columns=[
            "exception_type",
            "record_id",
            "claim_id",
            "description",
            "status"
        ]
    )

    if not exception_df.empty:
        exception_df.insert(
            0,
            "investigation_id",
            [
                f"FIN-INV-{i:04d}"
                for i in range(1, len(exception_df) + 1)
            ]
        )
    else:
        exception_df = pd.DataFrame(
            columns=EXCEPTION_COLUMNS
        )

    # Save exception report
    output_file = OUTPUT_DIR / "financial_exceptions.csv"

    exception_df.to_csv(
        output_file,
        index=False
    )

    print("Financial anomaly detection completed!")

    print("\nException summary:")

    if not exception_df.empty:
        print(exception_df["exception_type"].value_counts())

        print("\nInvestigation IDs and statuses:")
        print(
            exception_df[["investigation_id", "status"]]
        )
    else:
        print("No financial exceptions found.")

    print("\nTotal exceptions:", len(exception_df))
    print("Report saved to:", output_file)

    return exception_df


if __name__ == "__main__":
    detect_financial_anomalies()
