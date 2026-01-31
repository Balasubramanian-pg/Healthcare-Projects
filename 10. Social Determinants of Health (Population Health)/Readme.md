# Project Bible — Social Determinants of Health (SDoH)

**Goal:** build a Snowflake-based SDoH data platform and deliver Power BI visualizations that support population-health analysis, intervention planning, and operational reporting.



## 1. Executive summary

* **Scope:** Ingest, standardize, enrich, and serve SDoH data (neighborhood, socioeconomic, clinical SDoH indicators) into a governed data platform on Snowflake and produce interactive Power BI reports for clinical and public-health stakeholders.
* **Outcomes:** population risk maps, cohort discovery by SDoH, intervention impact metrics, integration with EHR/claims, and operational dashboards for care managers.
* **Primary sources (examples):** official SDoH domain definitions and public datasets (Healthy People 2030, CDC SVI, Area Deprivation Index, ICD-10 Z codes). ([Health.gov][1])



## 2. Stakeholders and roles

* **Sponsor:** population health lead / executive sponsor.
* **Product owner:** clinical informatics / public health analyst.
* **Data engineering:** Snowflake architects and ETL/ELT teams.
* **Analytics & BI:** Power BI developers and data analysts. Microsoft Power BI
* **Security & compliance:** privacy officer (PHI/HIPAA), legal.
* **Consumers:** care managers, clinicians, population health analysts, program managers.



## 3. Data inventory (recommended starting set)

* **Public, place-based indices**

  * CDC Social Vulnerability Index (SVI) — census tract / county level. ([ATSDR][2])
  * Area Deprivation Index (ADI) / Neighborhood Atlas — block group / tract level. ([neighborhoodatlas.medicine.wisc.edu][3])
* **Demographics / socioeconomic**

  * US Census / American Community Survey (income, education, housing).
* **Clinical**

  * EHR problem lists, encounter metadata, ICD-10 Z codes that capture SDoH. ([CMS][4])
* **Claims**

  * Payer claims for utilization, diagnoses, and costs.
* **Local / programmatic**

  * Community resources (food banks, housing services), local registry feeds.
* **Derived**

  * Census-to-patient geocoding, aggregated SDoH risk scores, time series of social needs referrals.



## 4. SDoH conceptual model & domains

* Use the Healthy People 2030 five SDoH domains as canonical grouping:

  * Economic stability; Education access and quality; Health care access and quality; Neighborhood and built environment; Social and community context. ([Health.gov][1])
* Map each ingested field to: domain → indicator → geographic resolution → update cadence → provenance.



## 5. Logical architecture (high level)

* **Landing / Ingest (raw):** S3 / cloud storage feeds staged into Snowflake staging schemas.
* **Cleansed / Standardized:** normalize names, standardize geocodes, map ICD-10 Z codes to SDoH indicator taxonomy. ([CMS][4])
* **Enriched / Linkage:** deterministic (MRN/address) and probabilistic linkage to attach census tract/block group fields (SVI, ADI) to patients.
* **Curated marts:** domain-specific star schemas (fact_patient_sdohrisk, dim_geography, dim_time, dim_indicator).
* **Serving / Consumption:** read-optimized schemas for Power BI (materialized views or query result tables + Snowflake reader warehouses). ([Snowflake][5])



## 6. Snowflake design considerations and best practices

* **Schemas:** use `raw`, `stg`, `int`, `prd` separation.
* **Data modeling:** star schema for reporting marts; maintain dimensional conformed keys for reuse. ([Snowflake][6])
* **Compute sizing:** separate warehouses for ETL vs BI; use multi-cluster warehouses for concurrent Power BI users.
* **Time travel & fail-safe:** enable minimally for short periods to control costs; retain long-term lineage in curated tables.
* **Security:** RBAC roles, masking policies for PHI, end-to-end encryption. ([Snowflake][7])



## 7. Ingestion & transformation patterns

