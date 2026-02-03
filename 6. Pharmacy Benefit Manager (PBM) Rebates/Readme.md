# Project Bible

## Pharmacy Benefit Manager (PBM) Rebates Analytics Platform

### Snowflake-Based Enterprise Data Architecture

## Executive Summary

Pharmacy Benefit Managers (PBMs) sit at the financial and operational center of the U.S. prescription drug ecosystem. One of their most complex and least transparent functions is the administration of manufacturer rebates. Rebates are negotiated payments from pharmaceutical manufacturers to PBMs or plan sponsors in exchange for formulary placement or market share guarantees. While rebates are often positioned as a cost-containment mechanism, they introduce material complexity across contracting, adjudication, accounting, reporting, and compliance.

This Project Bible defines an enterprise-grade analytics and data platform for PBM rebate management, built on Snowflake. The platform is designed to provide a single source of truth for rebate eligibility, accruals, invoicing, collections, and downstream pass-through to clients. It emphasizes auditability, regulatory readiness, and financial accuracy while remaining scalable across millions of claims and thousands of contracts.

The document is written as if the platform were to be implemented by a real PBM or health benefits organization. Architectural decisions, modeling choices, and governance controls are explicitly justified, with trade-offs discussed. Assumptions are clearly labeled where real-world variability exists.

## Business Context and Problem Statement

### Industry Context

PBMs manage prescription drug benefits on behalf of health plans, employers, and government programs. Their core functions include formulary management, claims adjudication, pharmacy network management, and rebate negotiation.

Rebates represent a significant financial flow in this ecosystem. Depending on the therapeutic class and contract structure, rebates can exceed 30 percent of a drug’s list price. These funds may be retained partially by the PBM, passed through to plan sponsors, or shared according to contractual terms.

Despite their financial importance, rebate processes are often fragmented across systems. Contracting systems, claims engines, finance platforms, and client reporting tools frequently operate in silos. This fragmentation creates risk.

### Core Problems

The PBM rebate domain suffers from several structural issues:

First, rebate eligibility logic is complex and contract-specific. Eligibility may depend on drug identifiers, therapeutic classes, formulary tiers, market share thresholds, channel exclusions, and effective date ranges. These rules are rarely centralized.

Second, rebate calculations occur long after the original claim adjudication. Claims data is high volume and operationally optimized, while rebate calculations are analytical and retrospective. Bridging these worlds is non-trivial.

Third, financial reconciliation is difficult. Accrued rebates, invoiced amounts, collections, and client pass-throughs often diverge due to timing differences, disputes, restatements, or contract amendments.

Fourth, regulatory scrutiny is increasing. Clients, regulators, and auditors demand traceability from individual claims to rebate dollars. Many legacy systems cannot provide this lineage reliably.

### Problem Statement

The organization lacks a unified, auditable, and scalable data platform that can:

Explain how every rebate dollar was earned
Reconcile accruals, invoices, and cash
Support client-specific reporting and pass-through logic
Withstand financial audits and regulatory review

This project addresses that gap.

## Goals and Success Criteria

### Strategic Goals

The primary goal is to establish a Snowflake-based analytics platform that serves as the authoritative system for PBM rebate data.

The platform must align financial reporting, analytics, and operational insights without interfering with transactional systems.

### Success Criteria

Success is defined by measurable outcomes:

The platform can reproduce rebate financials reported to clients and manufacturers within acceptable tolerances.

Rebate calculations are explainable at the claim level, including eligibility rationale and applied rates.

Finance teams can reconcile accruals, invoices, and collections without manual spreadsheets.

Audit and compliance teams can trace reported values to source data with documented controls.

The architecture scales to support growth in claims volume, contracts, and client complexity.

## Stakeholders and Personas

### Executive Stakeholders

Executive leadership is concerned with financial accuracy, reputational risk, and regulatory exposure. They require confidence that rebate reporting is defensible and transparent.

### Finance and Accounting

Finance teams own accruals, revenue recognition, invoicing, and collections. They need consistent logic, period alignment, and clear reconciliation paths.

### Contracting and Rebate Operations

These teams manage manufacturer contracts and interpret rebate terms. They need visibility into how contract language translates into executable logic.

### Analytics and Reporting

Analysts build client reports, internal dashboards, and ad hoc analyses. They need curated, trustworthy datasets that abstract away raw complexity.

### Audit and Compliance

Audit teams require lineage, controls, and repeatability. They prioritize traceability over speed.

## Data Source Landscape

### Claims Adjudication Systems

Claims systems produce high-volume transactional data. Each record represents a dispensed prescription, including drug identifiers, quantities, pricing components, pharmacy identifiers, and member attributes.

These systems are optimized for speed and uptime, not analytics. Historical corrections and reversals are common.

### Contract Management Systems

Manufacturer rebate contracts are often stored in specialized systems or document repositories. Structured elements may exist, but many terms are semi-structured or interpreted manually.

### Pricing and Reference Data

Drug reference data such as NDC hierarchies, therapeutic classes, and brand-generic indicators are sourced from external vendors.

### Financial Systems

General ledger, accounts receivable, and cash application systems track financial outcomes but often lack claim-level detail.

### ASSUMPTION

This project assumes read-only access to source systems via batch extracts or CDC feeds. Real-time integration is out of scope.

## Architecture Overview

### Architectural Principles

The platform follows a layered warehouse architecture. Each layer has a clear purpose and contract.

