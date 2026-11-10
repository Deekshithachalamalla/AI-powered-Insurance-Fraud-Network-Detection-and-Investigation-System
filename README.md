# AI-Powered Insurance Fraud Network Detection and Investigation System

An end-to-end insurance fraud detection and investigation platform that analyzes insurance claims, identifies suspicious patterns, detects financial anomalies, and visualizes relationships between claimants, policies, providers, incidents, and claims.

The system combines explainable rule-based risk scoring, relationship network analysis, financial validation, investigation management, audit history, and an interactive Streamlit dashboard to help investigators prioritize suspicious cases.

## 1. Problem Statement

Insurance fraud can involve suspicious claim patterns, duplicate invoices, excessive payments, and connections between multiple claimants and service providers.

Traditional claim-by-claim reviews may fail to identify relationships across multiple records.

This project addresses these challenges by building a centralized system that:

- Analyzes insurance claims.
- Identifies suspicious claim patterns.
- Assigns explainable risk scores to claims.
- Detects duplicate invoices and excessive payments.
- Builds relationship networks between connected entities.
- Supports claim and financial exception investigations.
- Maintains investigation status history and audit records.
- Displays results through an interactive dashboard.

## 2. Project Objectives

- Generate and manage structured synthetic insurance datasets.
- Maintain relationships between claimants, policies, providers, incidents, and claims.
- Validate primary keys, foreign keys, and data integrity.
- Detect suspicious claims using explainable rule-based logic.
- Identify financial transaction anomalies.
- Visualize entity relationships using NetworkX.
- Manage investigation statuses and record status changes.
- Evaluate detection results using precision, recall, and F1-score where the available labels support meaningful evaluation.
- Store structured information in an SQLite database.

## 3. Key Features

### A. Synthetic Insurance Data Generation

Generates structured datasets for:

- Claimants
- Policies
- Providers
- Incidents
- Claims
- Invoices
- Payments

### B. Data Validation

Validates data integrity through:

- Primary key uniqueness checks.
- Foreign key validation.
- Missing-value checks.
- Claimant-policy consistency checks.
- Financial amount validation.
- Investigation history validation.
- Relationship network endpoint validation.

### C. Relationship Network Analysis

Uses NetworkX to create connections between:

- Claimants
- Policies
- Providers
- Incidents
- Claims
- Invoices
- Payments

The network helps identify entities connected through shared information and transaction relationships.

### D. Explainable Rule-Based Fraud Detection

The system assigns risk scores using configurable detection rules.

| Detection Rule | Risk Score |
|---|---:|
| Claimant has at least 4 claims | +30 |
| Claim amount is at least 350,000 | +30 |
| Claim amount exceeds approved amount by at least 200,000 | +20 |
| Shared claimant phone number | +20 |
| Provider has at least 12 claims | +20 |
| Provider connected to at least 8 distinct claimants | +40 |

The final risk score is capped at 100.

**Risk Categories**

- Low: 0–29
- Medium: 30–59
- High: 60–100

Each suspicious claim can include reasons explaining why it received its risk score.

Risk indicators help prioritize investigations; they are not proof of fraud.

### E. Financial Anomaly Detection

Implements financial validation rules to identify:

1. Duplicate invoice IDs across different claims.
2. Payments exceeding the approved claim amount.

Detected financial exceptions receive unique investigation IDs and an initial Open status.

### F. Claim Investigation Management

Investigators can update claim investigation statuses through the dashboard:

- Open
- Under Review
- Confirmed Fraud
- False Positive
- Closed

The system records investigation status changes, timestamps, and reasons in its audit history.

### G. Financial Exception Management

Financial exceptions have a separate investigation workflow:

- Open
- Under Review
- Confirmed Issue
- False Positive
- Closed

Status changes and their associated reasons are recorded in the database audit history.

### H. Interactive Streamlit Dashboard

Built using Streamlit and Plotly.

Dashboard capabilities include:

- Total claims and suspicious claims.
- High-risk claim metrics.
- Risk distribution charts.
- Risk score analysis.
- Suspicious claims table.
- Claim investigation management.
- Financial anomaly metrics.
- Financial exception management.
- Investigation status updates.
- Investigation audit history.
- Fraud relationship network visualization.
- Network statistics.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data processing and analysis |
| NumPy | Synthetic data generation |
| Scikit-learn | Evaluation metrics |
| NetworkX | Relationship network analysis |
| Plotly | Interactive charts and graphs |
| Streamlit | Interactive dashboard |
| SQLite | Database storage |
| Pytest | Automated testing |
| Git and GitHub | Version control |

## 5. Project Structure

```text
AI-powered-Insurance-Fraud-Network-Detection-and-Investigation-System/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── ground_truth/
│   └── insurance_fraud.db
│
├── src/
│   ├── data_generator.py
│   ├── data_validation.py
│   ├── relationship_builder.py
│   ├── fraud_detection.py
│   ├── investigation.py
│   ├── database.py
│   ├── evaluate_model.py
│   ├── inject_fraud_patterns.py
│   ├── financial_data.py
│   ├── inject_financial_anomalies.py
│   └── financial_anomaly_detection.py
│
├── dashboard/
│   ├── app.py
│   └── network_visualization.py
│
├── tests/
│   └── test_system.py
│
├── docs/
│   ├── data_dictionary.md
│   └── schema.md
│
├── screenshots/
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/Deekshithachalamalla/AI-powered-Insurance-Fraud-Network-Detection-and-Investigation-System.git
```

