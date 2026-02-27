# MiniSprint 8.3 — Compliance

## Overview

This mini sprint establishes **regulatory and enterprise compliance controls** for the pharma data platform.

By this stage the platform already supports:

* governed ingestion
* incremental processing
* auditing
* optimization
* dashboards

Compliance ensures the platform can operate safely in **regulated healthcare environments** where data handling must follow strict legal, privacy, and governance standards.

This sprint converts the platform from a technically correct system into a **regulatory-ready data platform**.

---

## Objective

* Protect sensitive healthcare data.
* Enforce controlled data access.
* Maintain regulatory auditability.
* Support data privacy regulations.
* Implement governance policies.
* Enable compliant analytics usage.
* Reduce organizational risk.

---

## Compliance Architecture

```text id="7k9a2p"
Data Ingestion
      ↓
Classification
      ↓
Access Control
      ↓
Masking / Protection
      ↓
Audit & Monitoring
      ↓
Compliant Consumption
```

Compliance is applied across the entire lifecycle.

---

# 1. Regulatory Landscape (Pharma Context)

Typical regulations affecting pharma analytics platforms:

* HIPAA (United States healthcare privacy)
* GDPR (European personal data protection)
* GxP data integrity principles
* FDA electronic record requirements
* Internal enterprise governance policies

Core principle:

```text id="kz6qwp"
Only authorized users access only required data
```

---

# 2. Data Classification Framework

Before applying controls, data must be classified.

Example classification tiers:

| Classification | Example Data        |
| -------------- | ------------------- |
| Public         | aggregated sales    |
| Internal       | territory metrics   |
| Confidential   | HCP identifiers     |
| Restricted     | patient information |

Classification table:

```sql id="s4pcz2"
CREATE TABLE GOVERNANCE.data_classification (
    table_name STRING,
    column_name STRING,
    classification STRING,
    owner STRING
);
```

This becomes the foundation of governance automation.

---

# 3. Role-Based Access Control (RBAC)

Snowflake security relies on roles.

Recommended pharma role hierarchy:

```text id="o9s2fh"
ACCOUNTADMIN
   ↓
DATA_PLATFORM_ADMIN
   ↓
DATA_ENGINEER
   ↓
ANALYST
   ↓
BUSINESS_VIEWER
```

Grant example:

```sql id="3hr7px"
GRANT SELECT ON TABLE FACT.sales_fact
TO ROLE ANALYST;
```

Principle applied:
Least privilege access.

---

# 4. Row-Level Security

Restrict data visibility based on geography or business unit.

Example:
Regional sales managers view only their territory.

Policy example:

```sql id="b0o6t7"
CREATE ROW ACCESS POLICY region_policy
AS (region STRING) RETURNS BOOLEAN ->
CURRENT_ROLE() IN (
    SELECT role_name
    FROM SECURITY.region_access
    WHERE allowed_region = region
);
```

Attach policy:

```sql id="g6y4c1"
ALTER TABLE FACT.sales_fact
ADD ROW ACCESS POLICY region_policy
ON (region);
```

---

# 5. Column-Level Masking

Sensitive identifiers must be protected.

Example:
Patient identifiers masked.

```sql id="i2svxt"
CREATE MASKING POLICY patient_mask
AS (val STRING) RETURNS STRING ->
CASE
    WHEN CURRENT_ROLE() IN ('DATA_PLATFORM_ADMIN')
        THEN val
    ELSE 'MASKED'
END;
```

Apply masking:

```sql id="uh78c3"
ALTER TABLE DIM.patient_dim
MODIFY COLUMN patient_id
SET MASKING POLICY patient_mask;
```

---

# 6. Data Encryption Controls

Snowflake automatically encrypts:

* data at rest
* data in transit

Additional governance includes:

* key management policies
* restricted data sharing
* secure stages.

No additional encryption coding required for most workloads.

---

# 7. Secure Data Sharing

Pharma organizations often share datasets externally.

Use secure shares instead of exports.

Example:

```sql id="r1y82g"
CREATE SHARE commercial_share;
GRANT SELECT ON VIEW secure_sales_view
TO SHARE commercial_share;
```

Benefits:

* no data duplication
* controlled revocation
* audit visibility.

---

# 8. Compliance Audit Logging

Compliance requires monitoring access behavior.

Query example:

```sql id="8rfph3"
SELECT
user_name,
query_text,
start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_text ILIKE '%patient%';
```

Tracks sensitive data usage.

---

# 9. Data Retention and Governance

Define retention rules.

Example:

```sql id="z3vq8m"
ALTER TABLE AUDIT.pipeline_run_log
SET DATA_RETENTION_TIME_IN_DAYS = 90;
```

Typical pharma policies:

* operational logs retained shorter
* curated analytics retained longer
* sensitive raw data minimized.

---

# 10. Compliance Monitoring Dashboard

Recommended compliance KPIs:

* unauthorized access attempts
* masked column access frequency
* data freshness SLA
* audit completeness
* failed policy checks.

These can be surfaced in Snowsight.

---

# 11. Governance Workflow

```text id="vmpo7s"
Data Created
      ↓
Classified
      ↓
Access Policy Applied
      ↓
Audited
      ↓
Approved for Analytics
```

Compliance becomes part of development lifecycle.

---

# 12. Pharma-Specific Compliance Considerations

Common real-world requirements:

* patient data tokenization
* territory-restricted analytics
* vendor contract data isolation
* controlled exports
* reproducible regulatory reports.

Design assumption:
Analytics environments should minimize exposure to raw patient identifiers.

---

# 13. Operational Responsibilities

Typical ownership model:

| Role             | Responsibility        |
| ---------------- | --------------------- |
| Data Engineering | policy implementation |
| Security Team    | access governance     |
| Compliance Team  | audit validation      |
| Business Owners  | data approval         |

---

# Acceptance Criteria

* Data classification documented.
* RBAC roles implemented.
* Row-level security active.
* Sensitive columns masked.
* Access audit queries operational.
* Secure sharing enabled.
* Retention policies defined.

---

# Explanation of Design Thinking

Compliance is introduced after optimization because:

1. Architecture must stabilize first.
2. Security controls depend on finalized datasets.
3. Audit infrastructure already exists.
4. Regulatory readiness requires end-to-end visibility.

The platform now moves from **data engineering system** to **enterprise-compliant healthcare platform**.

---

# Items Requiring Verification or Uncertain

* Applicable regulatory jurisdictions.
* Patient data handling requirements.
* Retention duration mandated by legal teams.
* External data sharing policies.
* Identity provider integration requirements.

---

## Next Mini Sprint

MiniSprint 9.1 — Production Readiness

This sprint finalizes deployment standards, operational playbooks, and enterprise rollout preparation.
