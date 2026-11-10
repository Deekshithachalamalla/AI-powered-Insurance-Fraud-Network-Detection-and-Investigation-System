
# Data Dictionary
## AI-Powered Insurance Fraud Network Detection and Investigation System

This document describes the datasets, columns, and key relationships used in the project.

## 1. Raw Datasets

### 1.1 Claimants (`claimants.csv`)

| Column | Description | Key |
|---|---|---|
| claimant_id | Unique claimant identifier | PK |
| name | Claimant name | |
| phone | Claimant phone number | |
| city | Claimant city | |

### 1.2 Policies (`policies.csv`)

| Column | Description | Key |
|---|---|---|
| policy_id | Unique policy identifier | PK |
| claimant_id | Owner of the policy | FK |
| policy_type | Type of insurance policy | |
| premium | Policy premium amount | |
| policy_status | Current policy status | |

### 1.3 Providers (`providers.csv`)

| Column | Description | Key |
|---|---|---|
| provider_id | Unique provider identifier | PK |
| provider_name | Provider name | |
| provider_type | Type of provider | |
| city | Provider city | |

### 1.4 Incidents (`incidents.csv`)

| Column | Description | Key |
|---|---|---|
| incident_id | Unique incident identifier | PK |
| incident_type | Type of incident | |
| incident_city | Incident location | |
| incident_date | Date of incident | |

### 1.5 Claims (`claims.csv`)

| Column | Description | Key |
|---|---|---|
| claim_id | Unique claim identifier | PK |
| claimant_id | Claimant who submitted the claim | FK |
| policy_id | Associated insurance policy | FK |
| incident_id | Associated incident | FK |
| provider_id | Provider handling the claim | FK |
| claim_amount | Amount requested | |
| approved_amount | Amount approved | |
| claim_status | Current claim status | |

### 1.6 Invoices (`invoices.csv`)

| Column | Description | Key |
|---|---|---|
| invoice_id | Unique invoice identifier | PK |
| claim_id | Associated claim | FK |
| provider_id | Provider issuing the invoice | FK |
| invoice_amount | Invoice amount | |
| invoice_status | Invoice status | |

### 1.7 Payments (`payments.csv`)

| Column | Description | Key |
|---|---|---|
| payment_id | Unique payment identifier | PK |
| claim_id | Associated claim | FK |
| payment_amount | Payment amount | |
| payment_status | Payment status | |

## 2. Processed Datasets

### 2.1 Relationship Edges (`relationship_edges.csv`)

| Column | Description |
|---|---|
| source | First entity identifier |
| target | Second entity identifier |
| relationship | Type of relationship between entities |

Relationship examples:
- OWNS
- SUBMITTED
- COVERED_BY
- HANDLED_BY

### 2.2 Fraud Results (`fraud_results.csv`)

| Column | Description |
|---|---|
| claim_id | Claim identifier |
| claimant_id | Claimant identifier |
| policy_id | Policy identifier |
| incident_id | Incident identifier |
| provider_id | Provider identifier |
| claim_amount | Requested claim amount |
| approved_amount | Approved amount |
| claim_status | Claim status |
| risk_score | Calculated fraud risk score |
| risk_reasons | Reasons contributing to the score |
| claimant_claim_count | Number of claims by claimant |
| amount_difference | Difference between requested and approved amounts |
| provider_claim_count | Number of claims handled by provider |
| provider_claimant_count | Number of distinct claimants connected to provider |
| risk_level | Low, Medium, or High |

### 2.3 Investigations (`investigations.csv`)

| Column | Description | Key |
|---|---|---|
| investigation_id | Unique investigation identifier | PK |
| claim_id | Claim under investigation | FK |
| risk_score | Claim risk score | |
| risk_level | Claim risk category | |
| evidence | Reasons supporting investigation | |
| investigation_status | Current investigation status | |
| assigned_to | Assigned investigator or team | |
| created_date | Investigation creation date | |

### 2.4 Financial Exceptions (`financial_exceptions.csv`)

| Column | Description |
|---|---|
| investigation_id | Financial exception investigation identifier |
| exception_type | Type of financial anomaly |
| record_id | Related invoice or payment record |
| claim_id | Associated claim identifier |
| description | Explanation of the anomaly |
| status | Current exception status |

## 3. Ground Truth Dataset

### Ground Truth (`ground_truth.csv`)

| Column | Description |
|---|---|
| claim_id | Claim identifier |
| is_fraud | Label indicating whether the claim is a planted fraud case |
| fraud_pattern | Description of the planted fraud pattern |

Ground truth is used to compare detection results against known synthetic fraud labels.

## 4. Key Relationships

| Parent Dataset | Child Dataset | Relationship |
|---|---|---|
| Claimants | Policies | One-to-Many |
| Claimants | Claims | One-to-Many |
| Policies | Claims | One-to-Many |
| Incidents | Claims | One-to-Many |
| Providers | Claims | One-to-Many |
| Claims | Invoices | One-to-Many |
| Claims | Payments | One-to-Many |
| Claims | Investigations | One-to-Many (logical association) |

## 5. Notes

- PK means Primary Key.
- FK means Foreign Key.
- Relationship descriptions represent the intended logical data model.
- Actual database constraints should be verified separately.
- Fraud risk scores indicate suspicious activity and do not establish confirmed fraud.
- The project uses synthetic demonstration data.
