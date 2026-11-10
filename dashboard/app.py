
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import networkx as nx
from pathlib import Path
from datetime import datetime

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Insurance Fraud Detection System",
    page_icon="🔍",
    layout="wide"
)

DB_PATH = Path("data/insurance_fraud.db")
PROCESSED_DIR = Path("data/processed")

EXCEPTIONS_PATH = PROCESSED_DIR / "financial_exceptions.csv"
INVESTIGATIONS_PATH = PROCESSED_DIR / "investigations.csv"
EXCEPTION_HISTORY_PATH = (
    PROCESSED_DIR / "financial_exception_status_history.csv"
)
INVESTIGATION_HISTORY_PATH = (
    PROCESSED_DIR / "investigation_status_history.csv"
)
EDGES_PATH = PROCESSED_DIR / "relationship_edges.csv"

st.title("🔍 AI-Powered Insurance Fraud Network Detection")
st.write("Insurance Claims Risk Analysis and Investigation Dashboard")


# ==================================================
# LOAD DATABASE DATA
# ==================================================

@st.cache_data
def load_data():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Please run the project pipeline first."
        )

    with sqlite3.connect(DB_PATH) as connection:

        fraud = pd.read_sql(
            "SELECT * FROM fraud_results", connection
        )

        investigations = pd.read_sql(
            "SELECT * FROM investigations", connection
        )

        claims = pd.read_sql(
            "SELECT * FROM claims", connection
        )

        financial_exceptions = pd.read_sql(
            "SELECT * FROM financial_exceptions", connection
        )

        investigation_history = pd.read_sql(
            "SELECT * FROM investigation_status_history",
            connection
        )

        exception_history = pd.read_sql(
            "SELECT * FROM financial_exception_status_history",
            connection
        )

    return (
        fraud,
        investigations,
        claims,
        financial_exceptions,
        investigation_history,
        exception_history
    )


try:
    (
        fraud,
        investigations,
        claims,
        financial_exceptions,
        investigation_history,
        exception_history
    ) = load_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()


# ==================================================
# STATUS UPDATE FUNCTION
# ==================================================

