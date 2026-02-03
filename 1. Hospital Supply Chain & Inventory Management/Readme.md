# Hospital Supply Chain & Inventory Management — Project Bible (starter deliverable)

## Executive summary

This Project Bible defines a production-ready Snowflake data platform and Power BI analytics layer for hospital supply chain and inventory management. It covers vision, scope, reference architecture, data model, ingestion and CDC patterns, transformation strategy with dbt, governance and compliance requirements, Power BI modeling and visualization guidance, operational runbook, rollout roadmap, and risks. The deliverable below is a comprehensive foundation you can act on immediately; I have included implementation-ready artifacts such as schema designs, example SQL patterns, dbt patterns, and Power BI guidance. Key platform facts that may change over time have been verified and are cited.

Key verified claims:

* Snowflake requires a signed Business Associate Agreement before storing protected health information. ([Snowflake Documentation][1])
* Use dbt with Snowflake following vendor and community best practices for performance and cost control. ([Snowflake][2])
* Power BI supports multiple connectivity modes; DirectQuery and import modes have capacity and row-return tradeoffs that affect design. ([Microsoft Learn][3])



## 1. Objectives and success criteria

### Primary objectives

* Provide single source of truth for inventory and supply chain data using Snowflake.
* Power BI visual layer for operational dashboards, replenishment workflows, audit reports, and executive KPIs.
* Ensure compliance for Protected Health Information (PHI) and healthcare regulatory regimes.
* Achieve near-real-time visibility for critical items and expirations with automated alerts.

### Success criteria (measurable)

* Inventory accuracy > 98% for tracked SKUs within 6 months.
* Stockout rate for critical items reduced by 60% within 12 months.
* Dashboard latency under 5 seconds for common operational queries.
* All PHI-handling systems operate under a signed BAA. ([Snowflake Documentation][1])



## 2. Scope and stakeholders

### In scope

* Clinical consumables, pharmaceuticals, implantables, surgical kits, PPE, and medical devices.
* Procurement, receiving, storeroom management, central supply, nursing units, sterile processing.

### Out of scope (initial)

* Manufacturer ERP changes, patient billing systems (unless required for reconciliation), and logistics partner systems beyond EDI/flat-file feeds.

### Primary stakeholders

* Supply chain director, procurement, pharmacy, nursing leadership, sterile processing, IT/data engineering, compliance, and vendor management.



## 3. High-level architecture

### Logical components

* **Source systems**: ERP (purchase orders, receipts), WMS, pharmacy systems, EDI feeds, vendor portals, IoT sensors (optional), manual CSV uploads.
* **Ingestion layer**: Snowpipe for event-driven loads, staged files in cloud storage (S3/Azure Blob/GCS), secure API endpoints.
* **Raw zone**: Snowflake raw schema with immutable ingestion tables and time-stamped partitions.
* **Staging and CDC**: Snowflake Streams + Tasks to capture changes; bronze tables for deduplication.
* **Transform (dbt) / Silver zone**: dbt models implementing cleaning, enrichment, SCD handling, and business rules. ([Snowflake][2])
* **Dimensional modeling (Gold zone)**: Star schemas for inventory transactions, on-hand views, reorder recommendations.
* **Serving layer**: Materialized views, ephemeral tables as needed, Power BI datasets (Import or DirectQuery / DirectLake depending on scale). ([Microsoft Learn][3])
* **Monitoring**: Usage and cost dashboards, SLO monitoring, data quality tests.

### Key platform choices and rationale

* **Snowflake** for scalable separation of storage and compute and for HIPAA/HITRUST posture (subject to signed agreements). ([Snowflake Documentation][4])
* **dbt** for modular, testable transformations and CI/CD pipelines. ([Snowflake][2])
* **Power BI** for enterprise reporting because of existing BI skillsets and interactive dashboards; choose connectivity mode per dataset size and latency needs. ([Microsoft Learn][3])



## 4. Data domains and canonical data model

### Core entities (recommended canonical tables)

* **fact_inventory_transaction** (granular receipts, issues, adjustments)
* **dim_item** (SKU, description, unit of measure, manufacturer, catalog numbers, shelf life days)
* **dim_location** (facility, building, storeroom, bin)
* **dim_supplier** (vendor metadata, lead times, contract terms)
* **dim_time** (date, week, month, fiscal attributes)
* **fact_purchase_order** (PO line items, statuses)
* **fact_vendor_performance** (on-time %, fill rate)
* **fact_expiration_event** (expiration notifications, disposition)

### Dimensional modeling notes

* Use star schema for gold layer to optimize Power BI reporting.
* Maintain SCD Type 2 for dim_item and dim_supplier to track changes to critical attributes like manufacturer or lead time.

