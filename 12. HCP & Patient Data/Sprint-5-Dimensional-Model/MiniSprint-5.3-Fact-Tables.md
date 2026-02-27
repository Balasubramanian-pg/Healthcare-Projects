# Fact Tables

## Overview

This mini sprint designs the fact tables that sit at the center of the star schema for the pharma commercial data platform. It covers fact types, grain definition, sample physical DDL, loading patterns, clustering and performance guidance for Snowflake, validation and monitoring, and rollout acceptance criteria.

Key authority references used while designing these patterns include classic dimensional modeling guidance and Snowflake storage and clustering behavior. ([Kimball Group][1])

---

## Objectives

* Define the fact table types needed for pharma reporting.
* Specify grains clearly and consistently for each fact.
* Provide production-ready DDL templates and loading patterns.
* Recommend Snowflake-specific clustering and micro-partitioning guidance.
* Describe validation, reconciliation, and monitoring checks.

---

## 1. Fact table types for a pharma platform

Design the minimal set of fact tables you will need to answer common commercial questions. Each fact has a clear grain and contained measures.

* **Transaction fact** (atomic sales or order events)
  Grain: one row = one sales order line or invoice line. Use for detailed analytics.
* **Prescription / Dispense fact**
  Grain: one row = one prescription or dispense event. Use for Rx analysis.
* **Periodic snapshot fact** (daily or monthly balances)
  Grain: one row = snapshot of a KPI at a time boundary (for inventory, open claims, monthly revenue).
* **Aggregated fact** (pre-aggregated rollups)
  Grain: aggregated by day/product/geography or other common reporting slices to accelerate dashboards.
* **Audit / Change fact** (optional)
  Grain: one row = an audit event or CDC record, useful for debugging and lineage.

These types follow Kimball-style dimensional modeling: facts contain numeric measures and keys to dimensions; grain must be stated in one sentence before design. ([Kimball Group][1])

---

## 2. How to choose and document the grain

Before building a fact table, write the grain in one sentence and confirm with stakeholders. Example:

* Transactional sales fact: “One row per order line item per order_id.”
* Prescription fact: “One row per dispensed prescription event per prescription_id.”

Why this matters

* Aggregations, deduplication, and join semantics all depend on the grain. If the grain is ambiguous analytics will be inconsistent. ([owox.com][2])

Document the grain as the first lines of every DDL file and in the repo README for the sprint.

---

## 3. Core design elements common to all fact tables

### Key columns

* `surrogate_fact_sk` — AUTOINCREMENT primary key (optional, useful for debugging)
* Dimension foreign keys (surrogate keys): `date_id`, `product_sk`, `hcp_sk`, `geography_sk`, `payer_sk`, `patient_sk` (as applicable)
* Business natural keys: `order_id`, `order_line_id`, `prescription_id` — used for idempotency and replay
* Measures: `quantity`, `amount_local`, `amount_usd`, `unit_price`, `discount`, `tax_amount`
* Metadata: `source_vendor`, `ingest_job_id`, `source_file`, `file_loaded_ts`, `row_hash`
* Operational flags: `is_active`, `is_correction`, `correction_reason`

### Best practice notes

* Keep facts narrow and measure-focused. Do not store descriptive text in fact tables; use dimensions.
* Store both local currency and USD amounts when possible, plus the exchange rate used for conversion.

---

## 4. Example DDLs

### 4.1 Transactional sales fact (atomic)

Grain: one row per sales order line.

