# Dimensions

## Overview

This mini sprint defines the dimension layer for the pharma commercial data warehouse. It covers purpose, canonical dimension list, logical and physical designs, DDL examples, surrogate key strategy, slowly changing dimension handling, ingestion/upsert patterns, clustering and performance guidance, testing and acceptance criteria, and items that require verification.

The goal is to deliver reusable, auditable, and analytics-ready dimension tables that support the star schema built from the unified events created in MiniSprint 5.1.

---

## Objectives

* Define required dimensions for commercial pharma analytics.
* Provide production-ready DDL templates for each dimension.
* Specify SCD handling strategy with example upsert patterns.
* Provide Snowpark and SQL snippets to build and refresh dimensions incrementally.
* Specify clustering, retention, and audit practices.
* Provide acceptance criteria and test plan.

---

## Dimension list and purpose

Keep the dimension set small and focused for Sprint 5.2. Each dimension must include lineage and minimal metadata.

Primary dimensions

* `product_dim` - drug and brand information
* `hcp_dim` - healthcare provider master, specialties, affiliation
* `patient_dim` - tokenized patient view or patient cohort attributes, minimal PHI
* `geography_dim` - country, region, market mapping
* `payer_dim` - payer or channel information
* `time_dim` - calendar and fiscal attributes
* `promotion_dim` - promotion and program metadata
* `organization_dim` - internal business entities, sales territories

Each dimension supports lookups from the unified dataset and provides surrogate keys for fact tables.

---

## Dimension design principles

* Surrogate key primary key on each dimension using AUTOINCREMENT or SEQUENCE.
* Maintain business natural key(s) for upserts and lineage.
* Preserve source provenance: columns `source_vendor`, `source_code`, `effective_from`, `effective_to`, `is_current`, `record_hash`.
* Use SCD Type 2 for dimensions that change over time and where history matters: `hcp_dim`, `product_dim`, `patient_dim` (limited), `organization_dim`.
* Use SCD Type 1 for dimensions where only current values matter: `geography_dim`, `time_dim`, `payer_dim` when payer attributes are stable.
* Always include metadata columns: `created_ts`, `created_by`, `last_updated_ts`, `last_updated_by`, `row_hash`.
* Tokenize or hash all PHI fields before storing in CURATED or DIMENSIONS unless explicitly approved.

---

## Sample DDL templates

### Common preamble

```sql
USE DATABASE HEALTHCARE_DB;
USE SCHEMA CONSUMPTION;
```

### Time dimension (permanent, SCD Type 1)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.time_dim (
  date_id           INT AUTOINCREMENT PRIMARY KEY,
  full_date         DATE NOT NULL,
  year              INT,
  quarter           INT,
  month             INT,
  day_of_month      INT,
  day_of_week       INT,
  is_weekend        BOOLEAN,
  fiscal_year       INT,
  fiscal_period     INT,
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  created_by        VARCHAR,
  row_hash          VARCHAR
);
```

### Product dimension (SCD Type 2)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.product_dim (
  product_sk        BIGINT AUTOINCREMENT PRIMARY KEY,
  product_code      VARCHAR,              -- natural/business key
  brand_name        VARCHAR,
  generic_name      VARCHAR,
  atc_code          VARCHAR,
  therapy_area      VARCHAR,
  effective_from    DATE,
  effective_to      DATE,
  is_current        BOOLEAN DEFAULT TRUE,
  source_vendor     VARCHAR,
  source_ref        VARCHAR,              -- original vendor id/code
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  last_updated_ts   TIMESTAMP_TZ,
  last_updated_by   VARCHAR,
  record_hash       VARCHAR
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_product_natural ON CONSUMPTION.product_dim(product_code, source_vendor, effective_from);
```

### HCP dimension (SCD Type 2)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.hcp_dim (
  hcp_sk            BIGINT AUTOINCREMENT PRIMARY KEY,
  hcp_npi           VARCHAR,              -- natural key if available
  hcp_name          VARCHAR,
  specialty         VARCHAR,
  affiliation       VARCHAR,
  country           VARCHAR,
  region            VARCHAR,
  effective_from    DATE,
  effective_to      DATE,
  is_current        BOOLEAN DEFAULT TRUE,
  source_vendor     VARCHAR,
  source_ref        VARCHAR,
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  last_updated_ts   TIMESTAMP_TZ,
  last_updated_by   VARCHAR,
  record_hash       VARCHAR
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_hcp_natural ON CONSUMPTION.hcp_dim(hcp_npi, source_vendor, effective_from);
```

### Patient dimension (limited, tokenized, SCD Type 2 minimal)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.patient_dim (
  patient_sk        BIGINT AUTOINCREMENT PRIMARY KEY,
  patient_token     VARCHAR,             -- hashed/tokenized id
  cohort_code       VARCHAR,             -- derived cohort or segment
  dob               DATE,
  gender            VARCHAR,
  country           VARCHAR,
  effective_from    DATE,
  effective_to      DATE,
  is_current        BOOLEAN DEFAULT TRUE,
  source_vendor     VARCHAR,
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  last_updated_ts   TIMESTAMP_TZ,
  record_hash       VARCHAR
);
```

