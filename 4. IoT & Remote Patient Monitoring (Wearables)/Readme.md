# IoT and Remote Patient Monitoring (Wearables)

## Snowflake Data Engineering Project Bible

## 1. Purpose of This Project Bible

This project bible serves as the single source of truth for designing, building, operating, and scaling an IoT-based Remote Patient Monitoring (RPM) data platform using **Snowflake**.

It is intended for:

* Data engineers
* Analytics engineers
* BI developers
* Platform and security teams
* Stakeholders evaluating architecture and scalability

The document focuses on **data engineering concerns**, not application development or clinical decision-making logic.

## 2. Business Context and Objectives

### 2.1 Business Problem

Wearable devices used in remote patient monitoring continuously generate physiological and activity data. This data is:

* High-volume
* Time-series oriented
* Semi-structured
* Highly sensitive

Organizations need a platform that can:

* Ingest data continuously
* Preserve raw sensor fidelity
* Transform data into analytics-ready models
* Support near-real-time insights
* Enforce strong data security and governance

### 2.2 Business Objectives

The platform must:

* Enable clinicians to monitor patient trends over time
* Enable analysts to study population-level patterns
* Support alerting and predictive modeling
* Scale without re-architecture as device volume increases

### 2.3 Success Criteria

Success is defined by:

* Stable ingestion of streaming wearable data
* Reliable transformation into analytics-ready tables
* Low-latency analytical queries
* Strong access control and auditability
* Cost-efficient scaling

## 3. Scope Definition

### 3.1 In Scope

* Wearable sensor data ingestion
* Batch and near-real-time processing
* Data modeling and transformation
* Analytics and BI consumption
* Platform security and governance

### 3.2 Out of Scope

* Device firmware logic
* Mobile or web application development
* Clinical diagnosis algorithms
* Real-time life-critical alerting systems

## 4. High-Level Architecture Overview

### 4.1 Architectural Philosophy

The platform follows an **ELT-first** philosophy:

* Load data in raw form
* Transform inside Snowflake
* Preserve history and replay capability

This approach minimizes data loss and maximizes flexibility.

### 4.2 Logical Architecture Layers

* Data Sources
* Landing and Ingestion
* Raw Data Layer
* Transformation Layer
* Analytics and Consumption Layer

## 5. Data Sources

### 5.1 Wearable Device Data

Typical data includes:

* Heart rate
* Step count
* Sleep stages
* Body temperature
* Blood oxygen levels

Data arrives as:

* JSON payloads
* Time-stamped sensor readings
* Device metadata

### 5.2 Metadata and Reference Data

* Patient identifiers
* Device registration records
* Time zone mappings
* Clinical enrollment details

ASSUMPTION
Patient identifiers are pseudonymized before ingestion. This assumption is necessary to avoid storing direct personal identifiers in the analytics platform.

## 6. Ingestion Layer Design

### 6.1 Landing Zone

Raw data is first written to cloud object storage.

Key principles:

* Immutable files
* Append-only writes
* Partitioning by ingestion date and device type

### 6.2 Ingestion Strategy

Two ingestion modes are supported:

* Micro-batch ingestion for API-based exports
* Streaming ingestion for near-real-time sensor feeds

Snowpipe is used to load files automatically into Snowflake tables as they arrive.

### 6.3 Ingestion Reliability

* File-level idempotency
* Metadata tracking for load status
* Dead-letter handling for malformed records

## 7. Raw Data Layer

### 7.1 Purpose

The raw layer stores data exactly as received.

Why this matters:

* Schema evolution is inevitable
* Debugging requires original payloads
* Regulatory audits may require original records

### 7.2 Table Design

* One table per source or device family
* Variant columns for semi-structured payloads
* Ingestion metadata fields:

  * Load timestamp
  * Source file name
  * Source system

No transformations are applied at this stage.

## 8. Staging and Transformation Layer

### 8.1 Transformation Philosophy

Transformations are:

* Deterministic
* Re-runnable
* Incremental where possible

### 8.2 Staging Tables

Staging tables:

* Flatten nested JSON
* Standardize units of measure
* Normalize timestamps to UTC

Examples:

* Extract heart rate values from nested structures
* Convert step counts to integers
* Normalize sleep stage labels

### 8.3 Data Quality Rules

Data quality checks include:

* Null and range validation
* Duplicate detection
* Timestamp sanity checks

Invalid records are flagged, not deleted.

## 9. Analytics Data Model

### 9.1 Modeling Approach

A dimensional model is used to support analytical workloads.

Reasons:

* Predictable query performance
* BI tool compatibility
* Intuitive business semantics

### 9.2 Dimension Tables

Common dimensions include:

* Patient
* Device
* Time
* Location

Dimensions are slowly changing where appropriate.

### 9.3 Fact Tables

Fact tables store time-series sensor readings:

* One row per measurement per time interval
* Foreign keys to dimensions
* Measures stored in standardized units

Grain is explicitly documented for each fact table.

## 10. Incremental Processing and Orchestration

### 10.1 Incremental Strategy

Incremental loads are based on:

* Ingestion timestamps
* Device event timestamps

Late-arriving data is supported.

### 10.2 Orchestration

Snowflake tasks orchestrate:

* Raw to staging transformations
* Staging to analytics transformations
* Aggregation refreshes

Dependencies are clearly defined to prevent race conditions.

## 11. Aggregation and Performance Optimization

### 11.1 Aggregation Strategy

Pre-aggregated tables support:

* Daily averages
* Rolling windows
* Threshold-based summaries

### 11.2 Performance Techniques

* Clustering on time and device keys
* Materialized views for hot queries
* Separate virtual warehouses by workload type

## 12. Security and Governance

### 12.1 Access Control

Access is controlled via:

* Roles
* Secure views
* Column-level masking

Different roles exist for:

* Engineers
* Analysts
* Clinicians

### 12.2 Data Privacy

* Pseudonymized identifiers
* Encrypted storage and transport
* Auditable access logs

### 12.3 Data Retention

Retention policies define:

* Raw data retention duration
* Aggregated data retention
* Archive and purge rules

## 13. Monitoring and Observability

### 13.1 Pipeline Monitoring

Metrics tracked include:

* Ingestion latency
* Transformation success rates
* Data volume trends

### 13.2 Cost Monitoring

* Warehouse usage tracking
* Storage growth monitoring
* Query cost attribution by role

## 14. Failure Scenarios and Recovery

### 14.1 Common Failure Types

* Schema drift
* Late or missing data
* Upstream API outages

### 14.2 Recovery Strategies

* Raw data replay
* Task re-execution
* Backfill procedures

All recovery steps are documented and repeatable.

## 15. Deployment and Environment Strategy

### 15.1 Environments

Separate environments exist for:

* Development
* Testing
* Production

### 15.2 Promotion Process

* Version-controlled SQL
* Environment-specific parameters
* Controlled release cycles

## 16. Future Enhancements

Potential future extensions include:

* Real-time alert feeds
* Machine learning feature stores
* Device anomaly detection
* Cross-device correlation analysis

## 17. Known Uncertainties and Assumptions

* Wearable data schemas vary by manufacturer. I cannot verify a universal schema.
* Regulatory requirements depend on jurisdiction. I cannot verify compliance obligations without region-specific context.

## 18. Reasoning Summary

This project bible emphasizes durability, scalability, and auditability. By preserving raw data, transforming incrementally, and modeling analytically, the platform supports both operational monitoring and long-term analytical use cases without repeated redesign.
