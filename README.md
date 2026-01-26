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

**Which one of these sparks your interest for the next script?** I can build the "Messy Logic" for any of them.
