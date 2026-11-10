
import pandas as pd
import networkx as nx
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def test_claim_data_exists():
    claims = pd.read_csv(RAW_DIR / "claims.csv")

    assert len(claims) == 200
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

    assert claims["claimant_id"].isin(claimants["claimant_id"]).all()
    assert claims["policy_id"].isin(policies["policy_id"]).all()
    assert claims["provider_id"].isin(providers["provider_id"]).all()
    assert claims["incident_id"].isin(incidents["incident_id"]).all()


def test_fraud_results_exist():
    fraud = pd.read_csv(PROCESSED_DIR / "fraud_results.csv")

    assert len(fraud) == 200
    assert "risk_score" in fraud.columns
    assert "risk_level" in fraud.columns
    assert fraud["risk_score"].between(0, 100).all()


def test_financial_anomalies_detected():
    exceptions = pd.read_csv(
        PROCESSED_DIR / "financial_exceptions.csv"
    )

    assert len(exceptions) == 3
    assert exceptions["investigation_id"].notna().all()

    assert (
        exceptions["exception_type"] == "Duplicate Invoice"
    ).sum() == 2

    assert (
        exceptions["exception_type"] == "Excess Payment"
    ).sum() == 1


def test_relationship_network_exists():
    edges = pd.read_csv(
        PROCESSED_DIR / "relationship_edges.csv"
    )

    graph = nx.from_pandas_edgelist(
        edges,
        source="source",
        target="target"
    )

    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() == 750
