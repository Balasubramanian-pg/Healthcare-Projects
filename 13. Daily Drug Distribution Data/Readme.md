# Project Plan — Pharma Drug Distribution Analytics using IQVIA Xponent Data in Microsoft Fabric

## 1. Project Overview

This project builds a Microsoft Fabric data platform to analyze **daily drug distribution using IQVIA Xponent data**. The system ingests high-volume prescription transactions and supporting reference datasets, transforms them through Bronze, Silver, and Golden layers, and produces analytics and ML insights for pharmaceutical commercial and market access teams.

The objective is to monitor:

* Daily prescription volume trends
* Prescriber behavior and adoption
* Market share vs competitors
* Geographic performance
* Early prescription signals for launches
* Demand forecasting

IQVIA Xponent is widely used in the pharmaceutical industry to estimate prescription activity and physician prescribing patterns derived from retail pharmacy data sources.

## 2. Business Objectives

### Primary goals

* Track **daily prescription distribution for branded drugs**
* Monitor **market share vs competitor products**
* Identify **high-value prescribers and territories**
* Enable **sales performance analytics**
* Support **forecasting models for drug demand**

### Key business questions

* Which prescribers drive the most prescriptions?
* Which geographies show the fastest growth?
* How is market share evolving daily or weekly?
* Which territories require sales intervention?

## 3. Data Sources

### High-Volume Data (Primary IQVIA datasets)

| Dataset                   | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| Xponent Prescription Data | Daily prescription transactions by drug, pharmacy, prescriber |
| Xponent NRx               | New prescriptions                                             |
| Xponent TRx               | Total prescriptions                                           |
| Pharmacy Distribution     | Retail pharmacy dispense information                          |
| Territory Mapping         | Sales territory assignments                                   |

These datasets typically contain **millions of rows per day** depending on coverage.

### Low-Volume Reference Data

| Dataset             | Description                                  |
| ------------------- | -------------------------------------------- |
| Drug Master         | Drug name, NDC, brand/generic classification |
| HCP Master          | Prescriber information (NPI, specialty)      |
| Territory Hierarchy | Region, district, territory mapping          |
| Payer Reference     | Payer type classification                    |
| ZIP-Geo Mapping     | Geography enrichment                         |

## 4. End-to-End Fabric Architecture

The architecture directly follows the pipeline structure in the diagram.

### Step 1 — High-Volume Data Ingestion

Sources include:

* IQVIA Xponent daily extracts (CSV / Parquet / SFTP)
* Pharmacy transactions
* Territory assignments

Ingested using:

* Fabric Data Pipelines
* Scheduled ingestion jobs
* Event-based ingestion (if streaming feeds exist)

Stored in:

**Bronze Lakehouse raw tables**

### Step 2 — Low-Volume Data Ingestion

Reference tables ingested weekly or monthly:

* Drug master
* HCP master
* Geographic mapping
* Payer classification

These datasets support enrichment and joins.

### Step 3 — Bronze Layer (Raw Data Storage)

Bronze stores raw, unprocessed data.

Example tables:

| Table              | Description                   |
| ------------------ | ----------------------------- |
| bronze_xponent_rx  | Raw prescription transactions |
| bronze_drug_master | Drug reference                |
| bronze_hcp_master  | Prescriber details            |
| bronze_territory   | Territory mapping             |

Design principles:

* Immutable raw data
* Partition by ingestion date
* Minimal transformations
* Maintain source lineage

Example schema for prescription data:

| Column      | Description           |
| ----------- | --------------------- |
| rx_date     | Prescription date     |
| ndc         | Drug NDC code         |
| npi         | Prescriber identifier |
| pharmacy_id | Pharmacy identifier   |
| trx         | Total prescriptions   |
| nrx         | New prescriptions     |
| zip         | Pharmacy ZIP          |
| source_file | Original file         |

## 5. Initial Processing Layer

Initial processing prepares raw data for analytical transformation.

Tasks include:

* Schema standardization
* Date normalization
* Deduplication
* Data type validation
* Null checks

Example transformation:

Convert prescription date formats and ensure numeric fields are valid.

Example SQL:

```sql
SELECT
  CAST(rx_date AS DATE) AS rx_date,
  ndc,
  npi,
  pharmacy_id,
  CAST(trx AS INTEGER) AS trx,
  CAST(nrx AS INTEGER) AS nrx,
  zip
FROM bronze_xponent_rx
WHERE trx IS NOT NULL
```

Output stored in staging tables.

## 6. Silver Layer (Curated Data)

Silver layer contains **clean, standardized, enriched datasets**.

Key tables:

| Table                 | Description                     |
| --------------------- | ------------------------------- |
| silver_prescriptions  | Clean prescription transactions |
| silver_hcp_dimension  | Prescriber attributes           |
| silver_drug_dimension | Drug details                    |
| silver_geo_dimension  | Geographic hierarchy            |

Transformations performed:

