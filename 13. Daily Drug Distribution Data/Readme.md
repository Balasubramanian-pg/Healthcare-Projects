# Project Plan — Pharma Pharmacovigilance Data Fabric (Microsoft Fabric style)

## 1. Executive summary

This project builds a pharma-focused data fabric to support pharmacovigilance and medication safety analytics. The pipeline follows the image you provided: ingest high-volume and low-volume sources, land into Bronze, perform initial processing, build Silver (curated) stores, run further transforms to Golden (trusted) assets, then power visualizations and ML serving. Primary outcomes:

* Continuous adverse event detection and case prioritization
* Self-service analytics for safety and regulatory teams
* Production ML model to score reports and flag signals
* Full lineage, access controls, and audit trail for compliance

Sources used to ground regulatory expectations: WHO and FDA pharmacovigilance definitions and guidance, plus HIPAA and GDPR overviews. ([World Health Organization][1])

---

## 2. Use case, scope, and assumptions

### 2.1 Use case

* Pharmacovigilance: ingest adverse event reports, EHR extracts, claims, lab results, and marketing/sales data to detect safety signals, prioritize cases for review, and report to regulators.

### 2.2 In scope

* Design and implement end-to-end data fabric: ingestion, Bronze/Silver/Golden layers, cataloging, data quality, transformations, Power BI reports, and ML model training + serving.
* Security controls, role-based access, and a compliance checklist for PHI/personal data handling.
* MLOps pipeline for model retraining and inference endpoints.

### 2.3 Out of scope (initial MVP)

* On-prem integration of legacy systems requiring device-level changes
* Full regulatory submission automation (can be phased)
* Global multi-region failover (optional phase 2)

### 2.4 ASSUMPTIONS (explicit)

* ASSUMPTION: Microsoft Fabric (OneLake + Lakehouses + Dataflows + Notebooks + Power BI + model serving) will be the target platform. If another platform is chosen, some implementation details will change.
* ASSUMPTION: Data owners will provide sample extracts and access credentials for each source during discovery.
* ASSUMPTION: Project team has legal/compliance contacts to approve de-identification / data sharing rules.

---

## 3. Stakeholders and roles

* Project sponsor: Head of Safety / Pharmacovigilance
* Product owner: PV analyst lead
* Project manager: delivery lead
* Data engineer(s): 2 FTE (ingest, transformations, pipelines)
* Data architect: 0.5 FTE
* Data scientist(s): 1–2 FTE (feature engineering, model)
* BI developer: 1 FTE (Power BI)
* DevOps/security: 0.5 FTE
* QA/testers: 0.5 FTE
* Regulatory/compliance SME: as needed

---

## 4. Architecture and components (high level)

* Ingest layer

  * High-volume streaming/batch sources (EHR, claims, device telemetry)
  * Low-volume sources (safety case forms, regulatory reference tables, drug master)
* Bronze (raw landing) lakehouse

  * Immutable raw files (parquet/CSV), partitioned by ingestion date and source
* Initial process

  * Lightweight parsing, schema attachment, basic validation
* Silver (curated) datasets

  * Standardized tables: patient_pseudonym, drug_master, adverse_event_raw_parsed, lab_results_norm
* Further transform

  * Entity resolution, deduplication, enrichment (drug mapping, ATC codes), de-identification
* Golden (trusted) assets

  * Flattened safety case view, signal analytics tables, ML feature store
* Consumers

  * Power BI datasets and reports for safety dashboards
  * ML serving endpoints for real-time scoring and triage queues
* Governance

  * Data catalog and lineage, access controls, monitoring and alerting

---

## 5. Deliverables (explicit)

* Discovery and data inventory document
* Data model: Bronze / Silver / Golden schemas
* Ingestion pipelines and scripts (parameterized)
* Transformation notebooks and SQLs
* Data quality rules and automated tests
* Metadata catalog entries and lineage diagrams
* Power BI report pack (safety dashboard, trend analyzers, RCA views)
* Trained ML model + serving endpoint and CI/CD for retraining
* Runbooks, security controls checklist, and handover docs

---

## 6. Work breakdown and 10-week delivery plan (recommended MVP)