### Example simplified table schemas

* **fact_inventory_transaction**: transaction_id, item_id, location_id, transaction_type, quantity, unit_cost, transaction_timestamp, source_system, reference_id.
* **dim_item**: item_id, sku, description, uom, category, manufacturer_id, shelf_life_days, created_at, effective_from, effective_to, current_flag.



## 5. Ingestion, CDC and change handling

### Ingestion patterns

* **Event-driven**: Snowpipe ingesting files dropped to cloud stage or via APIs for near-real-time ingestion.
* **Batch**: Scheduled loads for less time-sensitive systems.
* **Streaming**: For IoT telemetry use Kafka <> Snowflake connectors if needed.

### CDC and deduplication

* Use **Snowflake Streams** to capture DML changes and **Tasks** to orchestrate incremental processing. This allows near-real-time application of inserts/updates/deletes into staging tables before merging into SCD-managed dimensions. ([Snowflake Documentation][4])

### Idempotency and dedupe

* Use a composite business key plus a source_timestamp for deduplication. Apply deterministic `MERGE` statements keyed on (source_system, reference_id, transaction_timestamp).



## 6. Transformation strategy with dbt

### dbt project structure (recommended)

* `models/staging/` : raw cleaning models, type casts, timestamps.
* `models/marts/` : dimensional models and facts.
* `models/operations/` : operational reports and materializations.
* `tests/` : uniqueness, not_null, relationships.
* `macros/` : reusable SQL snippets for cost/time optimizations.

### Materializations

* Use `incremental` models for large fact tables. Use `ephemeral` for small helper models. Use `table` or `view` for curated small sets used in many downstream reports.

### Testing and CI/CD

* Run dbt unit tests and snapshot SCD logic on every PR. Use ephemeral developer environments and a promotion pipeline (dev → test → prod) with role-based credentials. ([Snowflake][2])



## 7. Security, privacy and compliance

### Compliance posture

* Before storing PHI, ensure a **signed Business Associate Agreement** is in place with Snowflake and any third-party processors. ([Snowflake Documentation][1])
* Map sensitive elements (item lot numbers linked to patient use, serial numbers) and apply data handling rules.

### Technical controls

* **Encryption**: Snowflake encrypts data at rest and in transit by default. Configure customer-managed keys if required. ([Snowflake Documentation][4])
* **Row access policies**: Implement row-level access policies in Snowflake to enforce least privilege on PHI-adjacent datasets.
* **Masking**: Dynamic data masking for sensitive columns.
* **RBAC**: Define roles for ingestion, transformations, analytics, and read-only consumers. Principle of least privilege.
* **Audit logging**: Enable Snowflake access logs and integrate with SIEM.

### Organizational controls

* Data use agreements, training for supply chain staff, retention and purge policies, and documented incident response.



## 8. Power BI architecture and model strategy

### Connectivity mode guidance

* **Operational dashboards with near-real-time needs**: Use DirectQuery or Direct Lake to avoid dataset refresh latency. Note DirectQuery has row limits for visual returns; Power BI Premium changes capacity constraints. ([Microsoft Learn][3])
* **Analytical / aggregated reporting**: Use Import (star schema) to maximize performance for large aggregations. Partition and aggregate in Snowflake and load summarized tables to Power BI for heavier analytics.

### Dataset sizing and limits

* Power BI service dataset size and row limits vary by license and feature set; design to keep datasets under service limits or leverage Premium/Gen2 features if needed. Verify target tenant capacity and licensing before finalizing mode. ([BizAcuity][5])

### Modeling best practices for inventory

* Use star schema from Snowflake; keep measures in a semantic layer, not in visuals.
* Implement common measures: on_hand_qty, available_qty, committed_qty, days_of_stock, turnover_rate, stockout_rate, days_to_expiry. Provide parameter tables for safety stock constants and lead times.

### Example DAX measures

* On-hand quantity (simple):

  ```
  OnHandQty = SUM(fact_inventory_transaction[quantity])
  ```
* Days of stock:

  ```
  DaysOfStock = DIVIDE([OnHandQty], [AvgDailyUsage])
  ```
* Reorder flag:

  ```
  ReorderFlag = IF([DaysOfStock] <= [SafetyStockDays], 1, 0)
  ```



## 9. Inventory analytics and optimization

### Core KPIs

* Inventory accuracy, days of inventory on hand, fill rate, stockout rate, expired items %, obsolescence cost.

### Replenishment algorithms (practical)

* **Min-max with safety stock** for most SKUs.
* **Economic Order Quantity (EOQ)** for bulk items.
* **ABC segmentation**: focus tighter controls and automation on A items.
* **Kanban** for high-velocity consumables.

### Safety stock calculation example (explicit arithmetic)

