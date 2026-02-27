# Schema Strategy

## Overview

This document translates the logical design into a concrete schema strategy for Snowflake. It defines schema responsibilities, table types, naming conventions, partitioning and clustering guidance, sample DDL, security and RBAC guidance, retention and cost controls, and a checklist for implementation and verification.

---

## Objectives

* Provide clear, implementable schema definitions for Source, Curated, Reference, Consumption, Common, and Audit layers.
* Standardize naming, table properties, and metadata columns so downstream code and audits are consistent.
* Balance cost, performance, and compliance requirements for pharma data.
* Deliver ready-to-run example DDL and an implementation task list.

---

## Principles and rules applied

* Single responsibility per schema: each schema hosts objects for one stage of the pipeline.
* Metadata-included rows: every persisted row must contain file and lineage metadata.
* Minimal PHI exposure: tokenization or masking occurs before data lands in curated or consumption schemas if PHI is present.
* Use transient objects for intermediate data to reduce storage cost while preserving recoverability.
* Design for incremental loads by storing file and row-level checksums.
* Keep naming predictable and scriptable.

---

## Schemas and responsibilities

* `SOURCE` (landing)

  * Raw copies of vendor feeds after stage -> table copy
  * Transient tables allowed
  * Minimal transformations, only type casting and metadata capture

* `CURATED`

  * Cleaned, deduplicated, enriched, normalized records
  * No PHI in cleartext unless authorized
  * Canonical column names and fixed data types

* `REFERENCE` or `COMMON`

  * Master data and shared objects: drug master, NPI registry, geography maps, file formats
  * File format definitions and stage objects can also live here

* `CONSUMPTION`

  * Denormalized dimensions and fact tables for analytics and dashboards
  * Optimized for reads

* `AUDIT`

  * `file_audit`, `load_audit`, `data_quality_metrics`
  * Stores processing history and metrics

---

## Naming conventions

* Schema names: uppercase and short, for example `SOURCE`, `CURATED`, `REFERENCE`, `CONSUMPTION`, `AUDIT`.
* Tables: `<schema>.<subject>_tbl` for operational tables, for example `CURATED.claims_tbl`.
* Views: `<schema>.<subject>_vw`.
* Sequences: `<schema>.<subject>_seq`.
* Columns:

  * Surrogate keys: `<entity>_id` (integer)
  * Foreign keys: `<entity>_id_fk`
  * Metadata: `file_name`, `file_path`, `file_checksum`, `file_loaded_ts`, `ingest_job_id`, `row_hash`
* Branch-specific branches are not referenced here; commit DDL to repository as SQL files.

---

## Table type choices and rationale

* `TRANSIENT` tables for `SOURCE` layer: lower storage cost, no failsafe retention required.
* `PERMANENT` tables for `CURATED` and `CONSUMPTION`: durable, can be cloned and time-traveled if needed.
* `TEMPORARY` sessions-only tables for ephemeral steps inside single session jobs.
* Use `AUTOINCREMENT` or `SEQUENCE` for surrogate keys where appropriate.

---

## Metadata columns (mandatory)

Include in every persisted table:

* `file_name` (VARCHAR)
* `file_path` (VARCHAR)
* `file_checksum` (VARCHAR)
* `file_loaded_ts` (TIMESTAMP_TZ)
* `ingest_job_id` (VARCHAR)
* `row_hash` (VARCHAR)  : for dedupe and late-arrival detection
* `record_status` (VARCHAR)  : values `active`, `superseded`, `deleted`

---

## Partitioning and clustering guidance

* Snowflake micro-partitions are automatic. Use clustering when queries repeatedly filter on the same column and performance needs justify maintenance cost.
* Suggested clustering keys:

  * `SOURCE` tables: `file_loaded_ts`, `vendor_id`
  * `CURATED` tables: `event_date` or `claim_date`
  * `CONSUMPTION` fact tables: `date_id`, `product_id`, `geography_id`
* Keep cluster depth modest and monitor `SYSTEM$CLUSTERING_INFORMATION` for improvement.
* Use partition-style folder structure on stage: `vendor=vendorA/year=YYYY/month=MM/day=DD` so COPY commands can target partitions efficiently.

---

## Retention and cost controls

