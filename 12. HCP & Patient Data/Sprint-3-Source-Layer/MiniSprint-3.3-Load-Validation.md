# Load Validation

## Overview

This mini sprint establishes the **data load validation framework** for the pharma data platform.
After files are ingested into Source tables, validation ensures that:

* Data was loaded completely
* No silent corruption occurred
* Vendor deliveries match expectations
* Downstream curated processing receives trusted input

In real pharma environments, ingestion failures are rarely obvious. The biggest risk is **silent bad data**, not pipeline crashes.
This sprint introduces systematic verification before data progresses further.

---

# Objectives

* Validate successful Stage → Source data loads.
* Detect missing, duplicate, or partial vendor deliveries.
* Verify schema integrity and data quality baselines.
* Reconcile vendor expectations with warehouse results.
* Establish automated validation rules reusable across vendors.

---

# Validation Philosophy

The validation model follows three layers.

```
File Validation
        ↓
Load Validation
        ↓
Data Quality Validation
```

Each layer answers a different question:

| Layer           | Question Answered                  |
| --------------- | ---------------------------------- |
| File Validation | Did we receive the correct files?  |
| Load Validation | Did Snowflake load them correctly? |
| Data Validation | Does the data make business sense? |

---

# Validation Architecture

```
Vendor Files
      ↓
Internal Stage
      ↓
COPY INTO SOURCE
      ↓
Load Validation Engine
      ↓
AUDIT Tables + Alerts
```

Validation runs immediately after ingestion.

---

# 1. File-Level Validation

## Purpose

Confirm expected files arrived and were processed exactly once.

### Checks Performed

* File exists in stage
* File recorded in `AUDIT.file_audit`
* Checksum verified
* File not processed previously
* File size within expected range

### Validation Query Example

```sql
SELECT
    file_name,
    status,
    file_checksum
FROM AUDIT.file_audit
WHERE arrival_ts >= DATEADD(hour,-24,CURRENT_TIMESTAMP());
```

### Expected Result

All files must show:

```
status = processed
```

---

# 2. COPY Load Validation

## Purpose

Ensure COPY INTO correctly loaded records into SOURCE tables.

Snowflake provides load metadata automatically.

### COPY History Validation

```sql
SELECT *
FROM TABLE(
    INFORMATION_SCHEMA.COPY_HISTORY(
        TABLE_NAME=>'CLAIMS_SRC_TBL',
        START_TIME=>DATEADD(hour,-24,CURRENT_TIMESTAMP())
    )
);
```

Validation Checks:

* files_loaded > 0
* error_count acceptable
* load duration normal

