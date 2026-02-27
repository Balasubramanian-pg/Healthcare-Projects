# MiniSprint 8.1 — Audit

(Work In Progress)

## Overview

This mini sprint introduces the **Audit Framework** for the pharma data platform.

Until now the platform can:

* ingest data
* process deltas
* update dimensions and facts
* power dashboards

However, enterprise healthcare systems require something more important:

**provable data accountability.**

Audit capabilities allow teams to answer questions such as:

* What data was loaded?
* When was it processed?
* Which pipeline created a record?
* Why did counts change?
* Which vendor file caused an issue?

This sprint establishes the foundation for **observability, compliance, and traceability**.

---

## Objective

* Track every pipeline execution.
* Capture file ingestion history.
* Monitor record movement across layers.
* Enable reconciliation between stages.
* Support regulatory and operational audits.
* Provide debugging capability for failures.

---

## Audit Architecture

```text id="k5g1a2"
Vendor Files
      ↓
Ingestion Audit
      ↓
Processing Audit
      ↓
Transformation Audit
      ↓
Consumption Audit
```

Audit data flows alongside business data.

---

## Audit Design Philosophy

Healthcare platforms must assume:

* pipelines will fail
* vendors resend files
* corrections occur frequently
* regulators may request lineage proof

Therefore audit design follows three principles:

1. **Every run is traceable**
2. **Every record movement is measurable**
3. **Nothing important is overwritten**

---

# Audit Layers

## 1. Pipeline Run Audit

Tracks each ETL execution.

Table:

```sql id="1odv77"
CREATE TABLE AUDIT.pipeline_run_log (
    run_id STRING,
    pipeline_name STRING,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status STRING,
    triggered_by STRING,
    warehouse_used STRING,
    total_runtime_sec NUMBER
);
```

Purpose:

* operational monitoring
* SLA tracking
* failure investigation

---

## 2. File Ingestion Audit

Tracks vendor file lifecycle.

```sql id="5w2l9y"
CREATE TABLE AUDIT.file_audit (
    file_name STRING,
    source_vendor STRING,
    file_size NUMBER,
    arrival_ts TIMESTAMP,
    processed_ts TIMESTAMP,
    records_loaded NUMBER,
    records_rejected NUMBER,
    checksum STRING,
    status STRING
);
```

Key Benefits:

* prevents duplicate loads
* enables delta detection
* validates vendor delivery

---

## 3. Data Movement Audit

Tracks row movement between layers.

```sql id="e7o9ra"
CREATE TABLE AUDIT.layer_movement_log (
    run_id STRING,
    source_layer STRING,
    target_layer STRING,
    rows_read NUMBER,
    rows_inserted NUMBER,
    rows_updated NUMBER,
    rows_rejected NUMBER,
    execution_ts TIMESTAMP
);
```

Example tracking:

```text id="k3rtwq"
SOURCE → CURATED
CURATED → UNIFIED
UNIFIED → FACT
```

---

## 4. Data Quality Audit

Stores validation outcomes.

```sql id="z1vm6h"
CREATE TABLE AUDIT.data_quality_log (
    rule_name STRING,
    table_name STRING,
    failed_records NUMBER,
    severity STRING,
    validation_ts TIMESTAMP
);
```

Examples:

* null patient_id detected
* invalid drug_code
* negative quantity

---

## 5. Delta Processing Audit

Tracks incremental behavior.

```sql id="9s8y8x"
CREATE TABLE AUDIT.delta_audit (
    run_id STRING,
    files_detected NUMBER,
    rows_new NUMBER,
    rows_changed NUMBER,
    rows_ignored NUMBER,
    execution_ts TIMESTAMP
);
```

Helps confirm incremental logic works correctly.

---

# Audit Identifiers

Every pipeline run generates:

```text id="0xqjve"
RUN_ID
```

This ID propagates across:

* ingestion
* transformation
* fact loading
* dashboard refresh

Result:
Full lineage reconstruction possible.

---

# Snowpark Logging Example

```python id="k7n9pa"
run_id = str(uuid.uuid4())

session.sql(f"""
INSERT INTO AUDIT.pipeline_run_log
VALUES (
    '{run_id}',
    'incremental_pipeline',
    CURRENT_TIMESTAMP(),
    NULL,
    'RUNNING',
    CURRENT_USER(),
    CURRENT_WAREHOUSE(),
    NULL
)
""").collect()
```

Update after completion:

```python id="x4n2hb"
session.sql(f"""
UPDATE AUDIT.pipeline_run_log
SET end_time = CURRENT_TIMESTAMP(),
    status = 'SUCCESS'
WHERE run_id = '{run_id}'
""").collect()
```

---

# Reconciliation Framework

Audit enables reconciliation checks.

Example:

```sql id="s4l9km"
SELECT
    source_count,
    curated_count,
    source_count - curated_count AS variance
FROM reconciliation_view;
```

Goal:
Counts must reconcile within expected tolerance.

---

# Operational Monitoring Queries

Recent failures:

```sql id="k6ewy1"
SELECT *
FROM AUDIT.pipeline_run_log
WHERE status = 'FAILED'
ORDER BY start_time DESC;
```

File backlog detection:

```sql id="y7cfvr"
SELECT *
FROM AUDIT.file_audit
WHERE status <> 'processed';
```

---

# Pharma Compliance Importance

Audit systems support:

* FDA validation environments
* commercial reporting verification
* vendor dispute resolution
* financial reconciliation
* data lineage inspection

Audit tables often become mandatory in regulated environments.

---

# Performance Considerations

Design decisions:

* Audit tables append-only.
* Small row footprint.
* Indexed by run timestamp.
* Partition logically by execution date.

Audit writes must never slow pipelines.

---

# Acceptance Criteria

* Every pipeline run logged.
* File ingestion traceable.
* Row movement measurable.
* Data quality failures recorded.
* Delta processing tracked.
* Reconciliation queries available.

---

# Current Work In Progress Scope

This sprint currently establishes:

* audit schema structure
* core logging tables
* run identifier propagation
* basic monitoring queries

Upcoming expansion may include:

* automated alerting
* SLA monitoring dashboards
* anomaly detection
* lineage visualization.

---

# Explanation of Design Thinking

Audit was introduced after incremental processing because:

1. Production systems require visibility.
2. Incremental pipelines are harder to debug.
3. Healthcare environments demand traceability.
4. Operational trust depends on measurable movement of data.

Instead of auditing only failures, the system audits **everything**.

---

# Items Requiring Verification or Uncertain

* Regulatory audit retention duration.
* Required lineage depth for compliance audits.
* Whether audit tables require immutability controls.
* Alerting integration requirements.
* Expected operational SLA thresholds.

---

## Next Mini Sprint

MiniSprint 8.2 — Monitoring and Alerting

This sprint converts audit data into **real-time operational intelligence** for pipeline reliability.
