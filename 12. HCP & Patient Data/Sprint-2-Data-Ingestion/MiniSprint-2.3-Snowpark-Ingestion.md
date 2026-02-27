# Snowpark Ingestion

## Overview

This mini sprint implements the **programmatic ingestion framework using Snowpark Python**.
The goal is to move vendor files from local landing or integration locations into Snowflake stages and then load them into Source tables in a controlled, auditable, and repeatable way.

This sprint converts everything designed previously into an **actual ingestion engine**.

Scope of this sprint:

* Snowpark session setup
* Automated file discovery
* Stage upload using Snowpark File API
* Metadata capture
* COPY execution into SOURCE tables
* Incremental ingestion behavior
* Logging and audit integration

This sprint does not perform transformation or curation. It strictly focuses on ingestion.

---

# Objectives

* Build reusable Snowpark ingestion framework.
* Upload partitioned vendor data into Snowflake stages.
* Load staged data into SOURCE schema tables.
* Prevent duplicate file processing.
* Capture ingestion metadata automatically.
* Enable scalable ingestion across multiple vendors.

---

# High-Level Ingestion Flow

Vendor Files
→ Local Landing Directory
→ Snowpark File Upload
→ Snowflake Internal Stage
→ COPY INTO SOURCE Tables
→ Audit Logging

---

# Design Principles Used

## 1. Idempotent ingestion

Running ingestion multiple times must not duplicate data.

Achieved using:

* file checksum
* file audit tracking
* COPY history
* incremental filtering

## 2. Vendor-agnostic framework

Same code should ingest:

* Claims
* Rx
* Patient programs
* Market data

Only configuration changes.

## 3. Metadata-first ingestion

Every file and record must be traceable.

---

# Architecture Components

## Snowpark Session Layer

Responsible for:

* Authentication
* Warehouse usage
* Execution of SQL and file operations

## File Discovery Layer

Responsible for:

* Traversing vendor folders
* Identifying supported formats
* Building ingestion batches

## Stage Upload Layer

Responsible for:

* Uploading files
* Maintaining partition structure

## Load Execution Layer

Responsible for:

* COPY INTO execution
* Data type casting
* Error handling

## Audit Layer

Responsible for:

* Recording ingestion activity
* Tracking processed files

---

# Folder Structure Assumption

Example local landing structure:

```
landing/
 ├── vendorA/
 │   └── claims/
 │       └── year=2026/month=02/day=27/
 │           claims_01.csv
 ├── vendorB/
 │   └── rx/
 │       rx_20260227.parquet
```

Stage structure mirrors this exactly.

Reason:
Maintaining identical structure simplifies debugging and replay.

---

# Snowpark Ingestion Strategy

Two ingestion operations exist.

## Operation 1: Upload files to Stage

Snowpark File API uploads files while preserving partition paths.

## Operation 2: Load Stage → SOURCE

COPY command loads structured tables.

Snowpark orchestrates both.

---

# Snowpark Ingestion Script

Below is a reusable ingestion framework.