* Staged files retention: 90 days in stage
* `SOURCE` data retention: 365 days in TRANSIENT tables (or as legal requires)
* `CURATED` and `CONSUMPTION`: retention per business SLA; keep time travel retention short if cost sensitive
* Use Time Travel and Fail-safe settings sparingly to control cost
* Implement scheduled housekeeping for stale stage folders and old transient objects

---

## Security and PHI handling

* Apply RBAC: roles such as `DATA_INGEST_ROLE`, `DATA_ENGINEER_ROLE`, `DATA_STEWARD_ROLE`, `ANALYTICS_ROLE`
* Mask/tokenize patient identifiers before persisted to `CURATED` unless explicitly allowed
* Keep `CURATED` and `CONSUMPTION` schemas restricted to `DATA_STEWARD_ROLE` and `ANALYTICS_ROLE` only
* Audit every DDL and data change through `AUDIT` schema and Snowflake account usage logs

---

## File formats and stage objects

Create reusable file formats in `REFERENCE` schema. Example:

* `REFERENCE.ff_csv`
* `REFERENCE.ff_json`
* `REFERENCE.ff_parquet`

Keep stage objects named with vendor context:

* `REFERENCE.stage_vendorA_internal`
* `REFERENCE.stage_vendorB_internal`

---

## Sample DDL templates

### 1. File format creation (REFERENCE)

```sql
USE SCHEMA REFERENCE;

CREATE OR REPLACE FILE FORMAT ff_csv
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  STRIP_NULL_VALUES = TRUE
  TRIM_SPACE = TRUE
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;

CREATE OR REPLACE FILE FORMAT ff_json
  TYPE = 'JSON'
  STRIP_NULL_VALUES = TRUE;
```

### 2. Source table example (SOURCE)

```sql
CREATE OR REPLACE TRANSIENT TABLE SOURCE.claims_tbl (
  vendor_claim_id VARCHAR,
  vendor_id VARCHAR,
  claim_date DATE,
  hcp_identifier VARCHAR,
  patient_identifier VARCHAR,
  drug_code VARCHAR,
  quantity NUMBER,
  amount_local NUMBER(18,4),
  currency VARCHAR,
  file_name VARCHAR,
  file_path VARCHAR,
  file_checksum VARCHAR,
  file_loaded_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR,
  row_hash VARCHAR
);
```

### 3. Curated table example (CURATED)

```sql
CREATE OR REPLACE TABLE CURATED.claims_tbl (
  claim_id BIGINT AUTOINCREMENT,
  vendor_claim_id VARCHAR,
  vendor_id VARCHAR,
  claim_date DATE,
  hcp_id_fk BIGINT,
  patient_token VARCHAR,
  drug_id_fk BIGINT,
  quantity NUMBER,
  amount_local NUMBER(18,4),
  currency VARCHAR,
  amount_usd NUMBER(18,4),
  file_name VARCHAR,
  file_path VARCHAR,
  file_checksum VARCHAR,
  file_loaded_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR,
  row_hash VARCHAR,
  record_status VARCHAR DEFAULT 'active'
);
```

### 4. Reference table example (REFERENCE)

```sql
CREATE OR REPLACE TABLE REFERENCE.drug_dim (
  drug_id BIGINT AUTOINCREMENT,
  drug_code VARCHAR,
  brand_name VARCHAR,
  generic_name VARCHAR,
  atc_code VARCHAR,
  therapy_area VARCHAR,
  is_active BOOLEAN,
  effective_date DATE
);
```

### 5. Consumption fact example (CONSUMPTION)

```sql
CREATE OR REPLACE TABLE CONSUMPTION.sales_fact (
  sales_fact_id BIGINT AUTOINCREMENT,
  event_date DATE,
  date_id INTEGER,
  product_id BIGINT,
  hcp_id BIGINT,
  geography_id BIGINT,
  quantity NUMBER,
  amount_usd NUMBER(18,4),
  source_vendor VARCHAR,
  file_name VARCHAR,
  ingest_job_id VARCHAR
)
CLUSTER BY (event_date);
```

### 6. Audit tables (AUDIT)

