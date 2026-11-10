
import pandas as pd
import networkx as nx
from pathlib import Path

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_relationships():
    print("Building insurance relationship network...")

    claimants = pd.read_csv(DATA_DIR / "claimants.csv")
    policies = pd.read_csv(DATA_DIR / "policies.csv")
    providers = pd.read_csv(DATA_DIR / "providers.csv")
    claims = pd.read_csv(DATA_DIR / "claims.csv")

    graph = nx.Graph()
    edges = []

    # Add claimant nodes
    for _, row in claimants.iterrows():
        graph.add_node(row["claimant_id"], node_type="Claimant")

    # Add policy nodes and claimant-policy relationships
    for _, row in policies.iterrows():
        graph.add_node(row["policy_id"], node_type="Policy")

        graph.add_edge(
            row["claimant_id"],
            row["policy_id"],
            relationship="OWNS"
        )

        edges.append({
            "source": row["claimant_id"],
            "target": row["policy_id"],
            "relationship": "OWNS"
        })

    # Add provider nodes
    for _, row in providers.iterrows():
        graph.add_node(row["provider_id"], node_type="Provider")

    # Add claim relationships
    for _, row in claims.iterrows():

        claim_id = row["claim_id"]

        graph.add_node(claim_id, node_type="Claim")

        relationships = [
            (row["claimant_id"], "SUBMITTED"),
            (row["policy_id"], "COVERED_BY"),
            (row["provider_id"], "HANDLED_BY")
        ]

        for related_id, relationship in relationships:
            graph.add_edge(
                claim_id,
                related_id,
                relationship=relationship
            )

            edges.append({
                "source": claim_id,
                "target": related_id,
                "relationship": relationship
            })

    # Save relationship edges
    edge_df = pd.DataFrame(edges)
    edge_df.to_csv(OUTPUT_DIR / "relationship_edges.csv", index=False)

    print("\nRelationship network created!")
    print("Total nodes:", graph.number_of_nodes())
    print("Total edges:", graph.number_of_edges())
    print("Connected groups:", nx.number_connected_components(graph))

    return graph


if __name__ == "__main__":
    build_relationships()
