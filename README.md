# Healthcare-Projects

Here are **10 distinct healthcare/pharma dataset ideas** that move beyond standard Claims and EHR data. Each one is designed to solve a specific, high-value industry problem and includes "Messy Logic" to challenge your analytics skills.

### 1. Hospital Supply Chain & Inventory Management
**The Problem:** Hospitals waste billions on expired supplies or cancel surgeries because they ran out of a $50 screw.
*   **The Story:** You are the Supply Chain Director trying to optimize "Just-in-Time" ordering while preventing stockouts of critical life-saving items.
*   **The Schema:** `InventoryID`, `ItemName` (e.g., Stent, IV Bag), `BinLocation`, `ExpirationDate`, `ParLevel`, `CurrentStock`, `VendorID`, `CostPerUnit`.
*   **Messy Logic:**
    *   **Nurse Hoarding:** Specific departments show zero stock systematically because nurses hide supplies in their pockets/drawers fearing shortages.
    *   **The "Recall" Panic:** Randomly flag a specific batch of "Hip Implants" as recalled; you must identify every patient who received one.
    *   **Ghost Inventory:** The system says 10 units are there, but physical count is 0 (theft or shrinkage).

### 2. Emergency Room (ER) Throughput & Triage
**The Problem:** Overcrowding leads to patients "Leaving Without Being Seen" (LWBS), which is lost revenue and a lawsuit risk.
*   **The Story:** Analyze bottlenecks. Is it the Triage Nurse? The CT Scanner? Or lack of inpatient beds upstairs?
*   **The Schema:** `VisitID`, `ArrivalTimestamp`, `TriageLevel` (1-5), `Door_to_Doc_Time`, `Disposition` (Admit/Discharge), `Boarding_Hours`.
*   **Messy Logic:**
    *   **The "Frequent Flyer":** 5% of patients account for 50% of visits (homelessness/psych issues).
    *   **Ambulance Diversion:** On Friday nights, the ER gets saturated and has to turn away ambulances.
    *   **Shift Change Dip:** Wait times spike exactly at 7 AM and 7 PM (Shift change handoffs).

### 3. Precision Medicine & Genomics (Oncology)
**The Problem:** Moving from "Chemo for everyone" to "Targeted Gene Therapy."
*   **The Story:** Correlate specific gene mutations with drug survival rates to find the next "Blockbuster" indication.
*   **The Schema:** `PatientID`, `TumorType` (Lung, Breast), `Biomarkers` (BRCA1, KRAS, PD-L1), `TreatmentDrug`, `ProgressionFreeSurvival_Days`.
*   **Messy Logic:**
    *   **VUS (Variant of Unknown Significance):** Genetic tests often return results that doctors don't know how to interpret (Data ambiguity).
    *   **Resistant Mutations:** A patient responds well for 6 months, then develops a secondary mutation (T790M) and relapses.
    *   **Expensive Failures:** Patients with low PD-L1 expression are given expensive immunotherapy ($15k/month) but don't respond.

### 4. IoT & Remote Patient Monitoring (Wearables)
**The Problem:** Moving care from the hospital to the home using Apple Watches/Fitbits.
*   **The Story:** Detect Atrial Fibrillation (Heart issue) or Sleep Apnea before the patient has a stroke.
*   **The Schema:** `DeviceID`, `Timestamp` (Second-level), `HeartRate`, `O2Saturation`, `StepCount`, `SleepStage`, `BatteryLevel`.
*   **Messy Logic:**
    *   **Artifact Noise:** Heart rate spikes to 180bpm not because of a heart attack, but because the watch was loose while running.
    *   **Data Gaps:** Patient took the watch off to charge it and forgot to put it back on for 2 days.
    *   **False Alarms:** O2 Saturation drops to 80% (critical) but it's just a sensor error due to cold hands.

