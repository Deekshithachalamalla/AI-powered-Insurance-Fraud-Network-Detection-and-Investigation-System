
import sqlite3
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DB_DIR = Path("data")
DB_PATH = DB_DIR / "insurance_fraud.db"


def create_database():
    print("Creating insurance database...\n")

    connection = sqlite3.connect(DB_PATH)

    files = {
        "claimants": RAW_DIR / "claimants.csv",
        "policies": RAW_DIR / "policies.csv",
        "providers": RAW_DIR / "providers.csv",
        "incidents": RAW_DIR / "incidents.csv",
        "claims": RAW_DIR / "claims.csv",
        "relationship_edges": PROCESSED_DIR / "relationship_edges.csv",
        "fraud_results": PROCESSED_DIR / "fraud_results.csv",
                "investigations": PROCESSED_DIR / "investigations.csv",
        "invoices": RAW_DIR / "invoices.csv",
        "payments": RAW_DIR / "payments.csv",
        "financial_exceptions": PROCESSED_DIR / "financial_exceptions.csv"
    }

    for table_name, file_path in files.items():
        dataframe = pd.read_csv(file_path)

        dataframe.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False
        )

        print(f"Saved table: {table_name} ({len(dataframe)} records)")

    connection.close()

    print("\nDatabase created successfully!")
    print("Database location:", DB_PATH)


if __name__ == "__main__":
    create_database()
