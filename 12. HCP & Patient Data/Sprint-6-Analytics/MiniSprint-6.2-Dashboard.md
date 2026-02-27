# MiniSprint 6.2 — Snowsight Dashboard

## Overview

This mini sprint designs and delivers a production Snowsight dashboard for the pharma commercial platform. The dashboard is built from Snowsight worksheets and visualizations, uses shared filters, is secure and auditable, and is tuned for performance and governability. The outcome is a repeatable, documented dashboard asset you can hand to BI users and ops.

Key Snowsight facts used in this design:

* Dashboards are collections of tiles driven by worksheets. ([Snowflake Documentation][1])
* Worksheets let you run SQL and produce visualizations such as scorecards, line charts, bars, heat grids, and tables. ([Snowflake Documentation][2])
* Snowsight supports global and custom dashboard filters that feed into underlying worksheet queries. ([Snowflake Documentation][3])

---

## Objectives

* Create an executive-plus-ops Snowsight dashboard for pharma KPIs and monitoring.
* Provide worksheets for every tile so queries are auditable and versionable.
* Implement shared filters for date, country, brand, and territory.
* Ensure dashboard performance by using parameterized queries, date-bounded filters, and aggregated materializations where needed.
* Provide runbook for owners and simple acceptance tests.

---

## Dashboard audience and pages

* **Exec Overview** — top-line scorecards and trend lines for revenue, growth, units, unique HCPs.
* **Commercial Drill** — brand, product, channel breakdowns, product × geography heat grid, top HCPs.
* **Operational Health** — ingest freshness, files in error, quarantine counts, SLA violations.
* **Exploration / Ad hoc** — table and filters for analysts to slice raw unified events.

---

## Layout and tile catalogue

### Top row — Executive scorecards (single-number tiles)

* Total Revenue (MTD YTD) — worksheet: `kpi_total_revenue.sql`
* Revenue MoM % — worksheet: `kpi_revenue_mom.sql`
* Units Sold (period) — worksheet: `kpi_units.sql`
* Unique HCPs Engaged — worksheet: `kpi_hcp_count.sql`

### Second row — Trends and seasonality

* Revenue time series (daily with rolling average) — `trend_revenue.sql`
* Units time series (daily) — `trend_units.sql`

### Third row — Breakdowns (interactive)

* Revenue by Brand (bar) — `breakdown_brand.sql`
* Revenue by Channel / Payer (stacked bar) — `breakdown_channel.sql`
* Product × Geography heat grid (matrix) — `heat_product_geography.sql`

### Fourth row — Operations and monitoring

* Data freshness and last processed file (scorecard + small table) — `monitor_freshness.sql`
* Files in error / quarantine (table) — `monitor_errors.sql`
* Ingest latency histogram (chart) — `monitor_latency.sql`

### Bottom row — Detail and ad hoc

* Unified events table with filters and download action — `events_detail.sql`
* Snapshot and pre-aggregates refresh status — `agg_status.sql`

---

## Worksheets and SQL mapping

Every tile is backed by a worksheet that contains the canonical SQL, a short business definition, and a test query. Example worksheet snippets you can drop into Snowsight:

**Total revenue (current month) — worksheet `kpi_total_revenue.sql`**

```sql
WITH month_start AS (SELECT DATE_TRUNC('month', CURRENT_DATE) AS start_dt)
SELECT ROUND(SUM(amount_usd),2) total_revenue_usd
FROM CONSUMPTION.sales_fact f
JOIN CONSUMPTION.time_dim t ON f.date_id = t.date_id
WHERE t.full_date >= (SELECT start_dt FROM month_start)
  AND t.full_date < DATEADD(month,1,(SELECT start_dt FROM month_start));
```

**Data freshness — worksheet `monitor_freshness.sql`**

```sql
SELECT
  MAX(arrival_ts) AS last_file_arrival,
  MAX(processed_ts) AS last_processed_ts,
  DATEDIFF(hour, MAX(processed_ts), CURRENT_TIMESTAMP()) AS hours_since_last_processed,
  SUM(CASE WHEN status <> 'processed' THEN 1 ELSE 0 END) AS files_in_error
FROM AUDIT.file_audit;
```

Place each SQL in a worksheet and then create a chart or scorecard from the worksheet results. Snowsight docs explain this flow. ([Snowflake Documentation][2])

---

## Filters and interactivity

* **Global filters** to define: date range, country / region, brand, product, promotion, HCP specialty, territory.
* Implement filters as Snowsight dashboard filters so that a single filter control passes values into multiple worksheet queries. Use parameter placeholders in worksheets or `WHERE` clauses that reference dashboard filter variables. Snowsight supports system and custom filters. ([Snowflake Documentation][3])
* Keep top-level filters low in cardinality. For high-cardinality lists (for example, HCP names) use typeahead or separate drill-through controls to avoid heavy UI state.

