# MiniSprint 8.2 — Optimization

## Overview

This mini sprint focuses on **platform optimization** after the pipeline becomes fully operational with incremental processing and auditing.

At this stage the pharma data platform already supports:

* ingestion
* delta detection
* incremental loads
* dimensional modeling
* dashboards
* auditing

Optimization ensures the system runs **efficiently at scale** as data volume, users, and workloads grow.

The goal is not redesigning architecture but **making the existing system faster, cheaper, and more reliable**.

---

## Objective

* Reduce Snowflake compute consumption.
* Improve query performance.
* Optimize incremental pipelines.
* Improve dashboard responsiveness.
* Reduce data scan volume.
* Stabilize warehouse utilization.
* Prepare platform for enterprise scale.

---

## Optimization Scope

```text id="8m2xrd"
Storage Optimization
        +
Compute Optimization
        +
Query Optimization
        +
Pipeline Optimization
        +
Dashboard Optimization
```

All five layers must be tuned together.

---

# 1. Storage Optimization

Snowflake automatically manages storage using micro-partitions, but design decisions still affect performance.

## Recommended Table Design

Large fact tables should organize around analytical access patterns.

Typical pharma query pattern:

```text id="j7r9df"
Date
Product
Region
```

Recommended clustering:

```sql id="u4pq4p"
ALTER TABLE FACT.sales_fact
CLUSTER BY (date_id, product_sk);
```

Reason:
Most analytics filter by time and product.

---

## Reduce Data Duplication

Avoid storing:

* repeated descriptive attributes
* derived columns already computable

Move descriptive attributes into dimensions.

---

## Data Retention Optimization

Historical raw data grows rapidly.

Strategy:

* retain raw source data short term
* retain curated and fact data long term

Example:

```sql id="sk3c8p"
ALTER TABLE SOURCE.claims_raw
SET DATA_RETENTION_TIME_IN_DAYS = 1;
```

---

# 2. Compute Optimization

Warehouse configuration strongly impacts cost.

## Warehouse Segmentation

Separate workloads:

| Warehouse | Purpose    |
| --------- | ---------- |
| ETL_WH    | Pipelines  |
| BI_WH     | Dashboards |
| ADHOC_WH  | Analysts   |

Prevents resource contention.

---

## Auto Suspend Configuration

```sql id="p3ovrf"
ALTER WAREHOUSE ETL_WH
SET AUTO_SUSPEND = 60;
```

Stops unused compute automatically.

---

## Right-Sizing Warehouses

Guideline:

* Short heavy loads → larger warehouse briefly.
* Continuous small jobs → smaller warehouse.

Scaling vertically often cheaper than long runtimes.

---

# 3. Query Optimization

Most performance issues originate from inefficient SQL.

## Avoid Full Table Scans

Bad pattern:

```sql id="wrsc21"
SELECT *
FROM FACT.sales_fact;
```

Optimized pattern:

```sql id="b4x3km"
SELECT *
FROM FACT.sales_fact
WHERE date_id BETWEEN :start AND :end;
```

---

## Column Pruning

Select only required columns.

Benefits:

* reduced I/O
* faster execution

---

## Predicate Pushdown

Filters must occur early.

Snowflake automatically pushes predicates when queries are structured correctly.

---

# 4. Incremental Pipeline Optimization

Incremental pipelines must remain lightweight.

### Optimize MERGE Operations

Limit merge scope:

```sql id="2u9xwd"
MERGE INTO FACT.sales_fact tgt
USING delta_data src
ON tgt.order_id = src.order_id
AND tgt.date_id >= DATEADD(day,-14,CURRENT_DATE);
```

Avoid scanning full fact table.

---

### Partition-Based Processing

Process only impacted windows.

Example:

```text id="9cuxmu"
Process last 14 days only
```

Common pharma late-arrival window.

---

### Reduce Snowpark Data Movement

Best practice:

* keep transformations inside Snowflake engine
* avoid collecting large datasets into Python memory.

---

# 5. Dashboard Optimization

Snowsight dashboards must remain interactive.

## Use Aggregated Tables

Instead of querying billions of rows:

```text id="7ndv9g"
sales_fact → agg_monthly_sales
```

Example aggregation:

```sql id="r2prv3"
CREATE TABLE AGG.monthly_sales AS
SELECT
    month_id,
    product_sk,
    SUM(amount_usd) revenue
FROM FACT.sales_fact
GROUP BY 1,2;
```

---

## Cache-Friendly Queries

Repeated dashboard queries benefit from Snowflake result caching.

Avoid random functions that invalidate cache.

---

## Limit Visualization Cardinality

Charts with thousands of categories slow dashboards.

Recommendation:
Top N + Others grouping.

---

# 6. Monitoring Optimization Impact

Measure improvement using query history.

Example:

```sql id="0t2i9a"
SELECT
query_text,
execution_time,
bytes_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
ORDER BY start_time DESC;
```

Track:

* runtime reduction
* bytes scanned reduction
* warehouse credits consumed.

---

# 7. Optimization Metrics

Platform health indicators:

| Metric              | Target        |
| ------------------- | ------------- |
| Pipeline runtime    | decreasing    |
| Bytes scanned       | minimized     |
| Warehouse idle time | near zero     |
| Dashboard latency   | < few seconds |
| Merge runtime       | stable growth |

---

# 8. Cost Optimization Strategy

Major Snowflake cost drivers:

* unnecessary scans
* oversized warehouses
* repeated full reloads
* inefficient joins

Optimization approach:

```text id="tzy5qf"
Process Less Data
Scan Less Data
Run Shorter Queries
Suspend Faster
```

---

# Acceptance Criteria

* Fact queries show reduced scan volume.
* Incremental jobs run faster than baseline.
* Warehouse idle cost reduced.
* Dashboard response improved.
* Aggregated tables implemented.
* Query history confirms optimization gains.

---

# Explanation of Design Thinking

Optimization happens after system stability because:

1. Premature optimization hides architectural issues.
2. Real workload patterns must be observed first.
3. Snowflake performance depends heavily on usage behavior.
4. Pharma datasets grow continuously over time.

Therefore optimization focuses on **measured improvements**, not assumptions.

---

# Items Requiring Verification or Uncertain

* Expected long-term data growth rate.
* Dashboard concurrency expectations.
* Acceptable warehouse credit budget.
* Late-arriving data window size.
* Regulatory retention requirements affecting storage optimization.

---

## Next Mini Sprint

MiniSprint 8.3 — Monitoring and Alerting

This sprint converts audit and optimization insights into **automated operational alerts and platform observability**.
