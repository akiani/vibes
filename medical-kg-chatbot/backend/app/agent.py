"""The grounded agent: a Claude tool-use loop over the GraphQL schema.

The whole idea of this app lives here. Claude gets exactly one tool --
`run_graphql_query` -- and a system prompt forbidding it from answering from
memory, so every factual claim has to come from a query you can inspect.

The loop is written out by hand rather than using the SDK's
`client.beta.messages.tool_runner`, because the loop is the thing being shown
and because we want each query/result pair for the UI trace.
"""

from __future__ import annotations

import json
import os

import anthropic

from .kg import schema

MAX_ITERATIONS = 6  # a grounded answer normally needs 1-3 rounds

SYSTEM_PROMPT = """You are a clinical reference assistant for a medical knowledge graph.

Your knowledge of this domain comes ONLY from the graph. Rules:

1. Call `run_graphql_query` before making any factual claim about a condition,
   symptom, medication or patient. Never answer from your own memory.
2. If the graph has no entry for something, say so plainly. Do not fill the gap
   from general medical knowledge.
3. Cite the entity IDs you used, e.g. "Metformin (M_METFORMIN) is
   contraindicated in CKD stage 3 (C_CKD3)".
4. Start broad to find IDs, then traverse. If a query returns an error, read the
   message and fix it.
5. Flag connections worth noticing: a patient taking two drugs that interact, or
   a drug contraindicated in a condition they have.
6. This is fictional demonstration data, not medical advice.

Answer in short paragraphs or bullets. Be direct -- no preamble."""

# The description carries the schema SDL, so the model always sees the current
# shape of the graph. Change kg.py and this updates itself.
QUERY_TOOL = {
    "name": "run_graphql_query",
    "description": (
        "Run a GraphQL query against the medical knowledge graph and get JSON back.\n\n"
        "Root fields take an optional `id` and an optional `search` (case-insensitive "
        "name substring). Passing neither returns every node of that type, which is the "
        "easiest way to discover IDs. Relationship fields traverse several hops in one "
        "query -- prefer one deep query over many shallow ones.\n\n"
        "Schema:\n\n```graphql\n" + schema.as_str() + "\n```"
    ),
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The GraphQL query to execute."}},
        "required": ["query"],
        "additionalProperties": False,
    },
}


def run_graphql_query(query: str) -> tuple[str, bool]:
    """Execute a query, returning (result_text, is_error).

    Errors go back to Claude as tool errors rather than raised, so it can read
    the parser's message and correct its own query on the next iteration.
    """
    result = schema.execute_sync(query)
    if result.errors:
        return "GraphQL error: " + "; ".join(str(e) for e in result.errors), True
    return json.dumps(result.data, indent=2), False


def answer(messages: list[dict]) -> tuple[str, list[dict]]:
    """Answer the latest message, grounded in the graph.

    Returns (answer_text, trace), where trace lists every query run and what it
    returned. The frontend renders it so a reader can check the answer.
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5")
    convo = [{"role": m["role"], "content": m["content"]} for m in messages]
    trace: list[dict] = []

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            tools=[QUERY_TOOL],
            messages=convo,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            text = "\n".join(b.text for b in response.content if b.type == "text").strip()
            # Refusals and a few other stop reasons come back with no text.
            return text or f"No answer produced (stop_reason: {response.stop_reason}).", trace

        # Keep the assistant turn verbatim: it carries the tool_use and thinking
        # blocks the next request has to echo back.
        convo.append({"role": "assistant", "content": response.content})

        results = []
        for block in tool_uses:
            query = block.input.get("query", "")
            text, is_error = run_graphql_query(query)
            trace.append({"query": query, "result": text, "ok": not is_error})
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": text, "is_error": is_error})

        # All results for one assistant turn go back in a single user message.
        convo.append({"role": "user", "content": results})

    return f"Ran {len(trace)} queries without settling on an answer. Try asking something narrower.", trace