### Geography dimension (SCD Type 1)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.geography_dim (
  geography_sk      INT AUTOINCREMENT PRIMARY KEY,
  country_code      VARCHAR,
  country_name      VARCHAR,
  region            VARCHAR,
  iso_region_code   VARCHAR,
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  record_hash       VARCHAR
);
```

### Payer dimension (SCD Type 1)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.payer_dim (
  payer_sk          INT AUTOINCREMENT PRIMARY KEY,
  payer_code        VARCHAR,
  payer_name        VARCHAR,
  channel           VARCHAR,
  created_ts        TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  record_hash       VARCHAR
);
```

---

## Surrogate key and sequence strategy

* Prefer `AUTOINCREMENT` for readability and simplicity in Snowflake.
* For deterministic upserts from external systems, also maintain natural keys and `source_ref`.
* Where concurrency or cross-region deployments may cause conflicts, use sequences in a central control schema to allocate batches.

---

## Row hashing and record_hash

* Compute `record_hash` as SHA256 over canonicalized attribute set relevant to the dimension record.
* Use `record_hash` to detect attribute-level changes and decide whether to insert a new SCD Type 2 row or to ignore.

Example hash inputs for `hcp_dim`: `lower(trim(hcp_npi)) + '|' + lower(trim(hcp_name)) + '|' + lower(trim(specialty)) + '|' + country`.

---

## SCD patterns and example upsert logic

### SCD Type 2 general pattern (SQL)

1. Identify incoming natural key matches in current dimension rows.
2. For matched rows where `record_hash` differs, update existing row to set `is_current = FALSE` and `effective_to = incoming_effective_from - 1`.
3. Insert the new row with `is_current = TRUE` and `effective_from = incoming_effective_from`.

Example SQL (pseudo):

```sql
-- 1. expire existing rows
UPDATE CONSUMPTION.hcp_dim d
SET d.is_current = FALSE,
    d.effective_to = DATEADD(day, -1, v.effective_from),
    d.last_updated_ts = CURRENT_TIMESTAMP()
FROM (
  SELECT hcp_npi, MIN(effective_from) as effective_from, record_hash FROM staging_hcp GROUP BY hcp_npi, record_hash
) v
WHERE d.hcp_npi = v.hcp_npi
  AND d.is_current = TRUE
  AND d.record_hash <> v.record_hash;

-- 2. insert new rows
INSERT INTO CONSUMPTION.hcp_dim (hcp_npi, hcp_name, specialty, country, effective_from, effective_to, is_current, source_vendor, source_ref, created_ts, record_hash)
SELECT hcp_npi, hcp_name, specialty, country, effective_from, '9999-12-31', TRUE, source_vendor, source_ref, CURRENT_TIMESTAMP(), record_hash
FROM staging_hcp s
WHERE NOT EXISTS (
  SELECT 1 FROM CONSUMPTION.hcp_dim d
  WHERE d.hcp_npi = s.hcp_npi
    AND d.record_hash = s.record_hash
);
```

### Snowpark upsert skeleton for SCD Type 2

```python
from snowflake.snowpark.functions import col, sha2, concat, lit, current_timestamp
from snowflake.snowpark.window import Window
from snowflake.snowpark import Session

session = Session.builder.configs(conn_params).create()

stg = session.table("STAGING.hcp_stg")  # staging contains incoming standardized hcp records

# compute record_hash in Snowpark
stg_hash = stg.with_column("record_hash",
                          sha2(concat(col("hcp_npi"), lit("|"), col("hcp_name"), lit("|"), col("specialty"), lit("|"), col("country")), lit(256)))

# 1. expire current rows that changed
expire_sql = """
UPDATE CONSUMPTION.hcp_dim d
SET is_current = FALSE,
    effective_to = DATEADD(day, -1, v.effective_from),
    last_updated_ts = CURRENT_TIMESTAMP()
FROM (
  SELECT hcp_npi, MIN(effective_from) as effective_from, record_hash FROM STAGING.hcp_stg GROUP BY hcp_npi, record_hash
) v
WHERE d.hcp_npi = v.hcp_npi
  AND d.is_current = TRUE
  AND d.record_hash <> v.record_hash
"""
session.sql(expire_sql).collect()

# 2. insert new current rows
insert_sql = """
INSERT INTO CONSUMPTION.hcp_dim (hcp_npi, hcp_name, specialty, country, effective_from, effective_to, is_current, source_vendor, source_ref, created_ts, record_hash)
SELECT hcp_npi, hcp_name, specialty, country, effective_from, '9999-12-31', TRUE, source_vendor, source_ref, CURRENT_TIMESTAMP(), record_hash
FROM STAGING.hcp_stg s
WHERE NOT EXISTS (
  SELECT 1 FROM CONSUMPTION.hcp_dim d
  WHERE d.hcp_npi = s.hcp_npi
    AND d.record_hash = s.record_hash
);
"""
session.sql(insert_sql).collect()
```