Snowflake is selected for its separation of storage and compute, scalability, and native support for semi-structured data.

### High-Level Layers

Raw layer for immutable ingestion
Cleansed layer for standardized and validated data
Business layer for domain models
Analytics layer for consumption-ready datasets

This separation reduces coupling and improves auditability.

### Data Flow

Source data is ingested into Snowflake with minimal transformation. Subsequent layers apply deterministic, versioned logic.

All transformations are expressed as code, not manual processes.

## Data Modeling Strategy

### Modeling Philosophy

The rebate domain is both financial and contractual. A pure dimensional model is insufficient without domain context.

A hybrid approach is used:

Core facts are modeled dimensionally for performance and usability.

Contracts and eligibility logic are modeled as domain entities with temporal validity.

### Key Modeling Challenges

Many-to-many relationships between drugs and contracts
Time-bound eligibility
Retroactive adjustments

These are addressed through explicit bridge tables and effective dating.

## Core Domain Entities

### Claim

The claim is the atomic unit of rebate eligibility. Each claim record includes identifiers, pricing components, and timestamps.

Claims are immutable once loaded into the raw layer. Adjustments are represented as new records.

### Drug

Drugs are represented at multiple levels: NDC, brand, therapeutic class. Hierarchies are preserved to support contract logic.

### Contract

Contracts represent agreements with manufacturers. Each contract has effective dates, eligible drugs, rate structures, and performance clauses.

### Rebate Program

A rebate program is a logical construct that ties contracts to calculation logic. It allows reuse of logic across manufacturers.

## Data Engineering Pipelines

### Ingestion

Data is ingested using scheduled batch jobs. Files are landed in cloud storage and loaded into Snowflake stages.

Metadata such as load timestamps, source file names, and record counts are captured for audit purposes.

### Transformation

Transformations are implemented using SQL-based models orchestrated by a workflow tool.

Each model is idempotent and deterministic. Re-runs produce identical results given the same inputs.

### Incremental Processing

Claims data is processed incrementally based on service date and load date. Late-arriving data is handled via reprocessing windows.

Contracts are versioned. Historical calculations reference the contract version effective at the time of service.

## Rebate Calculation Logic

### Eligibility Determination

Eligibility is evaluated by joining claims to contract criteria:

Drug inclusion or exclusion
Date alignment
Channel and formulary conditions

Eligibility decisions are stored explicitly, not inferred downstream.

### Rate Application

Rates may be flat, tiered, or performance-based. The applied rate is stored alongside the claim.

This enables explanation of how each dollar was calculated.

### Accruals

Accruals are calculated monthly based on eligible claims. Accrual snapshots are preserved to support period reporting.

## Analytics and Metrics Framework

### Core Metrics

Total rebate eligible spend
Accrued rebate amount
Invoiced amount
Collected amount
Pass-through to clients

Each metric is defined once and reused.

### Dimensional Analysis

Metrics can be sliced by:

Client
Manufacturer
Drug
Therapeutic class
Time period

This supports both operational and executive reporting.

## BI and Consumption Layer

### Data Marts

Consumption-facing data marts abstract complex joins and calculations. They are designed for BI tools and ad hoc queries.

### Self-Service Enablement

Analysts are provided governed access to curated schemas. Raw layers are restricted.

## Governance, Security, and Compliance

### Access Control

Role-based access controls restrict sensitive financial data. Client-specific views enforce data isolation.

### Data Masking

Member identifiers and other PHI are masked or tokenized in analytical layers.

### Auditability

Every transformation is traceable. Source-to-report lineage is documented and queryable.

## Data Quality and Monitoring

### Quality Dimensions

Completeness
Accuracy
Timeliness
Consistency

Each dimension has defined checks.

### Monitoring

Automated checks validate row counts, key distributions, and financial totals. Exceptions trigger alerts.

## Performance and Cost Optimization

### Compute Strategy

Workloads are separated by warehouse. Heavy transformations do not compete with reporting queries.

### Storage Optimization

Clustering is applied to large fact tables based on access patterns.

## Testing and Deployment Strategy

### Testing Levels

Unit tests validate transformation logic. Reconciliation tests compare outputs to known financials.

### Deployment

Changes are version-controlled and promoted through environments.

## Risks, Assumptions, and Constraints

### Key Risks

Incomplete contract data
Late claim adjustments
Regulatory changes

Each risk has mitigation strategies.

### ASSUMPTIONS

Contract terms can be codified deterministically. Where ambiguity exists, business rules are documented.

## Roadmap and Future Enhancements

### Near-Term Enhancements

Automation of contract ingestion
Enhanced dispute tracking

### Long-Term Vision

Near real-time rebate visibility
Predictive analytics for rebate optimization

## Conclusion

PBM rebate management is a high-stakes, high-complexity domain where analytics platforms must balance flexibility with rigor. This Project Bible outlines a Snowflake-based architecture that treats rebate data as a financial asset requiring precision, transparency, and governance.

By centralizing logic, preserving lineage, and aligning stakeholders around a single source of truth, the platform enables the organization to move from reactive reconciliation to proactive insight. The result is not just better reporting, but increased trust in the numbers that underpin billions of dollars in drug spend.

## Verification and Uncertainty Notes

Certain industry practices and rebate structures vary significantly by organization and contract. Where specific implementations differ, assumptions have been explicitly labeled. Regulatory interpretations may evolve; governance and compliance sections should be reviewed periodically with legal and compliance teams.