```python
from snowflake.snowpark import Session
import os
import hashlib
from datetime import datetime

# ------------------------------------------------
# CONNECTION CONFIG
# ------------------------------------------------

connection_parameters = {
    "account": "ACCOUNT",
    "user": "USER",
    "password": "PASSWORD",
    "role": "DATA_INGEST_ROLE",
    "warehouse": "INGEST_WH",
    "database": "HEALTHCARE_DB",
    "schema": "REFERENCE"
}

session = Session.builder.configs(connection_parameters).create()

# ------------------------------------------------
# CONFIGURATION
# ------------------------------------------------

LOCAL_BASE_PATH = "./landing"
STAGE_NAME = "@REFERENCE.stage_vendorA"

SUPPORTED_FORMATS = [".csv", ".json", ".parquet"]

# ------------------------------------------------
# CHECKSUM FUNCTION
# ------------------------------------------------

def generate_checksum(file_path):
    hash_sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()

# ------------------------------------------------
# FILE DISCOVERY
# ------------------------------------------------

def discover_files(base_path):
    file_list = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_FORMATS):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, base_path)
                file_list.append((full_path, relative_path))

    return file_list

# ------------------------------------------------
# AUDIT CHECK
# ------------------------------------------------

def file_already_processed(checksum):
    query = f"""
        SELECT COUNT(1)
        FROM AUDIT.file_audit
        WHERE file_checksum = '{checksum}'
        AND status = 'processed'
    """

    result = session.sql(query).collect()[0][0]
    return result > 0

# ------------------------------------------------
# UPLOAD FILE
# ------------------------------------------------

def upload_file(local_path, stage_path):
    session.file.put(
        local_path,
        f"{STAGE_NAME}/{stage_path}",
        auto_compress=False,
        overwrite=False
    )

# ------------------------------------------------
# AUDIT INSERT
# ------------------------------------------------

def log_file(stage_path, checksum):
    session.sql(f"""
        INSERT INTO AUDIT.file_audit(
            file_name,
            file_path,
            file_checksum,
            arrival_ts,
            status
        )
        VALUES (
            '{os.path.basename(stage_path)}',
            '{stage_path}',
            '{checksum}',
            CURRENT_TIMESTAMP(),
            'uploaded'
        )
    """).collect()

# ------------------------------------------------
# COPY INTO SOURCE
# ------------------------------------------------

def copy_into_source(feed):
    session.sql(f"""
        COPY INTO SOURCE.{feed}_tbl
        FROM {STAGE_NAME}/{feed}
        FILE_FORMAT = (FORMAT_NAME = 'REFERENCE.ff_csv')
        ON_ERROR = 'CONTINUE'
    """).collect()

# ------------------------------------------------
# MAIN INGESTION
# ------------------------------------------------

def run_ingestion():

    files = discover_files(LOCAL_BASE_PATH)

    for local_path, relative_path in files:

        checksum = generate_checksum(local_path)

        if file_already_processed(checksum):
            print("Skipping already processed:", relative_path)
            continue

        upload_file(local_path, relative_path)
        log_file(relative_path, checksum)

    copy_into_source("claims")

run_ingestion()
```

---

# Thought Process Behind Design

## Why Snowpark instead of manual COPY

Snowpark allows orchestration logic in Python while still executing SQL inside Snowflake compute.

Benefits:

* Centralized ingestion logic
* Dynamic vendor onboarding
* Easier automation
* Reusable ingestion engine

## Why checksum validation

Vendors frequently resend files.

Checksum ensures:

* No duplicate ingestion
* Reliable delta processing
* Audit traceability

## Why recursive discovery

Vendors may send historical backfills.

Recursive scanning automatically ingests:

* new partitions
* late arriving data

## Why COPY remains SQL

Snowflake COPY INTO is highly optimized internally.

Snowpark should orchestrate, not replace optimized warehouse operations.

---

# Error Handling Strategy

Handled scenarios:

* Duplicate file upload
* Partial COPY failure
* Schema mismatch
* Bad records

ON_ERROR = CONTINUE allows ingestion to proceed while logging rejected rows.

Rejected rows should later move to quarantine analysis.

---

# Performance Considerations

Recommended practices:

* Upload files between 50 MB and 250 MB.
* Parallelize ingestion by vendor.
* Use dedicated ingestion warehouse.
* Batch COPY operations per partition instead of entire stage scan.

---

# Monitoring Metrics

Track:

* files_ingested_per_run
* ingestion_duration
* rows_loaded
* rejected_rows
* duplicate_files_detected

Expose via AUDIT dashboards.

---

# Acceptance Criteria

* Snowpark session successfully connects.
* Files uploaded preserving partition structure.
* Duplicate files skipped automatically.
* COPY INTO loads SOURCE tables correctly.
* AUDIT.file_audit populated.
* Re-running ingestion produces no duplicates.

---

# Risks and Mitigation

Risk: Vendor sends malformed files
Mitigation: schema validation and quarantine logic.

Risk: Massive backfill overloads warehouse
Mitigation: partition-based ingestion scheduling.

Risk: Missing metadata
Mitigation: mandatory audit logging before COPY.

---

# Items Requiring Verification or Uncertain

* Exact vendor file sizes and daily volume.
* Whether ingestion must support near real-time feeds.
* Regulatory requirement for staging retention duration.
* Whether multi-threaded ingestion is required immediately.

---

# Reasoning Summary

Design decisions prioritized:

* repeatability
* auditability
* vendor scalability
* incremental processing safety
* operational simplicity

The ingestion engine is intentionally modular so future vendors require configuration rather than new pipelines.

---

## Next Logical Step

Next sprint normally becomes:

MiniSprint 3.1
Source Layer Table Engineering

If you want, I can also generate the **production-grade version** large pharma companies actually run, including:

* configuration-driven ingestion
* multi-vendor YAML control table
* parallel Snowpark ingestion
* automatic schema evolution handling.
