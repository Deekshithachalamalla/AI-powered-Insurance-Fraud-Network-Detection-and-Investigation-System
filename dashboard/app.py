
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import networkx as nx
from pathlib import Path

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Insurance Fraud Detection System",
    page_icon="🔍",
    layout="wide"
)

DB_PATH = Path("data/insurance_fraud.db")
EXCEPTIONS_PATH = Path("data/processed/financial_exceptions.csv")
EDGES_PATH = Path("data/processed/relationship_edges.csv")

st.title("🔍 AI-Powered Insurance Fraud Network Detection")
st.write("Insurance Claims Risk Analysis and Investigation Dashboard")


# ==================================================
# LOAD DATABASE DATA
# ==================================================

@st.cache_data
def load_data():

    connection = sqlite3.connect(DB_PATH)

    fraud = pd.read_sql(
        "SELECT * FROM fraud_results",
        connection
    )

    investigations = pd.read_sql(
        "SELECT * FROM investigations",
        connection
    )

    claims = pd.read_sql(
        "SELECT * FROM claims",
        connection
    )

    financial_exceptions = pd.read_sql(
        "SELECT * FROM financial_exceptions",
        connection
    )

    connection.close()

    return fraud, investigations, claims, financial_exceptions


fraud, investigations, claims, financial_exceptions = load_data()


# ==================================================
# DASHBOARD TABS
# ==================================================

analysis_tab, network_tab = st.tabs([
    "📊 Fraud Analysis & Investigation",
    "🕸️ Fraud Network Visualization"
])


# ==================================================
# TAB 1: FRAUD ANALYSIS AND INVESTIGATION
# ==================================================

