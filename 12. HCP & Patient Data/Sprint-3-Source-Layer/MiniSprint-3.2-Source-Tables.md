# MiniSprint 3.2: Source Tables

## Overview

This mini sprint defines the design, DDL, operational patterns, and validation for the Source layer tables that receive staged vendor files. Source tables are the canonical raw copy of vendor data inside the warehouse. They are intentionally minimal in transformation, but strict about metadata, lineage, and idempotency support.

## Objectives

* Specify table types, mandatory metadata columns, and sample DDL.
* Define ingest patterns and COPY recommendations.
* Recommend clustering and retention settings for Source tables.
* Provide test plans, acceptance criteria, and rollbacks.
* Explain the design reasoning and list items that require verification.

---

## Key design decisions (summary)

* Use TRANSIENT tables for most Source tables to reduce time travel cost while keeping data durable long enough for backfills and replays. Snowflake documents differences between temporary, transient, and permanent tables. ([Snowflake Documentation][1])
* Keep transformations out of Source. Only apply type casting, basic normalization, and metadata capture. Use CURATED layer for harmonization.
* Capture file-level and row-level lineage: file_name, file_path, file_checksum, file_loaded_ts, ingest_job_id, row_hash.
* Use COPY INTO to load staged files into Source tables and rely on file-level targeting to avoid scanning unrelated partitions. ([Snowflake Documentation][2])
* Start without clustering; add CLUSTER BY when pruning metrics indicate benefit. Use SYSTEM$CLUSTERING_INFORMATION to evaluate clustering effectiveness. ([Snowflake Documentation][3])

---

## Mandatory metadata columns (every Source table)

* `file_name` VARCHAR
* `file_path` VARCHAR
* `file_checksum` VARCHAR
* `file_size_bytes` NUMBER
* `file_loaded_ts` TIMESTAMP_TZ
* `ingest_job_id` VARCHAR
* `row_hash` VARCHAR
* `vendor_id` VARCHAR
* `load_sequence` BIGINT  (optional, maps to vendor batch number)

Rationale: these fields make loads auditable, enable idempotency checks, and support row-level dedupe in the curated step.

---

## Table types and retention guidance

* Table type: `TRANSIENT` for regular Source tables to reduce storage cost related to time travel and fail-safe. Use `PERMANENT` only when legal or operational rules require long time travel. See Snowflake guidance on transient versus permanent tables. ([Snowflake Documentation][1])
* Retention policy: keep Source transient data for at least 7 to 90 days depending on vendor SLA, then archive if needed.
* If vendor data contains PHI, verify regulatory retention rules before selecting transient versus permanent.

---

## Example DDLs

### Generic claims source table (TRANSIENT)

```sql
CREATE OR REPLACE TRANSIENT TABLE SOURCE.claims_src_tbl (
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
  file_size_bytes NUMBER,
  file_loaded_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR,
  row_hash VARCHAR,
  load_sequence BIGINT
);
```

### Generic rx source table (TRANSIENT)

```sql
CREATE OR REPLACE TRANSIENT TABLE SOURCE.rx_src_tbl (
  rx_id VARCHAR,
  vendor_id VARCHAR,
  rx_date DATE,
  patient_id VARCHAR,
  drug_code VARCHAR,
  quantity NUMBER,
  amount_local NUMBER(18,4),
  currency VARCHAR,
  file_name VARCHAR,
  file_path VARCHAR,
  file_checksum VARCHAR,
  file_size_bytes NUMBER,
  file_loaded_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR,
  row_hash VARCHAR,
  load_sequence BIGINT
);
```

---

## COPY INTO pattern and best practices

* Target specific partition path in the stage when running COPY INTO to limit scan scope, for example `@REF.stage_vendorA/claims/year=YYYY/month=MM/day=DD/`. COPY INTO documentation explains supported stage locations and options. ([Snowflake Documentation][2])
* Use `FILE_FORMAT = (FORMAT_NAME = 'REFERENCE.ff_csv_claims')` to reuse file format objects rather than embedding format options inline. ([Snowflake Documentation][4])
* Use `ON_ERROR = 'CONTINUE'` during initial loads to capture bad rows, then reprocess quarantined rows after analysis.
* For pre-validation, run `VALIDATION_MODE = 'RETURN_ERRORS'` before production loads to inspect failing rows.

Example COPY statement:

```sql
COPY INTO SOURCE.claims_src_tbl
FROM @REFERENCE.stage_vendorA/claims/year=2026/month=02/day=27/
FILE_FORMAT = (FORMAT_NAME = 'REFERENCE.ff_csv_claims')
ON_ERROR = 'CONTINUE'
PURGE = FALSE;
```

Notes:

* `PURGE = FALSE` keeps staged files until audit confirms successful processing.
* Record rows_loaded into `AUDIT.file_audit` after COPY completes.

---

## Row hashing and dedupe keys

* Compute `row_hash` as SHA256 of the natural business key plus normalized payload columns to detect duplicates and changes.
* Example pseudo formula: `row_hash = sha2(concat(vendor_id, '|', vendor_claim_id, '|', normalize(amount_local), '|', claim_date), 256)`.
* Store `row_hash` in SOURCE so curated pipelines can left-anti join on natural key plus row_hash to identify new or changed rows.