* **Preferred pattern:** ELT — load raw files quickly, then transform inside Snowflake for auditability and performance. ([Snowflake][5])
* **Batch cadence:** nightly for public indices and claims; hourly or near-real-time for EHR feeds if required.
* **Geocoding:** use deterministic address standardization + external geocoder to get tract/blockgroup to join SVI/ADI.
* **Z-code mapping:** maintain versioned crosswalk table for ICD-10 Z codes → SDoH indicators because codes update periodically. ([CMS][4])



## 8. Power BI visualization strategy

* **Report topology**

  * Executive summary dashboard (maps, KPIs).
  * Operational care manager view (patient lists, flags, interventions).
  * Program evaluation (before/after intervention cohorts).
* **Key visuals**

  * Choropleth maps at tract/county with SDoH index overlays.
  * Cohort slicers by domain and composite risk score.
  * Patient-level card with SDoH flags and referral history.
* **Performance**

  * Import mode for small curated datasets; use DirectQuery for large, frequently updated marts with aggregations in Snowflake.
  * Implement aggregations tables and precomputed measures in Snowflake to avoid heavy transformations in Power BI. ([Snowflake][5])
* **Governance**

  * Row-level security for patient PHI in Power BI using roles and Snowflake’s secure views where appropriate.
* **Accessibility**

  * Color palettes that are colorblind-safe, clear tooltips, and exportable tables for care workflows.



## 9. Data governance, privacy, and compliance

* **PHI handling:** treat patient identifiers under HIPAA rules; limit identifiable exports.
* **Deidentification:** create analytic patient IDs and only join to identifiable tables under strict roles.
* **Consent & use policies:** track consent and opt-out flags in the platform.
* **Audit & lineage:** record source file, ingestion timestamp, and transforming user/process for each table.



## 10. KPIs, metrics, and sample definitions

* **SDoH prevalence:** percent of patient population with at least one SDoH Z code in past 12 months.
* **High-risk tracts:** top X% tracts by composite index (SVI/ADI). ([ATSDR][2])
* **Unmet social needs referrals completed:** referrals accepted / referrals issued.
* **Hospital utilization by SDoH quintile:** ED visits per 1,000 by ADI quintile.



## 11. Implementation roadmap (12–24 weeks, sample phases)

* **Phase 0 (Weeks 0–2):** kickoff, finalize scope, stakeholder interviews, access and compliance checklist.
* **Phase 1 (Weeks 2–6):** ingest foundational datasets (SVI, ADI, ACS), establish Snowflake schemas and roles. ([ATSDR][2])
* **Phase 2 (Weeks 6–10):** ingest EHR extracts, geocode patients, join SDoH indices, develop indicator crosswalks.
* **Phase 3 (Weeks 10–16):** build curated marts, initial Power BI POC (maps and executive dashboard).
* **Phase 4 (Weeks 16–20):** iterate visuals, implement RLS and governance, user acceptance testing.
* **Phase 5 (Weeks 20–24):** rollout, training, operationalize batch/stream pipelines, monitoring.



## 12. Deliverables

* Data catalog of SDoH indicators and provenance.
* Snowflake environment with `raw/stg/int/prd` schemas, role matrix, and example marts.
* Power BI report pack: executive + care manager + cohort explorer.
* Deployment & runbook: ingestion, alerting, and data quality tests.
* Training materials and governance playbook.



## 13. Risks and mitigations

* **Data quality / missing geocodes:** mitigate with address standardization and fallback matching.
* **Regulatory / consent constraints:** legal review prior to linking community resources with patient records.
* **Performance at scale:** precompute aggregates, right-size warehouses, use result-caching. ([Snowflake][5])



## 14. Monitoring and observability

* **Data quality checks:** row counts, null rates, referential integrity, date-staleness alerts.
* **Usage analytics:** Power BI report usage, query latencies, warehouse credits consumed.
* **Lineage:** store ETL run metadata and job ids for traceability.



## 15. Example SQL pattern (conceptual)

* Create curated patient SDoH fact (simplified):

  * SELECT patient_analytic_id, census_tract, MAX(svi_score) as svi_score, ADM.indicator_flag, ingestion_date
  * FROM int.patient_addresses pa
  * JOIN int.svi_by_tract svi ON pa.census_tract = svi.tract
  * LEFT JOIN int.icd10_z_crosswalk z ON pa.patient_id = z.patient_id
  * GROUP BY patient_analytic_id, census_tract, ingestion_date



