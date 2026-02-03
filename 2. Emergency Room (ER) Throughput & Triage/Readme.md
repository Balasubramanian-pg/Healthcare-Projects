# Emergency Department Throughput & Triage Analytics

**Project Bible | Snowflake Data Cloud, Snowpark, Streamlit**

**Version:** 1.0

**Last updated:** 2026-01-29

## 1. Executive Summary and Strategic Vision

This Project Bible defines the architecture, data flows, operational use cases, governance, and implementation roadmap for an ED throughput and triage analytics platform built on Snowflake and Snowpark with Streamlit-driven operational UX. The system will move the organization from retrospective reporting to near real-time situational awareness and short-term forecasting (rolling 4-hour horizon). Core outcomes include measurable reductions in boarding time, fewer LWBS events, and improved triage accuracy.

## 2. Strategic Objectives

* **Systemic bottleneck identification**

  * Identify boarding latency drivers (EVS, transport, handovers) and reduce median boarding time by 15 to 20 percent.
* **Clinical safety and quality assurance**

  * Reduce LWBS by automated surveillance and escalation for high-acuity patients.
* **Dynamic resource optimization**

  * Align staffing to forecasted arrival surges using historical seasonality and external context feeds.
* **Clinical triage validation**

  * Correlate ESI with downstream resource intensity and outcomes to provide feedback loops for triage staff.

## 3. Success Criteria and KPIs

* Median boarding time reduced by 15 to 20 percent relative to baseline.
* LWBS rate reduced by X percent (define baseline and target in workshop).
* Door-to-provider median time within target threshold (facility-specific target).
* Prediction lead time of at least 4 hours for high-confidence admission events (probability threshold configurable).
* Data latency from EHR event to dashboard under 60 seconds.

## 4. Scope and Boundaries

* **Included**: Real-time ADT, observation vitals, orders/results, imaging events, workforce rosters, EMS feeds, and external context streams.
* **Excluded**: Full clinical chart review, billing adjudication, and full-scale population health analytics outside ED operations (can be future phases).

## 5. Stakeholders and Roles

* **Executive Sponsor**: Chief Medical Officer or Chief Operating Officer
* **Clinical Stakeholders**: Medical Directorate, Nursing Administration, Charge Nurses, ED Physicians
* **Quality and Compliance**: Chief Quality Office
* **Data & Security**: Information Security, Data Engineering
* **Operations & Support**: ED Operations Manager, Bed Management, Environmental Services
* **Deliverable Owners**: BI Engineer (Snowflake pipelines), Data Scientist (Snowpark ML), Frontend Lead (Streamlit dashboards)

## 6. Patient Journey Milestones (T-Milestones)

Define canonical timestamps to ensure consistent measurement and analytics:

* **T0 - Arrival**: Definitive check-in or EMS handover timestamp.
* **T1 - Triage Completion**: ESI assigned and vitals recorded.
* **T2 - Provider Assignment**: LIP assumes care.
* **T2.5 - Diagnostic Interval**: Lab and imaging order-to-result intervals.
* **T3a - Decision to Admit**: Formal inpatient admission order.
* **T3b - Disposition Finalization**: Discharge order or disposition executed.
* **T4 - Physical Departure**: Wheels out timestamp. Boarding time = T4 - T3a.

## 7. High-Level Architecture

* **Cloud Data Platform**: Snowflake Data Cloud with separate Bronze, Silver, Gold layers.
* **Processing**: Snowpark (Python/PySpark compatible) for stateful transforms, temporal spine, and ML.
* **Ingestion**: Snowpipe for serverless, near real-time ingestion from secure cloud storage.
* **Presentation**: Streamlit for operational HUDs and leadership dashboards.
* **Security**: RBAC, Row Level Security, Dynamic Data Masking, PHI tagging.

## 8. Phase-by-Phase Implementation

### Phase 1: Discovery and Clinical Requirements

* Conduct workshops with Medical Directorate, Nursing, CQO, InfoSec.
* Establish baseline metrics for boarding, LWBS, door-to-provider, 72-hour revisits.
* Agree on T-milestones and canonical event definitions.