* Join HCP and drug master
* Resolve duplicates
* Enrich ZIP with geographic attributes
* Map NDC to brand names

Example transformation:

```sql
SELECT
  p.rx_date,
  d.brand_name,
  d.generic_name,
  p.trx,
  p.nrx,
  h.specialty,
  g.state,
  g.region
FROM silver_prescriptions p
LEFT JOIN silver_drug_dimension d
ON p.ndc = d.ndc
LEFT JOIN silver_hcp_dimension h
ON p.npi = h.npi
LEFT JOIN silver_geo_dimension g
ON p.zip = g.zip
```

## 7. Further Transformations

Advanced analytical transformations:

### Market Share Calculation

Compute brand share relative to competitors.

Example:

```sql
SELECT
  rx_date,
  brand_name,
  SUM(trx) AS total_trx,
  SUM(trx) / SUM(SUM(trx)) OVER (PARTITION BY rx_date) AS market_share
FROM silver_prescriptions
GROUP BY rx_date, brand_name
```

### Prescriber Segmentation

Identify:

* High-value prescribers
* New adopters
* Declining prescribers

### Sales Territory Aggregation

Aggregate metrics:

* Territory TRx
* Territory growth rate
* Rep performance indicators

## 8. Golden Layer (Business Ready Data)

Golden datasets are optimized for reporting and ML.

Key tables:

| Table                        | Purpose                   |
| ---------------------------- | ------------------------- |
| golden_market_share          | Market share trends       |
| golden_hcp_performance       | Prescriber ranking        |
| golden_territory_performance | Sales territory analytics |
| golden_rx_trends             | Daily prescription trends |

Example schema for territory performance:

| Column       | Description         |
| ------------ | ------------------- |
| territory_id | Sales territory     |
| rx_date      | Date                |
| total_trx    | Total prescriptions |
| growth_rate  | Daily growth        |
| brand_share  | Market share        |

Golden tables are used directly in Power BI and ML pipelines.

## 9. Data Visualization (Power BI)

Dashboards created from Golden datasets.

### Executive Dashboard

Metrics:

* Total prescriptions
* Market share
* Growth trends
* Territory performance

### Sales Dashboard

Insights:

* Top prescribers
* Prescriber growth
* Territory performance

### Market Intelligence Dashboard

Insights:

* Brand vs competitor share
* Launch performance
* Regional demand patterns

## 10. ML Serving Layer

Machine learning models analyze prescription trends.

Possible models:

### Demand Forecasting

Predict future prescriptions using time-series models.

Inputs:

* Historical TRx
* Market share
* Seasonality
* Territory adoption

Outputs:

* 30-day demand forecast
* Territory demand forecast

### Prescriber Propensity Model

Predict likelihood of an HCP prescribing a drug.

Features:

* Past prescription history
* Specialty
* Territory adoption
* Peer influence

Output:

Probability score per prescriber.

## 11. Data Governance and Compliance

Key governance elements:

* Data lineage tracking
* Role-based access control
* Audit logs
* Data catalog

Sensitive identifiers such as NPI must be handled with appropriate access restrictions.

## 12. Project Timeline

Estimated delivery timeline: **10 weeks**

| Phase                    | Duration |
| ------------------------ | -------- |
| Discovery and design     | 1 week   |
| Data ingestion pipelines | 2 weeks  |
| Bronze implementation    | 1 week   |
| Silver transformations   | 2 weeks  |
| Golden datasets          | 2 weeks  |
| Power BI dashboards      | 1 week   |
| ML models                | 1 week   |

## 13. Risks and Mitigation

### Data latency

Daily feeds may arrive late.

Mitigation:

Implement ingestion monitoring.

### Schema changes

IQVIA may change data schema.

Mitigation:

Schema validation checks.

### Data quality issues

Missing prescriber or drug mappings.

Mitigation:

Reference data validation.

## 14. Success Metrics

Project success measured by:

* Daily data refresh reliability > 99%
* Query response < 5 seconds in Power BI
* Accurate market share calculation
* Adoption by commercial analytics team

## 15. Items That Require Verification

The following require confirmation with IQVIA or internal teams:

* Exact schema of Xponent daily extracts
* Delivery format (CSV, SFTP, API)
* Availability of NRx vs TRx fields
* Territory mapping dataset format
* Refresh frequency (daily vs weekly)

These items cannot be verified without the specific client data contract.

## 16. Reasoning Summary

The project plan maps the Fabric pipeline architecture to a real pharmaceutical analytics workflow based on IQVIA Xponent prescription data. The pipeline transforms raw prescription data into curated analytical datasets supporting market share analysis, sales insights, and predictive analytics.

If needed, the next step can include:

* A **complete table schema for every Bronze, Silver, and Golden dataset**
* **Synthetic sample Xponent dataset generator (Python)**
* **Exact Fabric pipeline setup instructions matching your diagram**
* **Power BI dashboard wireframes**.
