# Medical KG Chatbot

A minimal reference implementation of a **chatbot whose answers are grounded in a
knowledge graph** rather than in the model's own recall.

Claude is given exactly one tool — `run_graphql_query` — and a system prompt that
forbids answering from memory. To say anything about a condition, drug or patient
it must first query a real GraphQL schema over a medical knowledge graph. The UI
shows you the queries it ran under every answer, so you can check the reasoning
against the data.

```
React + Vite (:5173)
  │  POST /api/chat  { messages: [...] }
  ▼
FastAPI (:8000)
  │
  ├── agent.py ─── tool-use loop ⇄ Claude API
  │                  tool: run_graphql_query(query)
  │                       │
  │                       ▼
  ├── schema.py ── Strawberry GraphQL ── also served at /graphql (GraphiQL)
  │                       │
  ├── graph.py ─── in-memory node/edge indices
  └── data.py ──── the mock medical graph (plain Python dicts)
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- An Anthropic API key — [console.anthropic.com](https://console.anthropic.com/settings/keys)

## Setup

**Backend** (terminal 1):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env and paste in your API key

python smoke_test.py               # verifies the graph — no API key needed
uvicorn app.main:app --reload
```

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

Two things worth checking if something misbehaves:

- <http://localhost:8000/api/health> reports whether your API key was picked up.
- <http://localhost:8000/graphql> is a GraphiQL playground on the same schema the
  agent uses. Running the agent's queries by hand is the quickest way to confirm
  the answers really come from the graph.

## Try it

```
What is type 2 diabetes and how is it diagnosed?
Which conditions cause fatigue?
Patient P-002 is on several medications — anything to watch for?
Is anything Ada Whitfield takes risky given her conditions?
What's the treatment for lupus?
```

The last three are the interesting ones. Two findings are reachable only by
traversing the graph, not by looking at any single node:

- **P-002** takes warfarin *and* ibuprofen, which the graph records as
  interacting.
- **P-001 (Ada Whitfield)** has CKD stage 3 and takes metformin and lisinopril,
  both of which are marked contraindicated in that condition.

And the lupus question demonstrates the other half of grounding: the graph has no
lupus entry, so the agent should say so rather than answering from its own
knowledge.

## How the grounding works

1. The frontend POSTs the whole conversation to `/api/chat`. The backend is
   stateless — the client owns the history.
2. `agent.py` calls Claude with a system prompt that requires a query before any
   factual claim, plus one tool whose description embeds the schema SDL.
3. Claude replies with a `tool_use` block containing a GraphQL query.
4. The backend executes it with `schema.execute_sync()` and appends the JSON
   result as a `tool_result`. A malformed query comes back as a tool error with
   the GraphQL parser's message, so Claude can correct itself and retry.
5. Steps 2–4 repeat (up to `MAX_ITERATIONS = 6`) until Claude answers in prose.
   Every query and result is collected into a `trace` that ships with the answer
   and gets rendered in the collapsible panel under each reply.

The load-bearing detail is in step 2: **the tool description is generated from
the schema** (`schema.as_str()`), not hand-written. Add a field to `schema.py`
and the agent knows about it on the next request, with no prompt to update.

## The knowledge graph

Six node types and eight relations, all defined in `backend/app/data.py`:

| Relation | From → To |
|---|---|
| `PRESENTS_WITH` | Condition → Symptom |
| `TREATED_BY` | Condition → Medication |
| `DIAGNOSED_BY` | Condition → LabTest |
| `HAS_RISK_FACTOR` | Condition → RiskFactor |
| `CONTRAINDICATED_IN` | Medication → Condition |
| `INTERACTS_WITH` | Medication ↔ Medication (undirected) |
| `HAS_CONDITION` | Patient → Condition |
| `TAKES` | Patient → Medication |

Roughly 8 conditions, 14 symptoms, 12 medications, 9 lab tests, 6 risk factors
and 5 fictional patients. Every root field in the GraphQL schema accepts an
optional `id` and an optional `search` (case-insensitive substring), and
returns everything of that type when given neither — which is how the agent
discovers IDs it does not yet know.

## Project layout

```
backend/
  .env.example        ANTHROPIC_API_KEY and optional ANTHROPIC_MODEL
  requirements.txt
  smoke_test.py       verifies the graph + GraphQL layer, no API key needed
  app/
    data.py           the knowledge graph: NODES and EDGES
    graph.py          builds adjacency indices; swap this for a real graph DB
    schema.py         Strawberry types and the Query root
    agent.py          the Claude tool-use loop and trace capture
    main.py           FastAPI: /api/chat, /api/health, /graphql
frontend/
  vite.config.js      proxies /api and /graphql to :8000
  src/App.jsx         chat UI and the query-trace panel
```

## Extending it

**Add an entity type.** Three edits, in this order: add nodes and edges to
`data.py`, add a `@strawberry.type` and a root field in `schema.py`, done. The
agent picks it up automatically because its tool description is the schema.

**Use a real graph database.** Only `graph.py` talks to storage. Replace
`get_node`, `neighbors` and `find` with Cypher (Neo4j) or Gremlin queries and
nothing above it changes.

**Let the SDK drive the loop.** `agent.py` runs the tool-use loop by hand because
the loop is the thing being demonstrated. In production you would likely use
`client.beta.messages.tool_runner` with an `@beta_tool`-decorated function and
skip the loop entirely — you would just need another way to capture the trace.

**Stream the response.** `/api/chat` returns a single JSON blob, so the UI shows a
spinner while the agent works. Switching to `client.messages.stream()` behind
Server-Sent Events would let you show the queries as they are issued.

**Cache the prompt.** The system prompt and tool schema are identical on every
request. Adding `cache_control` to them cuts input costs on multi-turn
conversations; it only takes effect once the cached prefix exceeds the model's
minimum, so check `usage.cache_read_input_tokens` to confirm it is working.

## Notes

The medical data here is fictional, simplified, and assembled to make the demo
legible. It is not clinically complete and is not medical advice.
