# KPI Design for Snowsight

## Goal

Design a production-ready set of KPIs and a Snowsight dashboard pattern for pharma commercial analytics that is performant, auditable, and easy for business users to consume. This mini sprint covers KPI selection, data model mapping, example SQL / scorecard queries, dashboard layout and filters, performance and governance guidance, validation tests, acceptance criteria, and items needing verification.

---

## 1. KPI selection and business mapping

### Primary KPI categories (high value for pharma commercial teams)

* Revenue and Revenue Growth

  * Total Revenue USD (period-to-date)
  * Revenue MoM and YoY % change
* Volume and Utilization

  * Units Sold (quantity) by product / brand
  * Prescription Count
* Market Coverage and Reach

  * Unique HCPs with activity (period)
  * New HCPs engaged this period
* Customer / Channel Performance

  * Revenue by Channel / Payer
  * Market share vs peers (if available)
* Operational / Quality KPIs

  * Data freshness lag (hours)
  * Ingest failures and quarantine rate
  * Delta vs historical variance (anomaly)
* Business health indicators

  * Promotion uplift (promotion vs baseline)
  * Average price / unit and discounts

### Example KPI-to-source mapping

* Total Revenue USD → `sales_fact.amount_usd` summed by date_id
* Units Sold → `sales_fact.quantity`
* Unique HCPs → distinct count of `sales_fact.hcp_sk`
* Data freshness lag → `CURRENT_TIMESTAMP() - max(file_loaded_ts)` from `AUDIT.file_audit`

---

## 2. Snowsight tile types and UX patterns

### Tile types to use

* Scorecards for single-number KPIs (Total Revenue, Units, Unique HCPs).
  Snowsight supports scorecards and chart tiles rendered from worksheet queries. ([Snowflake Documentation][1])
* Time series charts for trends (revenue by day / week / month). ([Snowflake Documentation][1])
* Bar / stacked bar for breakdowns (revenue by brand, channel). ([Snowflake Documentation][1])
* Heat grid or table for pivot-style views (product × geography matrix). ([Snowflake Documentation][1])
* KPI delta widgets or small charts next to scorecards to show change vs previous period.
* Filters panel on top or side for cross-filtering by date range, country, brand, promotion, and sales territory. Snowsight supports custom filters on dashboard tiles. ([Snowflake Documentation][2])

### UX recommendations

* Put 3–5 scorecards in the top row for instant executive overview.
* Below top row place 2 time series charts (revenue trend and units trend).
* Place breakdown charts (brand, channel) on the next row with an optional heat grid or table for details.
* Reserve one tile for monitoring (data freshness and ingest errors) so ops and data teams can spot issues quickly. Snowsight dashboards are tile-based collections of charts from worksheets. ([Snowflake Documentation][3])

---

## 3. Example SQL snippets (ready for Snowsight worksheets)

> Tip: create a named worksheet per KPI group and use those worksheets as dashboard tiles. Snowsight lets you create tiles from worksheet results. ([Snowflake Documentation][3])

### 3.1 Total Revenue USD (scorecard — current month)

```sql
WITH params AS (SELECT DATE_TRUNC('month', CURRENT_DATE) AS month_start)
SELECT
  SUM(amount_usd) AS total_revenue_usd
FROM CONSUMPTION.sales_fact f
JOIN CONSUMPTION.time_dim t ON f.date_id = t.date_id
WHERE t.full_date >= (SELECT month_start FROM params)
  AND t.full_date < DATEADD(month, 1, (SELECT month_start FROM params));
```

### 3.2 Revenue MoM % change (scorecard delta)

```sql
WITH cur AS (
  SELECT SUM(amount_usd) revenue
  FROM CONSUMPTION.sales_fact f
  JOIN CONSUMPTION.time_dim t ON f.date_id = t.date_id
  WHERE t.full_date BETWEEN DATE_TRUNC('month', CURRENT_DATE)
                        AND DATEADD(day, -1, CURRENT_DATE)
),
prev AS (
  SELECT SUM(amount_usd) revenue
  FROM CONSUMPTION.sales_fact f
  JOIN CONSUMPTION.time_dim t ON f.date_id = t.date_id
  WHERE t.full_date BETWEEN DATEADD(month, -1, DATE_TRUNC('month', CURRENT_DATE))
                        AND DATEADD(day, -1, DATEADD(month, -1, CURRENT_DATE))
)
SELECT
  cur.revenue AS revenue_current,
  prev.revenue AS revenue_prev,
  CASE
    WHEN prev.revenue = 0 THEN NULL
    ELSE ROUND( (cur.revenue - prev.revenue) / prev.revenue * 100, 2)
  END AS pct_change_mom
FROM cur CROSS JOIN prev;
```

### 3.3 Units by Product (bar chart)

```sql
SELECT p.brand_name || ' - ' || p.product_code AS product_label,
       SUM(f.quantity) AS units_sold
FROM CONSUMPTION.sales_fact f
JOIN CONSUMPTION.product_dim p ON f.product_sk = p.product_sk
WHERE f.date_id BETWEEN :date_from AND :date_to
GROUP BY product_label
ORDER BY units_sold DESC
LIMIT 50;
```

### 3.4 Data freshness and ingest errors (monitor tile)

```sql
SELECT
  MAX(arrival_ts) AS last_file_arrival,
  MAX(processed_ts) AS last_processed_ts,
  DATEDIFF(hour, MAX(processed_ts), CURRENT_TIMESTAMP()) AS hours_since_last_processed,
  SUM(CASE WHEN status <> 'processed' THEN 1 ELSE 0 END) AS files_in_error
FROM AUDIT.file_audit;
```

---

## 4. Filters and interactivity

### Recommended global filters

