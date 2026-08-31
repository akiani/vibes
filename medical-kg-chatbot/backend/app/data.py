"""The mock medical knowledge graph.

Everything the chatbot can possibly know lives in this file. It is deliberately
plain Python -- no database, no ORM, no graph engine -- so that the shape of the
data is obvious at a glance and easy to extend.

To add knowledge: append to NODES and/or EDGES. `graph.py` rebuilds its indices
from these two structures at import time, and `schema.py` exposes them over
GraphQL. Nothing else needs to change.

All data here is fictional and simplified for demonstration purposes.
"""

# --- Nodes -----------------------------------------------------------------
#
# Each node has an "id" and a "type". The remaining keys are the node's
# attributes and vary by type -- see schema.py for how they map to GraphQL.

NODES = [
    # --- Conditions --------------------------------------------------------
    {
        "id": "C_T2DM",
        "type": "Condition",
        "name": "Type 2 Diabetes Mellitus",
        "icd10": "E11",
        "category": "Endocrine",
        "description": "A chronic condition in which the body becomes resistant to insulin, leading to elevated blood glucose.",
    },
    {
        "id": "C_HTN",
        "type": "Condition",
        "name": "Essential Hypertension",
        "icd10": "I10",
        "category": "Cardiovascular",
        "description": "Persistently elevated arterial blood pressure with no identifiable secondary cause.",
    },
    {
        "id": "C_CKD3",
        "type": "Condition",
        "name": "Chronic Kidney Disease Stage 3",
        "icd10": "N18.3",
        "category": "Renal",
        "description": "Moderately reduced kidney function, with an eGFR between 30 and 59 mL/min/1.73m2.",
    },
    {
        "id": "C_AFIB",
        "type": "Condition",
        "name": "Atrial Fibrillation",
        "icd10": "I48",
        "category": "Cardiovascular",
        "description": "An irregular and often rapid heart rhythm that raises the risk of stroke.",
    },
    {
        "id": "C_ASTHMA",
        "type": "Condition",
        "name": "Asthma",
        "icd10": "J45",
        "category": "Respiratory",
        "description": "Chronic inflammation of the airways causing reversible airflow obstruction.",
    },
    {
        "id": "C_MIGRAINE",
        "type": "Condition",
        "name": "Migraine",
        "icd10": "G43",
        "category": "Neurological",
        "description": "Recurrent moderate-to-severe headache, often unilateral and accompanied by nausea or photophobia.",
    },
    {
        "id": "C_HYPOTHY",
        "type": "Condition",
        "name": "Hypothyroidism",
        "icd10": "E03",
        "category": "Endocrine",
        "description": "Underactive thyroid gland producing insufficient thyroid hormone.",
    },
    {
        "id": "C_CAP",
        "type": "Condition",
        "name": "Community-Acquired Pneumonia",
        "icd10": "J18",
        "category": "Respiratory",
        "description": "Infection of the lung parenchyma acquired outside of a hospital setting.",
    },

    # --- Symptoms ----------------------------------------------------------
    {"id": "S_POLYURIA", "type": "Symptom", "name": "Polyuria", "body_system": "Renal"},
    {"id": "S_POLYDIPSIA", "type": "Symptom", "name": "Excessive thirst", "body_system": "General"},
    {"id": "S_FATIGUE", "type": "Symptom", "name": "Fatigue", "body_system": "General"},
    {"id": "S_BLURRED", "type": "Symptom", "name": "Blurred vision", "body_system": "Ophthalmic"},
    {"id": "S_HEADACHE", "type": "Symptom", "name": "Headache", "body_system": "Neurological"},
    {"id": "S_PALPITATIONS", "type": "Symptom", "name": "Palpitations", "body_system": "Cardiovascular"},
    {"id": "S_DYSPNEA", "type": "Symptom", "name": "Shortness of breath", "body_system": "Respiratory"},
    {"id": "S_EDEMA", "type": "Symptom", "name": "Peripheral edema", "body_system": "Cardiovascular"},
    {"id": "S_WHEEZE", "type": "Symptom", "name": "Wheezing", "body_system": "Respiratory"},
    {"id": "S_COUGH", "type": "Symptom", "name": "Productive cough", "body_system": "Respiratory"},
    {"id": "S_FEVER", "type": "Symptom", "name": "Fever", "body_system": "General"},
    {"id": "S_PHOTOPHOBIA", "type": "Symptom", "name": "Photophobia", "body_system": "Neurological"},
    {"id": "S_COLDINTOL", "type": "Symptom", "name": "Cold intolerance", "body_system": "General"},
    {"id": "S_WEIGHTGAIN", "type": "Symptom", "name": "Weight gain", "body_system": "General"},

    # --- Medications -------------------------------------------------------
    {"id": "M_METFORMIN", "type": "Medication", "name": "Metformin", "drug_class": "Biguanide", "route": "Oral"},
    {"id": "M_LISINOPRIL", "type": "Medication", "name": "Lisinopril", "drug_class": "ACE inhibitor", "route": "Oral"},
    {"id": "M_AMLODIPINE", "type": "Medication", "name": "Amlodipine", "drug_class": "Calcium channel blocker", "route": "Oral"},
    {"id": "M_METOPROLOL", "type": "Medication", "name": "Metoprolol", "drug_class": "Beta blocker", "route": "Oral"},
    {"id": "M_WARFARIN", "type": "Medication", "name": "Warfarin", "drug_class": "Vitamin K antagonist", "route": "Oral"},
    {"id": "M_APIXABAN", "type": "Medication", "name": "Apixaban", "drug_class": "Direct factor Xa inhibitor", "route": "Oral"},
    {"id": "M_ATORVASTATIN", "type": "Medication", "name": "Atorvastatin", "drug_class": "Statin", "route": "Oral"},
    {"id": "M_LEVOTHYROXINE", "type": "Medication", "name": "Levothyroxine", "drug_class": "Thyroid hormone", "route": "Oral"},
    {"id": "M_ALBUTEROL", "type": "Medication", "name": "Albuterol", "drug_class": "Short-acting beta agonist", "route": "Inhaled"},
    {"id": "M_SUMATRIPTAN", "type": "Medication", "name": "Sumatriptan", "drug_class": "Triptan", "route": "Oral"},
    {"id": "M_AMOXICILLIN", "type": "Medication", "name": "Amoxicillin", "drug_class": "Aminopenicillin", "route": "Oral"},
    {"id": "M_IBUPROFEN", "type": "Medication", "name": "Ibuprofen", "drug_class": "NSAID", "route": "Oral"},

    # --- Lab tests ---------------------------------------------------------
    {"id": "L_HBA1C", "type": "LabTest", "name": "Hemoglobin A1c", "unit": "%", "reference_range": "4.0-5.6"},
    {"id": "L_FPG", "type": "LabTest", "name": "Fasting plasma glucose", "unit": "mg/dL", "reference_range": "70-99"},
    {"id": "L_EGFR", "type": "LabTest", "name": "Estimated GFR", "unit": "mL/min/1.73m2", "reference_range": "90-120"},
    {"id": "L_CREAT", "type": "LabTest", "name": "Serum creatinine", "unit": "mg/dL", "reference_range": "0.6-1.2"},
    {"id": "L_TSH", "type": "LabTest", "name": "Thyroid stimulating hormone", "unit": "mIU/L", "reference_range": "0.4-4.0"},
    {"id": "L_LIPID", "type": "LabTest", "name": "Lipid panel", "unit": "mg/dL", "reference_range": "LDL < 100"},
    {"id": "L_INR", "type": "LabTest", "name": "International normalized ratio", "unit": "ratio", "reference_range": "0.8-1.2 (2.0-3.0 on warfarin)"},
    {"id": "L_CXR", "type": "LabTest", "name": "Chest radiograph", "unit": "n/a", "reference_range": "No consolidation"},
    {"id": "L_ECG", "type": "LabTest", "name": "12-lead ECG", "unit": "n/a", "reference_range": "Normal sinus rhythm"},

    # --- Risk factors ------------------------------------------------------
    {"id": "R_OBESITY", "type": "RiskFactor", "name": "Obesity", "modifiable": True},
    {"id": "R_SMOKING", "type": "RiskFactor", "name": "Tobacco smoking", "modifiable": True},
    {"id": "R_SEDENTARY", "type": "RiskFactor", "name": "Sedentary lifestyle", "modifiable": True},
    {"id": "R_FAMHX", "type": "RiskFactor", "name": "Family history", "modifiable": False},
    {"id": "R_AGE", "type": "RiskFactor", "name": "Advanced age", "modifiable": False},
    {"id": "R_HIGHSODIUM", "type": "RiskFactor", "name": "High sodium diet", "modifiable": True},

    # --- Patients (fictional) ---------------------------------------------
    {"id": "P-001", "type": "Patient", "name": "Ada Whitfield", "age": 62, "sex": "female"},
    {"id": "P-002", "type": "Patient", "name": "Marcus Bell", "age": 71, "sex": "male"},
    {"id": "P-003", "type": "Patient", "name": "Priya Raman", "age": 34, "sex": "female"},
    {"id": "P-004", "type": "Patient", "name": "Tomas Lindqvist", "age": 58, "sex": "male"},
    {"id": "P-005", "type": "Patient", "name": "Grace Okonkwo", "age": 45, "sex": "female"},
]

