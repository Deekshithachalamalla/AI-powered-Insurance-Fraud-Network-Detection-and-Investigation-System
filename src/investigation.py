
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/processed")


def create_investigations():
    print("Creating investigation records...\n")

    results = pd.read_csv(DATA_DIR / "fraud_results.csv")

    # Select medium and high-risk claims
    suspicious = results[
        results["risk_level"].isin(["Medium", "High"])
    ].copy()

    # Create investigation records
    investigations = pd.DataFrame({
        "investigation_id": [
            f"INVG-2026-{i:06d}"
            for i in range(1, len(suspicious) + 1)
        ],
        "claim_id": suspicious["claim_id"].values,
        "risk_score": suspicious["risk_score"].values,
        "risk_level": suspicious["risk_level"].values,
        "evidence": suspicious["risk_reasons"].values,
        "investigation_status": "Open",
        "assigned_to": "Risk Analyst",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    })

    # Save investigation records
    investigations.to_csv(
        OUTPUT_DIR / "investigations.csv",
        index=False
    )

    print("Investigation records created!")
    print("Total investigations:", len(investigations))

    print("\nInvestigation status:")
    print(investigations["investigation_status"].value_counts())

    print("\nSaved to data/processed/investigations.csv")

    return investigations


if __name__ == "__main__":
    create_investigations()