### 5. Nurse Staffing & Burnout (Workforce Analytics)
**The Problem:** Nursing turnover is the #1 cost for hospitals. Agency nurses cost 3x full-time staff.
*   **The Story:** Predict which units (ICU vs. MedSurg) are about to have a mass exodus of staff.
*   **The Schema:** `NurseID`, `ShiftDate`, `HoursWorked`, `Unit`, `Patient_to_Nurse_Ratio`, `Agency_Nurse_Flag`, `Overtime_Hours`.
*   **Messy Logic:**
    *   **The "Sunday Flu":** Call-outs spike on SuperBowl Sunday or holidays.
    *   **Burnout Cascade:** If the Ratio exceeds 1:6, the probability of that nurse quitting in the next 30 days doubles.
    *   **Premium Pay Wars:** Nurses quit to go to the hospital across the street for a $5/hr sign-on bonus.

### 6. Pharmacy Benefit Manager (PBM) Rebates
**The Problem:** The "Middleman" game. Why does Insulin cost $300?
*   **The Story:** Analyze the "Spread Pricing" between what the PBM charges the insurance and what they pay the pharmacy.
*   **The Schema:** `ClaimID`, `DrugNDC`, `WholesaleAcquisitionCost`, `PBM_Rebate_Amount`, `Patient_Copay`, `Pharmacy_Reimbursement`.
*   **Messy Logic:**
    *   **Rebate Walls:** A cheaper drug is denied coverage because the expensive drug offers the PBM a higher kickback (rebate).
    *   **Clawbacks:** The patient pays a $20 copay, but the drug only costs $5. The PBM "claws back" the $15 difference.
    *   **Formulary Exclusion:** Suddenly, a popular drug is removed from the approved list on Jan 1st.

### 7. Surgical Operating Room (OR) Utilization
**The Problem:** An OR minute costs ~$100. Empty rooms burn money.
*   **The Story:** Optimize the schedule. Surgeons always claim they need 2 hours but only take 45 mins (sandbagging).
*   **The Schema:** `CaseID`, `SurgeonID`, `ScheduledStart`, `ActualStart`, `WheelsIn`, `WheelsOut`, `TurnoverTime`, `ProcedureType`.
*   **Messy Logic:**
    *   **First Case Starts:** If the 7:00 AM case starts late, the whole day is delayed. (Surgeon was late vs. Anesthesia delay).
    *   **Add-on Chaos:** An emergency trauma case bumps all scheduled elective surgeries (Revenue loss).
    *   **Block Utilization:** Dr. Smith "owns" the OR on Tuesdays but only uses 40% of the time. Politics prevents taking it away.

### 8. Call Center & Patient Access
**The Problem:** "Press 1 for Appointments." (Wait time: 45 minutes). Patients hang up and go elsewhere.
*   **The Story:** Analyze call center logs to reduce abandonment rates and improve "First Call Resolution."
*   **The Schema:** `CallID`, `CallerPhone`, `QueueName` (Billing vs Clinical), `WaitTime`, `TalkTime`, `Abandon_Flag`, `Sentiment_Score`.
*   **Messy Logic:**
    *   **The "Death Spiral":** On Monday mornings, wait times hit 30 mins, abandonment hits 50%.
    *   **Agent Cherry Picking:** Agents hang up on difficult calls to keep their "Average Handle Time" low.
    *   **IVR Hell:** Patients loop in the automated menu for 5 minutes before reaching a human.

### 9. Clinical Trial Site Feasibility
**The Problem:** Pharma companies pick hospital sites to run trials, but 50% of sites fail to recruit a single patient.
*   **The Story:** Predict which hospitals will actually find patients for a rare disease study.
*   **The Schema:** `SiteID`, `PrincipalInvestigator`, `TherapeuticArea`, `TargetRecruitment`, `ActualRecruitment`, `IRB_Approval_Time`, `Protocol_Deviations`.
*   **Messy Logic:**
    *   **The Optimist PI:** Dr. Jones promises 50 patients but enrolls 2.
    *   **Geographic Bias:** Sites in rural areas fail to recruit because patients can't travel for weekly visits.
    *   **Protocol Deviations:** A site enrolls ineligible patients, ruining the data integrity.

### 10. Social Determinants of Health (Population Health)
**The Problem:** Your zip code is a better predictor of health than your genetic code.
*   **The Story:** Map "Food Deserts" and "Transportation Barriers" to Hospital Readmission rates.
*   **The Schema:** `ZipCode`, `DiabetesRate`, `MedianIncome`, `DistanceToGrocery`, `PublicTransitScore`, `FastFoodDensity`, `ER_Utilization_Rate`.
*   **Messy Logic:**
    *   **The "Amazon Effect":** Rural areas with high Amazon delivery usage have better medication adherence (mail order) than urban food deserts.
    *   **Heat Wave Spikes:** Low-income areas with poor AC see spikes in ER visits during summer.
    *   **Gentrification:** A zip code's income rises, but the health outcomes lag behind by 5 years.

