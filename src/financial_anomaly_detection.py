
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def detect_financial_anomalies():
    print("Checking financial transactions...\n")

    invoices = pd.read_csv(RAW_DIR / "invoices.csv")
    payments = pd.read_csv(RAW_DIR / "payments.csv")
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    exceptions = []

    # Rule 1: Duplicate invoice IDs across different claims
    duplicate_invoices = invoices[
        invoices.duplicated("invoice_id", keep=False)
    ]

    for _, row in duplicate_invoices.iterrows():
        exceptions.append({
            "exception_type": "Duplicate Invoice",
            "record_id": row["invoice_id"],
            "claim_id": row["claim_id"],
            "description": "Invoice ID is repeated",
            "status": "Open"
        })

    # Rule 2: Payment exceeds approved claim amount
    payment_check = payments.merge(
        claims[["claim_id", "approved_amount"]],
        on="claim_id",
        how="left",
        validate="many_to_one"
    )

    excessive_payments = payment_check[
        payment_check["payment_amount"] >
        payment_check["approved_amount"]
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

    # Create investigation IDs
    exception_df = pd.DataFrame(exceptions)

    if not exception_df.empty:
        exception_df.insert(
            0,
            "investigation_id",
            [
                f"FIN-INV-{i:04d}"
                for i in range(1, len(exception_df) + 1)
            ]
        )

    # Save exception report
    output_file = OUTPUT_DIR / "financial_exceptions.csv"

    exception_df.to_csv(output_file, index=False)

    print("Financial anomaly detection completed!")
    print("\nException summary:")

    if not exception_df.empty:
        print(exception_df["exception_type"].value_counts())
        print("\nInvestigation IDs and statuses:")
        print(exception_df[["investigation_id", "status"]])
    else:
        print("No financial exceptions found.")

    print("\nTotal exceptions:", len(exception_df))
    print("Report saved to:", output_file)

    return exception_df


if __name__ == "__main__":
    detect_financial_anomalies()
