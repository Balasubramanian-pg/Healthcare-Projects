# Unified Dataset

(Curated Consolidation Layer)

## Overview

This mini sprint creates the **Unified Dataset**, the point where all curated healthcare data sources merge into a single enterprise-ready dataset.

Until now:

* Each vendor was processed independently.
* Each dataset followed its own ingestion and correction lifecycle.

From this sprint onward, the platform shifts perspective from **vendor-centric data** to **enterprise healthcare intelligence**.

The unified dataset becomes the foundation for:

* dimensional modeling
* KPI calculation
* commercial analytics
* reporting and dashboards

---

## Objectives

* Combine curated datasets across vendors and regions.
* Create a single standardized healthcare transaction dataset.
* Align business entities across sources.
* Resolve cross-vendor overlaps.
* Prepare data for fact and dimension modeling.
* Maintain lineage and traceability.

---

## Pipeline Position

```text id="k8urfi"
Vendor Curated Tables
        ↓
Deduplicated Records
        ↓
Unified Dataset
        ↓
Dimensional Modeling
```

This layer represents **enterprise truth before modeling**.

---

# Why a Unified Dataset Is Needed

In pharma ecosystems, data arrives fragmented.

Example sources:

* Claims vendor
* Prescription vendor
* Patient support programs
* Market sales feeds
* Specialty pharmacy data

Each represents part of reality.

Analytics requires:

```text id="8og4mk"
One Patient View
One HCP View
One Product View
One Transaction View
```

The unified dataset enables this consolidation.

---

# Conceptual Design

Unified dataset acts as a **canonical transaction layer**.

Example structure:

| event_id | event_type | hcp_id | patient_id | drug_code | event_date | quantity | amount_usd |
| -------- | ---------- | ------ | ---------- | --------- | ---------- | -------- | ---------- |

Multiple feeds normalize into one schema.

---

# Data Sources Combined

Typical pharma feeds merged:

* claims_curated
* rx_curated
* sales_curated
* patient_program_curated

Each feed contributes standardized columns.

---

# Standard Union Strategy

All datasets aligned before merging.

Example:

```sql id="l98c4k"
SELECT
    claim_id AS event_id,
    'CLAIM' AS event_type,
    hcp_id,
    patient_id,
    drug_code,
    event_date,
    quantity,
    amount_usd
FROM CURATED.claims_final
```

Prescription dataset:

```sql id="94hjpf"
SELECT
    rx_id AS event_id,
    'PRESCRIPTION' AS event_type,
    hcp_id,
    patient_id,
    drug_code,
    rx_date AS event_date,
    quantity,
    amount_usd
FROM CURATED.rx_final
```

Unified dataset:

```sql id="bbqwo0"
SELECT * FROM claims_view
UNION ALL
SELECT * FROM rx_view;
```

---

# Entity Alignment

Even after standardization, entity mismatches exist.

Examples:

* Same HCP across vendors
* Drug naming differences
* Geography variations

Unified layer applies enterprise mappings.

Example:

```sql id="w39bb4"
SELECT
    m.enterprise_hcp_id,
    u.*
FROM unified_raw u
JOIN MASTER.hcp_mapping m
ON u.hcp_id = m.source_hcp_id;
```

---

# Event Classification Model

Unified dataset introduces event taxonomy.

Example:

| Event Type | Meaning               |
| ---------- | --------------------- |
| CLAIM      | Insurance claim       |
| RX         | Prescription          |
| SHIPMENT   | Pharmacy shipment     |
| ENROLLMENT | Patient program event |

This enables cross-domain analytics.

---

# Currency Harmonization

At this stage financial values become comparable.

Fields introduced:

* amount_local
* currency_code
* exchange_rate
* amount_usd

Example:

```sql id="c5f57p"
amount_local * exchange_rate AS amount_usd
```

Reason:
Global pharma reporting requires USD normalization.

---

# Snowpark Unified Processing Example

```python id="81g6ax"
claims_df = session.table("CURATED.claims_final")
rx_df = session.table("CURATED.rx_final")

unified_df = claims_df.union_all(rx_df)
```

Add event metadata:

```python id="x93wod"
unified_df = unified_df.with_column(
    "platform_load_ts",
    current_timestamp()
)
```

---

# Lineage Preservation

Unified dataset retains origin tracking.

Mandatory lineage fields:

* source_vendor
* source_table
* ingest_job_id
* source_file
* record_version

Reason:
Healthcare audits require traceability.

---

# Handling Cross-Vendor Overlap

Two vendors may report same event.

Strategy:
Reuse survivorship rules created earlier.

Process:

* match enterprise keys
* rank sources
* keep trusted record

Unified dataset never duplicates events.

---

# Data Volume Considerations

Unified tables grow rapidly.

Design decisions:

* partition by event_date
* incremental union processing
* avoid full rebuilds
* append-only architecture

---

# Unified Table Example

```sql id="rs3r6p"
CREATE TABLE CURATED.unified_events (
    event_id STRING,
    event_type STRING,
    enterprise_hcp_id STRING,
    patient_id STRING,
    drug_code STRING,
    event_date DATE,
    quantity NUMBER,
    amount_usd NUMBER,
    source_vendor STRING,
    load_ts TIMESTAMP_TZ
);
```

---

# Validation After Unification

Checks performed:

* record counts per source
* duplicate enterprise events
* missing entity mappings
* currency conversion success

Example:

```sql id="4x3nb1"
SELECT event_type, COUNT(*)
FROM CURATED.unified_events
GROUP BY event_type;
```

---

# Acceptance Criteria

* All curated datasets merged successfully.
* Enterprise identifiers applied.
* Currency standardized.
* Event taxonomy introduced.
* Lineage fields preserved.
* No duplicate enterprise events.
* Incremental loads supported.

---

# Explanation of Thought Process

The unified dataset solves a structural problem.

Earlier layers focused on correctness per vendor.
This layer focuses on **organizational understanding**.

Key reasoning:

1. Analytics should never depend on vendor structure.
2. Business questions span multiple healthcare domains.
3. Entity alignment must occur before modeling.
4. Consolidation simplifies downstream architecture.

This layer becomes the **single analytical entry point**.

---

# Items Requiring Verification or Uncertain

* Enterprise master data availability.
* Final event taxonomy approval.
* Currency conversion authority source.
* Cross-vendor overlap frequency.
* Historical reconciliation requirements.

---

## Next Mini Sprint

MiniSprint 5.2
Dimension Table Creation

This is where the platform transforms unified healthcare events into a **Star Schema used for analytics and BI systems**.
