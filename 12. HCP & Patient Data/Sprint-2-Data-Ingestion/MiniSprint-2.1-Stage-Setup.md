Stage Setup

## Overview

This mini sprint creates the ingestion staging layer that will receive vendor files, hold them temporarily, and provide the controlled input surface for downstream COPY and Snowpark processes. The document covers naming and folder conventions, stage types to create, file format objects, secure permissions, audit metadata capture, housekeeping rules, and validation steps.

## Objectives

* Create named internal stages for each vendor and for common inbound feeds.
* Standardize folder layout and filename conventions to support efficient incremental loads.
* Create file format objects to parse CSV, JSON, and Parquet consistently.
* Implement file-level audit capture and checksum-based idempotency.
* Define retention and housekeeping rules for staged files.
* Provide examples for PUT, COPY INTO, and an initial file_audit DDL.

## Deliverables for this mini sprint

* SQL to create named internal stages and file formats.
* Example folder layout and filename conventions document.
* DDL for `AUDIT.file_audit` and `AUDIT.stage_inventory` tables.
* Sample PUT and COPY INTO command snippets for daily ingestion.
* Test plan and acceptance criteria.

---

## Why staging matters

A disciplined stage layer makes ingestion idempotent, auditable, and efficient. Using named internal stages simplifies access control and reduces upload latency for local files. Snowflake supports several stage types and expects staged files to be present before COPY commands run. ([Snowflake Documentation][1])

---

## Stage types and recommendations

### Use named internal stages for vendor feeds

* Create one named stage per vendor or per vendor feed where the vendor is the source of files that you will PUT from local or push into. Named internal stages are simple to manage for repo-style batch ingestion, reduce round-trips, and are ideal for test and dev usage. ([Snowflake Documentation][1])

### When to use external stages

* Use external stages only if the vendor pushes files directly to S3, Azure Blob, or GCS and you want Snowflake to reference that object store directly. External stages are appropriate for high-volume continuous feeds, but they add external storage management. COPY and Snowpipe both support external stages. ([Snowflake Documentation][2])

---

## Folder layout and filename convention

### Stage folder pattern

Use a deterministic, queryable folder pattern that supports targeted COPY operations:

```
@<stage_name>/<vendor>/<feed>/year=YYYY/month=MM/day=DD/hour=HH/<filename>
```

Example:

```
@stage_vendorA/claims/year=2026/month=02/day=27/hour=15/vendorA_claims_20260227_153245_0001.csv
```

### Filename guidelines

* `<vendor>_<feed>_YYYYMMDD_HHMMSS_<sequence>.<ext>`
* Include a timestamp and sequence to make ordering and uniqueness trivial.
* Keep filenames ASCII and avoid spaces.
* Vendors should deliver files in the 50 MB to 250 MB range when possible for best COPY throughput. Smaller files increase metadata overhead; larger files reduce parallelism. ([Snowflake Documentation][3])

### Rationale

This structure allows list and pattern operations to target narrow partitions, which makes COPY INTO operations faster and easier to parallelize. It also simplifies file discovery and delta detection.

---

## File format objects

Create reusable file formats in the `REFERENCE` schema. Example SQL:

```sql
CREATE OR REPLACE FILE FORMAT REFERENCE.ff_csv
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  STRIP_NULL_VALUES = TRUE
  TRIM_SPACE = TRUE
  ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;

CREATE OR REPLACE FILE FORMAT REFERENCE.ff_json
  TYPE = 'JSON'
  STRIP_NULL_VALUES = TRUE;

CREATE OR REPLACE FILE FORMAT REFERENCE.ff_parquet
  TYPE = 'PARQUET';
```

Reason

* Centralizing file formats avoids inconsistencies across COPY jobs and simplifies parsing logic.

Reference: Snowflake file format and CREATE STAGE docs. ([Snowflake Documentation][4])

---

## Stage creation examples

