"""Verify the knowledge graph and GraphQL layer. Needs no API key.

Run this first when setting the project up -- if it passes, the graph half of
the app works and any remaining problem is with the Claude API key or the
frontend.

    python smoke_test.py
"""

import json

from app.schema import schema


def run(label: str, query: str) -> dict:
    result = schema.execute_sync(query)
    assert not result.errors, f"{label} failed: {result.errors}"
    print(f"\n=== {label} ===")
    print(json.dumps(result.data, indent=2))
    return result.data


def main() -> None:
    data = run(
        "Conditions treated by metformin, and where it must be avoided",
        """
        query {
          medications(search: "metformin") {
            id name drugClass
            treats { id name }
            contraindicatedIn { id name }
          }
        }
        """,
    )
    med = data["medications"][0]
    assert med["id"] == "M_METFORMIN"
    assert any(c["id"] == "C_CKD3" for c in med["contraindicatedIn"]), \
        "expected metformin to be contraindicated in CKD stage 3"

    data = run(
        "Patient P-001: a drug she takes is contraindicated by a condition she has",
        """
        query {
          patients(id: "P-001") {
            id name
            conditions { id name }
            medications { id name contraindicatedIn { id name } }
          }
        }
        """,
    )
    patient = data["patients"][0]
    condition_ids = {c["id"] for c in patient["conditions"]}
    conflicts = [
        (m["name"], c["name"])
        for m in patient["medications"]
        for c in m["contraindicatedIn"]
        if c["id"] in condition_ids
    ]
    assert conflicts, "expected at least one contraindication conflict for P-001"
    print(f"\n-> conflicts found: {conflicts}")

    data = run(
        "Patient P-002: two medications that interact with each other",
        """
        query {
          patients(id: "P-002") {
            id name
            medications { id name interactsWith { id name } }
          }
        }
        """,
    )
    meds = data["patients"][0]["medications"]
    taken = {m["id"] for m in meds}
    interactions = [
        (m["name"], other["name"])
        for m in meds
        for other in m["interactsWith"]
        if other["id"] in taken
    ]
    assert interactions, "expected an interaction between two of P-002's medications"
    print(f"\n-> interactions found: {interactions}")

    run(
        "Reverse traversal: which conditions cause fatigue",
        """
        query { symptoms(search: "fatigue") { id name conditions { id name } } }
        """,
    )

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
