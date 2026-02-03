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

### 11. Pharma Supply Chain (Cold Chain Logistics)
*   **The Scenario:** You are moving \$50,000 vials of a temperature-sensitive cancer drug (Biologic) from a factory in Ireland to a hospital in Chicago.
*   **The Data:** IoT sensor readings (Time, GPS, Temperature, Humidity, Shock/Vibration).
*   **The "Messy" Logic:**
    *   **Temperature Excursions:** The drug must stay between 2°C and 8°C. Create spikes where it sat on a hot tarmac in Dubai (15 minutes at 30°C). Is the drug spoiled?
    *   **Customs Delays:** Packages stuck in FDA clearance for 4 days (timestamp gaps).
*   **The Insight:** "We lost \$4M in inventory last year because Carrier B lets packages sit in the sun at JFK airport."

### 12. Emergency Department (ED) Throughput & Triage
*   **The Scenario:** An overcrowded ER trying to balance heart attacks vs. stubbed toes.
*   **The Data:** Arrival Time, Triage Acuity (1-5), Time to Doctor, Lab Turnaround Time, Disposition (Admit/Discharge), "Left Without Being Seen" (LWBS).
*   **The "Messy" Logic:**
    *   **Bed Block:** Patients admitted to the hospital but stuck in the ER hallway for 12 hours because the ICU is full.
    *   **Shift Change Slump:** Wait times spike at 7 AM/7 PM during nurse handoffs.
*   **The Insight:** "Our LWBS rate hits 15% on Mondays at 6 PM. We are losing revenue because patients leave before seeing a doctor."

### 13. Oncology Genomics & Precision Medicine
*   **The Scenario:** Analyzing why a drug works for Patient A but fails for Patient B based on their DNA.
*   **The Data:** PatientID, Tumor Type, Genetic Mutations (BRCA1, EGFR, KRAS), Drug Treatment, Survival Months, Tumor Shrinkage %.
*   **The "Messy" Logic:**
    *   **Variant of Unknown Significance (VUS):** Genetic mutations that we don't know if they are harmful or benign.
    *   **Drug Resistance:** The tumor shrinks for 6 months, then mutates (T790M mutation) and grows again.
*   **The Insight:** "Patients with the KRAS G12C mutation respond 40% better to Drug X than Drug Y."

### 14. Nurse Staffing & Patient Acuity (Workforce Mgmt)
*   **The Scenario:** Preventing nurse burnout while managing budget.
*   **The Data:** Shift Roster, Nurse Certification (RN, LPN, CNA), Patient Acuity Score (How sick they are), Nurse-to-Patient Ratio, Overtime Hours.
*   **The "Messy" Logic:**
    *   **The "Call-Out" Cascade:** One nurse calls in sick, forcing three others into mandatory overtime.
    *   **Skill Mismatch:** An ICU patient is placed in a General Ward because of overcrowding, requiring a nurse who isn't certified for that equipment.
*   **The Insight:** "Burnout turnover costs us \$2M/year. It correlates directly with weeks where the Nurse-to-Patient ratio exceeds 1:5."

### 15. Medical Device Predictive Maintenance (IoT)
*   **The Scenario:** Keeping MRI and CT scanners running. If they break, the hospital loses \$10k/hour.
*   **The Data:** MachineID, Helium Levels, Coil Temperature, Scan Count, Error Logs, Maintenance Dates.
*   **The "Messy" Logic:**
    *   **Intermittent Failures:** The machine throws an "Error 404" only on Tuesdays (when the cleaning crew plugs in a vacuum to the same circuit).
    *   **Utilization Abuse:** Radiologists running the machine at 110% speed, causing overheating.
*   **The Insight:** "We can predict MRI coil failure 48 hours in advance by monitoring helium decay rates, saving \$50k in emergency repairs."

### 16. Pharmacy Benefit Manager (PBM) "Spread Pricing"
*   **The Scenario:** The shady middleman world of drug pricing.
*   **The Data:** Drug NDC, PharmacyID, PayerID, WAC (Wholesale Cost), AWP (Average Wholesale Price), Amount Insurance Paid, Amount Pharmacy Received, Rebate Amount.
*   **The "Messy" Logic:**
    *   **The Spread:** PBM charges the employer \$100 for a pill, pays the pharmacy \$10, and keeps \$90.
    *   **Clawbacks:** PBM takes money *back* from the pharmacy months later.
*   **The Insight:** "The PBM is retaining 40% of the spread on Generic Lipitor, while our pharmacy is dispensing it at a loss."

