# Partition Design

## Overview

This document defines the partitioning strategy for the pharma commercial data platform. It explains the partition structure used for staged files, source loads, curated tables, and consumption fact tables. It also explains the rationale and tradeoffs behind each choice and gives an implementation checklist and verification points.

---

# 1. Goals and constraints considered

### Primary goals

* Make ingestion and delta detection efficient for very large feeds.
* Support selective re-load and targeted backfill by date, vendor, or region.
* Keep query performance predictable for common analytics patterns.
* Minimize storage and compute cost where possible.

### Constraints and domain specifics

* Data is multi-vendor and multi-region, arriving in CSV, JSON, and Parquet formats.
* Regulatory constraints for PHI may require masking before long term storage.
* Snowflake uses automatic micro-partitioning; explicit partitioning is implemented via stage folder layout, copy filtering, clustering keys, and pragmatic table design.
* Need robust delta processing and deduplication across repeated file deliveries.

---

# 2. Partitioning layers and recommended patterns

Partitioning is applied at four levels. Each level solves different operational and performance problems.

### 2.1 Stage folder partitioning (file organization)

Use folder-based partitions inside the internal or external stage to make file discovery and COPY operations efficient.

Recommended path pattern

* `/<vendor>/<source_type>/year=YYYY/month=MM/day=DD/HH=hh/<filename>`
  Examples
* `vendorA/claims/year=2026/month=02/day=27/claims_20260227_001.csv`
* `vendorB/rx/year=2026/month=02/day=26/rx_2026-02-26.parquet`

Why

* Easy to list unprocessed files for a given day or vendor
* COPY INTO and PUT can target narrow partitions and avoid scanning everything
* Supports parallel ingestion by partition

Notes

* Include a vendor identifier and source_type at top level to simplify ACLs and processing rules.
* Use padded numeric fields for ordering and lexicographic sorting.

### 2.2 File naming and metadata

Embed useful metadata in filenames and keep file-level metadata in an audit table.

Filename conventions

* `<vendor>_<feed>_YYYYMMDD_HHMMSS_<sequence>.ext`
* Example: `vendorA_claims_20260227_153245_0001.csv`

Metadata to capture on ingest

* file_path
* file_name
* file_checksum (md5/sha256)
* vendor_id
* feed_name
* rows_expected (optional)
* file_arrival_ts

Why

* File checksum and path are required for idempotency and delta detection
* A reliable audit enables reproducible replays and forensic investigation

### 2.3 Source table partitioning and clustering

Source tables are transient copies of staged data with metadata columns. Use the following design:

Logical clustering keys

* `vendor_id`
* `file_loaded_ts`
* `event_date` or `claim_date`

Table type

* TRANSIENT or TEMPORARY depending on retention policy and compliance

Why

* Most incremental processes operate by vendor and file timestamp
* Clustering on `event_date` or `claim_date` supports date-range queries and reduces micro-partition scanning for common analytical queries

Implementation notes for Snowflake

* Snowflake micro-partitions are automatic. Use `CLUSTER BY` when query patterns justify maintenance cost.
* Start without clustering, monitor query performance, and add clustering if micro-partition pruning is insufficient.

### 2.4 Curated table partitioning and clustering

Curated tables are the canonical, cleaned records used to build the model.

Recommended clustering keys

* `event_date` or `claim_date`
* `country` or `region`
* `drug_id_fk` for product heavy queries

Table type

* PERMANENT (with controlled time travel settings)

Why

* Date queries and regional rollups are the most common patterns
* Clustering by `drug_id_fk` helps product analysis queries that filter by therapy area or brand

Retention and time travel

* Configure time travel to the minimum required for operational recovery to reduce cost
* Implement archival or tiered storage if long-term retention is required

### 2.5 Consumption fact table clustering

Fact tables should be optimized for read performance.

Suggested cluster keys

* `date_id`
* `product_id`
* `geography_id`

Why

* These keys match common group-by dimensions in dashboards and reduce query scan costs

Notes

* Keep cluster key cardinality balanced. Very high cardinality keys can cause clustering overhead.
* Use materialized aggregates for extremely high cardinality queries rather than deep clustering.

---

# 3. Delta detection and deduplication pattern

### Strategy

1. Record every staged file in `AUDIT.file_audit` with checksum and file_loaded_ts.
2. When copying into `SOURCE`, populate `file_name`, `file_path`, `file_checksum`, and `file_loaded_ts`.
3. Compute a `row_hash` for each source row derived from the natural key and business attributes.
4. For CURATED insertion:

   * Use left anti-join between incoming `SOURCE` rows and existing `CURATED` rows on natural key plus `row_hash` to find new or changed rows.
   * Insert new rows and mark older versions as `superseded` when necessary.