* Date range (with presets: YTD, Last 12 months, Last 30 days)
* Country / Region
* Brand / Product
* Promotion (active / inactive)
* HCP specialty or territory

### Implementation notes

* Use Snowsight dashboard filters tied to worksheet queries so each tile responds to a shared filter. ([Snowflake Documentation][2])
* Keep filter cardinality low for global filters. For high-cardinality fields provide a dedicated lookup tile or drill-through worksheet.

---

## 5. Performance and cost guidance

### Query design

* Push aggregations into SQL, avoid fetching raw detail for visual summaries.
* Limit tile queries to the date window and partition keys where possible.
* Use parameterized worksheets and pass dashboard filters into WHERE clauses to maximize micro-partition pruning.

### Snowsight and warehouse sizing

* Use a dedicated read warehouse for dashboards sized to expected concurrency.
* Cache frequently used materialized aggregates or nightly summary tables for heavy dashboard tiles to reduce compute cost and latency.

### Monitoring dashboard performance

* Track bytes scanned and query duration using `QUERY_HISTORY` or `ACCOUNT_USAGE` views to identify expensive tiles. Use Snowflake monitoring guidance and account usage patterns for operational dashboards. ([Snowflake][4])

---

## 6. Data governance, security and sharing

### Access control

* Apply row-level data restrictions in views if users should only see region-specific data.
* Share dashboards using Snowsight folder permissions; tie roles to Snowflake RBAC.
* For PHI-sensitive KPIs restrict viewer roles and mask fields via secure UDFs or views.

### Lineage and auditability

* Every KPI should map to explicit SQL and use enterprise data objects (unified dataset, dims, facts). Store the source worksheet and query with the dashboard tile for traceability. Snowsight stores worksheets and dashboards in the UI. ([Snowflake Documentation][5])

---

## 7. Validation tests and acceptance criteria

### Acceptance criteria (must pass)

* Each KPI tile has an authoritative SQL worksheet and a one line business definition (grain, measure, filter).
* Scorecards and trend tiles return expected values for a sample validation date and reconcile to fact table queries.
* Dashboard responds correctly to global filters.
* Data freshness tile shows last processed file time and flags stale data when lag exceeds SLA.
* Query runtime for each tile is within SLA for interactive use (example: < 5s for scorecards, < 10s for charts). If not, use pre-aggregates.
* Access controls enforce data visibility rules for PHI or restricted geographies.

### Test checklist

* Reconcile top-line revenue with `SELECT SUM(amount_usd)` over the same date range; results match.
* Filter chainer test: select a country filter and validate the numbers change and reconcile to country-level queries.
* Load failure simulation: insert a sample error entry into `AUDIT.file_audit` and confirm the monitoring tile shows it.
* Concurrent load test: run 5 parallel users and measure dashboard response times.

---

## 8. Implementation plan and sprint tasks

### Sprint tasks (deliverables)

* Create worksheets for each KPI with documented SQL and a short business definition.
* Build Snowsight dashboard and add tiles from worksheets, add filters.
* Implement a monitoring tile (data freshness and ingest errors).
* Create nightly aggregate tables for top-heavy tiles if needed.
* Write acceptance tests and run reconciliation for sample periods.
* Document dashboard runbook and owner.

### Folder and repo structure suggestion

* `sprints/06_KPIs/snowsight/`

  * `worksheets/` — SQL files (one per KPI)
  * `dashboards/` — JSON export or notebook with dashboard creation steps
  * `tests/` — SQL test cases and expected values
  * `README.md` — business definitions and owners

---

## 9. Short explanation of reasoning steps taken

* Mapped business priorities to a compact set of KPIs used daily by commercial teams.
* Chose Snowsight-native tiles and worksheets to keep the stack simple and auditable. Snowsight supports tile-driven dashboards and worksheet-based visuals. ([Snowflake Documentation][3])
* Prioritized performance by recommending pre-aggregation and filter-aware SQL to leverage Snowflake micro-partition pruning and avoid unnecessary scans. ([Snowflake][4])
* Included monitoring and governance as integral KPI tiles so data ops and business have the same single pane of truth.

---

## 10. Items requiring verification or uncertain

* Which KPIs must be PHI-free vs acceptable to display with tokenized patient info. This impacts sharing and masks. **(Verification required)**
* Target interactive SLA for chart and scorecard response times under expected concurrency. **(Verification required)**
* Exact fiscal calendar rules used for YoY and fiscal period KPIs in target markets. **(Verification required)**
* Whether Snowsight tenant has any organizational policy that mandates use of external BI tools instead of in-UI dashboards. **(Verification required)**
* Historical baseline numbers or gold-standard reports to reconcile KPIs for initial validation. **(Verification required)**

---

## Next steps I can produce now

* Full set of worksheet SQL files for the KPIs above, tuned to your consumption schema.
* Snowsight dashboard creation checklist and an exportable JSON/template (if you want a repeatable build).
* A small test harness SQL file to run the acceptance tests and produce a reconciliation report.

Tell me which of those you want and I will generate it.

[1]: https://docs.snowflake.com/en/user-guide/ui-snowsight-visualizations?utm_source=chatgpt.com "Visualizing worksheet data - Source: Snowflake Documentation"
[2]: https://docs.snowflake.com/en/user-guide/ui-snowsight-filters?utm_source=chatgpt.com "Filter query results in dashboards and worksheets"
[3]: https://docs.snowflake.com/en/user-guide/ui-snowsight-dashboards?utm_source=chatgpt.com "Visualizing data with dashboards | Snowflake Documentation"
[4]: https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/?utm_source=chatgpt.com "Operational Excellence"
[5]: https://docs.snowflake.com/en/user-guide/ui-snowsight?utm_source=chatgpt.com "Snowsight: The Snowflake web interface"
