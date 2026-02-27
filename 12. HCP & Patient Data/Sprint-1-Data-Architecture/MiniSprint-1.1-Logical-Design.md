# The Logical Design 

We will cover the understanding of the terminologies used, create a plan to support multi-format ingestion, Develop a strategy for internal snowflake stages

## Overview

This document defines the logical design for the pharma commercial analytics pipeline. It translates high level architecture into clear data flows, schemas, data contracts, and acceptance criteria for MiniSprint 1.1. The deliverable is a ready-to-implement blueprint that downstream developers can follow when building ingestion and curation code.

## Objectives

* Define end-to-end logical data flow from vendor files to curated datasets.
* Specify schemas for Source, Curated, Reference, Audit, and Consumption layers.
* Establish data contracts for each incoming feed.
* Define partitioning and storage strategy to support large volume, incremental loads, and efficient querying.
* Capture security, privacy and compliance primitives relevant to pharma data.
* Produce clear acceptance criteria and a task checklist for implementation.

## Scope

Included:

* HCP claims, prescription (Rx), patient support program, and market sales feeds.
* Multi-format ingestion: CSV, JSON, Parquet.
* Internal Snowflake stages and Snowpark Python based processing.
* Currency normalization via Forex reference table.
* Deduplication, basic enrichment, and standardized column naming.

Excluded:

* Machine learning model training and serving.
* Real time streaming beyond periodic delta file processing.
* Vendor onboarding operational tasks beyond defining contracts.

## Inputs and Outputs

### Inputs