---

## Dimension refresh cadence and incremental approach

* Dimensions must be updated incrementally per source batch rather than full rebuilds.
* Use staging tables that collect the batch, compute `record_hash`, and run the SCD upsert flow.
* For slow-changing reference dims such as `geography_dim` and `time_dim`, perform scheduled full refreshes as needed.

---

## Clustering and performance guidance

* Cluster large dimensions by `effective_from` or `country` when queries filter heavily by date or region.
* Keep clustering moderate; measure `SYSTEM$CLUSTERING_INFORMATION` before and after.
* For `product_dim` and `hcp_dim`, creating indexes on natural keys helps join performance even though Snowflake does not enforce them as conventional RDBMS indexes.

---

## Audit, lineage and versioning

* Each dimension change must be logged in `AUDIT.dimension_audit` with fields: `audit_id`, `dimension_name`, `operation` (INSERT/UPDATE), `natural_key`, `record_hash`, `run_id`, `executed_by`, `executed_ts`.
* Keep staging snapshots for one run in `STAGING` for replay ability.

---

## Testing and acceptance criteria

Acceptance tests for each dimension

* DDL exists and is deployed to `CONSUMPTION` schema.
* Surrogate keys generate and are unique.
* Ingest pipeline inserts new natural keys.
* Upserts for changed attributes create new SCD Type 2 rows and mark old rows as not current.
* `record_hash` changes only when attribute values change.
* Join tests: facts joining to dims produce non-null surrogate keys for 100% of recent events.
* Performance test: incremental update completes within allotted SLA for nightly window.

Sample test queries

* Validate current row count equals expected unique natural keys:

```sql
SELECT COUNT(1) FROM CONSUMPTION.hcp_dim WHERE is_current = TRUE;
```

* Validate no overlapping effective ranges per natural key:

```sql
SELECT hcp_npi FROM CONSUMPTION.hcp_dim
GROUP BY hcp_npi
HAVING MAX(effective_from) > MIN(effective_to);
```

* Validate fact to dimension joins:

```sql
SELECT COUNT(*) FROM FACT.sales_fact f
LEFT JOIN CONSUMPTION.product_dim p ON f.product_id = p.product_sk
WHERE p.product_sk IS NULL;
```

---

## Rollback and backfill strategies

* Use `ingest_job_id` tracked in staging and audit to delete or reverse a batch if necessary.
* For backfills, load staging with `ingest_job_id = BACKFILL_<date>` and run SCD logic constrained to impacted natural keys and date windows.
* Preserve previous dimension versions in `*_duplicate_archive` or `*_history` tables for audit.

---

## Short explanation of reasoning steps taken

* Selected SCD Type 2 where historical accuracy matters and SCD Type 1 where only current values used.
* Emphasized surrogate keys for stable joins and natural keys for idempotent upserts.
* Added `record_hash` to detect attribute-level changes and avoid unnecessary churn.
* Built patterns that work incrementally to scale with large pharma datasets.
* Ensured auditability and replay capability for regulatory and vendor dispute needs.

---

## Items requiring verification or uncertain

* Confirm canonical natural key choices per dimension, for example whether `hcp_npi` is always available and authoritative.
* Agree on retention windows for historical dimension versions.
* Confirm whether patient-level PHI can be stored tokenized in consumption schema, or whether stricter separation is required.
* Confirm vendor trust order for cross-vendor record survivorship in `product_dim` and `hcp_dim`.
* Confirm acceptable SLA for dimension update runtimes during nightly windows.

---

If you want, I will now generate:

* SQL files for each DDL ready to commit to the repo,
* Snowpark dimension upsert scripts parameterized by dimension name,
* A small test dataset and SQL test suite to validate SCD behavior.
