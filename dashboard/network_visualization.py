
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path

DATA_PATH = Path("data/processed/relationship_edges.csv")


def create_network_graph():
    st.title("🕸️ Insurance Fraud Network Visualization")

    if not DATA_PATH.exists():
        st.error("Relationship data not found. Run relationship_builder.py first.")
        return

    edges = pd.read_csv(DATA_PATH)

    if edges.empty:
        st.warning("No relationship data available.")
        return

    graph = nx.Graph()

    for _, row in edges.iterrows():
        graph.add_edge(
            row["source"],
            row["target"],
            relationship=row["relationship"]
        )

    positions = nx.spring_layout(
        graph,
        seed=42,
        k=0.5
    )

    edge_x = []
    edge_y = []

    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=0.7, color="#999999"),
        hoverinfo="none"
    )

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node in graph.nodes():
        x, y = positions[node]

        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))

        if str(node).startswith("CLM"):
            node_colors.append("orange")
        elif str(node).startswith("PRV"):
            node_colors.append("red")
        elif str(node).startswith("POL"):
            node_colors.append("green")
        else:
            node_colors.append("blue")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=9,
            color=node_colors,
            line=dict(width=1, color="white")
        )
    )

    figure = go.Figure(
        data=[edge_trace, node_trace]
    )

    figure.update_layout(
        title="Claimant - Policy - Provider - Claim Network",
        showlegend=False,
        hovermode="closest",
        height=700,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    st.plotly_chart(figure, use_container_width=True)

    st.subheader("Network Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Nodes", graph.number_of_nodes())
    col2.metric("Total Connections", graph.number_of_edges())
    col3.metric(
        "Connected Groups",
        nx.number_connected_components(graph)
    )

    st.subheader("Relationship Records")

    st.dataframe(
        edges,
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    create_network_graph()