Rationale: `row_hash` enables cheap equality checks and avoids expensive wide comparisons during delta detection.

---

## Sequencing and idempotency

* Use `AUDIT.file_audit` to track processed files with checksum and rows_loaded. Only process files not present or whose checksum changed.
* Include `ingest_job_id` in each file and table row to tie rows to a run for replayability and rollback.

---

## Clustering recommendations

* Start without clustering unless table size and query patterns justify it.
* If queries frequently filter by `claim_date` or `file_loaded_ts` and micro-partition pruning is insufficient, add `CLUSTER BY (claim_date)` or `CLUSTER BY (file_loaded_ts, vendor_id)`. Snowflake clustering docs explain how clustering keys influence micro-partition layout and when to apply them. ([Snowflake Documentation][3])
* Consider Snowflake automatic clustering service for large tables that would benefit from continuous reclustering. ([Snowflake Documentation][5])

---

## Operational patterns

### Load staging checklist

* Validate file checksum and record it in `AUDIT.file_audit`.
* Run `COPY INTO` targeted to the partition.
* Capture `rows_loaded` and errors into `AUDIT.load_audit`.
* If `rows_loaded` equals 0 and errors exist, move file to quarantine path.

### Backfill pattern

* Backfills should be run on an isolated schedule to avoid contention with daily loads.
* Use `COPY INTO` with explicit path and set `INGEST_JOB_ID` to a backfill identifier.
* Monitor warehouse credits and parallelism.

### Rollback pattern

* If a bad load is detected, use `ingest_job_id` to identify rows to delete from SOURCE, or use time travel to restore pre-load state if table is permanent and time travel window permits.

---

## Test plan and validation queries

### Basic connectivity test

* Verify `SHOW STAGES` lists expected stages.

### Sanity checks after a COPY

* Count rows by file:

```sql
SELECT file_name, COUNT(*) as rows
FROM SOURCE.claims_src_tbl
WHERE file_loaded_ts >= DATEADD(day, -1, CURRENT_TIMESTAMP())
GROUP BY file_name;
```

### Row hash uniqueness

* Ensure row_hash is not null and duplicates within the same file are expected or flagged:

```sql
SELECT file_name, row_hash, COUNT(*) as cnt
FROM SOURCE.claims_src_tbl
GROUP BY file_name, row_hash
HAVING COUNT(*) > 1;
```

### Audit reconciliation

* Validate rows_loaded from `COPY` equals rows recorded in `AUDIT.load_audit` for the ingest_job_id.

---

## Acceptance criteria

* Source tables created and accessible by `data_ingest_role`.
* Ingested sample vendor files appear in SOURCE with exactly one row per source row and mandatory metadata populated.
* `AUDIT.file_audit` and `AUDIT.load_audit` entries exist and reconcile with table counts.
* Re-running ingestion for already processed file does not duplicate rows.
* Quarantine process moves malformed files with an error record.

---

## Short explanation of reasoning steps taken

* Chose TRANSIENT for Source tables to lower storage cost while preserving enough history for typical backfills, following Snowflake guidance on table types. ([Snowflake Documentation][1])
* Kept Source minimal to avoid mixing ingestion and curation concerns. This reduces rework when vendor schemas change.
* Added robust metadata and row_hash to enable deterministic dedupe in the CURATED stage.
* Recommended targeted COPY into partition paths to reduce unnecessary file scans and speed loads, supported by Snowflake COPY documentation. ([Snowflake Documentation][2])

---

## Assumptions and items requiring verification

* ASSUMPTION: Vendor will include a stable vendor-provided unique id per record for natural keying. If not, we must derive a robust natural key.
* Verify vendor daily volume and average file size to tune warehouse size and COPY parallelism.
* Confirm regulatory requirements for PHI retention to decide if any Source tables must be PERMANENT rather than TRANSIENT.
* Confirm whether upstream producers will provide `rows_expected` or manifests for faster reconciliation.
* Verify whether automatic clustering is enabled and budgeted; if not, clustering should be applied manually only when justified.

---

## Next actionable outputs I can produce now

* Parameterized SQL files for all Source table DDLs organized per feed.
* A Snowpark Python snippet to compute `row_hash`, PUT files to stage, run COPY INTO, and write `AUDIT` records.
* A small test dataset and SQL test suite to validate ingestion and idempotency.

Tell me which of the three you want and I will generate it.

[1]: https://docs.snowflake.com/en/user-guide/tables-temp-transient?utm_source=chatgpt.com "Working with Temporary and Transient Tables"
[2]: https://docs.snowflake.com/en/sql-reference/sql/copy-into-table?utm_source=chatgpt.com "COPY INTO <table> | Snowflake Documentation"
[3]: https://docs.snowflake.com/en/user-guide/tables-clustering-keys?utm_source=chatgpt.com "Clustering Keys & Clustered Tables | Snowflake Documentation"
[4]: https://docs.snowflake.com/en/sql-reference/sql/create-file-format?utm_source=chatgpt.com "CREATE FILE FORMAT | Snowflake Documentation"
[5]: https://docs.snowflake.com/en/user-guide/tables-auto-reclustering?utm_source=chatgpt.com "Automatic Clustering - Source: Snowflake Documentation"
