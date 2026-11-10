
# Database Schema
## AI-Powered Insurance Fraud Network Detection and Investigation System

## 1. Overview

The system uses structured datasets to manage insurance claim information, identify suspicious relationships, detect financial anomalies, and support investigations.

The logical data model contains the following entities:

1. Claimant
2. Policy
3. Provider
4. Incident
5. Claim
6. Invoice
7. Payment
8. Relationship Edge
9. Fraud Result
10. Investigation
11. Financial Exception
12. Ground Truth

## 2. Entity Relationships

### 2.1 Claimant and Policy

- One claimant can own multiple policies.
- Each policy is associated with a claimant.
- Relationship: One-to-Many.

`claimants.claimant_id` → `policies.claimant_id`

### 2.2 Claimant and Claim

- One claimant can submit multiple claims.
- Each claim references a claimant.
- Relationship: One-to-Many.

`claimants.claimant_id` → `claims.claimant_id`

### 2.3 Policy and Claim

- One policy can be associated with multiple claims.
- Each claim references a policy.
- Relationship: One-to-Many.

`policies.policy_id` → `claims.policy_id`

### 2.4 Incident and Claim

- One incident can be associated with multiple claims.
- Each claim references an incident.
- Relationship: One-to-Many.

`incidents.incident_id` → `claims.incident_id`

### 2.5 Provider and Claim

- One provider can handle multiple claims.
- Each claim references a provider.
- Relationship: One-to-Many.

`providers.provider_id` → `claims.provider_id`

### 2.6 Claim and Invoice

- A claim can have invoice records.
- Each invoice references a claim and provider.
- Relationship: One-to-Many (logical association).

`claims.claim_id` → `invoices.claim_id`

### 2.7 Claim and Payment

- A claim can have payment records.
- Each payment references a claim.
- Relationship: One-to-Many (logical association).

`claims.claim_id` → `payments.claim_id`

### 2.8 Claim and Investigation

- A claim can be selected for investigation.
- Investigation records reference claims.
- Relationship: One-to-Many (logical association).

`claims.claim_id` → `investigations.claim_id`

## 3. Relationship Network

The `relationship_edges` dataset stores connections between entities.

Columns:

- `source`: First entity ID.
- `target`: Second entity ID.
- `relationship`: Connection type.

Implemented relationship types:

| Relationship | Meaning |
|---|---|
| OWNS | Claimant owns policy |
| SUBMITTED | Claimant submitted claim |
| COVERED_BY | Claim is associated with policy |
| HANDLED_BY | Provider handles claim |

Network analysis uses these connections to identify shared entities and suspicious patterns.

## 4. Fraud Detection Data Flow

1. Claimant, policy, provider, incident, and claim records are generated.
2. Fraud patterns are injected into selected synthetic records.
3. Relationship edges are created.
4. Fraud detection rules calculate claim risk scores.
5. Risk results are saved in `fraud_results.csv`.
6. Medium-risk and high-risk claims are selected for investigation.
7. Financial records are checked for anomalies.
8. Results are stored in CSV files and SQLite.
9. Streamlit displays the results.

## 5. Risk Scoring

| Rule | Score |
|---|---:|
| Claimant has at least 4 claims | +30 |
| Claim amount is at least 350,000 | +30 |
| Claim amount exceeds approved amount by at least 200,000 | +20 |
| Shared claimant phone number | +20 |
| Provider has at least 12 claims | +20 |
| Provider connected to at least 8 distinct claimants | +40 |

Maximum risk score: 100.

Risk categories:

- Low: 0–29
- Medium: 30–59
- High: 60–100

## 6. Financial Anomaly Detection

The system currently checks:

1. Duplicate invoice IDs.
2. Payment amounts exceeding approved claim amounts.

Detected exceptions are recorded in `financial_exceptions.csv`.

## 7. Database Storage

The system uses SQLite.

Database file:

`data/insurance_fraud.db`

The database contains:

- claimants
- policies
- providers
- incidents
- claims
- relationship_edges
- fraud_results
- investigations
- invoices
- payments
- financial_exceptions

## 8. Current Limitations

- The database tables are currently created from CSV data.
- Explicit primary-key and foreign-key constraints are not yet enforced by the database creation script.
- Investigation status history is not currently maintained as a separate event table.
- The system uses rule-based risk scoring rather than a trained machine learning classifier.
- The current evaluation uses only three labelled positive fraud examples.

## 9. Future Improvements

- Enforce primary-key and foreign-key constraints.
- Add investigation status history and audit events.
- Support larger configurable datasets.
- Add comprehensive data validation.
- Improve ground-truth labelling and evaluation.
- Add additional fraud relationship patterns.