```sql
CREATE OR REPLACE TABLE CONSUMPTION.sales_fact (
  sales_fact_sk      BIGINT AUTOINCREMENT PRIMARY KEY,
  order_id           VARCHAR NOT NULL,
  order_line_id      VARCHAR,
  date_id            INT,                -- FK to time_dim
  product_sk         BIGINT,             -- FK to product_dim
  hcp_sk             BIGINT,             -- FK to hcp_dim
  geography_sk       INT,                -- FK to geography_dim
  payer_sk           INT,
  quantity           NUMBER,
  unit_price_local   NUMBER(18,4),
  amount_local       NUMBER(18,4),
  exchange_rate      NUMBER(18,8),
  amount_usd         NUMBER(18,4),
  discount_amt       NUMBER(18,4),
  tax_amount         NUMBER(18,4),
  source_vendor      VARCHAR,
  ingest_job_id      VARCHAR,
  source_file        VARCHAR,
  file_loaded_ts     TIMESTAMP_TZ,
  row_hash           VARCHAR,
  is_correction      BOOLEAN DEFAULT FALSE
);
```

### 4.2 Prescription / Dispense fact

Grain: one row per prescription dispense event.

```sql
CREATE OR REPLACE TABLE CONSUMPTION.prescription_fact (
  prescription_fact_sk BIGINT AUTOINCREMENT PRIMARY KEY,
  prescription_id      VARCHAR,
  date_id              INT,
  patient_sk           BIGINT,
  product_sk           BIGINT,
  hcp_sk               BIGINT,
  quantity             NUMBER,
  days_supply          INT,
  amount_local         NUMBER(18,4),
  amount_usd           NUMBER(18,4),
  source_vendor        VARCHAR,
  ingest_job_id        VARCHAR,
  source_file          VARCHAR,
  file_loaded_ts       TIMESTAMP_TZ,
  row_hash             VARCHAR
);
```

### 4.3 Periodic snapshot fact (daily sales)

Grain: one row per date/product/geography.

```sql
CREATE OR REPLACE TABLE CONSUMPTION.daily_sales_snapshot (
  snapshot_date     DATE,
  product_sk        BIGINT,
  geography_sk      INT,
  total_quantity    NUMBER,
  total_amount_usd  NUMBER(18,4),
  snapshot_source   VARCHAR,    -- indicator: derived from sales_fact
  last_updated_ts   TIMESTAMP_TZ
);
```

---

## 5. Loading and idempotency patterns

### Append-only transactional loads

* For most atomic facts prefer append-only loads keyed by `row_hash` and natural keys.
* To avoid duplicates run an idempotency filter: insert only rows whose `row_hash` and `order_id` do not already exist in the target fact for the same ingest window.

### Merge / upsert for corrections

* If vendor corrections and deletes are common, use `MERGE` semantics to apply corrections:

  * Match on natural key and/or `order_line_id`
  * If matched and `row_hash` differs, update the existing row (mark `is_active = FALSE`) and insert corrected row, or update measure values depending on survivorship policy.

### Delta / late-arriving data

* Maintain `audit` of ingest windows and list of processed files. When late data arrives for older `date_id`, run targeted reprocessing for the affected date range. Recompute aggregates or snapshot rows that include the date.

### Snapshot replacement

* For periodic snapshots, replace the snapshot rows for the date (truncate by date and insert new snapshot rows) to ensure snapshot is an atomic picture of the KPI at the date boundary.

---

## 6. Snowflake-specific performance and clustering guidance

### Micro-partition and clustering guidance

* Snowflake micro-partitions are automatic. Good clustering keys speed pruning for common predicates. Typical cluster keys for fact tables are `date_id` plus one or two high-usage dimensions such as `product_sk` or `geography_sk`. Limit cluster keys to 3 or 4 columns. ([Snowflake Documentation][3])

### Recommended cluster key examples

* `CLUSTER BY (date_id)` for date-heavy queries
* `CLUSTER BY (date_id, product_sk)` if queries frequently filter by product and date
* Avoid clustering on very high cardinality keys with little pruning benefit

### Practical points

* Start without a cluster key; measure micro-partition pruning using `SYSTEM$CLUSTERING_INFORMATION` and add clustering when needed. Automatic clustering is an option but has cost implications. ([Snowflake Documentation][4])

---

## 7. Partitioning, retention and maintenance