> Reasoning summary: I divided the work into discovery, iterative delivery of each data layer, early analytics + ML prototyping, and finalization. Each sprint ends with a demo and acceptance criteria.

### Weeks 0–1 — Discovery & design

* Tasks:

  * Kickoff, stakeholder interviews, identify sources and sample data
  * Define success metrics and acceptance criteria
  * Finalize platform, environments, and access
* Deliverables: Data inventory, architecture diagram, project backlog

### Weeks 2–3 — Ingest and Bronze

* Tasks:

  * Implement connectors for each source (API pulls, SFTP, streaming)
  * Landing raw files into Bronze lakehouse; partitioning strategy
  * Implement basic schema registry and raw metadata capture
* Deliverables: Working ingestion pipelines for all sources, Bronze QA

### Weeks 4–5 — Initial processing and Silver

* Tasks:

  * Parsing, canonicalization of fields, initial data quality checks
  * Build Silver tables: normalized drug master, patient pseudonymization, adverse_event_parsed
* Deliverables: Silver datasets + data quality reports

### Weeks 6–7 — Further transforms and Golden

* Tasks:

  * De-duplication, entity resolution, enrichment (ATC mapping), merging signals
  * Create Golden views for reporting and ML feature store
* Deliverables: Golden dataset, lineage and dataset documentation

### Weeks 8 — Analytics, BI and UAT

* Tasks:

  * Build Power BI reports and datasets: dashboard, signal explorer, case queue
  * User acceptance testing with PV team
* Deliverables: Power BI report pack, UAT sign-offs

### Weeks 9 — ML model and serving

* Tasks:

  * Prototype model to score case priority (training, validation)
  * Deploy model to serving endpoint or batch scoring job
  * Integrate scores into Golden dataset and BI
* Deliverables: Model + inference endpoint + evaluation report

### Week 10 — Harden, security, handover

* Tasks:

  * Implement RBAC, encryption, logging, retention policies
  * Final security/compliance review and docs
  * Handover, runbooks, training sessions
* Deliverables: Production handover pack, SLA definitions

---

## 7. Technical tasks and examples

### 7.1 Ingestion patterns

* High-volume: streaming ingestion or micro-batch (use event hubs, Kafka, or scheduled Spark jobs)
* Low-volume: scheduled API pulls or SFTP fetches

### 7.2 Bronze conventions (example)

* Path pattern: `/oneLake/bronze/{source}/{year}/{month}/{day}/sourcefile.parquet`
* Metadata per file: source, received_ts, file_checksum, schema_version

### 7.3 Example Bronze → Silver transform (SQL pseudocode)

```sql
-- parse adverse event raw JSON into canonical table
INSERT INTO silver.adverse_events
SELECT
  file_metadata.source_filename,
  parsed.event_id,
  parsed.report_date::date as report_date,
  parsed.patient_id_hashed as patient_id,
  parsed.drug_code,
  parsed.reaction_code,
  parsed.severity,
  parsed.report_text
FROM bronze.adverse_events_raw r
CROSS APPLY OPENJSON(r.payload) WITH (...)
WHERE r.ingest_date = CURRENT_DATE();
```

### 7.4 De-identification guidance (high level)

* Pseudonymize patient identifiers using HMAC with a keyed secret (do not store mapping in same dataset)
* Remove or mask direct identifiers in Golden outputs unless business-justified and authorized
* Retain linkage keys in secure key vault and separate environment

---

## 8. Data model (key tables)

* `bronze.adverse_events_raw` — raw payloads
* `silver.adverse_events_parsed` — canonical fields, timestamps, source ids
* `silver.drug_master` — drug codes, ATC, ingredient mapping
* `silver.patient_pseudonym` — hashed patient id and minimal demographics
* `golden.safety_case` — flattened, enrichment, score, review status
* `golden.feature_store` — model-ready features with versioning

---

## 9. Data quality and test plan

* Define checks for:

  * Completeness: percent nulls by critical columns
  * Schema drift: unexpected new fields
  * Duplicate detection threshold
  * Value validation: date ranges, code lists
* Implement automated tests as part of CI/CD and fail pipelines if critical thresholds exceeded

---

## 10. Security, compliance, and audit (short)

* Controls:

  * RBAC for lakehouses and Power BI
  * Encryption at rest and in transit
  * Audit logging and dataset lineage