Here are 10 high-value, distinct healthcare/pharma dataset ideas. These cover the full spectrum from **Factory Floor (Pharma)** to **Hospital Bed (Operations)** to **Patient Home (IoT)**.

Any of these would make for a portfolio-level project.

### 1. Pharma Supply Chain (Cold Chain Logistics)
*   **The Scenario:** You are moving \$50,000 vials of a temperature-sensitive cancer drug (Biologic) from a factory in Ireland to a hospital in Chicago.
*   **The Data:** IoT sensor readings (Time, GPS, Temperature, Humidity, Shock/Vibration).
*   **The "Messy" Logic:**
    *   **Temperature Excursions:** The drug must stay between 2°C and 8°C. Create spikes where it sat on a hot tarmac in Dubai (15 minutes at 30°C). Is the drug spoiled?
    *   **Customs Delays:** Packages stuck in FDA clearance for 4 days (timestamp gaps).
*   **The Insight:** "We lost \$4M in inventory last year because Carrier B lets packages sit in the sun at JFK airport."

### 2. Emergency Department (ED) Throughput & Triage
*   **The Scenario:** An overcrowded ER trying to balance heart attacks vs. stubbed toes.
*   **The Data:** Arrival Time, Triage Acuity (1-5), Time to Doctor, Lab Turnaround Time, Disposition (Admit/Discharge), "Left Without Being Seen" (LWBS).
*   **The "Messy" Logic:**
    *   **Bed Block:** Patients admitted to the hospital but stuck in the ER hallway for 12 hours because the ICU is full.
    *   **Shift Change Slump:** Wait times spike at 7 AM/7 PM during nurse handoffs.
*   **The Insight:** "Our LWBS rate hits 15% on Mondays at 6 PM. We are losing revenue because patients leave before seeing a doctor."

### 3. Oncology Genomics & Precision Medicine
*   **The Scenario:** Analyzing why a drug works for Patient A but fails for Patient B based on their DNA.
*   **The Data:** PatientID, Tumor Type, Genetic Mutations (BRCA1, EGFR, KRAS), Drug Treatment, Survival Months, Tumor Shrinkage %.
*   **The "Messy" Logic:**
    *   **Variant of Unknown Significance (VUS):** Genetic mutations that we don't know if they are harmful or benign.
    *   **Drug Resistance:** The tumor shrinks for 6 months, then mutates (T790M mutation) and grows again.
*   **The Insight:** "Patients with the KRAS G12C mutation respond 40% better to Drug X than Drug Y."

### 4. Nurse Staffing & Patient Acuity (Workforce Mgmt)
*   **The Scenario:** Preventing nurse burnout while managing budget.
*   **The Data:** Shift Roster, Nurse Certification (RN, LPN, CNA), Patient Acuity Score (How sick they are), Nurse-to-Patient Ratio, Overtime Hours.
*   **The "Messy" Logic:**
    *   **The "Call-Out" Cascade:** One nurse calls in sick, forcing three others into mandatory overtime.
    *   **Skill Mismatch:** An ICU patient is placed in a General Ward because of overcrowding, requiring a nurse who isn't certified for that equipment.
*   **The Insight:** "Burnout turnover costs us \$2M/year. It correlates directly with weeks where the Nurse-to-Patient ratio exceeds 1:5."

### 5. Medical Device Predictive Maintenance (IoT)
*   **The Scenario:** Keeping MRI and CT scanners running. If they break, the hospital loses \$10k/hour.
*   **The Data:** MachineID, Helium Levels, Coil Temperature, Scan Count, Error Logs, Maintenance Dates.
*   **The "Messy" Logic:**
    *   **Intermittent Failures:** The machine throws an "Error 404" only on Tuesdays (when the cleaning crew plugs in a vacuum to the same circuit).
    *   **Utilization Abuse:** Radiologists running the machine at 110% speed, causing overheating.