* Do not rely on explicit partition columns for Snowflake. Use stage folder partitioning for efficient copy loads. Keep fact tables in permanent or transient form according to your retention needs and compliance.
* Schedule periodic housekeeping for very old rows only if needed for cost control. For most reporting needs keep facts permanent and use time travel minimally to control cost.

---

## 8. Validation and reconciliation queries

After each load run these checks:

* **Row count per file**
  Compare `AUDIT.file_audit.rows_loaded` to counts from `sales_fact` grouped by `source_file`.
* **Idempotency check**
  Ensure no duplicates: `SELECT order_id, COUNT(*) FROM sales_fact GROUP BY order_id HAVING COUNT(*) > 1` for the ingest window.
* **Amount reconciliation**
  Compare `SUM(amount_usd)` in `sales_fact` to the corresponding daily snapshot totals.
* **Late-arrival coverage**
  Verify reprocessed date windows have stable counts after backfill.

Write these checks into automated SQL jobs and log results to `AUDIT.load_validation`. Store the most important metrics in a monitoring dashboard.

---

## 9. Query patterns and materialized aggregates

* Provide pre-aggregated tables for heavy dashboard queries, e.g., `monthly_revenue_by_brand`. Recompute these nightly from `sales_fact` using `GROUP BY` and `INSERT OVERWRITE` or `MERGE` patterns. Pre-aggregates reduce interactive latency at cost of storage and refresh compute.

---

## 10. Acceptance criteria

* Each fact table has a clearly documented grain and DDL in the repo.
* Ingest pipeline populates fact tables with `row_hash` and lineage metadata.
* Idempotency check passes for repeated runs.
* At least one clustering strategy evaluation documented and cluster keys applied if pruning gains > threshold.
* Reconciliation checks pass for a sample set of files and a pilot day.
* Snapshot facts reflect expected values after backfill and delta processing.

---

## 11. Monitoring metrics to track

* Files processed per run, rows inserted, rejected rows.
* Ingest latency from file arrival to row visibility.
* Query latency for representative dashboard queries.
* Micro-partition scan reduction after clustering changes.
* Warehouse credits consumed per load job.

---

## 12. Short explanation of reasoning steps taken

* I started by listing the business analytics needs for pharma and matched them to canonical fact types.
* I enforced the discipline of writing an explicit grain for each fact because aggregation and deduplication depend on it. ([owox.com][2])
* I applied Snowflake-specific guidance around micro-partitions and clustering to recommend conservative cluster keys and an iterative approach: measure first then cluster. ([Snowflake Documentation][3])
* I preferred append-only atomic facts where possible, and `MERGE` patterns where corrections are frequent. This balances simplicity and correctness for late-arriving and corrected vendor data.

---

## 13. Items requiring verification or uncertain

* Confirm which natural keys vendors guarantee for transactional dedupe. If not present we must define robust composite keys.
* Confirm business policy on survivorship for corrected transactions: should corrected rows replace or coexist alongside originals with flags?
* Confirm acceptable SLA windows for snapshot refreshes and for incremental reprocessing of late arrivals.
* Confirm whether automatic clustering service is budgeted or manual clustering is preferred.

---

If you want, I can now:

* generate SQL files for the DDLs above and place them in the repo folder structure for this sprint, or
* produce a Snowpark Python load-and-merge template that implements idempotent loads, `MERGE`-style corrections, row hashing and post-load validation queries.

Which of those should I produce next?

[1]: https://www.kimballgroup.com/wp-content/uploads/2013/08/2013.09-Kimball-Dimensional-Modeling-Techniques11.pdf?utm_source=chatgpt.com "Kimball Dimensional Modeling Techniques"
[2]: https://www.owox.com/glossary/grain-in-fact-table?utm_source=chatgpt.com "What Is Grain in a Fact Table? – Definition and Examples"
[3]: https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions?utm_source=chatgpt.com "Micro-partitions & Data Clustering"
[4]: https://docs.snowflake.com/en/user-guide/tables-clustering-keys?utm_source=chatgpt.com "Clustering Keys & Clustered Tables"