# --- Edges -----------------------------------------------------------------
#
# A flat list of directed triples. INTERACTS_WITH is conceptually undirected --
# it is stored once here and symmetrised when the indices are built in graph.py,
# so the agent finds the interaction from either drug.

EDGES = [
    # Condition -> Symptom
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_POLYURIA"},
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_POLYDIPSIA"},
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_BLURRED"},
    {"src": "C_HTN", "rel": "PRESENTS_WITH", "dst": "S_HEADACHE"},
    {"src": "C_CKD3", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_CKD3", "rel": "PRESENTS_WITH", "dst": "S_EDEMA"},
    {"src": "C_AFIB", "rel": "PRESENTS_WITH", "dst": "S_PALPITATIONS"},
    {"src": "C_AFIB", "rel": "PRESENTS_WITH", "dst": "S_DYSPNEA"},
    {"src": "C_AFIB", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_ASTHMA", "rel": "PRESENTS_WITH", "dst": "S_WHEEZE"},
    {"src": "C_ASTHMA", "rel": "PRESENTS_WITH", "dst": "S_DYSPNEA"},
    {"src": "C_MIGRAINE", "rel": "PRESENTS_WITH", "dst": "S_HEADACHE"},
    {"src": "C_MIGRAINE", "rel": "PRESENTS_WITH", "dst": "S_PHOTOPHOBIA"},
    {"src": "C_HYPOTHY", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_HYPOTHY", "rel": "PRESENTS_WITH", "dst": "S_COLDINTOL"},
    {"src": "C_HYPOTHY", "rel": "PRESENTS_WITH", "dst": "S_WEIGHTGAIN"},
    {"src": "C_CAP", "rel": "PRESENTS_WITH", "dst": "S_COUGH"},
    {"src": "C_CAP", "rel": "PRESENTS_WITH", "dst": "S_FEVER"},
    {"src": "C_CAP", "rel": "PRESENTS_WITH", "dst": "S_DYSPNEA"},

    # Condition -> Medication
    {"src": "C_T2DM", "rel": "TREATED_BY", "dst": "M_METFORMIN"},
    {"src": "C_HTN", "rel": "TREATED_BY", "dst": "M_LISINOPRIL"},
    {"src": "C_HTN", "rel": "TREATED_BY", "dst": "M_AMLODIPINE"},
    {"src": "C_CKD3", "rel": "TREATED_BY", "dst": "M_LISINOPRIL"},
    {"src": "C_AFIB", "rel": "TREATED_BY", "dst": "M_METOPROLOL"},
    {"src": "C_AFIB", "rel": "TREATED_BY", "dst": "M_WARFARIN"},
    {"src": "C_AFIB", "rel": "TREATED_BY", "dst": "M_APIXABAN"},
    {"src": "C_ASTHMA", "rel": "TREATED_BY", "dst": "M_ALBUTEROL"},
    {"src": "C_MIGRAINE", "rel": "TREATED_BY", "dst": "M_SUMATRIPTAN"},
    {"src": "C_MIGRAINE", "rel": "TREATED_BY", "dst": "M_IBUPROFEN"},
    {"src": "C_HYPOTHY", "rel": "TREATED_BY", "dst": "M_LEVOTHYROXINE"},
    {"src": "C_CAP", "rel": "TREATED_BY", "dst": "M_AMOXICILLIN"},

    # Condition -> LabTest
    {"src": "C_T2DM", "rel": "DIAGNOSED_BY", "dst": "L_HBA1C"},
    {"src": "C_T2DM", "rel": "DIAGNOSED_BY", "dst": "L_FPG"},
    {"src": "C_CKD3", "rel": "DIAGNOSED_BY", "dst": "L_EGFR"},
    {"src": "C_CKD3", "rel": "DIAGNOSED_BY", "dst": "L_CREAT"},
    {"src": "C_HYPOTHY", "rel": "DIAGNOSED_BY", "dst": "L_TSH"},
    {"src": "C_AFIB", "rel": "DIAGNOSED_BY", "dst": "L_ECG"},
    {"src": "C_CAP", "rel": "DIAGNOSED_BY", "dst": "L_CXR"},
    {"src": "C_HTN", "rel": "DIAGNOSED_BY", "dst": "L_LIPID"},

    # Condition -> RiskFactor
    {"src": "C_T2DM", "rel": "HAS_RISK_FACTOR", "dst": "R_OBESITY"},
    {"src": "C_T2DM", "rel": "HAS_RISK_FACTOR", "dst": "R_SEDENTARY"},
    {"src": "C_T2DM", "rel": "HAS_RISK_FACTOR", "dst": "R_FAMHX"},
    {"src": "C_HTN", "rel": "HAS_RISK_FACTOR", "dst": "R_HIGHSODIUM"},
    {"src": "C_HTN", "rel": "HAS_RISK_FACTOR", "dst": "R_OBESITY"},
    {"src": "C_HTN", "rel": "HAS_RISK_FACTOR", "dst": "R_AGE"},
    {"src": "C_CKD3", "rel": "HAS_RISK_FACTOR", "dst": "R_AGE"},
    {"src": "C_AFIB", "rel": "HAS_RISK_FACTOR", "dst": "R_AGE"},
    {"src": "C_ASTHMA", "rel": "HAS_RISK_FACTOR", "dst": "R_SMOKING"},
    {"src": "C_CAP", "rel": "HAS_RISK_FACTOR", "dst": "R_SMOKING"},

    # Medication -> Condition (contraindications)
    # NOTE: metformin/CKD is one of the two "planted" findings -- it can only be
    # surfaced by traversing from a patient to both of their conditions.
    {"src": "M_METFORMIN", "rel": "CONTRAINDICATED_IN", "dst": "C_CKD3"},
    {"src": "M_METOPROLOL", "rel": "CONTRAINDICATED_IN", "dst": "C_ASTHMA"},
    {"src": "M_IBUPROFEN", "rel": "CONTRAINDICATED_IN", "dst": "C_CKD3"},
    {"src": "M_LISINOPRIL", "rel": "CONTRAINDICATED_IN", "dst": "C_CKD3"},

    # Medication <-> Medication (symmetrised in graph.py)
    # NOTE: warfarin/ibuprofen is the second "planted" finding.
    {"src": "M_WARFARIN", "rel": "INTERACTS_WITH", "dst": "M_IBUPROFEN"},
    {"src": "M_WARFARIN", "rel": "INTERACTS_WITH", "dst": "M_AMOXICILLIN"},
    {"src": "M_APIXABAN", "rel": "INTERACTS_WITH", "dst": "M_IBUPROFEN"},
    {"src": "M_LISINOPRIL", "rel": "INTERACTS_WITH", "dst": "M_IBUPROFEN"},
    {"src": "M_LEVOTHYROXINE", "rel": "INTERACTS_WITH", "dst": "M_METFORMIN"},

    # Patient -> Condition
    {"src": "P-001", "rel": "HAS_CONDITION", "dst": "C_T2DM"},
    {"src": "P-001", "rel": "HAS_CONDITION", "dst": "C_CKD3"},
    {"src": "P-002", "rel": "HAS_CONDITION", "dst": "C_AFIB"},
    {"src": "P-002", "rel": "HAS_CONDITION", "dst": "C_MIGRAINE"},
    {"src": "P-003", "rel": "HAS_CONDITION", "dst": "C_ASTHMA"},
    {"src": "P-004", "rel": "HAS_CONDITION", "dst": "C_HTN"},
    {"src": "P-004", "rel": "HAS_CONDITION", "dst": "C_T2DM"},
    {"src": "P-005", "rel": "HAS_CONDITION", "dst": "C_HYPOTHY"},

    # Patient -> Medication
    {"src": "P-001", "rel": "TAKES", "dst": "M_METFORMIN"},
    {"src": "P-001", "rel": "TAKES", "dst": "M_LISINOPRIL"},
    {"src": "P-002", "rel": "TAKES", "dst": "M_WARFARIN"},
    {"src": "P-002", "rel": "TAKES", "dst": "M_METOPROLOL"},
    {"src": "P-002", "rel": "TAKES", "dst": "M_IBUPROFEN"},
    {"src": "P-003", "rel": "TAKES", "dst": "M_ALBUTEROL"},
    {"src": "P-004", "rel": "TAKES", "dst": "M_AMLODIPINE"},
    {"src": "P-004", "rel": "TAKES", "dst": "M_METFORMIN"},
    {"src": "P-004", "rel": "TAKES", "dst": "M_ATORVASTATIN"},
    {"src": "P-005", "rel": "TAKES", "dst": "M_LEVOTHYROXINE"},
]
