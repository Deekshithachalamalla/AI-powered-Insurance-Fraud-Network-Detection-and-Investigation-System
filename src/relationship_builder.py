
import pandas as pd
import networkx as nx
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_relationships():
    print("Building insurance relationship network...")

    # Load master and transaction datasets
    claimants = pd.read_csv(DATA_DIR / "claimants.csv")
    policies = pd.read_csv(DATA_DIR / "policies.csv")
    providers = pd.read_csv(DATA_DIR / "providers.csv")
    incidents = pd.read_csv(DATA_DIR / "incidents.csv")
    claims = pd.read_csv(DATA_DIR / "claims.csv")

    graph = nx.Graph()
    edges = []

    def add_relationship(source, target, relationship):
        """Add a relationship to the graph and edge dataset."""
        graph.add_edge(
            source,
            target,
            relationship=relationship
        )

        edges.append({
            "source": source,
            "target": target,
            "relationship": relationship
        })

    # 1. Claimant nodes
    for _, row in claimants.iterrows():
        graph.add_node(
            row["claimant_id"],
            node_type="Claimant"
        )

    # 2. Policy nodes and ownership relationships
    for _, row in policies.iterrows():
        graph.add_node(
            row["policy_id"],
            node_type="Policy"
        )

        add_relationship(
            row["claimant_id"],
            row["policy_id"],
            "OWNS"
        )

    # 3. Provider nodes
    for _, row in providers.iterrows():
        graph.add_node(
            row["provider_id"],
            node_type="Provider"
        )

    # 4. Incident nodes
    for _, row in incidents.iterrows():
        graph.add_node(
            row["incident_id"],
            node_type="Incident"
        )

    # 5. Claim nodes and their relationships
    for _, row in claims.iterrows():
        claim_id = row["claim_id"]

        graph.add_node(
            claim_id,
            node_type="Claim"
        )

        add_relationship(
            claim_id,
            row["claimant_id"],
            "SUBMITTED"
        )

        add_relationship(
            claim_id,
            row["policy_id"],
            "COVERED_BY"
        )

        add_relationship(
            claim_id,
            row["provider_id"],
            "HANDLED_BY"
        )

        add_relationship(
            claim_id,
            row["incident_id"],
            "INVOLVES"
        )

    # 6. Invoice relationships (if invoice data exists)
    invoice_path = DATA_DIR / "invoices.csv"

    if invoice_path.exists():
        invoices = pd.read_csv(invoice_path)

        for _, row in invoices.iterrows():
            invoice_id = row["invoice_id"]

            graph.add_node(
                invoice_id,
                node_type="Invoice"
            )

            add_relationship(
                invoice_id,
                row["claim_id"],
                "BILLED_FOR"
            )

            add_relationship(
                invoice_id,
                row["provider_id"],
                "ISSUED_BY"
            )

    # 7. Payment relationships (if payment data exists)
    payment_path = DATA_DIR / "payments.csv"

    if payment_path.exists():
        payments = pd.read_csv(payment_path)

        for _, row in payments.iterrows():
            payment_id = row["payment_id"]

            graph.add_node(
                payment_id,
                node_type="Payment"
            )

            add_relationship(
                payment_id,
                row["claim_id"],
                "PAID_FOR"
            )

    # Save relationship edges
    edge_df = pd.DataFrame(
        edges,
        columns=["source", "target", "relationship"]
    )

    edge_df.to_csv(
        OUTPUT_DIR / "relationship_edges.csv",
        index=False
    )

    print("\nRelationship network created!")
    print("Total nodes:", graph.number_of_nodes())
    print("Total edges:", graph.number_of_edges())
    print(
        "Connected groups:",
        nx.number_connected_components(graph)
    )

    print("\nRelationship types:")
    print(edge_df["relationship"].value_counts())

    return graph


if __name__ == "__main__":
    build_relationships()