### Phase 2: Bronze Layer - Ingestion

* Implement Snowpipe and landing zones (S3/GCS/Azure Blob).
* Retain raw payloads (JSON/NDJSON/Parquet) immutable for reprocessing.
* Example pipeline snippet:

```sql
CREATE OR REPLACE PIPE BRONZE.ER_INGEST_PIPE
AUTO_INGEST = TRUE
AS
COPY INTO BRONZE.RAW_ER_MESSAGES
FROM @EXT_STAGE/ER_DATA/
FILE_FORMAT = (TYPE = 'JSON')
ON_ERROR = 'SKIP_FILE';
```

* Logging and monitoring: configure Snowpipe usage monitors and alerting for ingestion failures.

### Phase 3: Silver Layer - Normalization and Staging

* Flatten FHIR/HL7 payloads into relational staging tables.
* Normalize vitals, ADT snapshots, orders, results, and imaging metadata.
* Example vitals transform:

```sql
CREATE OR REPLACE TABLE SILVER.STG_VITALS AS
SELECT
  src:subject.reference::string AS patient_id,
  src:encounter.reference::string AS encounter_id,
  MAX(CASE WHEN src:code.coding[0].code = '8480-6' THEN src:valueQuantity.value END) AS systolic_bp,
  MAX(CASE WHEN src:code.coding[0].code = '8867-4' THEN src:valueQuantity.value END) AS heart_rate,
  MAX(CASE WHEN src:code.coding[0].code = '2708-6' THEN src:valueQuantity.value END) AS oxygen_sat,
  src:effectiveDateTime::timestamp AS recorded_at
FROM BRONZE.RAW_ER_MESSAGES
WHERE src:resourceType = 'Observation'
GROUP BY 1, 2, 4
QUALIFY ROW_NUMBER() OVER (PARTITION BY encounter_id ORDER BY recorded_at DESC) = 1;
```

* Implement deduplication and temporal standardization to UTC. Maintain facility timezone dimension.

### Phase 4: Gold Layer - Analytics and Snowpark

* Implement FACT_ER_PERFORMANCE star schema and dimensions (patient, provider, bed, time, facility).
* Build stateful Snowpark pipelines for temporal spine and minute-level occupancy calculation.
* Implement NLP enrichment as Snowpark Python UDFs for chief complaint classification.
* Train and deploy Snowpark ML models (Admission predictor) with versioning and staging.

### Phase 5: Presentation and Operationalization

* Streamlit HUDs for real-time leaders and shift-level Streamlit pages for charge nurses.
* Automated alerts (Slack, SMS, EHR inbox) driven by rule engine or model thresholds.
* Operational runbooks and escalation paths defined for each alert type.

## 9. Data Model and Schema

### FACT: FACT_ER_PERFORMANCE (sample columns)

* encounter_id
* facility_id
* arrival_ts_utc
* triage_complete_ts_utc
* provider_assigned_ts_utc
* decision_to_admit_ts_utc
* departure_ts_utc
* boarding_minutes
* door_to_provider_minutes
* disposition_type
* lwbs_flag
* revisit_72h_flag
* attending_provider_id
* primary_nurse_id

### DIMENSIONS (high level)

* DIM_TIME (minute granularity)
* DIM_PATIENT (hashed IDs, non-reversible tokens)
* DIM_PROVIDER
* DIM_FACILITY
* DIM_BED_LOCATION

## 10. Analytics and ML Patterns

* **Temporal Spine Occupancy**

  * Build minute-level spine and join encounter intervals to compute occupancy and crowding index.
* **NLP Chief Complaint Enrichment**

  * Snowpark hosted Python UDF using spaCy or scikit-learn to classify free text into HRS categories.
* **Admission Probability Model**

  * XGBoostClassifier trained in Snowpark ML with features: age, arrival mode, ESI, vitals z-scores, complaint category.
  * Persist model artifact to a Snowflake Stage and deploy as a scoring UDF.

## 11. Security, Privacy, and Compliance

