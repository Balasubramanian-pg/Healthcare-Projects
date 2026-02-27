# Data Standardization

(Source → Curated Layer)

## Overview

This mini sprint introduces **data standardization**, the first transformation step that converts vendor-specific Source data into a **consistent enterprise structure** inside the Curated layer.

At this stage, data is no longer treated as vendor-owned raw data.
It becomes **organization-owned standardized healthcare data**.

The purpose is not heavy transformation yet.
The goal is **uniform structure, naming, and interpretation** across all vendors.

---

## Objectives

* Standardize column names across vendors.
* Normalize healthcare entities.
* Align data types and formats.
* Introduce enterprise naming conventions.
* Prepare datasets for deduplication and enrichment.
* Reduce vendor variability before modeling.

---

## Why Standardization Is Critical in Pharma

Healthcare vendors rarely agree on schemas.

Example differences:

| Vendor A     | Vendor B     | Enterprise Standard |
| ------------ | ------------ | ------------------- |
| physician_id | npi          | hcp_id              |
| drug_cd      | product_code | drug_code           |
| trx_date     | claim_dt     | event_date          |
| amt          | claim_amount | amount_local        |

Without standardization:

* joins fail
* KPIs mismatch
* duplicate entities appear
* analytics become unreliable

Standardization creates a **single semantic language** for the platform.

---

## Data Flow

```text
SOURCE Tables
      ↓
Standardization Rules
      ↓
CURATED Tables
```

Source keeps vendor truth.
Curated introduces enterprise consistency.

---

## Standardization Dimensions

Standardization occurs across five areas.

### 1. Column Naming Standardization

Enterprise naming rules:

* snake_case format
* business meaning focused
* vendor-neutral terminology
* avoid abbreviations unless industry standard

Examples:

| Source Column | Curated Column |
| ------------- | -------------- |
| cust_nm       | customer_name  |
| trx_dt        | event_date     |
| phn           | contact_number |
| prod          | drug_code      |

Implementation example:

```sql
SELECT
    vendor_claim_id AS claim_id,
    claim_date AS event_date,
    drug_code,
    quantity,
    amount_local
FROM SOURCE.claims_src_tbl;
```

---

### 2. Data Type Normalization

Different vendors send inconsistent types.

Common issues:

* dates stored as strings
* numeric values stored as text
* currency precision mismatch

Standard conversions:

```sql
SELECT
    TRY_TO_DATE(claim_date) AS event_date,
    TRY_TO_NUMBER(quantity) AS quantity,
    TRY_TO_DECIMAL(amount_local,18,4) AS amount_local
FROM SOURCE.claims_src_tbl;
```

Reason:
Curated layer guarantees type safety.

---

### 3. Identifier Standardization

Healthcare identifiers must be unified.

Entities standardized:

* HCP identifiers
* Drug identifiers
* Geography codes
* Patient tokens

Example transformation:

```sql
UPPER(TRIM(hcp_identifier)) AS hcp_id
```

Rules applied:

* remove whitespace
* uppercase normalization
* remove formatting symbols

Example:

```
" npi-12345 "
→ NPI12345
```

---

### 4. Date and Time Standardization

Vendors deliver multiple formats:

```
MM/DD/YYYY
YYYY-MM-DD
DD-MON-YY
Timestamp UTC
Local timezone
```

Enterprise rule:
All curated timestamps stored as:

```
TIMESTAMP_TZ (UTC)
```

Example:

```sql
CONVERT_TIMEZONE('UTC', event_timestamp)
```

Reason:
Global pharma reporting requires timezone consistency.

---

### 5. Currency Standardization Preparation

At this stage:

* Preserve vendor currency.
* Prepare conversion fields.

Curated structure includes:

* currency_code
* amount_local
* exchange_rate (future enrichment)
* amount_usd (calculated later)

Reason:
Do not mix enrichment with standardization.

---

## Snowpark Standardization Pattern

Snowpark DataFrame API performs transformations.

Example:

```python
from snowflake.snowpark.functions import col, upper, trim

df = session.table("SOURCE.claims_src_tbl")

standardized_df = (
    df
    .with_column("hcp_id", upper(trim(col("hcp_identifier"))))
    .with_column("event_date", col("claim_date"))
    .with_column_renamed("vendor_claim_id","claim_id")
)
```

Then written to curated table.

---

## Curated Table Structure Example

```sql
CREATE TABLE CURATED.claims_tbl (
    claim_id STRING,
    event_date DATE,
    hcp_id STRING,
    drug_code STRING,
    quantity NUMBER,
    amount_local NUMBER(18,4),
    currency_code STRING,
    vendor_id STRING,
    record_status STRING,
    load_ts TIMESTAMP_TZ
);
```

---

## Standardization Rules Registry

Maintain rules centrally.

Recommended table:

```sql
REFERENCE.standardization_rules
```

Columns:

* source_field
* curated_field
* transformation_rule
* vendor_id
* active_flag

Purpose:
Future automation and governance.

---

## Handling Vendor Differences

Strategy used:

### Do Not Modify SOURCE

Source remains immutable.

### Apply Mapping Layer

Transform during Source → Curated only.

### Preserve Lineage

Always retain:

* vendor_id
* source_file
* ingest_job_id

---

## Common Pharma Standardizations

### HCP Specialty Mapping

```
Cardio
Cardiology
CARD
→ CARDIOLOGY
```

### Drug Normalization

```
Humira 40mg
HUMIRA-40 MG
Humira_40
→ HUMIRA 40MG
```

### Geography Alignment

```
USA
US
United States
→ UNITED_STATES
```

---

## Data Quality Controls Introduced

During standardization:

* invalid dates removed
* empty identifiers flagged
* whitespace cleaned
* invalid numeric values converted to NULL

But records are not deleted yet.

Deletion happens later after validation.

---

## Performance Strategy

Design considerations:

* Transform only newly loaded partitions.
* Avoid full table scans.
* Push transformations into Snowflake execution engine.
* Use Snowpark lazy execution.

Snowpark compiles transformations into optimized SQL automatically.

---

## Acceptance Criteria

* Curated tables created.
* Column naming standardized.
* Data types aligned.
* Identifiers normalized.
* Timezones unified.
* Vendor differences removed.
* Lineage metadata preserved.
* Snowpark transformation executes successfully.

---

## Explanation of Thought Process

Key reasoning applied:

1. Vendor inconsistency is inevitable.
2. Analytics requires semantic consistency.
3. Standardization must happen before deduplication.
4. Source data must remain untouched for auditability.
5. Transformations should be deterministic and reversible.

The curated layer becomes the **enterprise contract layer** between ingestion and analytics.

---

## Items Requiring Verification or Uncertain

* Official enterprise naming conventions approval.
* Canonical HCP identifier authority (NPI vs internal ID).
* Drug master reference system availability.
* Timezone handling rules for global markets.
* Currency conversion timing requirements.

---

## Next Mini Sprint

MiniSprint 4.2
Data Quality Processing

If you want, I can also show the **real pharma enterprise pattern** next where companies implement:

* semantic layer standardization
* master data reconciliation engine
* automated schema drift correction
* rule-driven Snowpark transformations.
