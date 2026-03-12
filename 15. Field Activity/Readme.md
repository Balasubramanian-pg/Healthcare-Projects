# Netflix-Style Recommendation Engine for Pharma Sales Reps Using IQVIA Xponent Data

## 1. Project Overview

This project builds a **prescriber recommendation engine** that suggests which healthcare professionals (HCPs) a pharmaceutical sales representative should visit next. The system analyzes prescription behavior from **IQVIA Xponent data**, historical engagement activity, and geographic constraints to produce ranked recommendations for each sales rep.

Conceptually it mirrors how Netflix recommends movies. Instead of recommending films to viewers, the system recommends **high-impact doctors to sales representatives**.

Outcome:
Each rep receives a prioritized list of physicians likely to increase prescriptions if engaged.

Prescription data platforms such as IQVIA Xponent estimate prescribing behavior from pharmacy dispensing data and are widely used for commercial pharmaceutical analytics.

---

# 2. Core Business Problem

Sales teams must decide:

* Which doctors to visit
* When to visit them
* Which product to discuss

Traditionally this is done using static reports.

A recommendation engine improves this by predicting:

* Which physicians are **most likely to prescribe**
* Which prescribers are **about to adopt**
* Which doctors are **declining competitors**

The system then generates **daily visit recommendations**.

---

# 3. What the System Recommends

For every sales representative:

Example output:

| Rank | Physician | Opportunity Score | Reason                   |
| ---- | --------- | ----------------- | ------------------------ |
| 1    | Dr. Patel | 0.91              | Rapid competitor growth  |
| 2    | Dr. Chen  | 0.88              | High TRx potential       |
| 3    | Dr. Singh | 0.82              | New prescriber candidate |

These recommendations are updated daily after the new Xponent data arrives.

---

# 4. End-to-End Architecture

The system uses the Fabric pipeline structure from the diagram.

## Data Flow

High Volume Data → Bronze → Silver → Golden → ML Model → Recommendation Output

---

# 5. Data Sources

### High-Volume Data

| Dataset           | Description            |
| ----------------- | ---------------------- |
| Xponent TRx       | Total prescriptions    |
| Xponent NRx       | New prescriptions      |
| Pharmacy data     | Dispensing information |
| Territory mapping | Rep assignment         |

Typical scale:

* Millions of rows per day

---

### Low-Volume Reference Data

| Dataset                  | Description          |
| ------------------------ | -------------------- |
| HCP master               | Physician attributes |
| Drug master              | Drug classification  |
| Territory hierarchy      | Sales regions        |
| Specialty classification | HCP specialties      |

---

# 6. Bronze Layer

Stores raw data.

Tables:

* bronze_xponent_rx
* bronze_hcp_master
* bronze_drug_master
* bronze_territory

Example schema:

| Column      | Description           |
| ----------- | --------------------- |
| rx_date     | Prescription date     |
| npi         | Prescriber identifier |
| ndc         | Drug code             |
| trx         | Total prescriptions   |
| nrx         | New prescriptions     |
| pharmacy_id | Pharmacy identifier   |

No transformations occur here.

---

# 7. Silver Layer

Curated data.

Transformations:

* Join drug master
* Map prescriber specialties
* Attach geographic attributes
* Remove duplicates

Example dataset:

silver_prescriptions

| Column       | Description         |
| ------------ | ------------------- |
| rx_date      | Date                |
| brand        | Drug name           |
| npi          | Prescriber          |
| trx          | Prescriptions       |
| specialty    | Physician specialty |
| territory_id | Sales territory     |

---

# 8. Golden Layer

Feature engineering happens here.

Golden datasets power the ML model.

Key tables:

| Table                    | Purpose                        |
| ------------------------ | ------------------------------ |
| golden_hcp_features      | Physician behavioral features  |
| golden_territory_metrics | Territory prescription metrics |
| golden_competitor_share  | Competitor share trends        |

Example engineered features:

| Feature          | Description                      |
| ---------------- | -------------------------------- |
| rx_growth_4w     | Prescription growth over 4 weeks |
| competitor_share | Competitor share percentage      |
| adoption_score   | New therapy adoption likelihood  |
| specialty_weight | Specialty influence              |