* Compliance:

  * Follow pharmacovigilance practice for signal reporting and retention
  * Ensure PHI handling complies with applicable laws (example references for PHI and data protection included). ([HHS.gov][2])

---

## 11. ML design and serving

* Problem: classify/report priority and identify likely serious adverse events
* Pipeline:

  * Feature assembly (temporal aggregations, text features from report_text via NLP)
  * Train/test split, model validation, explainability (SHAP)
  * Deploy model: batch scoring into Golden store and optional REST endpoint for real-time triage
* Monitoring: concept drift detection, model performance dashboard, automated retraining schedule

---

## 12. Monitoring, alerting, and ops

* Track pipeline latency, failure rates, data quality metrics
* Set alerts on ingestion failures, schema drift, DAG failures
* Build SLOs: 99% of daily ingest within 2 hours of source availability

---

## 13. Risks and mitigations

* Risk: Sensitive data access delays

  * Mitigation: run minimal PII-free proof-of-concept using synthetic data; parallel legal approval
* Risk: Schema drift from upstream sources

  * Mitigation: schema registry and automated alerts
* Risk: Regulatory requirements differ by region

  * Mitigation: include compliance SME and produce region-specific controls

---

## 14. Acceptance criteria (examples)

* Bronze: All configured sources land raw data with metadata for 7 consecutive days
* Silver: Canonical adverse_event_parsed contains 95% of expected critical fields populated
* Golden: Safety case view contains enrichment and integrated ML score for at least 90% of records
* BI: PV team can filter, export, and run ad hoc queries from reports; UAT sign-off

---

## 15. Repo and naming conventions (suggested)

* Repo: `pharma-pv-datafabric`
* Folders:

  * `/infrastructure` — IaC scripts (Terraform/ARM/Bicep)
  * `/pipelines` — pipeline definitions
  * `/notebooks` — exploration and transforms
  * `/models` — model training code and artifacts
  * `/docs` — runbooks and compliance docs
* Branching: `main`, `develop`, feature branches

---

## 16. Cost and resource estimate (ballpark for planning)

* Team for 10 weeks: ~5.5 FTE average (data engineers 2, data scientist 1.5, BI 1, PM/architect 1)
* Cloud compute: depends on ingest volume. Provide specific cost estimate after discovery (REQUIRES verification).

---

## 17. Handover, training, and documentation

* Deliver runbooks: operational playbooks for ingestion failures, model rollback steps
* Provide a 2-day training for PV analysts on dashboards and dataset usage
* Transfer ownership and schedule post-launch support for 4 weeks

---

## 18. Short, concise reasoning steps taken

* Identified the pharma use case (pharmacovigilance) and mapped it to the pipeline you provided
* Broke work into discovery, iterative implementation of Bronze→Silver→Golden, and consumer enablement (BI + ML)
* Emphasized compliance, data quality, and operationalization as nonfunctional requirements

---

## 19. Items that require verification or are uncertain

* Source availability, formats, and sample size (requires data inventory)
* Whether Microsoft Fabric is the mandated platform or if alternatives (Azure Data Factory + Synapse) are acceptable
* Exact regulatory requirements per country/region for PHI and reporting cadence
* Expected data volume and retention policy (cost impact)
* SLA expectations for latency and throughput

---

## 20. Next steps (immediate)

* Confirm platform choice and provide access to sample data extracts
* Run a 1-week spike: ingest one high-volume and one low-volume source into Bronze to validate schema and performance
* Produce a detailed backlog and sprint plan (Jira / Azure DevOps) for the 10-week delivery

---

If you want, I can now:

* Produce a ready-to-run sprint backlog with task-level breakdown and Jira-style tickets for the full 10-week plan
* Generate the example SQL/Notebook files and a sample repo layout (in markdown) to drop into GitHub
* Create the Power BI report wireframes and a sample Power BI dataset schema

Tell me which of those you want me to create first and I will generate it immediately.

[1]: https://www.who.int/teams/regulation-prequalification/regulation-and-safety/pharmacovigilance?utm_source=chatgpt.com "Pharmacovigilance WHO - Regulation and Prequalification"
[2]: https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html?utm_source=chatgpt.com "Summary of the HIPAA Privacy Rule"