* Claims feed (vendorA_claims/YYYY/MM/DD/*.csv)
* Prescription feed (vendorB_rx/YYYY/MM/DD/*.parquet)
* Patient program feed (vendorC_program/YYYY/MM/DD/*.json)
* Market sales feed (market_sales/YYYY/MM/*.csv)
* Forex daily rates (reference/forex.csv)
* Reference masters: drug master, NPI registry, geography mapping

### Outputs

* Source tables: claims_source, rx_source, patient_support_source, market_sales_source
* Curated tables: claims_curated, rx_curated, patient_support_curated, market_sales_curated
* Reference tables: drug_dim, hcp_dim, geography_dim, forex
* Consumption schema star model: sales_fact, claims_fact, rx_fact, product_dim, payer_dim, time_dim, hcp_dim
* Audit tables: load_audit, file_audit, data_quality_metrics

## Logical Data Flow

1. Vendor files landed to repo or SFTP by external process.
2. Files are uploaded to Snowflake internal stage under partitioned folders.
3. File format objects allow parsing of staged files.
4. Copy to source tables with basic type casting and metadata capture (file_name, file_ts, vendor_id).
5. Snowpark Python processes source tables into curated tables:

   * Standardize column names
   * Enrich with reference tables (drug mapping, NPI)
   * Deduplicate using ordering rules
   * Convert local currency to USD using forex table
6. Curated tables are merged and modeled into consumption star schema.
7. Dashboard views and aggregation tables are refreshed.

## Schema Design (Logical)

### Source schema (landing)

* claims_source

  * vendor_claim_id (string)
  * claim_date (date)
  * hcp_identifier (string)
  * patient_id (string)
  * drug_code (string)
  * quantity (int)
  * amount_local (decimal)
  * currency (string)
  * file_name (string)
  * file_processed_ts (timestamp)
  * vendor_id (string)

* rx_source

* patient_support_source

* market_sales_source

  * Similar pattern: source fields plus metadata columns

### Reference schema

* drug_dim

  * drug_id_pk (int)
  * drug_code (string)
  * brand_name (string)
  * generic_name (string)
  * atc_code (string)
  * therapy_area (string)
  * effective_date (date)
  * is_active (boolean)

* hcp_dim

  * hcp_id_pk (int)
  * npi (string)
  * name (string)
  * specialty (string)
  * country (string)
  * region (string)
  * is_active (boolean)

* forex

  * forex_date (date)
  * currency_code (string)
  * rate_to_usd (decimal)

### Curated schema

* claims_curated

  * sales_order_key (surrogate int)
  * vendor_claim_id
  * claim_date
  * hcp_id_fk
  * drug_id_fk
  * quantity
  * amount_local
  * currency
  * amount_usd
  * load_file_name
  * row_hash
  * record_status (active/archived)

* rx_curated, patient_support_curated, market_sales_curated similar

### Consumption schema

* product_dim, payer_dim, time_dim, hcp_dim (denormalized), sales_fact
* sales_fact measures: quantity, amount_usd, tax_usd, discount_usd

## Partitioning and Storage Strategy

* Partition staging by vendor, year, month, day: vendor=vendorA/year=YYYY/month=MM/day=DD
* Source tables: clustered by ingestion date and vendor_id for efficient delta loads
* Curated tables: partition by month of event date for hot queries and retention slicing
* Retention: staged files retained 90 days, source tables retained 365 days, curated & consumption retained per retention policy for analytics (configurable)

## File Formats and Parsing Rules

* CSV: UTF-8, header row, comma separator, quoted fields allowed, strict type casting with error logging
* JSON: newline delimited objects, use JSON_PARSE or VARIANT dollar notation as needed
* Parquet: use implicit schema, validate required columns presence
* On parse error: record into file_audit with failure reason and routing to quarantine area

## Data Contracts (per feed)

For each incoming feed define:

* Vendor name and contact
* Delivery cadence (hourly, daily, weekly)
* File naming convention
* File schema with required and optional fields
* Field-level semantics and allowed values
* Null handling rules
* SLA for delivery and correction window

Example contract excerpt for claims feed:

* Required fields: vendor_claim_id, claim_date, hcp_identifier, drug_code, quantity, amount_local, currency
* Claim date format: YYYY-MM-DD
* Currency codes: ISO 4217
* Missing required field: reject row into quarantine, log in data_quality_metrics

## Deduplication and Delta Strategy

* Deduplication key: composite of vendor_claim_id + vendor_id
* If same vendor_claim_id appears multiple times: pick record with latest file_processed_ts
* Delta identification:

  * Track processed file list in file_audit with checksum
  * New files are detected by file_audit absence and file timestamp
  * Copy command for stage -> source is idempotent if using metadata keys and on-error continue configured

## Currency Normalization

* Use forex table with daily rate effective_date
* For each record: lookup rate_to_usd by currency and claim_date (closest prior date if missing)
* amount_usd = amount_local * rate_to_usd

## Metadata and Lineage

* Every row in source and curated must include:

  * file_name
  * file_path
  * file_checksum
  * file_processed_ts
  * load_job_id
* Maintain file_audit: file_name, vendor_id, rows_expected, rows_loaded, checksum, status
* Maintain row-level row_hash to detect late-arriving updates

## Audit, Monitoring and Metrics

* load_audit table: job_id, feed_name, vendor_id, start_ts, end_ts, rows_input, rows_output, status, error_count
* data_quality_metrics: metric_name, feed_name, metric_value, measurement_ts
* Alerts:

  * Missing daily feed triggers pager or notification
  * Error rate above threshold (for example 1%) creates incident
* Observability:

  * Query history dashboards
  * Scheduled health check job that validates counts and raises anomalies

## Security and Compliance

* PHI handling:

  * Mask or tokenize patient identifiers at the earliest possible step
  * Restrict curated and consumption schemas to approved roles only
* Access control:

  * Role based access controls: data_ingest_role, data_engineer_role, analytics_role
  * Use Snowflake RBAC to separate duties
* Encryption:

  * Ensure Snowflake-managed encryption keys are enabled
* Audit logging:

  * Enable query and access logging for compliance review

## Roles and Responsibilities

* Data Owner (Vendor liaison): confirm data contract and SLA
* Product Owner: approve acceptance criteria and KPIs
* Data Engineer: implement ingestion, curation, transforms
* Data Steward: own reference tables and data quality rules
* Security Officer: approve access and PHI controls
* QA Analyst: design and execute test cases

## Acceptance Criteria

* All feeds land to internal stage with validated file checksum
* Source tables populated with metadata and no schema mismatch errors
* Curated tables contain deduplicated and enriched rows with amount_usd calculated correctly
* Reference tables are present and used in joins
* load_audit and file_audit record every batch with correct counts
* Automated unit tests and integration tests pass
* Documentation and data contracts stored in repo

## Implementation Task Checklist

* Create stage folders and file format objects
* Implement stage-to-source copy scripts with metadata capture
* Implement Snowpark Python pipelines for each feed:

  * Standardize
  * Enrich
  * Deduplicate
  * Currency conversion
  * Save to curated schema
* Implement reference loader scripts for drug_dim, hcp_dim, forex
* Create consumption model builder script to populate dimensions and facts
* Implement audit logging and monitoring views
* Write unit tests for transform logic
* Document data contracts and retention policies

## Test Plan

* Unit tests for transform functions: verify column mapping, currency conversion, row hashing
* Integration tests using sample mini-files for each vendor
* Delta test: ingest initial files then small delta set; verify incremental behavior
* Performance test: run ETL with 10x expected daily volume and measure runtime and warehouse usage
* Regression tests for schema changes

## Deliverables for MiniSprint 1.1

* Logical design document (this file)
* Data contracts template populated for claims feed and one Rx feed
* Schema DDL drafts for Source and Curated schemas
* Checklist of implementation tasks for next sprint

## Risks and Mitigations

* Risk: Vendor schema changes break parsing

  * Mitigation: enforce contract with schema versioning and fail-safe quarantine
* Risk: PHI leakage via permissive roles

  * Mitigation: enforce strict RBAC and tokenized PHI patterns
* Risk: Late-arriving files cause duplicate analytics

  * Mitigation: row_hash, file_audit, and left-anti joins to prevent reprocessing

## Items Requiring Verification or Uncertain

* Vendor delivery cadence and guaranteed fields for each feed
* Exact retention windows required by legal/compliance for PHI and non-PHI data
* Existing canonical HCP identifier source (NPI only, or internal mapping required)
* Permitted masking or tokenization method for patient identifiers
* Acceptance thresholds for data quality metrics (for example allowable error rate)
* Regional regulatory constraints that affect retention or cross-border data movement

## Next Steps

* Review and approve this logical design by Data Owner and Product Owner
* Populate data contract template for each vendor and confirm
* Proceed to Sprint 1.2 schema strategy and DDL creation
