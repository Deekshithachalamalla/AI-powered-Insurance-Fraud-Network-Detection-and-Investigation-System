
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")

rng = np.random.default_rng(20261022)


def generate_financial_data():
    print("Generating invoice and payment records...\n")

    claims = pd.read_csv(RAW_DIR / "claims.csv")

    # Generate one invoice for each claim
    invoices = pd.DataFrame({
        "invoice_id": [
            f"INV-2026-{i:06d}"
            for i in range(1, len(claims) + 1)
        ],
        "claim_id": claims["claim_id"],
        "provider_id": claims["provider_id"],
        "invoice_amount": claims["claim_amount"],
        "invoice_status": rng.choice(
            ["Submitted", "Verified", "Rejected"],
            len(claims)
        )
    })

    # Generate payment records
    payments = pd.DataFrame({
        "payment_id": [
            f"PAY-2026-{i:06d}"
            for i in range(1, len(claims) + 1)
        ],
        "claim_id": claims["claim_id"],
        "payment_amount": (
            claims["approved_amount"] * 0.8
        ).round(2),
        "payment_status": rng.choice(
            ["Pending", "Completed", "Failed"],
            len(claims)
        )
    })

    # Save records
    invoices.to_csv(
        RAW_DIR / "invoices.csv",
        index=False
    )

    payments.to_csv(
        RAW_DIR / "payments.csv",
        index=False
    )

    print("Financial data generated successfully!")
    print("Invoices:", len(invoices))
    print("Payments:", len(payments))


if __name__ == "__main__":
    generate_financial_data()