---

# 9. Feature Engineering

The system generates predictive variables.

### Prescriber Behavior Features

Examples:

* 4-week prescription trend
* 12-week growth
* competitor share
* brand loyalty

Example calculation:

```
rx_growth = (current_4w_rx - previous_4w_rx) / previous_4w_rx
```

---

### Territory Features

Examples:

* territory adoption rate
* competitor penetration
* territory growth

---

### Peer Influence

Doctors are influenced by nearby prescribers.

Feature:

```
peer_rx_avg
```

Average prescriptions among nearby doctors.

---

# 10. Machine Learning Model

The model predicts:

Probability a physician will prescribe the drug after engagement.

Model types commonly used:

* Gradient Boosted Trees
* XGBoost
* Random Forest

Example prediction output:

| Physician | Probability |
| --------- | ----------- |
| Dr. Patel | 0.91        |
| Dr. Singh | 0.83        |
| Dr. Chen  | 0.79        |

---

# 11. Ranking Algorithm

Final recommendation score combines multiple signals.

Example scoring formula:

```
opportunity_score =
0.4 * predicted_probability +
0.3 * rx_growth +
0.2 * competitor_share +
0.1 * territory_priority
```

Physicians are ranked by score.

---

# 12. Recommendation Output

The system generates a table:

golden_rep_recommendations

| rep_id | physician | opportunity_score | recommendation_rank |
| ------ | --------- | ----------------- | ------------------- |
| R102   | Dr. Patel | 0.91              | 1                   |
| R102   | Dr. Chen  | 0.88              | 2                   |
| R102   | Dr. Singh | 0.84              | 3                   |

Each rep receives a list of recommended physicians.

---

# 13. Power BI Dashboard

Sales teams see:

## Rep Recommendation Dashboard

Shows:

* Top physicians to visit
* Opportunity score
* Territory performance

---

## Territory Opportunity Dashboard

Shows:

* highest growth territories
* competitor threat regions
* new adoption clusters

---

## Prescriber Intelligence Dashboard

Shows:

* new adopters
* declining prescribers
* competitor loyalists

---

# 14. ML Serving

Daily scoring pipeline.

Steps:

1. New Xponent data arrives
2. Feature tables update
3. Model scores physicians
4. Recommendation table updates

The model runs daily.

---

# 15. Engineering Challenges

### Data Volume

Millions of prescriptions daily require:

* partitioned storage
* distributed transformations
* incremental updates

---

### Feature Computation

Rolling windows require optimized aggregations.

Example:

* 4-week moving averages
* 12-week trends

---

### Cold Start Problem

New physicians lack historical data.

Solution:

Use specialty averages.

---

# 16. Project Timeline

Estimated timeline:

| Phase                    | Duration |
| ------------------------ | -------- |
| Architecture and design  | 1 week   |
| Data ingestion pipelines | 2 weeks  |
| Bronze and Silver layers | 2 weeks  |
| Golden feature tables    | 2 weeks  |
| ML model training        | 1 week   |
| Recommendation engine    | 1 week   |
| Dashboards               | 1 week   |

Total:

10 weeks.

---

# 17. Why This Project Is Impressive

It demonstrates:

* large scale data engineering
* ML pipelines
* domain knowledge in pharma
* business impact

You are effectively building a **commercial intelligence platform**.

---

# 18. Items That Require Verification

These depend on the actual dataset license:

* Exact IQVIA Xponent schema
* Availability of prescriber identifiers
* Territory assignment format
* Daily file delivery method
* Geographic granularity

These elements vary between implementations and cannot be verified without access to the specific dataset.

---

# 19. Reasoning Summary

The recommendation engine uses prescription data to estimate physician prescribing behavior and prioritize engagement opportunities. By combining behavioral features, territory metrics, and predictive models, the system produces ranked visit recommendations for sales representatives.

---

If you want, the next step can be creating:

1. **Full SQL schema for all Bronze, Silver, and Golden tables**
2. **Feature engineering SQL scripts**
3. **ML training pipeline in Python**
4. **Synthetic IQVIA Xponent dataset generator**
5. **Exact Microsoft Fabric pipeline configuration**

This would make the project completely buildable end to end.