We show a simple safety stock calculation using service level method. Suppose:

* Average daily demand = 120 units
* Lead time = 7 days
* Demand standard deviation during lead time = 30 units
* Desired service factor (z) for 95% service level = 1.645

Safety stock formula: SafetyStock = z * σL

Digit-by-digit arithmetic:

* z = 1.645
* σL = 30
* Multiply digits:

  * 1.645 × 30
  * 1.645 × 3 = 4.935
  * append zero for ×30 gives 49.35
* SafetyStock = 49.35 units → round up to 50 units

Interpretation: maintain 50 units as safety stock for that SKU.



## 10. Operationalization, monitoring and SLOs

### Monitoring stack

* dbt tests and exposures for data quality.
* Snowflake resource monitors and query history for cost.
* Power BI telemetry for usage and refreshes.
* Alerting: Slack/Teams alerts on failed loads, data quality test failures, MOS (missing on-shelf) events.

### Runbook items

* Daily cron: verify Snowpipe success, run incremental dbt models, refresh critical Power BI DirectQuery caches if applicable.
* Weekly: reconcile physical counts vs system on-hand for sample SKUs.
* Monthly: inventory turnover, audit log review, access reviews.



## 11. CI/CD, environments and deployments

### Environments

* dev (isolated Snowflake role/account), test (integration), prod (live). Use separate Snowflake databases or separate accounts per environment per governance model.

### Git and dbt flow

* Feature branches → PR with tests → CI runs dbt run + dbt test on ephemeral environment → promote via merge to main for scheduled deploys.

### Automation

* Use orchestration (Airflow, GitHub Actions, or Snowflake Tasks) to orchestrate Snowpipe, dbt runs, and downstream refreshes.



## 12. Cost, licensing and sizing considerations

### Snowflake

* Snowflake costs are usage based (credits). Choose warehouse sizing per workload and use auto-suspend to reduce idle costs. Use resource monitors to avoid runaway costs. Estimated credits will depend on query concurrency and data volume; this needs a sizing exercise against sample workloads. ([Snowflake Documentation][4])

### Power BI

* If you need large import datasets or enhanced DirectQuery capacity, consider Power BI Premium. Dataset size limits and row return rules vary by license; verify tenant limits before committing. ([BizAcuity][5])

> Note: cost figures depend on contract terms and regional pricing and must be validated with procurement and platform providers. See the “Verification” section below.



## 13. Implementation roadmap (phased)

### Phase 0 — Foundations (0–4 weeks)

* Confirm contracts, BAAs, and security requirements. ([Snowflake Documentation][1])
* Provision Snowflake account(s) and set up network/security posture.
* Define canonical model and data dictionary.

### Phase 1 — Ingest and raw zone (4–8 weeks)

* Implement Snowpipe ingestion for key sources, create raw schemas, basic streaming with Streams and Tasks.

### Phase 2 — Transformation and dbt (8–16 weeks)

* Build staging models, core dim/fact models, implement tests and snapshots, set up CI/CD.

### Phase 3 — Serving and BI (12–20 weeks)

* Create gold marts, connect Power BI, build operational dashboards, and iterate with users.

### Phase 4 — Optimization and automation (20–32 weeks)

* Add predictive models, replenishment automation, vendor scorecards, and cost optimizations.



## 14. Example SQL patterns

### Idempotent merge for inventory transactions

```sql
MERGE INTO raw_staging.fact_inventory_transaction t
USING (
  SELECT * FROM @stage/inventory/landing_file.csv (file_format => 'csv_format')
) s
ON t.source_system = s.source_system
AND t.reference_id = s.reference_id
WHEN MATCHED AND s.is_deleted = 'Y' THEN DELETE
WHEN MATCHED THEN UPDATE SET
  t.quantity = s.quantity,
  t.transaction_timestamp = s.transaction_timestamp
WHEN NOT MATCHED THEN
  INSERT (transaction_id, item_id, location_id, quantity, transaction_timestamp, source_system, reference_id)
  VALUES (s.transaction_id, s.item_id, s.location_id, s.quantity, s.transaction_timestamp, s.source_system, s.reference_id);
```

### dbt incremental model pattern (simplified)

```sql
{{ config(materialized='incremental', unique_key='transaction_id') }}

with src as (
  select * from {{ ref('stg_inventory_transactions') }}
)

select *
from src

{% if is_incremental() %}
where transaction_timestamp > (select max(transaction_timestamp) from {{ this }})
{% endif %}
```



## 15. Governance, data catalog and metadata

* Implement a data catalog (Alation, Collibra, or open source) integrated with Snowflake metadata.
* Maintain a living data dictionary with ownership, SLA, sensitivity, and retention policy per object.



## 16. Risks and mitigations