* Enforce least privilege RBAC for all objects.
* Tag PHI columns with SENSITIVITY_LEVEL = 'PHI'.
* Configure Dynamic Data Masking and Row Level Security for multi-facility restrictions.
* Maintain audit logs for access and data lineage for regulatory review.

## 12. Monitoring and Observability

* Data latency dashboards: ingestion lag, Silver transform lag, model scoring lag.
* Platform health: Snowflake credit usage, Snowpipe failure rate, Streamlit availability.
* Operational alerts: trigger on defined thresholds and on data anomalies.

## 13. Alerts and Runbooks (examples)

* **High Acuity Unassigned**

  * Condition: ESI 2 patient without provider assignment for > 15 minutes.
  * Action: Send automated EHR inbox alert to Charge Nurse and attending physician. Escalate to ED Director at 30 minutes.
* **Crowding Diversion Recommendation**

  * Condition: Crowding Index > 1.2 for 20 consecutive minutes.
  * Action: Notify Bed Management and issue diversion recommendation to EMS through established protocols.

## 14. Governance and Data Ownership

* **Data Owners**: Clinical Data Steward, Lab Informatics, Radiology Informatics.
* **Platform Owner**: Data Engineering Team.
* **Change Control**: Every schema or pipeline change requires a documented change request and impact analysis.
* **Audit and Validation**: Monthly data quality reviews and quarterly governance meetings.

## 15. Implementation Timeline and Milestones

* **Month 0 (Planning)**

  * Stakeholder workshops, finalize T-milestones, define baseline KPIs.
* **Month 1**

  * Snowpipe ingestion for ADT and vitals. Silver layer normalization for ADT and vitals. Basic Streamlit operational dashboard prototype.
* **Month 2**

  * FACT_ER_PERFORMANCE deployed. Additional Silver transforms (orders, labs, imaging). Initial predictive models in dev.
* **Month 3**

  * Production launch of Admission Predictor and real-time HUD. Alerting and runbooks operational. Post-launch monitoring and tuning.

## 16. Roles, Responsibilities, and RACI

* **Project Sponsor**: Approve budget, escalations, and priorities. (Responsible: Executive Sponsor)
* **Product Owner**: Define clinical requirements and acceptance criteria. (Responsible: ED Clinical Lead)
* **Data Engineering**: Build Snowflake objects, Snowpipe, and transforms. (Responsible: BI/Data Engineering)
* **Data Science**: Model development and validation. (Responsible: Data Scientist)
* **DevOps/Platform**: Manage Streamlit deployment and monitoring. (Responsible: Frontend/Platform)
* **Clinical SMEs**: Provide domain validation and approve alerts. (Accountable/Consulted)

## 17. Risk Register and Mitigations

* **Risk: Data latency exceeds 60 seconds**

  * Mitigation: Increase Snowpipe concurrency, tune micro-batching, implement health checks and backfill strategy.
* **Risk: False positive alerts causing alarm fatigue**

  * Mitigation: Calibrate thresholds with clinical teams, create severity tiers, and implement suppression windows.
* **Risk: PHI exposure**

  * Mitigation: Enforce RLS, masking, audit logs, and periodic access reviews.

## 18. Acceptance Criteria and Handover

* All T-milestones are captured for 95 percent of encounters in production.
* Ingestion latency consistently below 60 seconds on operational days.
* Admission predictor meets defined AUC/precision thresholds on held-out validation set.
* Operational users accept Streamlit HUD in user acceptance testing.

## 19. Appendix

### 19.1 Glossary

* ADT - Admission Discharge Transfer
* ESI - Emergency Severity Index
* LWBS - Left Without Being Seen
* TAT - Turnaround Time
* PHI - Protected Health Information

### 19.2 Example SQL Snippets

* Snowpipe creation (see Phase 2)
* Vitals transform (see Phase 3)

### 19.3 Contacts and Communication Plan

* Project Slack channel: #ed-throughput-ops
* Weekly cadence: 30 minute standup with Data Engineering and Clinical Lead
* Monthly governance: 60 minute review with Sponsor and CQO
