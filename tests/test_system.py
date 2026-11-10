
import pandas as pd
import networkx as nx
import sqlite3
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
DB_PATH = Path("data/insurance_fraud.db")


def test_claim_data_exists():
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    assert len(claims) > 0
    assert "claim_id" in claims.columns


def test_claim_ids_are_unique():
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    assert claims["claim_id"].is_unique


def test_claim_foreign_keys_are_valid():
    claims = pd.read_csv(RAW_DIR / "claims.csv")
    claimants = pd.read_csv(RAW_DIR / "claimants.csv")
    policies = pd.read_csv(RAW_DIR / "policies.csv")
    providers = pd.read_csv(RAW_DIR / "providers.csv")
    incidents = pd.read_csv(RAW_DIR / "incidents.csv")

    assert claims["claimant_id"].isin(
        claimants["claimant_id"]
    ).all()

    assert claims["policy_id"].isin(
        policies["policy_id"]
    ).all()

    assert claims["provider_id"].isin(
        providers["provider_id"]
    ).all()

    assert claims["incident_id"].isin(
        incidents["incident_id"]
    ).all()


def test_claimant_policy_relationship_is_valid():
    claims = pd.read_csv(RAW_DIR / "claims.csv")
    policies = pd.read_csv(RAW_DIR / "policies.csv")

    merged = claims.merge(
        policies[["policy_id", "claimant_id"]],
        on="policy_id",
        suffixes=("_claim", "_policy"),
        validate="many_to_one"
    )

    assert (
        merged["claimant_id_claim"]
        == merged["claimant_id_policy"]
    ).all()


def test_claim_financial_values_are_valid():
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    assert (claims["claim_amount"] >= 0).all()
    assert (claims["approved_amount"] >= 0).all()

    assert (
        claims["approved_amount"] <= claims["claim_amount"]
    ).all()


def test_fraud_results_exist():
    fraud = pd.read_csv(
        PROCESSED_DIR / "fraud_results.csv"
    )

    claims = pd.read_csv(RAW_DIR / "claims.csv")

    assert len(fraud) == len(claims)
    assert fraud["claim_id"].is_unique
    assert "risk_score" in fraud.columns
    assert "risk_level" in fraud.columns

    assert fraud["risk_score"].between(0, 100).all()

    assert fraud["risk_level"].isin(
        ["Low", "Medium", "High"]
    ).all()


def test_financial_anomalies_detected():
    exceptions = pd.read_csv(
        PROCESSED_DIR / "financial_exceptions.csv"
    )

    assert len(exceptions) >= 1
    assert exceptions["investigation_id"].notna().all()

    assert (
        exceptions["exception_type"] == "Duplicate Invoice"
    ).sum() >= 2

    assert (
        exceptions["exception_type"] == "Excess Payment"
    ).sum() >= 1


def test_relationship_network_exists():
    edges = pd.read_csv(
        PROCESSED_DIR / "relationship_edges.csv"
    )

    assert len(edges) > 0

    graph = nx.from_pandas_edgelist(
        edges,
        source="source",
        target="target"
    )

    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


def test_investigation_records_exist():
    investigations = pd.read_csv(
        PROCESSED_DIR / "investigations.csv"
    )

    assert investigations["investigation_id"].is_unique

    assert investigations["claim_id"].is_unique

    assert investigations[
        "investigation_status"
    ].notna().all()


def test_investigation_history_exists():
    history_file = (
        PROCESSED_DIR / "investigation_status_history.csv"
    )

    assert history_file.exists()

    history = pd.read_csv(history_file)

    assert {
        "investigation_id",
        "old_status",
        "new_status",
        "changed_by",
        "changed_at",
        "change_reason"
    }.issubset(history.columns)


def test_database_tables_exist():
    assert DB_PATH.exists()

    expected_tables = {
        "claimants",
        "policies",
        "providers",
        "incidents",
        "claims",
        "invoices",
        "payments",
        "relationship_edges",
        "fraud_results",
        "investigations",
        "financial_exceptions",
        "ground_truth",
        "investigation_status_history",
        "financial_exception_status_history"
    }

    with sqlite3.connect(DB_PATH) as connection:

        actual_tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'"
            ).fetchall()
        }

        assert expected_tables.issubset(actual_tables)


def test_database_foreign_keys_are_valid():
    with sqlite3.connect(DB_PATH) as connection:

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        assert violations == []
