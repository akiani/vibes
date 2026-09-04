"""Verify the graph and GraphQL layer. Needs no API key.

Run this first when setting up: if it passes, the graph half works and any
remaining problem is the API key or the frontend.

    python smoke_test.py
"""

import json

from app.kg import schema

# Both facts below need two hops -- neither is visible on any single node.
QUERY = """
query {
  patients {
    id name
    conditions { id name }
    medications { id name contraindicatedIn { id } interactsWith { id } }
  }
}
"""

result = schema.execute_sync(QUERY)
assert not result.errors, result.errors
patients = {p["id"]: p for p in result.data["patients"]}
print(json.dumps(result.data, indent=2))

# P-001 takes a drug that is contraindicated in a condition she has.
ada = patients["P-001"]
her_conditions = {c["id"] for c in ada["conditions"]}
conflicts = [m["name"] for m in ada["medications"]
             if any(c["id"] in her_conditions for c in m["contraindicatedIn"])]
assert conflicts, "expected a contraindication conflict for P-001"

# P-002 takes two drugs that interact with each other.
marcus = patients["P-002"]
taken = {m["id"] for m in marcus["medications"]}
interactions = [(m["name"], o["id"]) for m in marcus["medications"]
                for o in m["interactsWith"] if o["id"] in taken]
assert interactions, "expected an interaction between two of P-002's medications"

print(f"\nP-001 contraindications: {conflicts}")
print(f"P-002 interactions: {interactions}")
print("\nAll smoke tests passed.")
