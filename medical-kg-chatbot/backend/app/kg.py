"""The knowledge graph: mock data, adjacency indices, and the GraphQL schema.

Reads top to bottom in three parts:

  1. NODES / EDGES  -- everything the chatbot can possibly know, as plain dicts
  2. the index      -- adjacency lookups built once at import; swap this part
                       for Neo4j and nothing above or below it changes
  3. the schema     -- Strawberry types whose relationship fields walk the index

Part 3 is also what the agent reads: agent.py embeds this schema's SDL in its
tool description, so adding a field here teaches the agent about it immediately.

All data is fictional and simplified for demonstration.
"""

from __future__ import annotations

from collections import defaultdict

import strawberry

# --- 1. The data -----------------------------------------------------------

NODES = [
    # Conditions
    {"id": "C_T2DM", "type": "Condition", "name": "Type 2 Diabetes Mellitus", "icd10": "E11",
     "description": "Insulin resistance leading to chronically elevated blood glucose."},
    {"id": "C_HTN", "type": "Condition", "name": "Essential Hypertension", "icd10": "I10",
     "description": "Persistently elevated arterial blood pressure with no secondary cause."},
    {"id": "C_CKD3", "type": "Condition", "name": "Chronic Kidney Disease Stage 3", "icd10": "N18.3",
     "description": "Moderately reduced kidney function, eGFR 30-59 mL/min/1.73m2."},
    {"id": "C_AFIB", "type": "Condition", "name": "Atrial Fibrillation", "icd10": "I48",
     "description": "Irregular, often rapid heart rhythm that raises stroke risk."},
    {"id": "C_MIGRAINE", "type": "Condition", "name": "Migraine", "icd10": "G43",
     "description": "Recurrent moderate-to-severe headache, often with nausea or photophobia."},

    # Symptoms
    {"id": "S_POLYURIA", "type": "Symptom", "name": "Polyuria"},
    {"id": "S_THIRST", "type": "Symptom", "name": "Excessive thirst"},
    {"id": "S_FATIGUE", "type": "Symptom", "name": "Fatigue"},
    {"id": "S_HEADACHE", "type": "Symptom", "name": "Headache"},
    {"id": "S_PALPITATIONS", "type": "Symptom", "name": "Palpitations"},
    {"id": "S_EDEMA", "type": "Symptom", "name": "Peripheral edema"},
    {"id": "S_PHOTOPHOBIA", "type": "Symptom", "name": "Photophobia"},

    # Medications
    {"id": "M_METFORMIN", "type": "Medication", "name": "Metformin", "drug_class": "Biguanide"},
    {"id": "M_LISINOPRIL", "type": "Medication", "name": "Lisinopril", "drug_class": "ACE inhibitor"},
    {"id": "M_AMLODIPINE", "type": "Medication", "name": "Amlodipine", "drug_class": "Calcium channel blocker"},
    {"id": "M_METOPROLOL", "type": "Medication", "name": "Metoprolol", "drug_class": "Beta blocker"},
    {"id": "M_WARFARIN", "type": "Medication", "name": "Warfarin", "drug_class": "Vitamin K antagonist"},
    {"id": "M_IBUPROFEN", "type": "Medication", "name": "Ibuprofen", "drug_class": "NSAID"},
    {"id": "M_SUMATRIPTAN", "type": "Medication", "name": "Sumatriptan", "drug_class": "Triptan"},

    # Patients (fictional)
    {"id": "P-001", "type": "Patient", "name": "Ada Whitfield", "age": 62},
    {"id": "P-002", "type": "Patient", "name": "Marcus Bell", "age": 71},
    {"id": "P-003", "type": "Patient", "name": "Priya Raman", "age": 45},
]

