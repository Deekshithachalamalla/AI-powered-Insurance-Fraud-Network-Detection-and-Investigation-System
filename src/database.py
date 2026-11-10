
import sqlite3
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
GROUND_TRUTH_DIR = Path("data/ground_truth")

DB_DIR = Path("data")
DB_PATH = DB_DIR / "insurance_fraud.db"
TEMP_DB_PATH = DB_DIR / "insurance_fraud_temp.db"


SCHEMAS = {
    "claimants": """
        claimant_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        city TEXT
    """,

    "policies": """
        policy_id TEXT PRIMARY KEY,
        claimant_id TEXT NOT NULL,
        policy_type TEXT,
        premium REAL,
        policy_status TEXT,
        FOREIGN KEY (claimant_id) REFERENCES claimants(claimant_id)
    """,

    "providers": """
        provider_id TEXT PRIMARY KEY,
        provider_name TEXT,
        provider_type TEXT,
        city TEXT
    """,

    "incidents": """
        incident_id TEXT PRIMARY KEY,
        incident_type TEXT,
        incident_city TEXT,
        incident_date TEXT
    """,

    "claims": """
        claim_id TEXT PRIMARY KEY,
        claimant_id TEXT NOT NULL,
        policy_id TEXT NOT NULL,
        incident_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        claim_amount REAL,
        approved_amount REAL,
        claim_status TEXT,
        FOREIGN KEY (claimant_id) REFERENCES claimants(claimant_id),
        FOREIGN KEY (policy_id) REFERENCES policies(policy_id),
        FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    """,

    # Composite primary key allows duplicate invoice IDs
    # across different claims.
    "invoices": """
        invoice_id TEXT NOT NULL,
        claim_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        invoice_amount REAL,
        invoice_status TEXT,
        PRIMARY KEY (invoice_id, claim_id),
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    """,

    "payments": """
        payment_id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        payment_amount REAL,
        payment_status TEXT,
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
    """,

    "relationship_edges": """
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        relationship TEXT NOT NULL
    """,

    "fraud_results": """
        claim_id TEXT PRIMARY KEY,
        claimant_id TEXT,
        policy_id TEXT,
        incident_id TEXT,
        provider_id TEXT,
        claim_amount REAL,
        approved_amount REAL,
        claim_status TEXT,
        risk_score REAL,
        risk_reasons TEXT,
        claimant_claim_count INTEGER,
        amount_difference REAL,
        provider_claim_count INTEGER,
        provider_claimant_count INTEGER,
        risk_level TEXT,
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
    """,

    "investigations": """
        investigation_id TEXT PRIMARY KEY,
        claim_id TEXT NOT NULL,
        risk_score REAL,
        risk_level TEXT,
        evidence TEXT,
        investigation_status TEXT,
        assigned_to TEXT,
        created_date TEXT,
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
    """,

    "financial_exceptions": """
        investigation_id TEXT PRIMARY KEY,
        exception_type TEXT,
        record_id TEXT,
        claim_id TEXT,
        description TEXT,
        status TEXT,
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
    """,

    "ground_truth": """
        claim_id TEXT PRIMARY KEY,
        is_fraud INTEGER,
        fraud_pattern TEXT,
        FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
    """,

    "investigation_status_history": """
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        investigation_id TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by TEXT,
        changed_at TEXT,
        change_reason TEXT,
        FOREIGN KEY (investigation_id)
            REFERENCES investigations(investigation_id)
    """,

    "financial_exception_status_history": """
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        investigation_id TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        changed_by TEXT,
        changed_at TEXT,
        change_reason TEXT,
        FOREIGN KEY (investigation_id)
            REFERENCES financial_exceptions(investigation_id)
    """
}


def create_database():
    print("Creating insurance database...\n")

    DB_DIR.mkdir(parents=True, exist_ok=True)

    if TEMP_DB_PATH.exists():
        TEMP_DB_PATH.unlink()

    files = {
        "claimants": RAW_DIR / "claimants.csv",
        "policies": RAW_DIR / "policies.csv",
        "providers": RAW_DIR / "providers.csv",
        "incidents": RAW_DIR / "incidents.csv",
        "claims": RAW_DIR / "claims.csv",
        "invoices": RAW_DIR / "invoices.csv",
        "payments": RAW_DIR / "payments.csv",
        "relationship_edges": PROCESSED_DIR / "relationship_edges.csv",
        "fraud_results": PROCESSED_DIR / "fraud_results.csv",
        "investigations": PROCESSED_DIR / "investigations.csv",
        "financial_exceptions": PROCESSED_DIR / "financial_exceptions.csv",
        "ground_truth": GROUND_TRUTH_DIR / "ground_truth.csv",
        "investigation_status_history": (
            PROCESSED_DIR / "investigation_status_history.csv"
        ),
        "financial_exception_status_history": (
            PROCESSED_DIR / "financial_exception_status_history.csv"
        )
    }

    optional_files = {
        "investigation_status_history",
        "financial_exception_status_history"
    }

    connection = sqlite3.connect(TEMP_DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Create database tables
        for table_name, schema in SCHEMAS.items():
            connection.execute(
                f"CREATE TABLE {table_name} ({schema})"
            )

        # Import CSV files
        for table_name, file_path in files.items():

            if not file_path.exists():
                if table_name in optional_files:
                    print(f"Optional history file not found: {file_path}")
                    continue

                raise FileNotFoundError(
                    f"Required file not found: {file_path}"
                )

            dataframe = pd.read_csv(file_path)

            if dataframe.columns.duplicated().any():
                raise ValueError(
                    f"Duplicate column names found in {table_name}"
                )

            # Convert ground truth labels
            if table_name == "ground_truth":
                dataframe["is_fraud"] = (
                    dataframe["is_fraud"]
                    .map({
                        True: 1,
                        False: 0,
                        "True": 1,
                        "False": 0,
                        1: 1,
                        0: 0
                    })
                )

                if dataframe["is_fraud"].isna().any():
                    raise ValueError(
                        "Invalid ground truth labels found."
                    )

            # Check CSV columns against database schema
            table_info = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

            expected_columns = [
                row[1]
                for row in table_info
                if not (
                    row[5] == 1
                    and row[2].upper() == "INTEGER"
                )
            ]

            if set(dataframe.columns) != set(expected_columns):
                raise ValueError(
                    f"Column mismatch in {table_name}.\n"
                    f"Expected: {expected_columns}\n"
                    f"Found: {list(dataframe.columns)}"
                )

            dataframe.to_sql(
                table_name,
                connection,
                if_exists="append",
                index=False
            )

            print(
                f"Loaded {table_name}: {len(dataframe)} records"
            )

        # Validate foreign-key relationships
        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise ValueError(
                f"Foreign-key violations: {violations[:10]}"
            )

        # Verify duplicate invoice IDs are stored correctly
        duplicate_invoices = connection.execute("""
            SELECT invoice_id, COUNT(*)
            FROM invoices
            GROUP BY invoice_id
            HAVING COUNT(*) > 1
        """).fetchall()

        print(
            "Duplicate invoice IDs stored:",
            len(duplicate_invoices)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        connection.close()

        if TEMP_DB_PATH.exists():
            TEMP_DB_PATH.unlink()

        raise

    connection.close()

    # Replace old database only after successful validation
    TEMP_DB_PATH.replace(DB_PATH)

    print("\nDatabase created successfully!")
    print("All foreign-key checks passed.")
    print("Total tables:", len(SCHEMAS))
    print("Database location:", DB_PATH)


if __name__ == "__main__":
    create_database()
