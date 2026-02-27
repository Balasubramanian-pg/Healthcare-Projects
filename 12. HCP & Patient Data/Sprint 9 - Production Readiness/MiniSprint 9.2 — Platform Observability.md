# MiniSprint 9.2 — Platform Observability

## Overview

This mini sprint introduces **Platform Observability**, the capability to understand the health, performance, reliability, and cost behavior of the pharma data platform in real time.

By this stage the platform already includes:

* incremental pipelines
* audit logging
* optimization controls
* compliance enforcement
* production scheduling

Observability connects all these components into a **single operational visibility layer**.

The goal is simple:

```text
Know what is happening in the platform at any moment.
```

---

## Objective

* Monitor pipeline health.
* Detect failures early.
* Track data freshness.
* Observe performance trends.
* Monitor Snowflake cost usage.
* Identify bottlenecks automatically.
* Enable faster incident resolution.

---

## Observability Architecture

```text
Pipelines
    ↓
Audit Tables
    ↓
System Metadata
    ↓
Monitoring Models
    ↓
Snowsight Observability Dashboard
```

Observability uses both **custom audit data** and **Snowflake system views**.

---

# Core Observability Pillars

## 1. Pipeline Observability

Answers:

* Did pipelines run?
* Did they succeed?
* How long did they take?

Source tables:

* `AUDIT.pipeline_run_log`
* `AUDIT.delta_audit`

Example monitoring query:

```sql
SELECT
pipeline_name,
status,
start_time,
end_time,
DATEDIFF(second,start_time,end_time) runtime_sec
FROM AUDIT.pipeline_run_log
ORDER BY start_time DESC;
```

Key metrics:

* success rate
* runtime trend
* failed executions.

---

## 2. Data Freshness Observability

Critical for pharma analytics.

Business question:
Is dashboard data current?

Example:

```sql
SELECT
MAX(processed_ts) last_processed_time,
DATEDIFF(minute,
MAX(processed_ts),
CURRENT_TIMESTAMP()) freshness_minutes
FROM AUDIT.file_audit;
```

Alert condition:
Freshness exceeds SLA threshold.

---

## 3. Data Volume Monitoring

Detect abnormal behavior.

Example anomalies:

* sudden drop in prescriptions
* unexpected spike in claims
* missing vendor feed.

Query:

```sql
SELECT
load_date,
COUNT(*) records_loaded
FROM FACT.sales_fact
GROUP BY load_date
ORDER BY load_date DESC;
```

Trend deviations indicate upstream issues.

---

## 4. Performance Observability

Uses Snowflake metadata.

Example query:

```sql
SELECT
query_text,
execution_time,
bytes_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
ORDER BY start_time DESC;
```

Track:

* slow queries
* excessive scans
* inefficient joins.

---

## 5. Warehouse Utilization Monitoring

Monitor compute efficiency.

Example:

```sql
SELECT
warehouse_name,
credits_used,
avg_running
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY;
```

Detect:

* idle warehouses
* over-provisioned compute
* workload contention.

---

## 6. Cost Observability

Cost visibility prevents uncontrolled growth.

Metrics:

* credits per pipeline
* credits per dashboard
* storage growth rate.

Example:

```sql
SELECT
DATE_TRUNC('day',start_time) usage_day,
SUM(credits_used)
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
GROUP BY 1;
```

---

## 7. Data Quality Observability

Uses earlier audit framework.

Example:

```sql
SELECT
rule_name,
failed_records,
validation_ts
FROM AUDIT.data_quality_log
ORDER BY validation_ts DESC;
```

Detect recurring quality failures.

---

# Observability Dashboard Design (Snowsight)

Recommended dashboard sections:

### Platform Health

* pipeline success rate
* failed jobs
* runtime trend.

### Data Freshness

* last ingestion time
* SLA breach indicator.

### Data Volume

* daily records trend
* anomaly detection view.

### Performance

* slowest queries
* bytes scanned trend.

### Cost Monitoring

* credits per day
* warehouse utilization.

---

# Alerting Strategy

Observability becomes useful when connected to alerts.

Typical alerts:

| Condition            | Alert             |
| -------------------- | ----------------- |
| Pipeline failure     | immediate         |
| Freshness SLA breach | warning           |
| Cost spike           | daily alert       |
| Data drop            | investigation     |
| Runtime increase     | performance alert |

Alerts may integrate with:

* email
* Slack
* incident systems.

---

# Observability Data Model

Create monitoring schema:

```sql
CREATE SCHEMA MONITORING;
```

Derived monitoring tables:

```text
pipeline_health
data_freshness
warehouse_usage
cost_summary
quality_summary
```

These simplify dashboard queries.

---

# Operational Workflow

```text
Issue Detected
      ↓
Observability Dashboard
      ↓
Root Cause Analysis
      ↓
Pipeline Fix
      ↓
Recovery
```

Mean Time To Resolution reduces significantly.

---

# Acceptance Criteria

* Observability schema created.
* Pipeline health visible.
* Data freshness tracked.
* Cost monitoring available.
* Performance metrics captured.
* Snowsight monitoring dashboard operational.
* Alerts defined for critical failures.

---

# Explanation of Design Thinking

Observability follows production readiness because:

1. Stable pipelines must exist before monitoring them.
2. Audit infrastructure already captures signals.
3. Enterprise systems require proactive monitoring.
4. Operational teams need a single source of truth.

The platform evolves into a **self-observable system**.

---

# Items Requiring Verification or Uncertain

* SLA thresholds for freshness alerts.
* Acceptable pipeline runtime variance.
* Cost alert limits.
* Alert delivery integration method.
* Required monitoring retention period.

---

## Next Mini Sprint

MiniSprint 9.3 — Reliability Engineering

This sprint introduces resiliency patterns such as retries, circuit breakers, and automated recovery mechanisms for enterprise-scale operation.
