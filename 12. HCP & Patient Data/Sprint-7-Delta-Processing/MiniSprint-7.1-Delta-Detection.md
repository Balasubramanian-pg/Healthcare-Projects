# MiniSprint 7.1 — Delta Detection

## Overview

This mini sprint introduces **Delta Detection**, the mechanism that allows the pharma data platform to process only **new or changed data** instead of reprocessing the entire historical dataset.

Up to this point:

* Full historical data was ingested.
* Curated datasets were standardized and deduplicated.
* Fact tables and dashboards were built.

From this sprint onward, the platform transitions into **continuous production operation**.

Delta detection ensures:

* faster pipelines
* lower Snowflake compute cost
* controlled late-arriving data handling
* reliable incremental refresh of analytics

---

## Objective

* Detect newly arrived files.
* Detect changed records inside existing business keys.
* Prevent reprocessing historical data.
* Support vendor corrections.
* Enable incremental Snowpark pipelines.
* Maintain auditability.

---

## Pipeline Position

```text
Vendor Files
      ↓
Stage Landing
      ↓
Delta Detection
      ↓
Incremental Processing
      ↓
Curated / Facts Update
```

Delta detection becomes the **entry control gate** for production ETL.

---

# Why Delta Detection Is Critical in Pharma

Healthcare data rarely arrives once.

Typical realities:

* vendors resend corrected claims
* delayed prescription submissions
* periodic backfills
* regulatory restatements
* partial file reloads

Without delta detection:

* metrics duplicate
* pipelines slow dramatically
* warehouse costs increase
* dashboards become unreliable

---

# Types of Delta Changes

Delta detection handles three scenarios.

## 1. New Data

Completely new business events.

Example:

```text
New prescription submitted today
```

Action:
Insert record.

---

## 2. Updated Records

Same business key but modified values.

Example:

```text
claim_id exists
amount changed
status updated
```

Action:
Update or supersede record.

---

## 3. Late Arriving Data

Historical event arrives after initial load.

Example:

```text
January claim received in March
```

Action:
Reprocess affected partitions only.

---

# Delta Detection Strategy

The platform uses **multi-layer detection**.

```text
File Level Detection
        +
Record Hash Detection
        +
Business Key Comparison
```

This prevents false positives.

---

# Layer 1: File-Level Delta Detection

Detect whether a file was already processed.

Audit table:

```sql
CREATE TABLE AUDIT.file_ingestion_log (
    file_name STRING,
    file_checksum STRING,
    arrival_ts TIMESTAMP,
    processed_flag BOOLEAN
);
```

Detection query:

```sql
SELECT *
FROM STAGE_FILES s
LEFT JOIN AUDIT.file_ingestion_log a
ON s.file_name = a.file_name
WHERE a.file_name IS NULL;
```

Only unseen files proceed.

---

## Thought Process

Files are the cheapest checkpoint.

If file already processed:

* skip immediately
* avoid compute usage

---

# Layer 2: Metadata-Based Detection

Snowflake stages expose metadata.

Useful fields:

* METADATA$FILENAME
* METADATA$FILE_LAST_MODIFIED
* METADATA$ROW_NUMBER

Example:

```sql
SELECT
  METADATA$FILENAME,
  METADATA$FILE_LAST_MODIFIED
FROM @SOURCE_STAGE;
```

If timestamp newer than audit record → process.

---

# Layer 3: Record Hash Detection

Even when files repeat, records may change.

Create deterministic hash.

Example:

```sql
SELECT
SHA2(
    CONCAT(
        claim_id,
        patient_id,
        drug_code,
        amount
    ),256
) AS row_hash
FROM SOURCE.claims;
```

Comparison logic:

```sql
WHERE incoming.row_hash <> existing.row_hash
```

Meaning:
Same event but updated values.

---

# Snowpark Delta Detection Example

```python
from snowflake.snowpark.functions import sha2, concat, col

df = df.with_column(
    "row_hash",
    sha2(
        concat(
            col("claim_id"),
            col("patient_id"),
            col("amount")
        ),
        256
    )
)
```

---

# Business Key Matching

Healthcare systems often lack perfect IDs.

Composite key example:

```text
hcp_id
patient_id
drug_code
event_date
```

Delta logic compares:

* business key
* row hash

Decision matrix:

| Case                 | Action |
| -------------------- | ------ |
| New key              | Insert |
| Same key + new hash  | Update |
| Same key + same hash | Ignore |

---

# Incremental Load Pattern

Instead of full reload:

```text
Incoming Batch
        ↓
Left Anti Join
        ↓
Process Only New Records
```

Example:

```sql
SELECT i.*
FROM incoming i
LEFT ANTI JOIN curated c
ON i.business_key = c.business_key;
```

---

# Handling Vendor Corrections

Two supported models.

## Type A: Replace Record

Old record updated.

## Type B: Versioned Record

Maintain history.

Example:

```sql
is_current = TRUE
valid_from
valid_to
```

Pharma audits often require versioned records.

---

# Delta Window Strategy

Process only impacted time windows.

Example:

```text
Last 7 days rolling window
```

Reason:
Late healthcare data typically arrives within bounded delay.

---

# Audit Tracking

Every delta run logged.

```sql
CREATE TABLE AUDIT.delta_run_log (
    run_id STRING,
    files_detected NUMBER,
    rows_inserted NUMBER,
    rows_updated NUMBER,
    execution_ts TIMESTAMP
);
```

---

# Performance Considerations

Key decisions made:

* Avoid full table scans.
* Compare hashes instead of columns.
* Partition processing by event_date.
* Maintain ingestion audit tables.
* Push computation into Snowflake engine.

---

# Validation Checks

After delta execution:

```sql
SELECT COUNT(*)
FROM FACT.sales_fact
WHERE load_date = CURRENT_DATE;
```

Verify:

* record growth expected
* no duplicate business keys

Duplicate check:

```sql
SELECT business_key, COUNT(*)
FROM FACT.sales_fact
GROUP BY business_key
HAVING COUNT(*) > 1;
```

---

# Acceptance Criteria

* Previously processed files skipped.
* Only new or changed records processed.
* Late arriving data supported.
* Hash comparison implemented.
* Audit logs updated.
* Incremental runtime significantly lower than full load.

---

# Explanation of Design Thinking

Delta detection was designed around production healthcare realities:

1. Vendors resend data frequently.
2. Corrections are normal events.
3. Historical reloads must be avoided.
4. Regulatory traceability must remain intact.

Therefore detection occurs progressively:

* first at file level
* then metadata level
* finally record level

This layered approach minimizes compute while maximizing correctness.

---

# Items Requiring Verification or Uncertain

* Maximum expected late-arrival window from vendors.
* Whether corrections overwrite or version records.
* Vendor guarantees around file uniqueness.
* Hash column selection approval.
* Regulatory retention requirements for historical versions.

---

## Next Mini Sprint

MiniSprint 7.2 — Incremental Processing

This sprint converts the full ETL pipeline into a **true production incremental Snowpark pipeline** that processes only detected delta records.