def update_status(
    table_name,
    history_table,
    id_column,
    record_id,
    old_status,
    new_status,
    reason,
    csv_path
):

    if old_status == new_status:
        st.warning("Please select a different status.")
        return False

    changed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed_by = "Risk Analyst"

    try:

        with sqlite3.connect(DB_PATH) as connection:

            connection.execute("PRAGMA foreign_keys = ON")

            # Update current status without replacing the table
            cursor = connection.execute(
                f"""
                UPDATE {table_name}
                SET {"status" if table_name == "financial_exceptions" else "investigation_status"} = ?
                WHERE {id_column} = ?
                """,
                (new_status, record_id)
            )

            if cursor.rowcount != 1:
                raise ValueError("Investigation record not found.")

            # Record status change in audit history
            connection.execute(
                f"""
                INSERT INTO {history_table}
                (
                    investigation_id,
                    old_status,
                    new_status,
                    changed_by,
                    changed_at,
                    change_reason
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    old_status,
                    new_status,
                    changed_by,
                    changed_at,
                    reason
                )
            )

        # Update corresponding CSV file
        dataframe = pd.read_csv(csv_path)

        status_column = (
            "status"
            if table_name == "financial_exceptions"
            else "investigation_status"
        )

        dataframe.loc[
            dataframe[id_column] == record_id,
            status_column
        ] = new_status

        dataframe.to_csv(csv_path, index=False)

        st.cache_data.clear()
        return True

    except Exception as error:
        st.error(f"Status update failed: {error}")
        return False


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

    # Dashboard metrics
    total_claims = len(fraud)
    suspicious_claims = int((fraud["risk_score"] >= 30).sum())
    high_risk = int((fraud["risk_level"] == "High").sum())
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

    st.plotly_chart(fig, use_container_width=True)

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

    st.plotly_chart(fig2, use_container_width=True)

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
    # REGULAR INVESTIGATION MANAGEMENT
    # ----------------------------------------------

    st.divider()
    st.subheader("Claim Investigation Management")

    st.dataframe(
        investigations,
        use_container_width=True,
        hide_index=True
    )

    if not investigations.empty:

        selected_investigation = st.selectbox(
            "Select Claim Investigation",
            investigations["investigation_id"].tolist(),
            key="claim_investigation"
        )

        selected_row = investigations[
            investigations["investigation_id"]
            == selected_investigation
        ].iloc[0]

        st.write("**Claim ID:**", selected_row["claim_id"])
        st.write(
            "**Current Status:**",
            selected_row["investigation_status"]
        )

        investigation_statuses = [
            "Open",
            "Under Review",
            "Confirmed Fraud",
            "False Positive",
            "Closed"
        ]

        current_status = selected_row["investigation_status"]

        new_status = st.selectbox(
            "Choose Investigation Status",
            investigation_statuses,
            index=(
                investigation_statuses.index(current_status)
                if current_status in investigation_statuses
                else 0
            ),
            key="claim_status"
        )

        investigation_reason = st.text_input(
            "Reason for Status Change",
            key="claim_reason"
        )

        if st.button("Update Claim Investigation"):

            if not investigation_reason.strip():
                st.warning("Please enter a reason for the change.")

            elif update_status(
                table_name="investigations",
                history_table="investigation_status_history",
                id_column="investigation_id",
                record_id=selected_investigation,
                old_status=current_status,
                new_status=new_status,
                reason=investigation_reason,
                csv_path=INVESTIGATIONS_PATH
            ):
                st.success("Claim investigation status updated!")
                st.rerun()

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

    col1.metric("Total Financial Exceptions", total_exceptions)
    col2.metric("Duplicate Invoices", int(duplicate_invoices))
    col3.metric("Excess Payments", int(excess_payments))

    # ----------------------------------------------
    # FINANCIAL EXCEPTION INVESTIGATION
    # ----------------------------------------------

    st.subheader("Financial Exception Investigation")

    st.dataframe(
        financial_exceptions,
        use_container_width=True,
        hide_index=True
    )

    if not financial_exceptions.empty:

        selected_id = st.selectbox(
            "Select Financial Investigation",
            financial_exceptions["investigation_id"].tolist(),
            key="financial_investigation"
        )

        selected_exception = financial_exceptions[
            financial_exceptions["investigation_id"] == selected_id
        ].iloc[0]

        st.write(
            "**Exception Type:**",
            selected_exception["exception_type"]
        )

        st.write(
            "**Claim ID:**",
            selected_exception["claim_id"]
        )

        st.write(
            "**Description:**",
            selected_exception["description"]
        )

        statuses = [
            "Open",
            "Under Review",
            "Confirmed Issue",
            "False Positive",
            "Closed"
        ]

        current_status = selected_exception["status"]

        selected_status = st.selectbox(
            "Choose Financial Exception Status",
            statuses,
            index=(
                statuses.index(current_status)
                if current_status in statuses
                else 0
            ),
            key="financial_status"
        )

        financial_reason = st.text_input(
            "Reason for Financial Status Change",
            key="financial_reason"
        )

        if st.button("Save Financial Investigation Status"):

            if not financial_reason.strip():
                st.warning("Please enter a reason for the change.")

            elif update_status(
                table_name="financial_exceptions",
                history_table="financial_exception_status_history",
                id_column="investigation_id",
                record_id=selected_id,
                old_status=current_status,
                new_status=selected_status,
                reason=financial_reason,
                csv_path=EXCEPTIONS_PATH
            ):
                st.success("Financial exception status updated!")
                st.rerun()

    else:
        st.info("No financial exceptions are currently available.")

    # ----------------------------------------------
    # AUDIT HISTORY
    # ----------------------------------------------

    st.divider()
    st.subheader("Investigation Audit History")

    st.write("**Claim Investigation History**")

    st.dataframe(
        investigation_history,
        use_container_width=True,
        hide_index=True
    )

    st.write("**Financial Exception History**")

    st.dataframe(
        exception_history,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# TAB 2: FRAUD NETWORK VISUALIZATION
# ==================================================

with network_tab:

    st.header("🕸️ Insurance Fraud Network Visualization")

    if EDGES_PATH.exists():

        edges = pd.read_csv(EDGES_PATH)

        if not edges.empty:

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

            # Network edges
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
                line=dict(
                    width=0.7,
                    color="#999999"
                ),
                hoverinfo="none"
            )

            # Network nodes
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
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )

            st.plotly_chart(
                figure,
                use_container_width=True
            )

            # Network statistics
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

            st.subheader("Relationship Records")

            st.dataframe(
                edges,
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Blue: Other entities | Green: Policies | "
                "Red: Providers | Orange: Claims"
            )

        else:
            st.warning("No relationship records available.")

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
