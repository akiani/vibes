"""The GraphQL schema over the medical knowledge graph.

This module has two consumers:

1. Humans, via the GraphiQL playground mounted at /graphql by main.py.
2. Claude, via agent.py -- which embeds this schema's SDL in its tool
   description, so the agent always knows exactly what it can ask for.

Because of (2) there is no separate, hand-maintained description of the graph
for the model to read. Add a field here and the agent can use it immediately.
"""

from __future__ import annotations

import strawberry

from . import graph

# --- Node types ------------------------------------------------------------
#
# Each type mirrors a node type in data.py. Scalar fields come straight from the
# node dict; relationship fields resolve lazily through graph.neighbors(), so a
# single query can traverse as many hops as it needs.


@strawberry.type(description="A sign or symptom a patient may report.")
class Symptom:
    id: strawberry.ID
    name: str
    body_system: str

    @strawberry.field(description="Conditions known to present with this symptom.")
    def conditions(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "PRESENTS_WITH", incoming=True)]

    @classmethod
    def from_node(cls, node: dict) -> Symptom:
        return cls(id=strawberry.ID(node["id"]), name=node["name"], body_system=node["body_system"])


@strawberry.type(description="A laboratory test or diagnostic study.")
class LabTest:
    id: strawberry.ID
    name: str
    unit: str
    reference_range: str

    @strawberry.field(description="Conditions this test helps diagnose or monitor.")
    def diagnoses(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "DIAGNOSED_BY", incoming=True)]

    @classmethod
    def from_node(cls, node: dict) -> LabTest:
        return cls(
            id=strawberry.ID(node["id"]),
            name=node["name"],
            unit=node["unit"],
            reference_range=node["reference_range"],
        )


@strawberry.type(description="Something that raises the likelihood of a condition.")
class RiskFactor:
    id: strawberry.ID
    name: str
    modifiable: bool

    @strawberry.field(description="Conditions this factor raises the risk of.")
    def conditions(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "HAS_RISK_FACTOR", incoming=True)]

    @classmethod
    def from_node(cls, node: dict) -> RiskFactor:
        return cls(id=strawberry.ID(node["id"]), name=node["name"], modifiable=node["modifiable"])


@strawberry.type(description="A drug that may be prescribed.")
class Medication:
    id: strawberry.ID
    name: str
    drug_class: str
    route: str

    @strawberry.field(description="Conditions this medication is used to treat.")
    def treats(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "TREATED_BY", incoming=True)]

    @strawberry.field(description="Other medications with a known interaction. Symmetric.")
    def interacts_with(self) -> list[Medication]:
        return [Medication.from_node(n) for n in graph.neighbors(self.id, "INTERACTS_WITH")]

    @strawberry.field(description="Conditions in which this medication should be avoided.")
    def contraindicated_in(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "CONTRAINDICATED_IN")]

    @strawberry.field(description="Patients currently taking this medication.")
    def patients(self) -> list[Patient]:
        return [Patient.from_node(n) for n in graph.neighbors(self.id, "TAKES", incoming=True)]

    @classmethod
    def from_node(cls, node: dict) -> Medication:
        return cls(
            id=strawberry.ID(node["id"]),
            name=node["name"],
            drug_class=node["drug_class"],
            route=node["route"],
        )


@strawberry.type(description="A disease or clinical condition.")
class Condition:
    id: strawberry.ID
    name: str
    icd10: str
    category: str
    description: str

    @strawberry.field(description="Symptoms this condition commonly presents with.")
    def symptoms(self) -> list[Symptom]:
        return [Symptom.from_node(n) for n in graph.neighbors(self.id, "PRESENTS_WITH")]

    @strawberry.field(description="Medications used to treat this condition.")
    def treated_by(self) -> list[Medication]:
        return [Medication.from_node(n) for n in graph.neighbors(self.id, "TREATED_BY")]

    @strawberry.field(description="Tests used to diagnose or monitor this condition.")
    def diagnosed_by(self) -> list[LabTest]:
        return [LabTest.from_node(n) for n in graph.neighbors(self.id, "DIAGNOSED_BY")]

    @strawberry.field(description="Known risk factors for this condition.")
    def risk_factors(self) -> list[RiskFactor]:
        return [RiskFactor.from_node(n) for n in graph.neighbors(self.id, "HAS_RISK_FACTOR")]

    @strawberry.field(description="Medications that should be avoided in this condition.")
    def contraindicated_medications(self) -> list[Medication]:
        return [Medication.from_node(n) for n in graph.neighbors(self.id, "CONTRAINDICATED_IN", incoming=True)]

    @strawberry.field(description="Patients recorded as having this condition.")
    def patients(self) -> list[Patient]:
        return [Patient.from_node(n) for n in graph.neighbors(self.id, "HAS_CONDITION", incoming=True)]

    @classmethod
    def from_node(cls, node: dict) -> Condition:
        return cls(
            id=strawberry.ID(node["id"]),
            name=node["name"],
            icd10=node["icd10"],
            category=node["category"],
            description=node["description"],
        )


@strawberry.type(description="A fictional patient record used for demonstration.")
class Patient:
    id: strawberry.ID
    name: str
    age: int
    sex: str

    @strawberry.field(description="Conditions this patient has been diagnosed with.")
    def conditions(self) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.neighbors(self.id, "HAS_CONDITION")]

    @strawberry.field(description="Medications this patient is currently taking.")
    def medications(self) -> list[Medication]:
        return [Medication.from_node(n) for n in graph.neighbors(self.id, "TAKES")]

    @classmethod
    def from_node(cls, node: dict) -> Patient:
        return cls(id=strawberry.ID(node["id"]), name=node["name"], age=node["age"], sex=node["sex"])


# --- Query root ------------------------------------------------------------
#
# Every root field takes an optional `id` and an optional `search` (a
# case-insensitive substring of the name). Passing neither returns everything of
# that type, which is how the agent orients itself when it does not yet know an id.


@strawberry.type
class Query:
    @strawberry.field(description="Look up conditions by id, by name substring, or list them all.")
    def conditions(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Condition]:
        return [Condition.from_node(n) for n in graph.find("Condition", id, search)]

    @strawberry.field(description="Look up medications by id, by name substring, or list them all.")
    def medications(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Medication]:
        return [Medication.from_node(n) for n in graph.find("Medication", id, search)]

    @strawberry.field(description="Look up symptoms by id, by name substring, or list them all.")
    def symptoms(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Symptom]:
        return [Symptom.from_node(n) for n in graph.find("Symptom", id, search)]

    @strawberry.field(description="Look up lab tests by id, by name substring, or list them all.")
    def lab_tests(self, id: strawberry.ID | None = None, search: str | None = None) -> list[LabTest]:
        return [LabTest.from_node(n) for n in graph.find("LabTest", id, search)]

    @strawberry.field(description="Look up risk factors by id, by name substring, or list them all.")
    def risk_factors(self, id: strawberry.ID | None = None, search: str | None = None) -> list[RiskFactor]:
        return [RiskFactor.from_node(n) for n in graph.find("RiskFactor", id, search)]

    @strawberry.field(description="Look up patients by id (e.g. \"P-001\"), by name substring, or list them all.")
    def patients(self, id: strawberry.ID | None = None, search: str | None = None) -> list[Patient]:
        return [Patient.from_node(n) for n in graph.find("Patient", id, search)]


schema = strawberry.Schema(query=Query)