# Directed triples. INTERACTS_WITH is conceptually undirected: it is written once
# here and indexed both ways below, so a query from either drug finds it.
EDGES = [
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_POLYURIA"},
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_THIRST"},
    {"src": "C_T2DM", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_HTN", "rel": "PRESENTS_WITH", "dst": "S_HEADACHE"},
    {"src": "C_CKD3", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_CKD3", "rel": "PRESENTS_WITH", "dst": "S_EDEMA"},
    {"src": "C_AFIB", "rel": "PRESENTS_WITH", "dst": "S_PALPITATIONS"},
    {"src": "C_AFIB", "rel": "PRESENTS_WITH", "dst": "S_FATIGUE"},
    {"src": "C_MIGRAINE", "rel": "PRESENTS_WITH", "dst": "S_HEADACHE"},
    {"src": "C_MIGRAINE", "rel": "PRESENTS_WITH", "dst": "S_PHOTOPHOBIA"},

    {"src": "C_T2DM", "rel": "TREATED_BY", "dst": "M_METFORMIN"},
    {"src": "C_HTN", "rel": "TREATED_BY", "dst": "M_LISINOPRIL"},
    {"src": "C_HTN", "rel": "TREATED_BY", "dst": "M_AMLODIPINE"},
    {"src": "C_AFIB", "rel": "TREATED_BY", "dst": "M_METOPROLOL"},
    {"src": "C_AFIB", "rel": "TREATED_BY", "dst": "M_WARFARIN"},
    {"src": "C_MIGRAINE", "rel": "TREATED_BY", "dst": "M_SUMATRIPTAN"},
    {"src": "C_MIGRAINE", "rel": "TREATED_BY", "dst": "M_IBUPROFEN"},

    # Reachable only by combining a patient's conditions with their medications.
    {"src": "M_METFORMIN", "rel": "CONTRAINDICATED_IN", "dst": "C_CKD3"},
    {"src": "M_IBUPROFEN", "rel": "CONTRAINDICATED_IN", "dst": "C_CKD3"},

    # Likewise: found only by cross-referencing one patient's medication list.
    {"src": "M_WARFARIN", "rel": "INTERACTS_WITH", "dst": "M_IBUPROFEN"},
    {"src": "M_LISINOPRIL", "rel": "INTERACTS_WITH", "dst": "M_IBUPROFEN"},

    {"src": "P-001", "rel": "HAS_CONDITION", "dst": "C_T2DM"},
    {"src": "P-001", "rel": "HAS_CONDITION", "dst": "C_CKD3"},
    {"src": "P-002", "rel": "HAS_CONDITION", "dst": "C_AFIB"},
    {"src": "P-002", "rel": "HAS_CONDITION", "dst": "C_MIGRAINE"},
    {"src": "P-003", "rel": "HAS_CONDITION", "dst": "C_HTN"},

    {"src": "P-001", "rel": "TAKES", "dst": "M_METFORMIN"},
    {"src": "P-002", "rel": "TAKES", "dst": "M_WARFARIN"},
    {"src": "P-002", "rel": "TAKES", "dst": "M_IBUPROFEN"},
    {"src": "P-003", "rel": "TAKES", "dst": "M_AMLODIPINE"},
]

# --- 2. The index ----------------------------------------------------------

SYMMETRIC_RELATIONS = {"INTERACTS_WITH"}

_NODES: dict[str, dict] = {n["id"]: n for n in NODES}
_OUT: dict[tuple[str, str], list[str]] = defaultdict(list)
_IN: dict[tuple[str, str], list[str]] = defaultdict(list)

for _edge in EDGES:
    _src, _rel, _dst = _edge["src"], _edge["rel"], _edge["dst"]
    if _src not in _NODES or _dst not in _NODES:
        raise ValueError(f"Edge references unknown node: {_edge}")
    _OUT[(_src, _rel)].append(_dst)
    _IN[(_dst, _rel)].append(_src)
    if _rel in SYMMETRIC_RELATIONS:
        _OUT[(_dst, _rel)].append(_src)
        _IN[(_src, _rel)].append(_dst)


def neighbors(node_id: str, relation: str, incoming: bool = False) -> list[dict]:
    """Nodes reachable from `node_id` over `relation`, forwards or backwards."""
    index = _IN if incoming else _OUT
    return [_NODES[nid] for nid in index.get((node_id, relation), [])]


def find(node_type: str, node_id: str | None = None, search: str | None = None) -> list[dict]:
    """Backs every root field: by id, by name substring, or everything of a type."""
    if node_id is not None:
        node = _NODES.get(node_id)
        return [node] if node and node["type"] == node_type else []
    matches = [n for n in NODES if n["type"] == node_type]
    if search:
        matches = [n for n in matches if search.lower() in n["name"].lower()]
    return matches


# --- 3. The schema ---------------------------------------------------------


@strawberry.type(description="A sign or symptom a patient may report.")
class Symptom:
    id: strawberry.ID
    name: str

    @strawberry.field(description="Conditions known to present with this symptom.")
    def conditions(self) -> list[Condition]:
        return [Condition.of(n) for n in neighbors(self.id, "PRESENTS_WITH", incoming=True)]

    @classmethod
    def of(cls, n: dict) -> Symptom:
        return cls(id=strawberry.ID(n["id"]), name=n["name"])


@strawberry.type(description="A drug that may be prescribed.")
class Medication:
    id: strawberry.ID
    name: str
    drug_class: str

    @strawberry.field(description="Conditions this medication is used to treat.")
    def treats(self) -> list[Condition]:
        return [Condition.of(n) for n in neighbors(self.id, "TREATED_BY", incoming=True)]

    @strawberry.field(description="Other medications with a known interaction. Symmetric.")
    def interacts_with(self) -> list[Medication]:
        return [Medication.of(n) for n in neighbors(self.id, "INTERACTS_WITH")]

    @strawberry.field(description="Conditions in which this medication should be avoided.")
    def contraindicated_in(self) -> list[Condition]:
        return [Condition.of(n) for n in neighbors(self.id, "CONTRAINDICATED_IN")]

    @classmethod
    def of(cls, n: dict) -> Medication:
        return cls(id=strawberry.ID(n["id"]), name=n["name"], drug_class=n["drug_class"])


@strawberry.type(description="A disease or clinical condition.")
class Condition:
    id: strawberry.ID
    name: str
    icd10: str
    description: str

    @strawberry.field(description="Symptoms this condition commonly presents with.")
    def symptoms(self) -> list[Symptom]:
        return [Symptom.of(n) for n in neighbors(self.id, "PRESENTS_WITH")]

    @strawberry.field(description="Medications used to treat this condition.")
    def treated_by(self) -> list[Medication]:
        return [Medication.of(n) for n in neighbors(self.id, "TREATED_BY")]

    @classmethod
    def of(cls, n: dict) -> Condition:
        return cls(id=strawberry.ID(n["id"]), name=n["name"], icd10=n["icd10"],
                   description=n["description"])


@strawberry.type(description="A fictional patient record used for demonstration.")
class Patient:
    id: strawberry.ID
    name: str
    age: int

    @strawberry.field(description="Conditions this patient has been diagnosed with.")
    def conditions(self) -> list[Condition]:
        return [Condition.of(n) for n in neighbors(self.id, "HAS_CONDITION")]

    @strawberry.field(description="Medications this patient is currently taking.")
    def medications(self) -> list[Medication]:
        return [Medication.of(n) for n in neighbors(self.id, "TAKES")]

    @classmethod
    def of(cls, n: dict) -> Patient:
        return cls(id=strawberry.ID(n["id"]), name=n["name"], age=n["age"])


@strawberry.type
class Query:
    """Every field takes an optional id and an optional name substring. Passing
    neither returns all nodes of that type, which is how the agent finds ids."""

    @strawberry.field
    def conditions(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Condition]:
        return [Condition.of(n) for n in find("Condition", id, search)]

    @strawberry.field
    def medications(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Medication]:
        return [Medication.of(n) for n in find("Medication", id, search)]

    @strawberry.field
    def symptoms(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Symptom]:
        return [Symptom.of(n) for n in find("Symptom", id, search)]

    @strawberry.field
    def patients(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Patient]:
        return [Patient.of(n) for n in find("Patient", id, search)]


schema = strawberry.Schema(query=Query)