5. Maintain `last_processed_file` and `last_processed_ts` per vendor to expedite incremental runs.

### Why this pattern

* File-level auditing ensures idempotent processing
* `row_hash` simplifies detection of updates vs duplicates
* Left anti-join prevents reprocessing records that have not changed

---

# 4. Tradeoffs and rationale

### Tradeoff: many small files versus fewer large files

* Many small files

  * Pro: easier granular reprocessing and parallel ingestion
  * Con: higher metadata overhead and more small-file operations
* Fewer large files

  * Pro: fewer file metadata entries and better throughput for bulk copy
  * Con: coarser granularity for delta detection

Choice

* Prefer daily partitioned files with reasonable chunk sizes to balance operational complexity and throughput. Aim for files in 50 MB to 500 MB range for text formats if vendor supports it.

### Tradeoff: pre-partitioned stage versus dynamic partitioning during COPY

* Pre-partitioned stage

  * Pro: very fast targeted COPY, easier to parallelize
  * Con: requires upstream partitioning discipline
* Dynamic partitioning

  * Pro: simpler vendor contract
  * Con: more work to filter and move files before COPY

Choice

* Require vendor-side partitioning where possible. Enforce through data contract. Support minor vendor exceptions with a small pre-processing service.

### Tradeoff: clustering maintenance cost versus query savings

* Clustering improves query performance but adds maintenance overhead and compute cost for reclustering.
* Start with no clustering, measure micro-partition pruning metrics, and add clustering only when ROI justifies it.

---

# 5. Implementation checklist

### Stage and file conventions

* [ ] Create stage folders following `/<vendor>/<feed>/year=YYYY/month=MM/day=DD/`
* [ ] Enforce file naming convention and checksum capture
* [ ] Implement a small file aggregator when files are too small

### Source layer

* [ ] Create TRANSIENT `SOURCE` tables with metadata columns
* [ ] Implement `COPY INTO` scripts that accept folder path parameters
* [ ] Populate `AUDIT.file_audit` during COPY

### Curated layer

* [ ] Implement `row_hash` generation logic
* [ ] Implement left anti-join delta insert pattern
* [ ] Implement `record_status` updates for superseded rows

### Clustering and performance

* [ ] Start without clustering, collect query stats
* [ ] If necessary, add `CLUSTER BY` on suggested keys and schedule `RECLUSTER` maintenance
* [ ] Add materialized views or aggregate tables for slow, high cardinality queries

### Monitoring and housekeeping

* [ ] Create a daily job to reconcile staged files to `file_audit`
* [ ] Implement retention cleanup for stage folders older than retention period
* [ ] Alert on missing daily vendor files or excessive parse errors

---

# 6. Acceptance criteria for MiniSprint 1.3

* Stage folder layout implemented and documented
* `AUDIT.file_audit` receives records for files placed in stage
* `SOURCE` load can target a single partition path and finish without scanning irrelevant files
* `CURATED` pipeline correctly inserts only new or updated rows using `row_hash` anti-join
* Query sample analytics that filter a one month date range show acceptable micro-partition pruning or indicate clustering need

---

# 7. Short, explicit explanation of reasoning steps taken

* Translated ingestion and delta needs into a stage folder layout that supports targeted COPY operations.
* Ensured metadata capture at file and row levels to enable idempotent processing and auditing.
* Selected clustering keys that align with common query patterns to reduce scan costs while keeping maintenance optional.
* Chose transient tables for stage layer to reduce storage cost and permanent tables for curated layer to preserve business history.
* Chose a `row_hash` plus left anti-join delta pattern because it is simple, deterministic, and avoids reprocessing unchanged rows.

---

# 8. Items requiring verification or uncertain

* Vendor willingness to produce files partitioned by date and vendor as specified
* Typical file sizes vendors will deliver so aggregation thresholds can be tuned
* Regulatory constraints that might force different retention or table types for `SOURCE` objects
* Exact query patterns and dashboards that drive clustering ROI calculations
* Business SLA for acceptable latency between file arrival and availability in `CONSUMPTION`

---

# 9. Next steps I can take for you

* Generate sample `COPY INTO` commands and parameterized ingestion scripts for each vendor.
* Produce SQL for `AUDIT.file_audit` and `SOURCE` table DDL with example `COPY` usage.
* Create a small Snowpark Python example that implements `row_hash` computation and left anti-join delta load.

Tell me which of those to produce next and I will create it.
