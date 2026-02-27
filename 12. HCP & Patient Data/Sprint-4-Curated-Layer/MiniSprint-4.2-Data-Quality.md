# MiniSprint 4.2: Data Quality

(Curated Layer Quality Enforcement)

## Overview

This mini sprint introduces **data quality enforcement** after standardization and before data becomes trusted enterprise data.

At this point:

* Data structure is standardized.
* Column names are aligned.
* Types are normalized.

Now the platform must answer a critical question:

**Can the business trust this data?**

Data Quality ensures curated datasets are:

* complete
* consistent
* valid
* explainable
* auditable

This sprint establishes the **quality control framework** used before dimensional modeling.

---

## Objectives

* Define enterprise healthcare data quality rules.
* Detect invalid or suspicious records.
* Measure dataset reliability.
* Prevent bad data propagation.
* Create automated quality scoring.
* Build reusable validation framework.

---

## Position in Data Pipeline

```text
SOURCE
   ↓
Standardization
   ↓
Data Quality Validation
   ↓
CURATED (Trusted Data)
```

Only validated records move forward.

---

## Core Data Quality Philosophy

Pharma platforms avoid deleting data blindly.

Instead:

```text
Detect
Classify
Score
Quarantine
Monitor
```

Bad data becomes observable rather than invisible.

---

# Data Quality Dimensions

Five major quality dimensions are enforced.

---

## 1. Completeness Validation

Ensures required healthcare fields exist.

Critical pharma fields:

* claim_id
* event_date
* hcp_id
* drug_code
* quantity

Validation example:

```sql
SELECT *
FROM CURATED.claims_tbl
WHERE claim_id IS NULL
   OR event_date IS NULL
   OR drug_code IS NULL;
```

Outcome:
Records flagged as incomplete.

---

### Thought Process

Missing identifiers break analytics joins and attribution models.

---

## 2. Validity Checks

Ensures values fall within acceptable ranges.

Examples:

Quantity validation:

```sql
SELECT *
FROM CURATED.claims_tbl
WHERE quantity <= 0;
```

Date validation:

```sql
SELECT *
FROM CURATED.claims_tbl
WHERE event_date > CURRENT_DATE;
```

Healthcare Example:
Future prescription dates indicate vendor errors.

---

## 3. Consistency Validation

Ensures internal agreement across fields.

Example rule:

```text
amount_local = quantity × unit_price
```

Validation:

```sql
SELECT *
FROM CURATED.sales_tbl
WHERE ABS(amount_local - (quantity * unit_price)) > 0.01;
```

---

### Pharma Importance

Revenue analytics depends heavily on consistent financial metrics.

---

## 4. Uniqueness Validation

Detect duplicate healthcare transactions.

Example:

```sql
SELECT claim_id, COUNT(*)
FROM CURATED.claims_tbl
GROUP BY claim_id
HAVING COUNT(*) > 1;
```

Duplicates originate from:

* vendor resend
* late corrections
* ingestion replay

Duplicates are flagged, not removed immediately.

---

## 5. Referential Integrity Validation

Checks whether records reference valid master entities.

Example:

```sql
SELECT c.*
FROM CURATED.claims_tbl c
LEFT JOIN MASTER.drug_dim d
ON c.drug_code = d.drug_code
WHERE d.drug_code IS NULL;
```

Purpose:
Prevent orphan analytical records.

---

# Data Quality Rule Framework

Centralized rule registry recommended.

```sql
CREATE TABLE REFERENCE.data_quality_rules (
    rule_id STRING,
    rule_name STRING,
    table_name STRING,
    rule_sql STRING,
    severity STRING,
    active_flag BOOLEAN
);
```

Benefits:

* rules configurable
* reusable across datasets
* governance friendly

---

# Quality Scoring Model

Each dataset receives a quality score.

Example scoring:

| Dimension             | Weight |
| --------------------- | ------ |
| Completeness          | 30%    |
| Validity              | 25%    |
| Consistency           | 20%    |
| Uniqueness            | 15%    |
| Referential Integrity | 10%    |

Score calculation example:

```text
Quality Score = Passed Checks / Total Checks
```

---

## Example Result

```text
Claims Dataset Quality Score: 96.4%
Status: APPROVED
```

---

# Quarantine Strategy

Invalid records move into quarantine tables.

```sql
CREATE TABLE CURATED.claims_quarantine LIKE CURATED.claims_tbl;
```

Process:

* valid rows → curated trusted table
* invalid rows → quarantine

Reason:
Healthcare audits require traceability.

---

# Snowpark Data Quality Execution

Snowpark orchestrates rule execution.

Example:

```python
dq_failed = df.filter(
    (col("claim_id").is_null()) |
    (col("quantity") <= 0)
)

dq_passed = df.subtract(dq_failed)
```

Write results:

```python
dq_failed.write.mode("append").save_as_table(
    "CURATED.claims_quarantine"
)
```

---

# Data Quality Audit Table

```sql
CREATE TABLE AUDIT.data_quality_results (
    run_id STRING,
    table_name STRING,
    rule_name STRING,
    failed_records NUMBER,
    quality_status STRING,
    execution_ts TIMESTAMP_TZ
);
```

Enables:

* monitoring
* trend tracking
* vendor performance measurement

---

# Vendor Quality Monitoring

Over time the platform builds:

Vendor Reliability Index.

Example metrics:

* failure rate
* schema drift frequency
* duplicate percentage
* delivery delays

Used for vendor governance.

---

# Operational Decision Logic

| Quality Result | Action                      |
| -------------- | --------------------------- |
| PASS           | Continue pipeline           |
| WARNING        | Load with alert             |
| FAIL           | Block downstream processing |

---

# Performance Strategy

Quality checks designed to avoid heavy scans.

Techniques used:

* validate only new partitions
* aggregate validation
* push execution into Snowflake engine
* avoid Python row iteration

---

# Acceptance Criteria

* Data quality rules defined.
* Automated validation executed.
* Quality score generated.
* Invalid records quarantined.
* Audit results stored.
* Pipeline gating enabled.
* Monitoring visibility available.

---

# Explanation of Thought Process

The design prioritizes controlled trust.

Key reasoning:

1. Pharma analytics decisions influence revenue and compliance.
2. Vendors cannot guarantee perfect data.
3. Rejecting entire datasets slows operations.
4. Observability is more valuable than strict rejection.

Therefore:
Data quality becomes a measurable system rather than manual inspection.

The curated layer evolves into a **trusted analytical foundation**.

---

# Items Requiring Verification or Uncertain

* Business-approved thresholds for failure rates.
* Regulatory expectations for rejected healthcare records.
* Whether automated correction rules should exist.
* Acceptable duplicate tolerance.
* SLA definitions tied to quality score.

---

## Next Mini Sprint

MiniSprint 4.3
Deduplication and Record Survivorship

This is where pharma-grade pipelines become significantly more advanced because we begin handling:

* late arriving claims
* vendor corrections
* historical restatements
* survivorship logic across sources.