### 17. Opioid Stewardship & Controlled Substance Monitoring
*   **The Scenario:** Detecting "Doctor Shoppers" and "Pill Mills" to comply with DEA regulations.
*   **The Data:** PrescriberID, PatientID, Pharmacy Location, Drug Schedule (II, III, IV), Morphine Milligram Equivalents (MME), Distance Traveled.
*   **The "Messy" Logic:**
    *   **Doctor Shopping:** A patient visits 5 doctors in 5 different zip codes in 10 days.
    *   **The "Trinity" Cocktail:** Flagging prescriptions where Opioids, Benzos, and Muscle Relaxers are prescribed together (highly dangerous).
*   **The Insight:** "Provider X prescribes 5x the state average of Oxycodone, and 80% of his patients travel >50 miles to see him. Flag for fraud."

### 18. Clinical Text NLP (Sentiment & Symptom Extraction)
*   **The Scenario:** Analyzing unstructured doctor notes and patient reviews.
*   **The Data:** Telehealth Chat Logs, Doctor Discharge Summaries (Free text), Patient Satisfaction Surveys (Free text).
*   **The "Messy" Logic:**
    *   **Negation:** "Patient denies chest pain" (NLP often mistakenly tags this as "Has chest pain").
    *   **Abbreviations:** "Pt c/o SOB" (Patient complains of Shortness of Breath).
*   **The Insight:** "Sentiment analysis shows that 'Wait Time' and 'Parking' are the biggest drivers of negative reviews, not 'Clinical Care'."

### 19. Readmissions & Population Health (Geo-Spatial)
*   **The Scenario:** Why do patients keep coming back to the hospital?
*   **The Data:** Zip Code, Income Level, Distance to Grocery Store (Food Desert), Pollution Index (PM2.5), Readmission Date, Diagnosis.
*   **The "Messy" Logic:**
    *   **The "Frequent Flyer":** 5% of patients account for 50% of costs due to homelessness/social issues.
    *   **Medication Non-Adherence:** Patients from Zip Code 90210 pick up meds 95% of the time; Zip Code 90211 only 40% (cost barrier).
*   **The Insight:** "Our highest readmission rates for Asthma come from Zip Codes located within 1 mile of the highway (pollution) and >5 miles from a pharmacy."

### 20. Call Center & Triage Operations
*   **The Scenario:** A Telehealth nurse line trying to route patients correctly.
*   **The Data:** Call Timestamp, Hold Time, Abandonment Rate, Symptom Category, Disposition (Home Care vs. ER vs. Urgent Care), Caller Anxiety Score.
*   **The "Messy" Logic:**
    *   **The Monday Morning Rush:** Call volume explodes at 8:00 AM Monday.
    *   **Over-Triage:** Risk-averse nurses sending "Sore Throat" to the ER (waste of money) vs. Under-Triage (sending "Chest Pain" to Urgent Care).
*   **The Insight:** "When hold times exceed 5 minutes, 20% of callers hang up. Historical data suggests 5% of those hang-ups were likely heart attacks."


Here are **5 Unique, Advanced Dataset Ideas** specifically designed to flex **SQL Window Functions**, **Complex Joins**, and **Power BI Storytelling**.

These move away from standard "Patient/Doctor" data into the high-pressure niches of healthcare operations.



### 1. The "Operating Room (OR) Tetris" Dataset
**The Domain:** Surgical Services (The most profitable department in a hospital).
**The Story:** The OR is a factory. Every minute an OR sits empty during the day costs the hospital $100. Your job is to analyze **"Block Utilization"** and **"Turnover Time."**

*   **The Schema:**
    *   `Fact_Surgeries`: CaseID, SurgeonID, RoomID, ScheduledStart, ScheduledEnd, **WheelsIn** (Patient enters), **CutTime** (Scalpel hits skin), **CloseTime** (Stitching), **WheelsOut** (Patient leaves).
    *   `Dim_OR_Rooms`: RoomID, Equipment (Robot, C-Arm), BlockOwner (e.g., "Orthopedics Team gets Mondays").
*   **The SQL Challenge:**
    *   Calculate **First Case On-Time Starts (FCOTS)**: Did the 7:30 AM surgery actually start at 7:30?
    *   Calculate **Turnover Time**: The gap between *Case A WheelsOut* and *Case B WheelsIn*.
    *   **Gap Analysis:** Find gaps > 60 minutes where no surgery happened (Wasted Block Time).
*   **The Power BI Challenge:**
    *   **Gantt Chart Visual:** Show the actual surgery bars vs. the scheduled bars.
    *   **Heatmap:** Room Utilization by Day of Week and Hour of Day.
    *   **Drill-Through:** Click a "Red" utilization room to see which Surgeon is constantly late.