*   **The Insight:** "We can predict MRI coil failure 48 hours in advance by monitoring helium decay rates, saving \$50k in emergency repairs."

### 6. Pharmacy Benefit Manager (PBM) "Spread Pricing"
*   **The Scenario:** The shady middleman world of drug pricing.
*   **The Data:** Drug NDC, PharmacyID, PayerID, WAC (Wholesale Cost), AWP (Average Wholesale Price), Amount Insurance Paid, Amount Pharmacy Received, Rebate Amount.
*   **The "Messy" Logic:**
    *   **The Spread:** PBM charges the employer \$100 for a pill, pays the pharmacy \$10, and keeps \$90.
    *   **Clawbacks:** PBM takes money *back* from the pharmacy months later.
*   **The Insight:** "The PBM is retaining 40% of the spread on Generic Lipitor, while our pharmacy is dispensing it at a loss."

### 7. Opioid Stewardship & Controlled Substance Monitoring
*   **The Scenario:** Detecting "Doctor Shoppers" and "Pill Mills" to comply with DEA regulations.
*   **The Data:** PrescriberID, PatientID, Pharmacy Location, Drug Schedule (II, III, IV), Morphine Milligram Equivalents (MME), Distance Traveled.
*   **The "Messy" Logic:**
    *   **Doctor Shopping:** A patient visits 5 doctors in 5 different zip codes in 10 days.
    *   **The "Trinity" Cocktail:** Flagging prescriptions where Opioids, Benzos, and Muscle Relaxers are prescribed together (highly dangerous).
*   **The Insight:** "Provider X prescribes 5x the state average of Oxycodone, and 80% of his patients travel >50 miles to see him. Flag for fraud."

### 8. Clinical Text NLP (Sentiment & Symptom Extraction)
*   **The Scenario:** Analyzing unstructured doctor notes and patient reviews.
*   **The Data:** Telehealth Chat Logs, Doctor Discharge Summaries (Free text), Patient Satisfaction Surveys (Free text).
*   **The "Messy" Logic:**
    *   **Negation:** "Patient denies chest pain" (NLP often mistakenly tags this as "Has chest pain").
    *   **Abbreviations:** "Pt c/o SOB" (Patient complains of Shortness of Breath).
*   **The Insight:** "Sentiment analysis shows that 'Wait Time' and 'Parking' are the biggest drivers of negative reviews, not 'Clinical Care'."

### 9. Readmissions & Population Health (Geo-Spatial)
*   **The Scenario:** Why do patients keep coming back to the hospital?
*   **The Data:** Zip Code, Income Level, Distance to Grocery Store (Food Desert), Pollution Index (PM2.5), Readmission Date, Diagnosis.
*   **The "Messy" Logic:**
    *   **The "Frequent Flyer":** 5% of patients account for 50% of costs due to homelessness/social issues.
    *   **Medication Non-Adherence:** Patients from Zip Code 90210 pick up meds 95% of the time; Zip Code 90211 only 40% (cost barrier).
*   **The Insight:** "Our highest readmission rates for Asthma come from Zip Codes located within 1 mile of the highway (pollution) and >5 miles from a pharmacy."

### 10. Call Center & Triage Operations
*   **The Scenario:** A Telehealth nurse line trying to route patients correctly.
*   **The Data:** Call Timestamp, Hold Time, Abandonment Rate, Symptom Category, Disposition (Home Care vs. ER vs. Urgent Care), Caller Anxiety Score.
*   **The "Messy" Logic:**
    *   **The Monday Morning Rush:** Call volume explodes at 8:00 AM Monday.
    *   **Over-Triage:** Risk-averse nurses sending "Sore Throat" to the ER (waste of money) vs. Under-Triage (sending "Chest Pain" to Urgent Care).
*   **The Insight:** "When hold times exceed 5 minutes, 20% of callers hang up. Historical data suggests 5% of those hang-ups were likely heart attacks."

---

**Which one sparks your interest?** I can build the same level of depth (Python script + Messy Logic) for any of these.

*   **Option 1 (Supply Chain)** is great for **Logistics/IoT** visualization.
*   **Option 2 (ER Data)** is a classic **Operations/Queue Theory** problem.
*   **Option 3 (Genomics)** is amazing for **Data Science/Bioinformatics**.
