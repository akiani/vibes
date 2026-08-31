"""In-memory graph store built from `data.py`.

This is the layer you would replace with a real graph database (Neo4j,
Memgraph, Neptune) in a production system. Everything above it -- the GraphQL
schema and the agent -- only talks to the three functions at the bottom of this
file, so swapping the storage does not touch the rest of the app.
"""

from collections import defaultdict

from . import data

# Relations that are conceptually undirected. They are written once in data.py
# and indexed in both directions here, so a query from either endpoint finds it.
SYMMETRIC_RELATIONS = {"INTERACTS_WITH"}

# id -> node dict
NODES: dict[str, dict] = {node["id"]: node for node in data.NODES}

# (node_id, relation) -> [node_id, ...], for each direction of traversal
_OUT: dict[tuple[str, str], list[str]] = defaultdict(list)
_IN: dict[tuple[str, str], list[str]] = defaultdict(list)


def _index_edges() -> None:
    for edge in data.EDGES:
        src, rel, dst = edge["src"], edge["rel"], edge["dst"]
        if src not in NODES or dst not in NODES:
            raise ValueError(f"Edge references unknown node: {edge}")
        _OUT[(src, rel)].append(dst)
        _IN[(dst, rel)].append(src)
        if rel in SYMMETRIC_RELATIONS:
            _OUT[(dst, rel)].append(src)
            _IN[(src, rel)].append(dst)


_index_edges()


def get_node(node_id: str) -> dict | None:
    """Look up a single node by id."""
    return NODES.get(node_id)


def neighbors(node_id: str, relation: str, incoming: bool = False) -> list[dict]:
    """Nodes reachable from `node_id` over `relation`.

    By default this follows the edge forwards (Condition -TREATED_BY-> Medication).
    Pass incoming=True to walk it backwards (Medication <-TREATED_BY- Condition),
    which is how a Medication reports the conditions it treats.
    """
    index = _IN if incoming else _OUT
    return [NODES[nid] for nid in index.get((node_id, relation), [])]


def find(node_type: str, node_id: str | None = None, search: str | None = None) -> list[dict]:
    """Entry point for the GraphQL root fields.

    With an id, returns that node (if it is of the requested type). With a
    search string, returns nodes of that type whose name contains it,
    case-insensitively. With neither, returns every node of the type.
    """
    if node_id is not None:
        node = NODES.get(node_id)
        return [node] if node and node["type"] == node_type else []

    matches = [n for n in data.NODES if n["type"] == node_type]
    if search:
        needle = search.lower()
        matches = [n for n in matches if needle in n["name"].lower()]
    return matches
