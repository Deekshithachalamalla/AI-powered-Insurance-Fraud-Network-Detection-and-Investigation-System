
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")

SEED = 20261022


def generate_financial_data(seed=SEED):
    print("Generating invoice and payment records...\n")

    rng = np.random.default_rng(seed)

    claims_path = RAW_DIR / "claims.csv"

    if not claims_path.exists():
        raise FileNotFoundError("Claims dataset not found.")

    claims = pd.read_csv(claims_path)

    required_columns = {
        "claim_id", "provider_id",
        "claim_amount", "approved_amount"
    }

    if not required_columns.issubset(claims.columns):
        raise ValueError("Claims dataset is missing required columns.")

    if claims["claim_id"].isna().any():
        raise ValueError("Claims contain missing claim IDs.")

    if claims["provider_id"].isna().any():
        raise ValueError("Claims contain missing provider IDs.")

    if claims["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim IDs found.")

    # Validate financial amounts
    claims["claim_amount"] = pd.to_numeric(
        claims["claim_amount"], errors="coerce"
    )

    claims["approved_amount"] = pd.to_numeric(
        claims["approved_amount"], errors="coerce"
    )

    if claims[
        ["claim_amount", "approved_amount"]
    ].isna().any().any():
        raise ValueError("Invalid claim financial amounts.")

    if (
        (claims["claim_amount"] < 0).any()
        or (claims["approved_amount"] < 0).any()
    ):
        raise ValueError("Negative claim amounts found.")

    if (
        claims["approved_amount"] > claims["claim_amount"]
    ).any():
        raise ValueError(
            "Approved amount cannot exceed claim amount."
        )

    # 1. Generate one invoice for each claim
    invoices = pd.DataFrame({
        "claim_id": claims["claim_id"],
        "provider_id": claims["provider_id"],
        "invoice_amount": claims["claim_amount"],
        "invoice_status": rng.choice(
            ["Submitted", "Verified", "Rejected"],
            len(claims)
        )
    })

    # Generate provider-based invoice IDs
    provider_sequence = (
        invoices.groupby("provider_id").cumcount() + 1
    )

    invoices.insert(
        0,
        "invoice_id",
        [
            f"INV-PRV-{provider_id}-{sequence:06d}"
            for provider_id, sequence in zip(
                invoices["provider_id"],
                provider_sequence
            )
        ]
    )

    # 2. Generate one payment for each claim
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

    # 3. Validate generated financial records
    if not invoices["claim_id"].isin(claims["claim_id"]).all():
        raise ValueError("Invalid invoice claim references.")

    if not invoices["provider_id"].isin(
        claims["provider_id"]
    ).all():
        raise ValueError("Invalid invoice provider references.")

    if not payments["claim_id"].isin(claims["claim_id"]).all():
        raise ValueError("Invalid payment claim references.")

    if (
        payments["payment_amount"]
        > claims["approved_amount"].reset_index(drop=True)
    ).any():
        raise ValueError("Payment exceeds approved claim amount.")

    # 4. Save financial datasets
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

    print("\nValidation:")
    print("Invoice IDs unique:", invoices["invoice_id"].is_unique)
    print("Payment IDs unique:", payments["payment_id"].is_unique)
    print("All invoice claim references valid: Yes")
    print("All payment claim references valid: Yes")

    return invoices, payments


if __name__ == "__main__":
    generate_financial_data()