---

## Security, sharing, and governance

* Use Snowflake RBAC to restrict who can edit the dashboard and who can run queries. Snowsight dashboard sharing respects Snowflake roles and session contexts. When sharing, ensure viewers have the role and warehouse permissions required to run underlying queries. ([Snowflake Documentation][1])
* For PHI-sensitive tiles, either hide sensitive fields in the query, present tokenized identifiers only, or implement row-level security via secure views. Document which tiles contain tokenized patient data.
* Keep worksheet SQL in the repo for versioning and audit. Store a short business definition and owner in the worksheet description.

---

## Performance and cost optimization

* **Use date-bounded queries.** Ensure every tile uses a `date` filter when scanning facts to leverage micro-partition pruning.
* **Pre-aggregate heavy tiles.** For slow, high-cardinality charts (for example product × geography matrices) create nightly summary tables and point tiles to those tables.
* **Dedicated BI warehouse.** Run dashboard tiles off a read-optimized warehouse sized for concurrency. Monitor credits and scale cluster size when needed.
* **Measure tile cost.** Use `QUERY_HISTORY` and `ACCOUNT_USAGE` to capture bytes scanned and runtime per tile, then iterate. Snowsight and Snowflake docs provide guidance. ([Snowflake Documentation][4])

---

## Implementation tasks and sprint backlog

Organize as sprint tickets, ordered and sized for a 1 or 2 week sprint.

1. **Create worksheets**

   * Deliverable: SQL file per tile under `sprints/06_KPIs/snowsight/worksheets/`
   * Owner: Data engineer

2. **Build dashboard skeleton**

   * Add tiles from worksheets, arrange layout, configure default filters and date window.
   * Owner: BI lead

3. **Add governance metadata**

   * For each worksheet, add business definition, owner, cadence, and test query. Commit to repo.
   * Owner: Data product owner

4. **Performance tuning**

   * Run load tests for concurrent users. Create nightly aggregates for expensive tiles.
   * Owner: Data engineer

5. **Security and sharing**

   * Configure folder and dashboard permissions in Snowsight. Add RBAC notes to runbook.
   * Owner: Security/data steward

6. **Acceptance tests**

   * Reconciliation queries and UI response time tests. Document outcomes.
   * Owner: QA / Data steward

---

## Acceptance criteria and validation tests

* Dashboard renders top-row scorecards within interactive SLA (example < 5s). If not, pre-aggregate.
* Each tile maps to a worksheet SQL file in the repo and includes a one-line business definition.
* Filters synchronize across tiles and change numbers consistently.
* Operational tiles show last processed file and errors correctly from `AUDIT` tables.
* Permissions restrict edit access and enforce view/run constraints per role.
* Reconciliation: top-line revenue from the dashboard equals `SELECT SUM(amount_usd)` over the same period from `sales_fact`.

---

## Runbook essentials (deliver with the dashboard)

* Owner and contact details.
* How to refresh pre-aggregates.
* How to add or change a filter.
* How to export data from a tile.
* Steps to debug slow tiles, including query id lookup in `QUERY_HISTORY`.
* How to rotate the BI warehouse size and where to see credit usage.

---

## Items requiring verification or uncertain

* Confirm the interactive SLA targets for your users and permitted warehouse cost budget.
* Confirm which KPIs are allowed to show PHI or tokenized patient fields. This affects tile design and RBAC rules.
* Confirm the canonical fiscal calendar rules for YoY and fiscal period computations.
* Verify whether the Snowsight tenant uses link-sharing or company-wide governance policies that affect sharing workflows. ([Snowflake Documentation][1])

---

## References

* Snowsight dashboards and tiles documentation. ([Snowflake Documentation][1])
* Snowsight filters guide. ([Snowflake Documentation][3])
* Visualizing worksheet data and available chart types. ([Snowflake Documentation][2])

---

If you want, I will now:

* generate all worksheet SQL files (one per tile) and place them in the repo structure, or
* produce a step-by-step Snowsight dashboard build script (checklist + JSON export template) you can import, or
* create the nightly pre-aggregate SQL templates for heavy tiles.

Tell me which of those to produce next and I will generate it.

[1]: https://docs.snowflake.com/en/user-guide/ui-snowsight-dashboards?utm_source=chatgpt.com "Visualizing data with dashboards | Snowflake Documentation"
[2]: https://docs.snowflake.com/en/user-guide/ui-snowsight-visualizations?utm_source=chatgpt.com "Visualizing worksheet data - Source: Snowflake Documentation"
[3]: https://docs.snowflake.com/en/user-guide/ui-snowsight-filters?utm_source=chatgpt.com "Filter query results in dashboards and worksheets"
[4]: https://docs.snowflake.com/en/user-guide/ui-snowsight?utm_source=chatgpt.com "Snowsight: The Snowflake web interface"