### 2. The "Cold Chain" Vaccine Logistics Dataset
**The Domain:** Pharma Supply Chain / IoT.
**The Story:** You are shipping temperature-sensitive biologics (like Covid vaccines or Insulin) from the Factory to the Pharmacy. If the temp goes above 8°C for more than 60 minutes, the batch is ruined.

*   **The Schema:**
    *   `Fact_Shipments`: ShipmentID, RouteID, DepartureTime, ArrivalTime, DrugID.
    *   `Fact_Sensor_Logs`: ShipmentID, Timestamp (every 15 mins), Temperature, Humidity, Shock (G-Force), GPS_Lat, GPS_Long.
    *   `Dim_Excursion_Rules`: DrugID, MinTemp, MaxTemp, MaxAllowedExcursionTime.
*   **The SQL Challenge:**
    *   **Islands & Gaps (Gaps and Islands problem):** Identify continuous periods where temp was > MaxTemp.
    *   Calculate **Total Cumulative Excursion Time** per shipment.
    *   Determine which shipments must be destroyed (Status = 'Spoiled').
*   **The Power BI Challenge:**
    *   **Map Visual:** Plot the GPS path, coloring the line Green (Good) or Red (Spoiled) based on temp at that location.
    *   **Decomposition Tree:** Root cause analysis of spoilage (Is it a specific Route? A specific Trucking Company? A specific Time of Year?).

### 3. The "Bed Management (ADT)" Dataset
**The Domain:** Hospital Capacity Planning.
**The Story:** A hospital is like a hotel that you can't book in advance. You have ADT data (**A**dmission, **D**ischarge, **T**ransfer). You need to visualize the "Flow" and predict "Bed Crunch."

*   **The Schema:**
    *   `Fact_Patient_Movement`: EventID, VisitID, PatientID, FromUnit, ToUnit, EventTime, EventType (Admit, Transfer, Discharge).
    *   `Dim_Units`: UnitID, MaxCapacity, Floor, CareLevel (ICU, MedSurg, Rehab).
*   **The SQL Challenge:**
    *   **The "Census" Query:** It is complex to write a SQL query that says "How many people were in the ICU at exactly 11:00 PM last Tuesday?" (Requires recursive CTEs or complex interval logic).
    *   Calculate **LOS (Length of Stay)** per unit. (e.g., Patient was in ICU for 2 days, then MedSurg for 4 days).
*   **The Power BI Challenge:**
    *   **Sankey Diagram:** Visualize the flow of patients. (ER -> ICU -> Floor -> Home).
    *   **Pulse Chart:** Real-time visualization of bed occupancy vs. capacity.

### 4. The "Antibiotic Stewardship" (Antibiogram) Dataset
**The Domain:** Clinical Quality / Infection Control.
**The Story:** Doctors are prescribing antibiotics, but bacteria are becoming resistant ("Superbugs"). You need to track which bugs are resistant to which drugs at your hospital.

*   **The Schema:**
    *   `Fact_Microbiology_Results`: SpecimenID, PatientID, CollectionDate, BacteriaIdentified (e.g., E. Coli), Source (Blood, Urine).
    *   `Fact_Susceptibility`: SpecimenID, AntibioticName, Result (Sensitive, Resistant, Intermediate), MIC_Value (Minimum Inhibitory Concentration).
    *   `Fact_Prescriptions`: (Standard Rx table).
*   **The SQL Challenge:**
    *   **Mismatch Logic:** Find instances where the doctor prescribed "Ciprofloxacin" but the lab result later showed the bacteria was "Resistant" to Ciprofloxacin (Inappropriate Therapy).
    *   Calculate **Resistance Rates %** per bacteria per year.