Snowflake documents COPY history tracking through metadata views.
[https://docs.snowflake.com/en/sql-reference/functions/copy_history](https://docs.snowflake.com/en/sql-reference/functions/copy_history)

---

## Row Count Reconciliation

Compare vendor expectation vs loaded rows.

```sql
SELECT
    a.file_name,
    a.rows_expected,
    b.loaded_rows
FROM AUDIT.file_audit a
JOIN (
    SELECT file_name,
           COUNT(*) loaded_rows
    FROM SOURCE.claims_src_tbl
    GROUP BY file_name
) b
ON a.file_name = b.file_name;
```

### Pass Condition

```
rows_expected = loaded_rows
```

If vendor does not provide counts, establish historical baseline validation.

---

# 3. Schema Validation

## Purpose

Detect vendor schema drift early.

### Checks

* Required columns exist
* Data types match expectation
* Unexpected columns logged

Example:

```sql
DESC TABLE SOURCE.claims_src_tbl;
```

Automated comparison against schema registry recommended.

Typical pharma issue detected here:

* vendor adds column mid-cycle
* column order changes
* datatype silently shifts

---

# 4. Null and Mandatory Field Validation

Healthcare datasets contain required business identifiers.

Critical fields example:

* claim_id
* hcp_identifier
* drug_code
* claim_date

Validation Query:

```sql
SELECT COUNT(*) invalid_rows
FROM SOURCE.claims_src_tbl
WHERE claim_date IS NULL
   OR drug_code IS NULL;
```

Threshold Example:

* Acceptable NULL rate < 0.5%

---

# 5. Duplicate Detection Validation

Duplicates commonly occur when vendors resend files.

Validation using row hash:

```sql
SELECT row_hash, COUNT(*)
FROM SOURCE.claims_src_tbl
GROUP BY row_hash
HAVING COUNT(*) > 1;
```

Outcome:

* duplicates logged
* not blocked at source layer
* resolved during curated processing

Reason:
Source layer preserves vendor truth.

---

# 6. Volume Anomaly Detection

Detect abnormal data delivery patterns.

Example checks:

* sudden drop in claims volume
* unexpected spike
* missing geography

Example:

```sql
SELECT
    claim_date,
    COUNT(*) records
FROM SOURCE.claims_src_tbl
GROUP BY claim_date
ORDER BY claim_date;
```

Compare against historical averages.

Typical pharma alert:

* claims drop > 30% day-over-day.

---

# 7. Data Type Validation

Ensure numeric and date parsing succeeded.

Example:

```sql
SELECT *
FROM SOURCE.claims_src_tbl
WHERE TRY_TO_DATE(claim_date) IS NULL;
```

Reason:
Bad parsing silently creates incorrect analytics later.

---

# 8. Validation Status Framework

Create validation outcome table.

```sql
CREATE TABLE AUDIT.load_validation (
    validation_id BIGINT AUTOINCREMENT,
    ingest_job_id VARCHAR,
    validation_type VARCHAR,
    validation_result VARCHAR,
    failed_records NUMBER,
    validation_ts TIMESTAMP_TZ
);
```

Possible Results:

* PASSED
* WARNING
* FAILED

---

# 9. Automated Validation Flow

Execution order:

1. File audit validation
2. COPY history validation
3. Row reconciliation
4. Mandatory field validation
5. Duplicate detection
6. Volume anomaly check
7. Write results to audit table
8. Trigger alerts if failure

---

# 10. Alerting Strategy

Trigger alerts when:

* Missing vendor file
* Load failure
* Record mismatch
* High NULL percentage
* Volume anomaly detected

Alert Channels:

* Email
* Slack
* Incident ticket
* Monitoring dashboard

---

# 11. Operational Decision Rules

| Result  | Action            |
| ------- | ----------------- |
| PASS    | Continue pipeline |
| WARNING | Continue + notify |
| FAIL    | Stop curated load |

---

# 12. Performance Considerations

Validation must not slow ingestion.

Design choices:

* Aggregate validations instead of row scans where possible.
* Validate only newly loaded partitions.
* Use metadata tables instead of full scans.

---

# 13. Acceptance Criteria

* Validation queries execute automatically after COPY.
* Audit table records validation outcomes.
* Row counts reconcile successfully.
* Duplicate detection operational.
* Schema drift detectable.
* Alerts generated on failure scenarios.
* Pipeline blocks downstream processing on critical failure.

---

# Explanation of Thought Process

While designing validation, the following risks were prioritized:

1. Pharma datasets are externally controlled.
2. Vendors frequently resend corrected data.
3. Silent failures cause incorrect commercial decisions.
4. Full blocking pipelines increase operational friction.

Therefore the system:

* validates aggressively,
* fails selectively,
* preserves raw truth,
* protects analytics layers.

Validation acts as a **quality gate between ingestion and transformation**.

---

# Items Requiring Verification or Uncertain

* Whether vendors provide official row counts or manifests.
* Acceptable failure thresholds defined by business stakeholders.
* Required regulatory audit retention duration.
* Whether anomaly detection should be statistical or rule-based initially.
* Frequency of late-arriving corrections from vendors.

---

## Next Mini Sprint

MiniSprint 4.1
Data Standardization (Source → Curated)

If you want, I can also build the **enterprise pharma validation framework** next, including:

* automated data observability model
* freshness scoring
* vendor reliability index
* SLA monitoring dashboards used in large pharma GCC environments.