```sql
CREATE OR REPLACE TABLE AUDIT.file_audit (
  file_audit_id BIGINT AUTOINCREMENT,
  file_name VARCHAR,
  vendor_id VARCHAR,
  file_path VARCHAR,
  file_checksum VARCHAR,
  rows_expected BIGINT,
  rows_loaded BIGINT,
  status VARCHAR,
  error_message VARCHAR,
  processed_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR
);

CREATE OR REPLACE TABLE AUDIT.load_audit (
  load_audit_id BIGINT AUTOINCREMENT,
  ingest_job_id VARCHAR,
  feed_name VARCHAR,
  vendor_id VARCHAR,
  start_ts TIMESTAMP_TZ,
  end_ts TIMESTAMP_TZ,
  rows_in BIGINT,
  rows_out BIGINT,
  status VARCHAR,
  error_count INTEGER
);
```

---

## Indexing, constraints and referential integrity

* Snowflake supports constraints but does not enforce them strictly; use constraints as documentation only and implement programmatic enforcement in ETL.
* Use foreign keys in DDL for clarity but enforce integrity with joins and validation steps.
* Use unique / primary key patterns with `row_hash` and surrogate keys for dedupe operations.

---

## Incremental load and delta handling strategy

* Maintain `file_audit` with checksums and `file_loaded_ts`.
* ETL job algorithm:

  1. List staged files for vendor and partition.
  2. Check `file_audit` to skip files already processed.
  3. COPY new files into `SOURCE` with metadata.
  4. Compute `row_hash` for every row in `SOURCE`.
  5. Left anti-join `CURATED` on natural key + `row_hash` to find inserts or updates.
  6. Mark older versions `record_status = 'superseded'` when updates occur.
* For massive reprocessing, provide safe backfill scripts and versioned runs.

---

## Testing and validation scaffolding

* SQL test queries to validate schema presence and column types.
* Data validation views for quick checks:

  * `AUDIT.daily_ingest_summary_vw`
  * `CURATED.claims_qc_vw` with null checks and outlier counts
* Unit test examples: small CSV / Parquet sample inputs and expected transformed output
* Integration test: run full pipeline on a small sample and validate `file_audit` and `load_audit` numbers match

---

## Implementation task list

* Create `REFERENCE` file formats and stages
* Create `SOURCE` transient tables and copy scripts
* Implement `AUDIT` tables and populate initial entries signifying readiness
* Create `CURATED` tables and build Snowpark transform skeleton
* Create `CONSUMPTION` model DDL and sample aggregation views
* Add role creation SQL and grant statements for RBAC
* Write unit and integration test SQL scripts
* Add CI pipeline job to run DDL and basic smoke tests

---

## Security and grants example

```sql
CREATE ROLE data_ingest_role;
CREATE ROLE data_engineer_role;
CREATE ROLE data_steward_role;
CREATE ROLE analytics_role;

GRANT USAGE ON DATABASE my_db TO ROLE data_ingest_role;
GRANT USAGE ON SCHEMA my_db.SOURCE TO ROLE data_ingest_role;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA my_db.SOURCE TO ROLE data_ingest_role;

GRANT USAGE ON SCHEMA my_db.CURATED TO ROLE data_engineer_role;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA my_db.CURATED TO ROLE data_engineer_role;

GRANT SELECT ON SCHEMA my_db.CONSUMPTION TO ROLE analytics_role;
```

---

## Acceptance criteria

* Schemas created and DDL committed to repo
* Each table contains mandatory metadata columns
* `REFERENCE` file formats and stages are created and validated with sample files
* `AUDIT` tables accurately reflect sample ingests with correct counts
* Basic access control roles exist and have appropriate grants
* Unit tests for transform logic run and pass

---

## Short explanation of reasoning steps taken

* Converted logical layer responsibilities into schema-level ownership.
* Selected table types to balance cost and retention needs.
* Enforced metadata and hash patterns to support deduplication and lineage.
* Provided DDL templates that teams can use immediately.
* Built testing and audit surfaces to make rollout safe and verifiable.

---

## Items requiring verification or uncertain

* The canonical HCP identifier source and whether NPI is universally available
* Regulatory retention period for PHI and whether tokenization is mandatory before `CURATED`
* Exact business SLA for stage retention and source retention windows
* Whether `TRANSIENT` tables are acceptable for your regulatory posture
* Any organization-specific naming or governance rules that must be applied

---

## Next steps

* I will generate the DDL files ready for commit if you want them organized into the repo folder structure.
* I can also produce the grant scripts for the exact role names you prefer.
* If you prefer identity columns instead of sequences I can adapt the DDL accordingly.

Which of these should I produce next: DDL files, RBAC grant scripts, or Snowpark transform skeletons?
