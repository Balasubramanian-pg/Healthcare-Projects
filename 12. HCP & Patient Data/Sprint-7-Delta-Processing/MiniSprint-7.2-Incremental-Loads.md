# MiniSprint 7.2 — Incremental Loads

## Overview

This mini sprint converts the pharma data platform from **batch historical processing** into a **continuous incremental pipeline**.

After MiniSprint 7.1 detected deltas, this sprint focuses on **processing only those deltas safely across all layers**:

* Source
* Curated
* Unified dataset
* Dimension tables
* Fact tables
* KPI dashboards

The objective is to ensure that every pipeline run processes **only new or changed data**, while maintaining correctness and auditability.

---

## Objective

* Process only delta records identified earlier.
* Avoid full table reloads.
* Support vendor corrections.
* Maintain dimensional consistency.
* Update fact tables incrementally.
* Reduce compute cost and runtime.
* Enable production-grade scheduling.

---

## Pipeline Evolution

### Before Incremental Loads

```text
All Files → Full Reload → Rebuild Tables
```

### After Incremental Loads

```text
New / Changed Data
        ↓
Incremental Processing
        ↓
Target Tables Updated
```

This is the transition from **development ETL** to **production ETL**.

---

# Incremental Load Architecture

```text id="1pi8r7"
Delta Detection
      ↓
Stage Increment
      ↓
Source Increment
      ↓
Curated Increment
      ↓
Dimension Update
      ↓
Fact Merge
      ↓
Dashboard Refresh
```

Each layer processes only impacted records.

---

# Incremental Processing Principles

## Principle 1: Idempotent Pipelines

Running the same job twice must not duplicate data.

Meaning:

```text
Same input → Same output
```

Achieved using:

* business keys
* row hashes
* merge logic

---

## Principle 2: Append First, Correct Later

Healthcare data often changes.

Strategy:

* insert new records quickly
* apply corrections using controlled merge logic

---

## Principle 3: Window-Based Reprocessing

Late arriving data handled using rolling windows.

Example:

```text
Reprocess last 14 days
```

Avoids scanning entire history.

---

# Step 1: Incremental Stage → Source Load

Snowflake COPY command already supports incremental behavior through load history.

Example:

```sql id="m8x7nv"
COPY INTO SOURCE.claims_raw
FROM @RAW_STAGE/claims/
FILE_FORMAT = (FORMAT_NAME = csv_format)
ON_ERROR = CONTINUE;
```

Snowflake automatically skips previously loaded files.

Key mechanism:

* file load metadata stored internally.

---

# Step 2: Source → Curated Increment

Process only records not yet curated.

Logic:

```sql id="4z5w1y"
SELECT s.*
FROM SOURCE.claims_raw s
LEFT ANTI JOIN CURATED.claims_clean c
ON s.claim_id = c.claim_id
AND s.row_hash = c.row_hash;
```

Result:
Only new or corrected records move forward.

---

## Snowpark Example

```python id="oc7yrr"
delta_df = source_df.join(
    curated_df,
    (source_df.claim_id == curated_df.claim_id) &
    (source_df.row_hash == curated_df.row_hash),
    how="left_anti"
)
```

---

# Step 3: Incremental Dimension Updates

Dimensions must support new members without rebuilding.

Example scenario:
New HCP appears.

Process:

1. Detect unseen dimension values.
2. Insert only missing members.

Example:

```sql id="91c3jw"
INSERT INTO DIM.hcp_dim
SELECT DISTINCT hcp_id, specialty
FROM delta_records d
LEFT JOIN DIM.hcp_dim h
ON d.hcp_id = h.hcp_id
WHERE h.hcp_id IS NULL;
```

---

## Slowly Changing Dimension Support

Recommended approach:

Type 1

* overwrite descriptive updates.

Type 2

* maintain history.

Example columns:

```text
effective_start_date
effective_end_date
is_current
```

Used when territory or affiliation changes.

---

# Step 4: Incremental Fact Table Loads

Facts use **MERGE operations**.

Example:

```sql id="p1o0zq"
MERGE INTO FACT.sales_fact tgt
USING delta_dataset src
ON tgt.order_id = src.order_id
WHEN MATCHED AND tgt.row_hash <> src.row_hash THEN
UPDATE SET amount_usd = src.amount_usd
WHEN NOT MATCHED THEN
INSERT VALUES (...);
```

Behavior:

* new record inserted
* corrected record updated

---

# Step 5: Incremental Unified Dataset Refresh

Instead of rebuilding unified tables:

```text
Union only delta curated datasets
```

Example:

```sql id="jztp7n"
INSERT INTO CURATED.unified_events
SELECT *
FROM curated_delta;
```

---

# Step 6: Incremental Aggregate Refresh

Dashboards depend on aggregates.

Strategy options:

## Option A: Recompute impacted dates

```sql
DELETE FROM agg_daily_sales
WHERE sales_date BETWEEN :start AND :end;
```

Then reload.

## Option B: Merge aggregates

Recommended for very large datasets.

---

# Incremental Scheduling Model

Typical pharma cadence:

| Job                | Frequency |
| ------------------ | --------- |
| Ingestion          | Hourly    |
| Curated Processing | Hourly    |
| Dimension Updates  | Hourly    |
| Fact Merge         | Hourly    |
| Dashboard Refresh  | Daily     |

---

# Audit and Monitoring

Track incremental performance.

```sql id="n1o26m"
CREATE TABLE AUDIT.incremental_run_log (
    run_id STRING,
    rows_processed NUMBER,
    rows_inserted NUMBER,
    rows_updated NUMBER,
    execution_time_sec NUMBER,
    run_ts TIMESTAMP
);
```

---

# Performance Optimization Decisions

Design choices made:

* Avoid table rebuilds.
* Process only delta partitions.
* Use MERGE instead of DELETE + INSERT.
* Push joins into Snowflake engine.
* Maintain hash comparison columns.

Result:
Massive reduction in compute usage.

---

# Validation Checks

Increment correctness validation:

Row growth check:

```sql id="k6nco7"
SELECT COUNT(*)
FROM FACT.sales_fact;
```

Duplicate prevention:

```sql id="e4yskm"
SELECT order_id, COUNT(*)
FROM FACT.sales_fact
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Delta sanity check:

```sql id="2nuvmo"
SELECT *
FROM AUDIT.incremental_run_log
ORDER BY run_ts DESC;
```

---

# Acceptance Criteria

* Incremental runs complete without full reload.
* Duplicate facts prevented.
* New dimensions inserted automatically.
* Corrections handled correctly.
* Late arriving data processed.
* Runtime significantly reduced.
* Audit logs captured.

---

# Explanation of Design Thinking

Incremental loads were designed around production pharma constraints:

1. Data volume continuously grows.
2. Vendors resend corrected datasets.
3. Dashboards require near-real-time updates.
4. Compute efficiency directly impacts cost.

Therefore the system evolves into:
Detect → Process → Merge → Validate.

This creates a scalable enterprise pipeline.

---

# Items Requiring Verification or Uncertain

* Expected vendor correction frequency.
* Acceptable late-arrival processing window.
* Dimension history policy approval.
* SLA expectations for incremental refresh.
* Warehouse sizing for concurrent runs.

---

## Next Mini Sprint

MiniSprint 7.3 — Production Orchestration

This sprint introduces task scheduling, dependency orchestration, retries, and automated pipeline execution inside Snowflake.