### Top risks

* **Regulatory noncompliance** if BAAs or data handling are incomplete. Mitigation: legal signoff before PHI ingestion. ([Snowflake Documentation][1])
* **Cost overruns** from unbounded compute usage. Mitigation: resource monitors and scheduled resizes.
* **Model divergence** across teams. Mitigation: dbt and CI/CD with enforced tests.



## 17. Annexes

### Appendix A — Inventory dimensional model (entity relationship)

* Fact and dimensions as outlined in Section 4. (Full ERD available on request)

### Appendix B — Sample Power BI pages

* Executive: inventory turnover, top 20 value-at-risk SKUs, vendor performance.
* Operational: current on-hand, pending receipts, reorder queue, items near expiry.
* Replenishment: suggested orders, EOQ-based batch suggestions, lead-time heatmap.

### Appendix C — Quick checklist for PHI

* Signed BAA with Snowflake and any cloud storage provider. ([Snowflake Documentation][1])
* Documented retention and purge policies.
* Access review schedule and strong authentication.



## Reasoning steps taken

* Translated business requirements into a cloud-native data platform pattern anchored on Snowflake and dbt.
* Chose star schema gold layer to fit Power BI strengths.
* Selected Snowflake Streams/Tasks and Snowpipe for CDC and near-real-time ingestion. ([Snowflake Documentation][4])
* Cross-referenced vendor docs concerning PHI handling and Power BI connectivity limits to avoid design choices that conflict with platform constraints. ([Snowflake Documentation][1])



## Verification checklist — items requiring confirmation

* Exact legal and contractual status: whether a signed BAA exists with Snowflake and any cloud storage providers. (Verify with legal/compliance). ([Snowflake Documentation][1])
* Power BI tenant licensing (Pro vs Premium) and dataset size / DirectQuery row limits for your tenant; these affect whether Import or DirectQuery is feasible. ([Microsoft Learn][3])
* Snowflake edition and features available under your contract (e.g., Customer-Managed Keys, multi-cluster warehouses, failover). ([Snowflake Documentation][1])
* Vendor integrations and EDI formats supported by your suppliers.
* Expected daily transaction volumes and concurrency so we can produce accurate cost/size estimates.



## What I delivered now and next steps

* Delivered a complete Project Bible foundation: objectives, architecture, canonical model, transformation patterns, compliance guidance, Power BI strategy, runbooks, and a phased roadmap.
* If you want, I can now immediately:

  * Expand any section into developer-ready tasks and sprint backlog items.
  * Generate dbt model skeletons and sample SQL files for `fact_inventory_transaction` and `dim_item`.
  * Produce a full ERD PNG and a Power BI report wireframe with example pages.

Please indicate which of the following you want next and I will generate it immediately:

* dbt model skeletons and `models/` folder structure.
* Detailed ERD and Snowflake DDL for core tables.
* Power BI report wireframe and sample PBIX design pattern.

If you want the cost sizing and a vendor negotiation checklist, I will produce a sizing worksheet next but note that cost numbers require tenant-specific and contract-specific inputs which you may need to confirm.



## Sources cited (most load-bearing)

* Snowflake: Data warehouse fundamentals and HIPAA/BAA notes. ([Snowflake][6])
* Snowflake + dbt optimization guidance. ([Snowflake][2])
* Power BI connectivity and DirectQuery limits. ([Microsoft Learn][3])
* Hospital supply chain best practices and inventory management literature. ([PMC][7])



If you want, I will now generate one of the concrete artifacts listed above (dbt skeletons, Snowflake DDL, Power BI wireframe). Tell me which artifact to produce first and I will generate it immediately.

[1]: https://docs.snowflake.com/en/user-guide/intro-editions?utm_source=chatgpt.com "Snowflake editions"
[2]: https://www.snowflake.com/resource/best-practices-for-optimizing-your-dbt-and-snowflake-deployment/?utm_source=chatgpt.com "Best Practices for Optimizing Your dbt and Snowflake ..."
[3]: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-use-directquery?utm_source=chatgpt.com "Use DirectQuery in Power BI Desktop"
[4]: https://docs.snowflake.com/en/user-guide/intro-key-concepts?utm_source=chatgpt.com "Snowflake key concepts and architecture"
[5]: https://bizacuity.com/blog/handling-large-volumes-of-data-in-power-bi/?utm_source=chatgpt.com "How Many Rows Can Power BI Handle? Big Data"
[6]: https://www.snowflake.com/en/fundamentals/data-warehouse-architecture-and-design/?utm_source=chatgpt.com "Data Warehouse Architecture and Design: Best Practices"
[7]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8428474/?utm_source=chatgpt.com "Principles of supply chain management in the time of crisis"