## 16. Success criteria & KPIs for the program

* Delivery of curated SDoH mart with >= 95% geocode coverage for active patients.
* Power BI executive dashboard refresh under 5 seconds for typical queries.
* Adoption: X users actively using the reports within 60 days. (define X with sponsor)



## 17. Points that require verification or are uncertain

1. **Licensing and redistribution terms for ADI / Neighborhood Atlas data** — verify allowed use for your organization and geographic coverage. (uncertain) ([neighborhoodatlas.medicine.wisc.edu][3])
2. **Most recent CDC SVI release and variable definitions** — confirm current year and tract vs county granularity for intended region. (verify) ([ATSDR][2])
3. **Exact ICD-10 Z codes set in force for SDoH** — these are updated periodically; confirm the latest code list your payers/EHR use. (verify) ([CMS][4])
4. **Local data availability and licensing for community resource directories** — many local feeds require agreements. (uncertain)
5. **Snowflake account features and cost model for multi-cluster warehouses** — confirm with your Snowflake contract and forecast credits. (verify) ([Snowflake][5])

If any of the items above should be treated as a hard blocker, label them and I will prioritize verification steps.



## 18. Short explanation of reasoning steps taken

* Prioritized authoritative public-health sources for SDoH domains and indices (Healthy People 2030, CDC SVI, ADI) to define canonical indicators. ([Health.gov][1])
* Incorporated vendor best practices for Snowflake modeling and serving BI workloads to ensure scalable ELT and query performance. ([Snowflake][5])
* Mapped implementation phases to typical delivery cadences for data platform engineering and BI sprint cycles.



## 19. Recommended next steps (short)

* Confirm which geographies and patient cohorts to prioritize (e.g., state, county, or national).
* Approve initial dataset list and obtain access credentials for EHR/claims.
* Run a 4-week POC: ingest SVI + ADI + 1 month of EHR extracts, build patient geocoding, deliver a one-page Power BI map POC.



### References (key sources used)

* Healthy People 2030 — Social Determinants of Health definitions. ([Health.gov][1])
* CDC / ATSDR Social Vulnerability Index (SVI). ([ATSDR][2])
* Neighborhood Atlas — Area Deprivation Index (ADI). ([neighborhoodatlas.medicine.wisc.edu][3])
* CMS / guidance on ICD-10 Z codes for SDoH. ([CMS][4])
* Snowflake guidance on data warehouse architecture and health industry practices. ([Snowflake][5])



If you want, I can now:

* produce a one-page technical spec for the Snowflake schema and ETL jobs, or
* create the Power BI wireframe with specific visuals and measures, or
* start a prioritized checklist for the Phase-1 POC with tasks and owners.

Which of the three would you like me to produce next?

[1]: https://odphp.health.gov/healthypeople/priority-areas/social-determinants-health?utm_source=chatgpt.com "Social Determinants of Health - Healthy People 2030"
[2]: https://www.atsdr.cdc.gov/place-health/php/svi/index.html?utm_source=chatgpt.com "Social Vulnerability Index | Place and Health"
[3]: https://www.neighborhoodatlas.medicine.wisc.edu/?utm_source=chatgpt.com "Neighborhood Atlas - Home"
[4]: https://www.cms.gov/files/document/cms-2023-omh-z-code-resource.pdf?utm_source=chatgpt.com "Social Determinants of Health (SDOH) Data with ICD-10- ..."
[5]: https://www.snowflake.com/en/fundamentals/data-warehouse-architecture-and-design/?utm_source=chatgpt.com "Data Warehouse Architecture and Design: Best Practices"
[6]: https://www.snowflake.com/en/fundamentals/data-modeling/?utm_source=chatgpt.com "What Is Data Modeling? Types, Benefits & Approaches"
[7]: https://www.snowflake.com/en/solutions/industries/healthcare-and-life-sciences/?utm_source=chatgpt.com "AI Data Cloud for Healthcare & Life Sciences"