*   **The Power BI Challenge:**
    *   **Matrix Heatmap (Antibiogram):** Rows = Bacteria, Cols = Antibiotics. Cells = % Sensitive. (Green = Good drug to use, Red = Don't use).
    *   **Trend Line:** Show the rise of MRSA (Methicillin-Resistant Staph Aureus) over 5 years.

### 5. The "EMS/Ambulance Response" Geospatial Dataset
**The Domain:** Pre-hospital Emergency Services.
**The Story:** Seconds save lives. You are analyzing the efficiency of the 911 ambulance fleet.

*   **The Schema:**
    *   `Fact_Incidents`: IncidentID, CallTime, DispatchTime, EnRouteTime, OnSceneTime, TransportStartTime, HospitalArrivalTime.
    *   `Dim_Stations`: StationID, Geo_Lat, Geo_Long, FleetSize.
    *   `Fact_GPS_Pings`: UnitID, Timestamp, Lat, Long, Speed, SirenStatus.
*   **The SQL Challenge:**
    *   Calculate **Chute Time** (Dispatch Time - Call Time) vs. **Travel Time** (On Scene - En Route).
    *   **Geospatial Distance:** Calculate the "Crow Flies" distance vs. Actual distance driven to check for inefficient routing.
    *   **Unit Utilization:** What % of the shift was the ambulance idle vs. on a call?
*   **The Power BI Challenge:**
    *   **Map with Heatmap Layer:** Hotspots for 911 calls (Where do accidents happen?).
    *   **Scatter Plot:** Distance (X-axis) vs. Response Time (Y-axis). Outliers indicate traffic issues or driver error.



### Which one should we choose?

*   **Option 1 (OR Tetris)** is the best for **Business ROI**. Every hospital CFO cares about this dashboard.
*   **Option 2 (Cold Chain)** is the best for **Modern Tech** (IoT/Sensors) and Pharma.
*   **Option 3 (Bed Mgmt)** is the hardest **SQL Challenge** (Time-series census is tricky).

Let me know which one you want, and I will generate the schema and the Python script!

Here are **10 more unique, high-level dataset ideas** that target specific niches in healthcare analytics. These are designed to be excellent portfolio pieces because they solve specific, expensive business problems.

### 1. Radiology Workflow & Turnaround Time (The "TAT" Dataset)
**The Domain:** Imaging / Diagnostics.
**The Story:** An ER doctor orders a CT scan for a stroke patient. Every minute of delay kills brain cells. You need to find the bottleneck: Is it the technician taking the image, or the radiologist reading it?
*   **The Schema:** `Fact_Exam_Timestamps` (OrderTime, ExamBegin, ExamEnd, ImageAvailable, RadiologistPickup, FinalReportSigned).
*   **SQL Challenge:** Calculating "interval deltas" (Time between Order and Begin, Time between ImageAvailable and Report). Handling business hours vs. nights/weekends logic.
*   **Power BI Challenge:** Box-and-Whisker plots to show outlier radiologists who take too long to read scans.

### 2. Home Health Routing & Mileage (The "Traveling Nurse" Dataset)
**The Domain:** Post-Acute Care / Logistics.
**The Story:** Nurses drive to patients' homes. You are paying thousands in mileage reimbursement and overtime. Are the routes optimized?
*   **The Schema:** `Fact_Visits` (NurseID, PatientID, Lat/Long, ScheduledTime, ActualArrivalTime, MilesDriven).
*   **SQL Challenge:** Geospatial clustering. Grouping patients by zip code to see if Nurse A drove past Patient B to get to Patient C (inefficiency).
*   **Power BI Challenge:** Map visualizations with route lines. Cost analysis of "Windshield Time" (Driving) vs. "Clinical Time" (Treating).

### 3. Sepsis Algorithm Performance (The "Model Audit" Dataset)
**The Domain:** Clinical Informatics / Data Science Ops.
**The Story:** The hospital installed an AI algorithm to predict Sepsis. Is it working? Or is it crying wolf (False Positives) causing doctors to ignore it?
*   **The Schema:** `Fact_Alerts` (PatientID, Timestamp, RiskScore), `Fact_Outcomes` (Did Patient actually have Sepsis? Yes/No, ICD-10 Code).
*   **SQL Challenge:** Building a **Confusion Matrix** in SQL. Calculating Sensitivity, Specificity, and Positive Predictive Value (PPV) by joining Alerts to Outcomes.
*   **Power BI Challenge:** A "Model Degradation" chart showing if the algorithm is getting worse over time.

### 4. 340B Drug Pricing & Compliance (The "Regulatory" Dataset)
**The Domain:** Pharmacy Finance (Huge niche in US Healthcare).
**The Story:** Hospitals buy drugs at a 50% discount (340B program) for low-income patients. If they give that discounted drug to an *ineligible* patient, they get fined millions.
*   **The Schema:** `Fact_Dispensing` (DrugNDC, PatientID), `Dim_Patient_Eligibility` (PayerStatus, IndigentFlag), `Fact_Purchases` (WAC_Price, 340B_Price).
*   **SQL Challenge:** Complex eligibility logic. Matching dispensing timestamps to patient visit timestamps to prove eligibility.
*   **Power BI Challenge:** "Savings Opportunity" waterfall chart. How much money did we save vs. potential savings lost due to bad data?

### 5. Hospital Dietary & Food Waste (The "Nutrition" Dataset)
**The Domain:** Support Services / Sustainability.
**The Story:** The kitchen makes 500 "Renal Diet" meals, but only 300 were ordered. Also, tracking patient nutrient intake vs. doctor orders.
*   **The Schema:** `Fact_Meal_Orders` (PatientID, DietType, Calories, Sodium), `Fact_Production` (MealsPrepared, MealsDiscarded, CostPerMeal).
*   **SQL Challenge:** Gap analysis between `Ordered_Diet` (Doctor's orders) and `Tray_Delivered` (Did the diabetic patient get a cake?).
*   **Power BI Challenge:** Waste reduction dashboard. Visualizing "Most Wasted Items" and cost impact.

### 6. HVAC & Infection Control (The "Facilities" Dataset)
**The Domain:** Engineering / Safety.
**The Story:** Operating Rooms and Isolation Rooms need specific air pressure (Positive/Negative) and Humidity. If humidity drops, static electricity can spark fires in oxygen-rich ORs.
*   **The Schema:** `Fact_Sensor_Readings` (RoomID, Timestamp_5min, PressureDifferential, Humidity, Temp).
*   **SQL Challenge:** Time-series "Islands and Gaps". Identifying continuous durations where a room was "Out of Spec" for > 30 minutes.
*   **Power BI Challenge:** Floorplan Heatmap. Coloring rooms Red/Green based on current air safety status.

### 7. Physical Therapy Recovery Curves (The "Rehab" Dataset)
**The Domain:** Clinical Outcomes.
**The Story:** Patient A and Patient B both have knee replacements. Patient A walks in 2 weeks; Patient B takes 6 weeks. Why?
*   **The Schema:** `Fact_Assessments` (PatientID, Date, FIM_Score - Functional Independence Measure, PainLevel).
*   **SQL Challenge:** Calculating the **Slope** of recovery (Rate of improvement) per patient. Ranking Therapists by their patients' recovery speed.
*   **Power BI Challenge:** "Recovery Trajectory" line charts. Comparing an individual patient against the "Average Recovery Curve."

### 8. Chargemaster (CDM) Price Transparency (The "Pricing" Dataset)
**The Domain:** Revenue Cycle / Compliance.
**The Story:** US Hospitals must publish their prices. You are comparing your hospital's prices against 3 competitors for "MRI Brain" and "C-Section".
*   **The Schema:** `Dim_CDM` (CPT_Code, Description, Gross_Charge, Cash_Price, Negotiated_Payer_A_Price, Negotiated_Payer_B_Price).
*   **SQL Challenge:** Fuzzy matching CPT codes or Descriptions across different hospital datasets (Data Cleaning nightmare).
*   **Power BI Challenge:** Competitive Benchmarking Radar Chart. "Are we the most expensive hospital in the city?"

### 9. Patient Transport Logistics (The "Porter" Dataset)
**The Domain:** Hospital Operations.
**The Story:** A patient is stuck in his room waiting for a wheelchair to go to Radiology. The MRI machine is empty waiting for the patient. The transporter is missing.
*   **The Schema:** `Fact_Transport_Jobs` (RequestTime, PickupTime, DropoffTime, Origin, Destination, TransporterID).
*   **SQL Challenge:** Calculating "Job Efficiency" and "Idle Time". Determining peak demand hours for wheelchairs.
*   **Power BI Challenge:** Staffing optimization. Histogram of transport requests by hour vs. Number of staff on shift.

### 10. Provider Credentialing & Expiry (The "HR Risk" Dataset)
**The Domain:** Medical Staff Office / HR.
**The Story:** If a doctor operates with an expired license, insurance won't pay and the hospital gets sued. You need to track thousands of expiration dates.
*   **The Schema:** `Dim_Provider` (ProviderID), `Fact_Credentials` (CredType: StateLicense, DEA, BoardCert, MalpracticeIns), `Date_Expires`.
*   **SQL Challenge:** Date logic. Identifying providers who expire in < 30, < 60, < 90 days. Handling "Grace Periods."
*   **Power BI Challenge:** "Compliance Risk Radar." A countdown dashboard showing exactly who needs to be suspended *tomorrow* if they don't renew.



### Which one fits your goals?

*   **For pure SQL Complexity:** #4 (**340B**) or #1 (**Radiology TAT**) involve difficult join logic and timestamps.
*   **For Visualization/Design:** #2 (**Home Health Map**) or #6 (**HVAC Floorplan**) are visually stunning.
*   **For Data Science/Stats:** #3 (**Sepsis Model**) or #7 (**Recovery Curves**) require statistical thinking.