### Step 2: Navigate to the project directory

```bash
cd AI-powered-Insurance-Fraud-Network-Detection-and-Investigation-System
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

## 7. Running the Project

Run the following commands from the project root in the specified order.

**Important:** These commands regenerate synthetic data and investigation outputs. Running them again can reset previously generated investigation statuses.

### Step 1: Generate synthetic insurance data

```bash
python src/data_generator.py
```

### Step 2: Generate invoice and payment data

```bash
python src/financial_data.py
```

### Step 3: Inject sample fraud patterns

```bash
python src/inject_fraud_patterns.py
```

### Step 4: Inject financial anomalies

```bash
python src/inject_financial_anomalies.py
```

### Step 5: Build the relationship network

```bash
python src/relationship_builder.py
```

### Step 6: Detect suspicious claims

```bash
python src/fraud_detection.py
```

### Step 7: Detect financial anomalies

```bash
python src/financial_anomaly_detection.py
```

### Step 8: Create claim investigations

```bash
python src/investigation.py
```

### Step 9: Create the SQLite database

```bash
python src/database.py
```

### Step 10: Validate the generated data

```bash
python src/data_validation.py
```

### Step 11: Run automated tests

```bash
python -m pytest tests/ -v
```

### Step 12: Evaluate detection results

```bash
python src/evaluate_model.py
```

### Step 13: Launch the dashboard

```bash
python -m streamlit run dashboard/app.py
```

The dashboard will open in your browser.

## 8. Current Demonstration Results

The current synthetic demonstration dataset produces the following results:

| Metric | Result |
|---|---:|
| Claimants | 100 |
| Policies | 150 |
| Providers | 30 |
| Incidents | 200 |
| Claims | 200 |
| Suspicious claims | 167 |
| High-risk claims | 96 |
| Investigations | 167 |
| Financial exceptions | 3 |
| Duplicate invoice exceptions | 2 |
| Excess payment exceptions | 1 |
| Relationship network nodes | 1,079 |
| Relationship network edges | 1,550 |
| Connected groups | 34 |
| SQLite database tables | 14 |

### Automated Testing

Latest verified Pytest results:

```text
12 passed in 1.03s
```

All 12 implemented automated tests passed in the latest test run.

### Data Validation

Latest verified validation results:

- Data validation errors: 0
- Expected warnings: 1
- The expected warning relates to an intentionally duplicated invoice ID used for anomaly detection.

### Detection Evaluation

The project includes an evaluation script that calculates metrics such as:

- Precision
- Recall
- F1-score

The synthetic dataset currently has 16 positive ground-truth labels after injecting fraud and financial anomaly patterns.

Evaluation metrics should be interpreted cautiously when the available labelled examples or class coverage are insufficient. These results do not establish real-world fraud detection accuracy.

## 9. Database

The system uses SQLite for structured data storage.

Database location:

```text
data/insurance_fraud.db
```

The database contains 14 tables covering:

- Claimants
- Policies
- Providers
- Incidents
- Claims
- Relationship edges
- Fraud results
- Investigations
- Invoices
- Payments
- Financial exceptions
- Investigation and audit-related records

The database uses primary key and foreign key constraints to maintain data integrity.

## 10. Live Demo

**Try the deployed application:**

[Open Insurance Fraud Detection Dashboard](https://bb5cdkfam5jxp4ivv894lp.streamlit.app/)

Explore claim risk scoring, suspicious claim investigations, financial anomaly detection, investigation history, and fraud relationship network visualization.

## 11. Project Screenshots

### 1. Dashboard Overview

![Dashboard Overview](screenshots/dashboard_overview.png)

### 2. Claim Risk Distribution

![Risk Distribution](screenshots/risk_distribution.png)

### 3. Risk Score Analysis

![Risk Score Analysis](screenshots/risk_score_analysis.png)

### 4. Suspicious Claims and Investigations

![Suspicious Claims and Investigations](screenshots/suspicious_claims_investigations.png)

### 5. Financial Anomaly Detection

![Financial Anomaly Detection](screenshots/financial_anomaly_detection.png)

### 6. Fraud Network Visualization

![Fraud Network Graph](screenshots/fraud_network_graph.png)

### 7. Network Statistics

![Network Statistics](screenshots/network_statistics.png)

## 12. Future Enhancements

- Machine learning-based fraud classification.
- Advanced graph-based fraud detection.
- Real-time claim monitoring.
- Interactive investigator assignment.
- Role-based access control.
- Additional financial anomaly detection rules.
- Larger labelled datasets for reliable model evaluation.
- Explainable AI reports for investigators.

## 13. Limitations

- The current datasets are synthetic and do not represent real insurance company records.
- Fraud detection currently uses rule-based scoring rather than a trained machine learning classifier.
- Evaluation results depend on the available synthetic ground-truth labels.
- Detection performance requires validation on larger, representative real-world datasets.
- Risk flags indicate suspicious activity and do not establish confirmed fraud.

