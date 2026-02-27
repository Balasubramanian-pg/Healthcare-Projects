# Vendor Onboarding

## Overview

This mini sprint defines the vendor onboarding process for bringing a new data provider into the pharma commercial analytics platform. It covers the end-to-end steps from initial intake to production handover, the data contract and schemas, security and compliance checks, test and validation plans, operational SLAs, and clear acceptance criteria. The goal is to make vendor onboarding repeatable, auditable, and low-risk.

## Objectives

* Establish a standardized onboarding workflow that reduces surprises and rework.
* Produce a data contract template and sample filled contract for one feed.
* Define technical validation steps for file delivery, format, content, and performance.
* Define security, privacy, and compliance checkboxes for PHI and PII handling.
* Define operational readiness gates and sign-off requirements.

## Expected outputs for this mini sprint

* Completed vendor onboarding checklist and timeline.
* Data contract template with required fields and example values.
* Test dataset requirements and validation queries.
* Roles and responsibilities mapping for onboarding tasks.
* Acceptance criteria and go/no-go checklist for production handover.

---

## 1. High-level onboarding flow

1. Vendor intake and capability assessment

   * Collect vendor contact, delivery methods, formats, and cadence.
   * Confirm legal and compliance constraints and any encryption/authentication requirements.

2. Data contract negotiation and sign-off

   * Agree file naming, folder partitioning, schema, encoding, required fields, and error handling rules.
   * Confirm SLAs, contact points, and escalation process.

3. Technical integration

   * Provision stage and access controls.
   * Establish file transfer method (SFTP, S3 push, vendor portal, or operator PUT).
   * Exchange sample files and schema.

4. Validation and testing

   * Parse sample files with production file formats.
   * Run data quality checks and schema validation.
   * Validate delta behavior and deduplication.

5. Pilot ingest and reconciliation

   * Perform pilot with a limited historical subset or a short live window.
   * Validate audit logs, row counts, and integrity.

6. Production cutover

   * Schedule go-live, monitor first n loads closely, and execute runbook for exceptions.

7. Operational handover

   * Document runbook, incident contacts, expected behavior, and monitoring dashboards.
   * Sign off by data owner and operations.

---

## 2. Vendor intake and capability assessment

### Questions to collect

* Vendor name and primary technical contact.
* Delivery method: SFTP, S3, Azure Blob, Google Cloud Storage, direct API, or push to our staging account.
* Preferred file formats: CSV, JSON newline, Parquet, Avro.
* Delivery cadence and time window: daily batch, hourly, weekly, ad-hoc.
* Typical file size and typical daily volume.
* File naming convention and whether vendor can produce partitioned folder layout.
* Whether files contain PHI or PII and any redaction/tokenization they already perform.
* Expected retention and archival policy on vendor side.
* Encryption/transfer requirements, e.g., SFTP with key auth, server-side encryption, TLS, PGP.

### Outcome

A completed vendor capabilities record that feeds the data contract draft.

---

## 3. Data contract template (core elements)

Provide this contract to the vendor and store a signed copy in the project repo. Example fields:

* Vendor metadata

  * vendor_id
  * vendor_contact_name / email / phone
  * legal entity and contract ID

* Delivery and transport

  * delivery_method
  * stage target path pattern
  * authentication details (keys, user accounts)
  * encryption at rest / in transit requirements

* File naming and partitioning

  * filename_pattern: `<vendor>_<feed>_YYYYMMDD_HHMMSS_<seq>.<ext>`
  * folder_pattern: `/<vendor>/<feed>/year=YYYY/month=MM/day=DD/`
  * compression policy: none or gzip/snappy
  * maximum and target file size

* Schema and semantics

  * canonical field names, types, nullability, and formats (date/time formats, numeric precision)
  * required fields and example values
  * field-level semantics and code lists (for example currency ISO 4217)

* Error handling and duplicates

  * behavior on bad rows: reject row to quarantine or attempt best-effort parsing and log
  * expected idempotence behavior: file-level checksum or unique file id
  * duplicate detection keys and recommended uniqueness guarantees

* Operational SLAs

  * delivery window in vendor local timezone
  * latency expectations for file availability in staging
  * maximum allowable missing-days per quarter
  * escalation contact and target response time

* Compliance and security

  * PHI/PII treatment and any tokenization requirements
  * audit and logging obligations
  * liability and breach reporting timeline

* Acceptance and sign-off

  * signature lines for vendor technical lead, vendor legal, and data product owner

---

## 4. Technical integration checklist

### Staging and access

* Provision Snowflake internal or external stage path for vendor.
* Provide vendor with upload credentials or test S3 bucket details.
* Create a test account or authorized service principal for uploads if required.
* Set minimal role grants: usage and read on stage for vendor service account.

### File format setup

* Create `REFERENCE` file formats for the vendor's declared formats.
* Validate parsing with sample files including corner cases, large rows, and nulls.

### Schema mapping

* Map vendor field names to canonical platform fields.
* Agree on source-to-curated column mapping and any transformations (for example currency_code -> currency, phone -> msisdn normalization).

### Security checks

* Verify file transfer is encrypted and keys are stored securely.
* If vendor will push PHI, confirm tokenization plan or encryption policy.
* Ensure audit logging is enabled for the stage, and that `AUDIT.file_audit` will capture arrival metadata.

---

## 5. Validation and testing plan

### Sample data requirements

