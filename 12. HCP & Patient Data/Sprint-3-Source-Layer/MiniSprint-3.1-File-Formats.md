# MiniSprint 3.1: File Formats

## Overview

This mini sprint establishes **standardized file format definitions** used to read vendor healthcare data reliably inside Snowflake.
File formats act as the translation layer between raw vendor files and structured warehouse tables.

In pharma data platforms, inconsistent file structures are one of the biggest ingestion risks. Vendors frequently differ in delimiters, encoding, null handling, and schema evolution behavior. This sprint removes that variability by defining controlled parsing rules.

This sprint prepares the platform so that **all ingestion pipelines behave predictably regardless of vendor source**.

---

# Objectives

* Standardize parsing rules for all supported vendor file types.
* Centralize file format objects in a shared schema.
* Prevent ingestion failures caused by formatting inconsistencies.
* Support schema evolution safely.
* Enable reusable COPY and Snowpark ingestion logic.

---

# Supported Vendor File Types

The platform supports three primary formats commonly used in healthcare ecosystems.

## CSV

Common for:

* Claims vendors
* Market access datasets
* Patient program exports
* Legacy healthcare systems

Characteristics:

* Human readable
* High variability across vendors
* Most ingestion errors originate here

---

## JSON

Common for:

* API exports
* Patient engagement platforms
* Digital health applications

Characteristics:

* Nested structure
* Semi-structured schema
* Requires field extraction logic

---

## Parquet

Common for:

* Large prescription datasets
* Data aggregators
* Modern analytics vendors

Characteristics:

* Columnar storage
* Highly compressed
* Best performance for analytics ingestion

---

# Design Principles Used

## Centralized Format Governance

All formats live inside:

```
REFERENCE schema
```

Reason:

* Prevent duplicate definitions
* Easier governance
* One update propagates everywhere

---

## Vendor Independence

COPY commands reference format objects instead of inline definitions.

Bad pattern:

```
COPY INTO table FILE_FORMAT=(TYPE=CSV ...)
```

Correct pattern:

```
FORMAT_NAME = REFERENCE.ff_csv_claims
```

This allows platform-wide updates without rewriting pipelines.

---

## Fail Soft, Audit Hard

Healthcare vendors occasionally send malformed rows.

Design choice:

* Continue ingestion
* Capture rejected records
* Audit failures instead of stopping pipelines

---

# File Format Architecture

```
Vendor File
      ↓
File Format Object
      ↓
Snowflake Parser
      ↓
Stage Query
      ↓
COPY INTO SOURCE
```

File format objects define how Snowflake interprets bytes in files.

---

# CSV File Format Strategy

CSV formats vary widely across vendors.
Instead of one global CSV format, define **domain-specific CSV formats**.

### Claims CSV Format

```sql
CREATE OR REPLACE FILE FORMAT REFERENCE.ff_csv_claims
TYPE = CSV
FIELD_DELIMITER = ','
SKIP_HEADER = 1
TRIM_SPACE = TRUE
EMPTY_FIELD_AS_NULL = TRUE
NULL_IF = ('NULL','null','')
ENCODING = 'UTF8'
ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE;
```

### Thought Process

* Skip header because vendors include column names.
* Trim spaces because healthcare exports often pad values.
* Treat empty values as NULL to avoid casting failures.
* Disable strict column mismatch because vendors sometimes append optional fields.

---

### Market Sales CSV Format

Some vendors use pipe delimiters.

```sql
CREATE OR REPLACE FILE FORMAT REFERENCE.ff_csv_sales
TYPE = CSV
FIELD_DELIMITER = '|'
SKIP_HEADER = 1
TRIM_SPACE = TRUE;
```

Reason:
Different delimiter avoids conflicts with commas inside addresses or notes.

---

# JSON File Format Strategy

Healthcare APIs often send nested JSON.

```sql
CREATE OR REPLACE FILE FORMAT REFERENCE.ff_json_standard
TYPE = JSON
STRIP_NULL_VALUES = TRUE
IGNORE_UTF8_ERRORS = TRUE;
```