Create named internal stages and attach file formats where useful:

```sql
USE SCHEMA REFERENCE;

CREATE OR REPLACE STAGE REFERENCE.stage_vendorA
  FILE_FORMAT = REFERENCE.ff_csv
  COMMENT = 'Internal stage for vendorA claims';

CREATE OR REPLACE STAGE REFERENCE.stage_vendorB
  FILE_FORMAT = REFERENCE.ff_parquet
  COMMENT = 'Internal stage for vendorB prescription parquet files';
```

Notes

* You can set DIRECTORY = (ENABLE = TRUE) on stages to allow easier browsing of subfolders. ([Snowflake Documentation][4])

---

## PUT and COPY workflow examples

### Upload local files to stage (developer / operator)

Use the SnowSQL PUT command for single-machine uploads, or the Snowpark file API for programmatic uploads.

Example (SnowSQL):

```sql
PUT file://./vendorA_claims_20260227_153245_0001.csv @REFERENCE.stage_vendorA/claims/year=2026/month=02/day=27/hour=15 auto_compress=false;
```

Programmatic alternative

* Use Snowpark file API or driver libraries to iterate local folders and call PUT for each file so you retain control over path and partition. This is the pattern used earlier in the retail tutorial.

### Load from stage to SOURCE table

Use COPY INTO with a targeted path to avoid scanning unrelated files:

```sql
COPY INTO SOURCE.claims_tbl
FROM @REFERENCE.stage_vendorA/claims/year=2026/month=02/day=27/
FILE_FORMAT = (FORMAT_NAME = 'REFERENCE.ff_csv')
ON_ERROR = 'CONTINUE';
```

Rationale

* COPY INTO will only read files under the specified path. Listing and pattern-targeted COPY reduces unnecessary scanning and improves predictability. See Snowflake COPY documentation. ([Snowflake Documentation][2])

---

## Auditing and idempotency

### Audit tables

Create and populate `AUDIT.file_audit` to record every file that arrives to a stage.

Example DDL:

```sql
CREATE OR REPLACE TABLE AUDIT.file_audit (
  file_audit_id BIGINT AUTOINCREMENT,
  stage_name VARCHAR,
  file_path VARCHAR,
  file_name VARCHAR,
  vendor_id VARCHAR,
  feed_name VARCHAR,
  file_checksum VARCHAR,
  file_size_bytes BIGINT,
  rows_expected BIGINT,
  rows_loaded BIGINT,
  status VARCHAR,
  error_message VARCHAR,
  arrival_ts TIMESTAMP_TZ,
  processed_ts TIMESTAMP_TZ,
  ingest_job_id VARCHAR
);
```

### Checksum and idempotency

* Compute a file checksum (for example SHA256) when the file arrives and store it in `file_audit`. Use checksum to detect duplicate uploads and to validate integrity after transfer. Best practices for checksum validation are recommended in Snowflake migration and ingestion guides. ([Snowflake][5])
* When COPY INTO runs, compare the file checksum and skip files already processed. For safety, mark `status` as `processed` and include `ingest_job_id`.

---

## Security and permissions

### Principle

Grant least privilege on stages and the REFERENCE schema.

Example RBAC snippet:

```sql
GRANT USAGE ON STAGE REFERENCE.stage_vendorA TO ROLE data_ingest_role;
GRANT READ ON STAGE REFERENCE.stage_vendorA TO ROLE data_ingest_role;
GRANT USAGE ON SCHEMA REFERENCE TO ROLE data_engineer_role;
```

Notes

* Avoid broad grants to `PUBLIC` on any stage that contains sensitive or PHI-related data.
* For PHI files, require the uploader to use an approved service account and ensure access is limited to `data_ingest_role`.

---

## Retention and housekeeping

### Retention policy recommendations

* Keep staged files for short window by default, for example 30 to 90 days based on operational needs and compliance.
* Archive older staged files to an external object store if long-term forensic retention is required.