with analysis_tab:

    st.header("Fraud Risk Analysis")

    # Sidebar filters
    st.sidebar.header("Dashboard Filters")

    risk_options = st.sidebar.multiselect(
        "Select Risk Level",
        options=["Low", "Medium", "High"],
        default=["Low", "Medium", "High"]
    )

    filtered = fraud[
        fraud["risk_level"].isin(risk_options)
    ]

    # Main dashboard metrics
    total_claims = len(fraud)

    suspicious_claims = (
        fraud["risk_score"] >= 30
    ).sum()

    high_risk = (
        fraud["risk_level"] == "High"
    ).sum()

    total_investigations = len(investigations)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Claims", total_claims)
    col2.metric("Suspicious Claims", suspicious_claims)
    col3.metric("High Risk Claims", high_risk)
    col4.metric("Investigations", total_investigations)

    st.divider()

    # ----------------------------------------------
    # CLAIM RISK DISTRIBUTION
    # ----------------------------------------------

    st.subheader("Claim Risk Distribution")

    risk_counts = (
        fraud["risk_level"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "Number of Claims"
    ]

    fig = px.pie(
        risk_counts,
        names="Risk Level",
        values="Number of Claims",
        title="Risk Level Distribution",
        hole=0.4
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ----------------------------------------------
    # RISK SCORE ANALYSIS
    # ----------------------------------------------

    st.subheader("Risk Score Analysis")

    fig2 = px.histogram(
        fraud,
        x="risk_score",
        color="risk_level",
        title="Distribution of Claim Risk Scores",
        labels={
            "risk_score": "Risk Score",
            "count": "Number of Claims"
        }
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # ----------------------------------------------
    # SUSPICIOUS CLAIMS
    # ----------------------------------------------

    st.subheader("Suspicious Claims")

    suspicious = filtered[
        filtered["risk_score"] >= 30
    ]

    st.dataframe(
        suspicious[
            [
                "claim_id",
                "claimant_id",
                "provider_id",
                "claim_amount",
                "risk_score",
                "risk_level",
                "risk_reasons"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # INVESTIGATION MANAGEMENT
    # ----------------------------------------------

    st.subheader("Investigation Management")

    st.dataframe(
        investigations,
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # FINANCIAL ANOMALY DETECTION
    # ----------------------------------------------

    st.divider()

    st.subheader("Financial Anomaly Detection")

    total_exceptions = len(financial_exceptions)

    duplicate_invoices = (
        financial_exceptions["exception_type"]
        == "Duplicate Invoice"
    ).sum()

    excess_payments = (
        financial_exceptions["exception_type"]
        == "Excess Payment"
    ).sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Financial Exceptions",
        total_exceptions
    )

    col2.metric(
        "Duplicate Invoices",
        int(duplicate_invoices)
    )

    col3.metric(
        "Excess Payments",
        int(excess_payments)
    )

    # ----------------------------------------------
    # FINANCIAL EXCEPTION INVESTIGATION
    # ----------------------------------------------

    st.subheader("Financial Exception Investigation")

    st.dataframe(
        financial_exceptions,
        use_container_width=True,
        hide_index=True
    )

    st.write("### Update Investigation Status")

    if not financial_exceptions.empty:

        selected_id = st.selectbox(
            "Select Investigation ID",
            financial_exceptions["investigation_id"].tolist()
        )

        selected_row = financial_exceptions[
            financial_exceptions["investigation_id"]
            == selected_id
        ].iloc[0]

        st.write(
            "**Exception Type:**",
            selected_row["exception_type"]
        )

        st.write(
            "**Claim ID:**",
            selected_row["claim_id"]
        )

        st.write(
            "**Description:**",
            selected_row["description"]
        )

        statuses = [
            "Open",
            "Under Review",
            "Confirmed Issue",
            "False Positive",
            "Closed"
        ]

        current_status = selected_row["status"]

        selected_status = st.selectbox(
            "Choose New Status",
            statuses,
            index=(
                statuses.index(current_status)
                if current_status in statuses
                else 0
            )
        )

        if st.button("Save Investigation Status"):

            financial_exceptions.loc[
                financial_exceptions["investigation_id"]
                == selected_id,
                "status"
            ] = selected_status

            # Save changes to CSV
            financial_exceptions.to_csv(
                EXCEPTIONS_PATH,
                index=False
            )

            # Save changes to SQLite
            connection = sqlite3.connect(DB_PATH)

            financial_exceptions.to_sql(
                "financial_exceptions",
                connection,
                if_exists="replace",
                index=False
            )

            connection.close()

            st.cache_data.clear()

            st.success(
                f"Investigation {selected_id} "
                f"updated to {selected_status}!"
            )

            st.rerun()

    else:

        st.info(
            "No financial exceptions are currently available."
        )


# ==================================================
# TAB 2: FRAUD NETWORK VISUALIZATION
# ==================================================

with network_tab:

    st.header("🕸️ Insurance Fraud Network Visualization")

    if EDGES_PATH.exists():

        edges = pd.read_csv(EDGES_PATH)

        if not edges.empty:

            # --------------------------------------
            # CREATE NETWORK GRAPH
            # --------------------------------------

            graph = nx.Graph()

            for _, row in edges.iterrows():

                graph.add_edge(
                    row["source"],
                    row["target"],
                    relationship=row["relationship"]
                )

            # Calculate node positions
            positions = nx.spring_layout(
                graph,
                seed=42,
                k=0.5
            )

            # --------------------------------------
            # CREATE NETWORK EDGES
            # --------------------------------------

            edge_x = []
            edge_y = []

            for source, target in graph.edges():

                x0, y0 = positions[source]
                x1, y1 = positions[target]

                edge_x.extend([
                    x0,
                    x1,
                    None
                ])

                edge_y.extend([
                    y0,
                    y1,
                    None
                ])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(
                    width=0.7,
                    color="#999999"
                ),
                hoverinfo="none"
            )

            # --------------------------------------
            # CREATE NETWORK NODES
            # --------------------------------------

            node_x = []
            node_y = []
            node_text = []
            node_colors = []

            for node in graph.nodes():

                x, y = positions[node]

                node_x.append(x)
                node_y.append(y)

                node_text.append(str(node))

                # Node colors based on entity type
                if str(node).startswith("CLM"):

                    node_colors.append("orange")

                elif str(node).startswith("PRV"):

                    node_colors.append("red")

                elif str(node).startswith("POL"):

                    node_colors.append("green")

                else:

                    node_colors.append("blue")

            # --------------------------------------
            # DISPLAY NODES WITHOUT PERMANENT LABELS
            # --------------------------------------

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers",
                hovertext=node_text,
                hovertemplate=(
                    "<b>Node ID:</b> %{hovertext}"
                    "<extra></extra>"
                ),
                marker=dict(
                    size=9,
                    color=node_colors,
                    line=dict(
                        width=1,
                        color="white"
                    )
                )
            )

            # --------------------------------------
            # CREATE FINAL NETWORK FIGURE
            # --------------------------------------

            figure = go.Figure(
                data=[
                    edge_trace,
                    node_trace
                ]
            )

            figure.update_layout(
                title="Claimant - Policy - Provider - Claim Network",
                showlegend=False,
                hovermode="closest",
                height=700,
                margin=dict(
                    l=10,
                    r=10,
                    t=50,
                    b=10
                ),
                xaxis=dict(
                    visible=False
                ),
                yaxis=dict(
                    visible=False
                )
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )

            # --------------------------------------
            # NETWORK STATISTICS
            # --------------------------------------

            st.subheader("Network Statistics")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Nodes",
                graph.number_of_nodes()
            )

            col2.metric(
                "Total Connections",
                graph.number_of_edges()
            )

            col3.metric(
                "Connected Groups",
                nx.number_connected_components(graph)
            )

            # --------------------------------------
            # RELATIONSHIP RECORDS
            # --------------------------------------

            st.subheader("Relationship Records")

            st.dataframe(
                edges,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Blue: Claimants | Green: Policies | "
                "Red: Providers | Orange: Claims"
            )

        else:

            st.warning(
                "No relationship records available."
            )

    else:

        st.error(
            "Relationship data not found. "
            "Run python src/relationship_builder.py first."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Insurance Fraud Detection System | "
    "Synthetic demonstration data | "
    "Risk flags indicate cases for review, not confirmed fraud."
)
