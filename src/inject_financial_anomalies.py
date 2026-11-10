
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")


def inject_anomalies():
    print("Injecting financial anomalies...\n")

    invoices = pd.read_csv(RAW_DIR / "invoices.csv")
    payments = pd.read_csv(RAW_DIR / "payments.csv")

    claims = pd.read_csv(RAW_DIR / "claims.csv")

    # Anomaly 1: Duplicate invoice ID across two claims
    invoices.loc[1, "invoice_id"] = invoices.loc[0, "invoice_id"]

    # Anomaly 2: Payment exceeds approved amount
    claims_by_id = claims.set_index("claim_id")

    first_payment_claim = payments.loc[0, "claim_id"]

    approved_amount = claims_by_id.loc[
        first_payment_claim, "approved_amount"
    ]

    payments.loc[0, "payment_amount"] = approved_amount + 100000

    # Save modified files
    invoices.to_csv(RAW_DIR / "invoices.csv", index=False)
    payments.to_csv(RAW_DIR / "payments.csv", index=False)

    print("Financial anomalies injected successfully!")
    print("1. Duplicate invoice ID created")
    print("2. Payment exceeding approved amount created")


if __name__ == "__main__":
    inject_anomalies()