### Housekeeping tasks

* Daily job to reconcile files on the stage with `AUDIT.file_audit`.
* Purge stage folders older than retention threshold and log purge activity to `AUDIT.file_audit`.
* Optionally compress or aggregate many small files into fewer larger files for archival.

Reference: Snowflake best practices advise balancing file size for throughput and metadata overhead. ([Snowflake Documentation][3])

---

## Monitoring and validation checks

Create light-weight validation queries and metrics:

* Verify that newly arrived files were inserted into `file_audit` within X minutes of arrival.
* Row-count delta checks: compare `rows_expected` if provided versus `rows_loaded` after COPY.
* Error rate alert: percent of records rejected during load above threshold raises an incident.

Recommended views:

* `AUDIT.daily_stage_inventory_vw`
* `AUDIT.failed_loads_vw`

---

## Testing plan

### Unit tests

* Upload a small sample CSV, JSON, and Parquet file into each stage and assert file checksum and audit record presence.
* Run COPY INTO for the known test partition and assert `rows_loaded` matches expected.

### Integration tests

* Simulate delta: upload file A, run ingest, upload file B with changed rows, run ingest, verify `row_hash`-based dedupe and correct `CURATED` inserts.

### Performance tests

* Upload a production-like set of files and measure COPY INTO job duration and warehouse credits consumed.
* Tune file size, number of parallel COPY jobs, and warehouse size for target SLA.

---

## Acceptance criteria

* Named internal stages created for each vendor and for common inbound feeds.
* File format objects validated by loading sample files for CSV, JSON, and Parquet.
* `AUDIT.file_audit` records created for every staged file with checksum populated.
* COPY INTO jobs can target partitioned directories and complete without scanning unrelated files.
* Housekeeping job able to purge staged files older than retention policy.

---

## Short explanation of reasoning steps taken

* Translated incremental ingestion and delta detection requirements into a deterministic stage layout that enables targeted COPY operations.
* Standardized file naming and folder patterns to make programmatic discovery and auditable processing trivial.
* Centralized file format definitions to limit parsing variability and reduce production surprises.
* Required checksums and an audit table to make ingestion idempotent and forensic-friendly.
* Recommended file sizing and housekeeping that balance load performance and operational cost.
* Where appropriate cited Snowflake documentation and official best practice guidance to ground recommendations. ([Snowflake Documentation][1])

---

## Items requiring verification or uncertain

* Vendor agreement to deliver partitioned files with the proposed filename convention.
* Expected per-file sizes and daily volume so staging retention and housekeeping thresholds can be tuned.
* Regulatory requirements for staged file retention and whether staged files with PHI must be purged faster.
* Whether Snowpipe is preferred over scheduled PUT + COPY for near-real-time ingestion in production.

---

## Next practical outputs I can produce for you now

* SQL file set to create the stages, file formats, and `AUDIT.file_audit`.
* A Python Snowpark uploader script that PUTs local files into the correct stage path and writes `file_audit` entries.
* Example COPY INTO scripts parameterized by vendor, date and feed.
* Snowflake Snowsight queries for monitoring stage inventory.

Tell me which of these to generate next and I will produce it.

[1]: https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage?utm_source=chatgpt.com "Choosing an internal stage for local files"
[2]: https://docs.snowflake.com/en/sql-reference/sql/copy-into-table?utm_source=chatgpt.com "COPY INTO <table> | Snowflake Documentation"
[3]: https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare?utm_source=chatgpt.com "Preparing your data files - Source: Snowflake Documentation"
[4]: https://docs.snowflake.com/en/sql-reference/sql/create-stage?utm_source=chatgpt.com "CREATE STAGE"
[5]: https://www.snowflake.com/en/blog/best-practices-for-migrating-historical-data-to-snowflake/?utm_source=chatgpt.com "Best Practices for Migrating Historical Data to Snowflake"
