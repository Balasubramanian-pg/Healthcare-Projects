# MiniSprint 4.3: Deduplication

(Curated Layer Record Survivorship)

## Overview

This mini sprint introduces **deduplication and record survivorship**, one of the most critical capabilities in healthcare and pharma data platforms.

After standardization and data quality validation, multiple records may still represent the **same real-world healthcare event**.

Common causes:

* vendors resend corrected files
* late arriving claims
* overlapping vendor coverage
* ingestion replay
* upstream system corrections

The goal of this sprint is to ensure that **only the correct version of a record survives for analytics**, while historical traceability remains intact.

---

## Objectives

* Detect duplicate healthcare records.
* Define enterprise survivorship logic.
* Handle late arriving and corrected data.
* Preserve auditability.
* Prevent metric inflation.
* Prepare clean datasets for dimensional modeling.

---

## Pipeline Position

```text id="6pt3ig"
SOURCE
   ↓
Standardization
   ↓
Data Quality
   ↓
Deduplication
   ↓
CURATED TRUSTED DATA
```

Deduplication produces the **final curated dataset**.

---

# Why Deduplication Is Hard in Pharma

Unlike transactional systems, healthcare data rarely has perfect primary keys.

Example scenario:

| claim_id | vendor   | load_time | amount |
| -------- | -------- | --------- | ------ |
| 1001     | Vendor A | Day 1     | 120    |
| 1001     | Vendor A | Day 3     | 125    |

Second record is a correction.

Another example:

| claim_id | vendor   |
| -------- | -------- |
| 1001     | Vendor A |
| 1001     | Vendor B |

Two vendors reporting the same event.

Simple duplicate removal would produce incorrect results.

---

# Deduplication Strategy

The platform applies **three-stage duplicate handling**.

```text id="e8yj9a"
Duplicate Detection
        ↓
Record Ranking
        ↓
Survivorship Selection
```

---

# 1. Duplicate Detection

Duplicates identified using **business keys**.

Typical healthcare composite key:

```text id="x8rd2b"
hcp_id
patient_id
drug_code
event_date
```

Example detection:

```sql id="q2kx18"
SELECT
    claim_id,
    COUNT(*)
FROM CURATED.claims_tbl
GROUP BY claim_id
HAVING COUNT(*) > 1;
```

If vendor keys unreliable, composite keys used.

---

## Row Hash Detection

Previously generated `row_hash` assists detection.

```sql id="45u3k5"
SELECT row_hash, COUNT(*)
FROM CURATED.claims_tbl
GROUP BY row_hash
HAVING COUNT(*) > 1;
```

Identifies identical records efficiently.

---

# 2. Record Ranking Logic

Duplicates must be ranked before removal.

Ranking criteria example:

Priority order:

1. Latest vendor correction
2. Highest data completeness
3. Trusted vendor priority
4. Latest ingestion timestamp

Implementation:

```sql id="gobpmh"
SELECT *,
ROW_NUMBER() OVER(
    PARTITION BY claim_id
    ORDER BY file_loaded_ts DESC
) AS record_rank
FROM CURATED.claims_tbl;
```

Rank = 1 becomes survivor.

---

## Vendor Trust Hierarchy Example

```text id="99gv8x"
Internal Data Provider → Rank 1
Primary Vendor → Rank 2
Secondary Aggregator → Rank 3
```

Used when multiple vendors overlap.

---

# 3. Survivorship Selection

Final curated dataset keeps only surviving records.

```sql id="76nh2p"
CREATE OR REPLACE TABLE CURATED.claims_final AS
SELECT *
FROM ranked_claims
WHERE record_rank = 1;
```

Duplicates preserved separately.

---

# Duplicate Archive Strategy

Duplicates are not deleted.

Stored in:

```sql id="l32ytf"
CURATED.claims_duplicate_archive
```

Purpose:

* regulatory audit
* vendor dispute analysis
* historical comparison

---

# Late Arriving Data Handling

Healthcare pipelines must support delayed submissions.

Scenario:

```text id="1z40qg"
January claim arrives in March
```

Solution:
Deduplication runs incrementally across affected partitions.

Process:

* reload impacted date window
* recompute rankings
* update survivor records

---

# Change Detection Logic

Detect vendor corrections.

Example:

```sql id="2nvxjs"
WHERE existing.row_hash <> incoming.row_hash
```

Meaning:
Same business key but updated values.

Handled as:

* old record expired
* new record survives

---

# Snowpark Deduplication Example

```python id="h0fy51"
from snowflake.snowpark.window import Window
from snowflake.snowpark.functions import row_number, col

window_spec = Window.partition_by("claim_id")\
                    .order_by(col("file_loaded_ts").desc())

dedup_df = df.with_column(
    "record_rank",
    row_number().over(window_spec)
)

final_df = dedup_df.filter(col("record_rank") == 1)
```

---

# Incremental Deduplication Strategy

Avoid full table recomputation.

Process only:

* new ingestion batch
* impacted business keys

Technique:
Left anti join against existing curated survivors.

Benefits:

* faster execution
* scalable platform

---

# Audit Tracking

Track deduplication outcomes.

```sql id="74fp07"
CREATE TABLE AUDIT.deduplication_log (
    run_id STRING,
    table_name STRING,
    duplicates_found NUMBER,
    survivors_created NUMBER,
    execution_ts TIMESTAMP_TZ
);
```

---

# Pharma-Specific Deduplication Cases

## Claim Reversals

Negative quantity replaces earlier claim.

## Prescription Adjustments

Updated dosage values.

## Vendor Overlap

Multiple commercial data providers.

## Patient Program Updates

Enrollment corrections.

Each requires survivorship logic instead of deletion.

---

# Performance Considerations

Design choices:

* Partition deduplication by event_date.
* Avoid global window scans.
* Use Snowflake compute pushdown.
* Maintain clustering on event_date if tables grow large.

---

# Acceptance Criteria

* Duplicate records detectable.
* Survivorship ranking implemented.
* Correct record retained.
* Duplicate archive maintained.
* Late arriving updates handled.
* Incremental processing operational.
* Audit logs generated.

---

# Explanation of Thought Process

Deduplication was designed around healthcare realities:

1. Data corrections are normal.
2. Multiple vendors overlap intentionally.
3. Historical traceability is mandatory.
4. Analytics must see one version of truth.

Therefore:
The system selects a survivor rather than removing duplicates blindly.

This converts curated data into **analytics-ready trusted datasets**.

---

# Items Requiring Verification or Uncertain

* Official enterprise survivorship rules.
* Vendor trust ranking agreement.
* Correction frequency expectations.
* Window size for late arriving data.
* Regulatory retention requirements for duplicate archives.

---

## Next Mini Sprint

MiniSprint 5.1
Unified Dataset Creation (Curated Consolidation)

This is where separate regional or vendor datasets merge into a **single enterprise healthcare dataset**, enabling dimensional modeling and analytics.
