
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data/processed")
OUTPUT_DIR = Path("data/processed")

INVESTIGATIONS_FILE = OUTPUT_DIR / "investigations.csv"
HISTORY_FILE = OUTPUT_DIR / "investigation_status_history.csv"


def create_investigations():
    print("Creating investigation records...\n")

    results = pd.read_csv(DATA_DIR / "fraud_results.csv")

    # Select medium and high-risk claims
    suspicious = results[
        results["risk_level"].isin(["Medium", "High"])
    ].copy()

    # Load previous investigation records
    if INVESTIGATIONS_FILE.exists():
        old_investigations = pd.read_csv(INVESTIGATIONS_FILE)
    else:
        old_investigations = pd.DataFrame()

    # Preserve previous investigation details by claim ID
    previous_records = {}

    if not old_investigations.empty:
        for _, row in old_investigations.iterrows():
            previous_records[str(row["claim_id"])] = row.to_dict()

    # Load previous history
    if HISTORY_FILE.exists():
        history = pd.read_csv(HISTORY_FILE)
    else:
        history = pd.DataFrame(columns=[
            "investigation_id",
            "old_status",
            "new_status",
            "changed_by",
            "changed_at",
            "change_reason"
        ])

    investigations = []
    new_events = []

    for _, row in suspicious.iterrows():

        claim_id = str(row["claim_id"])

        if claim_id in previous_records:

            # Preserve existing investigation ID and status
            previous = previous_records[claim_id]

            investigation = {
                "investigation_id": previous["investigation_id"],
                "claim_id": claim_id,
                "risk_score": row["risk_score"],
                "risk_level": row["risk_level"],
                "evidence": row["risk_reasons"],
                "investigation_status": previous["investigation_status"],
                "assigned_to": previous["assigned_to"],
                "created_date": previous["created_date"]
            }

        else:

            # Create a new investigation
            investigation_id = (
                f"INVG-2026-{len(investigations) + 1:06d}"
            )

            created_date = datetime.now().strftime("%Y-%m-%d")

            investigation = {
                "investigation_id": investigation_id,
                "claim_id": claim_id,
                "risk_score": row["risk_score"],
                "risk_level": row["risk_level"],
                "evidence": row["risk_reasons"],
                "investigation_status": "Open",
                "assigned_to": "Risk Analyst",
                "created_date": created_date
            }

            # Record initial status event
            new_events.append({
                "investigation_id": investigation_id,
                "old_status": None,
                "new_status": "Open",
                "changed_by": "System",
                "changed_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "change_reason": "Investigation created"
            })

        investigations.append(investigation)

    # Save investigation records
    investigation_df = pd.DataFrame(investigations)

    investigation_df.to_csv(
        INVESTIGATIONS_FILE,
        index=False
    )

    # Append only new history events
    if new_events:
        history = pd.concat(
            [history, pd.DataFrame(new_events)],
            ignore_index=True
        )

    history.to_csv(HISTORY_FILE, index=False)

    print("Investigation records created!")
    print("Total investigations:", len(investigation_df))
    print("New investigations:", len(new_events))

    print("\nInvestigation status:")
    if not investigation_df.empty:
        print(
            investigation_df[
                "investigation_status"
            ].value_counts()
        )

    print("\nHistory events:", len(history))
    print("Saved to:", INVESTIGATIONS_FILE)
    print("History saved to:", HISTORY_FILE)

    return investigation_df


if __name__ == "__main__":
    create_investigations()