### Thought Process

* Strip null fields to reduce storage noise.
* Ignore UTF8 errors because API payloads occasionally contain invalid characters.

JSON data loads into VARIANT columns first and is flattened later during curation.

---

# Parquet File Format Strategy

Parquet already contains schema metadata.

```sql
CREATE OR REPLACE FILE FORMAT REFERENCE.ff_parquet_standard
TYPE = PARQUET;
```

### Thought Process

Parquet parsing should remain minimal because:

* Schema already defined
* Compression optimized
* Snowflake reads column metadata automatically

Avoid over-configuration.

---

# Stage Validation Queries

Before loading into tables, validate files directly from stages.

Example CSV validation:

```sql
SELECT *
FROM @REFERENCE.stage_vendorA
(FILE_FORMAT => 'REFERENCE.ff_csv_claims')
LIMIT 10;
```

Example JSON validation:

```sql
SELECT $1:patient_id,
       $1:claim_amount
FROM @REFERENCE.stage_vendorB
(FILE_FORMAT => 'REFERENCE.ff_json_standard');
```

Reason:
Early validation prevents downstream failures.

---

# Schema Evolution Handling

Vendor schemas change frequently.

Strategy adopted:

* Allow additional columns during ingestion.
* Load raw data first.
* Handle schema alignment in curated layer.

Avoid strict parsing at ingestion stage.

---

# Error Handling Strategy

COPY configuration:

```sql
ON_ERROR = CONTINUE
```

Rejected rows captured using:

```
VALIDATION_MODE
```

Example:

```sql
COPY INTO SOURCE.claims_tbl
FROM @REFERENCE.stage_vendorA
FILE_FORMAT=(FORMAT_NAME='REFERENCE.ff_csv_claims')
VALIDATION_MODE='RETURN_ERRORS';
```

Purpose:
Detect issues before production loads.

---

# Governance Rules

Every file format must include:

* Owner
* Vendor mapping
* Supported feeds
* Last validation date
* Change history

Maintain documentation inside repository.

---

# Performance Considerations

Key observations used during design:

* CSV parsing consumes more compute than Parquet.
* JSON ingestion slower due to semi-structured parsing.
* Parquet preferred for large healthcare datasets.

Recommendation:
Encourage vendors to migrate toward Parquet when possible.

---

# Acceptance Criteria

* File format objects created in REFERENCE schema.
* CSV, JSON, and Parquet formats validated with sample files.
* Stage queries successfully preview vendor data.
* COPY INTO works without schema parsing failures.
* Documentation stored alongside SQL definitions.
* Reusable format names adopted across ingestion pipelines.

---

# Risks and Mitigation

Risk: Vendor encoding mismatch
Mitigation: UTF8 enforcement and validation testing.

Risk: Column order changes
Mitigation: schema alignment deferred to curated layer.

Risk: Nested JSON complexity
Mitigation: VARIANT ingestion followed by controlled flattening.

---

# Items Requiring Verification or Uncertain

* Exact delimiter standards across all vendors.
* Whether vendors include quoted multiline fields.
* Compression formats vendors will use in production.
* Frequency of schema evolution events.
* Requirement for strict schema enforcement at ingestion stage.

---

# Explanation of Thought Process

The design prioritizes stability over strict validation.

Key reasoning:

1. Vendor variability is unavoidable in pharma ecosystems.
2. Ingestion should almost never fail due to formatting issues.
3. Strict validation belongs in curated processing, not ingestion.
4. Centralized file formats reduce operational complexity.
5. Early stage preview queries dramatically reduce debugging time.

The file format layer therefore acts as a **controlled tolerance boundary** between unpredictable vendor data and structured analytics models.

---

## Next Mini Sprint

MiniSprint 3.2
Source Layer Table Design

If you want, I can also produce the **enterprise pharma version** including:

* dynamic format registry table
* automatic format detection
* schema drift monitoring
* ingestion compatibility scoring used in large pharma data platforms.