* Vendor supplies:

  * One index file that lists file names and row counts
  * 3 to 5 sample files covering normal, edge, and error cases
  * At least one compressed file if compression will be used in production

### Parsing validation

* Test that the file parses without data type errors using the production file format definition.
* Verify that date/time fields map correctly and timezone conventions are respected.

### Data quality checks

Run these checks on sample ingest and first pilot ingest:

* Required field completeness: no missing values for required fields.
* Value domain checks: enums and codes fall within expected lists.
* Referential checks against local reference sets where applicable, for example drug_code formats.
* Numeric sanity checks: negative or extremely large quantities flagged.
* Duplicate detection: verify same unique key repeated in multiple files is handled per contract.

### Reconciliation and counts

* Compare `rows_expected` (if provided) with `rows_loaded`.
* Confirm `file_checksum` saved equals computed checksum on arrival.
* Confirm `AUDIT.file_audit` entries for each file with status `processed` or `failed`.

### Delta and idempotency tests

* Upload an initial set of files and process them.
* Re-upload the same files with different timestamps to confirm the pipeline skips or rejects duplicates as agreed.
* Upload a delta file with updates and verify `row_hash` logic identifies changes and CURATED reflects updates and supersedes older records.

### Performance tests

* Simulate expected peak daily load and measure:

  * Stage upload duration
  * COPY INTO throughput
  * ETL runtime for curated transformation step
* Tune partition targeting, file sizes, and warehouse sizing accordingly.

---

## 6. Pilot and production cutover plan

### Pilot stage

* Duration: 3 to 5 business days, or one complete delivery cycle plus verification.
* Activities:

  * Run full ingestion pipeline on pilot files
  * Validate analytics metrics against vendor-provided reference numbers
  * Run reconciliation and QA dashboards
  * Adjust mappings and transforms based on findings

### Cutover to production

* Agree go-live date and time window
* Freeze changes to transform during the cutover window
* Monitor first 3 production runs with high-touch validation
* Execute rollback plan if repeated failures occur

---

## 7. Monitoring, alerts, and runbooks

### Monitoring items

* Stage arrival latency: time from vendor intended timestamp to actual arrival
* Parse error rate: percent of rows rejected during COPY or Snowpark parse
* Duplicate file frequency
* Volume anomalies: sudden increase or drop

### Alerting

* Missing daily file: immediate page to vendor contact and on-call
* Parse error rate above threshold: email + ticket
* Files failing checksum or with row_count mismatch: create incident

### Runbook content

* Manual steps to reingest a file
* Quarantine procedure for malformed files
* Contact list and escalation matrix
* Postmortem template

---

## 8. Roles and responsibilities

* Vendor technical contact

  * Provide sample files and adhere to contract
  * Respond to issues and deliver fixes

* Data product owner

  * Accept data quality and business acceptance
  * Coordinate sign-off

* Data engineer

  * Create stages, file formats, and COPY jobs
  * Implement Snowpark transforms and delta logic
  * Run pilot and troubleshooting

* Data steward

  * Validate reference mapping and quality rules
  * Maintain master data used in enrichments

* Security officer / compliance

  * Validate PHI handling and role grants
  * Approve any tokenization or masking approach

* Operations lead

  * On-call for first week of production
  * Ensure monitoring and alert rules exist

---

## 9. Acceptance criteria and go/no-go checklist

* Signed data contract exists and is stored in repo.
* Vendor successfully deposits files to assigned stage path.
* `AUDIT.file_audit` records created for all staged files with valid checksum.
* COPY INTO from staged partition to `SOURCE` completes without fatal errors.
* Sample pilot ingest passes data quality checks that include completeness, domain validity, and delta behavior.
* Performance tests show pipeline can handle expected daily volume within SLA limits.
* Security checks completed for transfer, storage, and PHI handling.
* Runbook and incident contacts confirmed.
* Data product owner signs off.

---

## 10. Example timeline and milestones

* Day 0 to Day 2: Intake and capability assessment, create draft data contract.
* Day 3 to Day 6: Technical provisioning, stage creation, and initial credential exchange.
* Day 7 to Day 9: Vendor supplies samples, parsing and mapping validation.
* Day 10 to Day 14: Pilot ingest and reconciliation, iterate on fixes.
* Day 15: Production cutover and close monitoring.
* Day 20: Operational handover and sign-off.

Adjust timeline based on vendor responsiveness and regulatory reviews.

---

## 11. Items requiring verification or uncertain

* Vendor ability to support the recommended partitioned folder layout and filename patterns.
* Vendor willingness to provide `rows_expected` or file manifest for reconciliation.
* Frequency and volume of deliveries to size warehouses and tune file chunking rules.
* Specific regulatory constraints for PHI in each vendor country that may require alternate handling.
* Whether vendor requires separate contractual language for data residency or restricted access.

---

## 12. Short explanation of reasoning steps taken

* Mapped onboarding tasks to the platform requirements established in prior mini sprints to ensure smooth downstream processing.
* Emphasized idempotency, auditability, and explicit metadata capture to reduce rework when vendor behavior is imperfect.
* Balanced operational practicality with compliance needs by designing a pilot-first approach that uncovers edge cases early.
* Prioritized clear acceptance gates and role responsibilities so handoff to operations is deterministic and low risk.

---

If you want, I will now generate:

* A fillable vendor data contract file in Markdown with placeholders
* A sample runbook for ingestion failures
* A Snowpark uploader script that PUTs files and writes `AUDIT.file_audit` entries

Tell me which of these to produce next.
