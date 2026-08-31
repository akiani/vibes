"""The grounded agent: a manual Claude tool-use loop over the GraphQL schema.

The whole idea of this reference app lives in this file. Claude is given exactly
one tool -- `run_graphql_query` -- and a system prompt that forbids answering
from its own knowledge. To say anything about a condition, drug or patient it
must first query the graph, so every claim in the final answer traces back to a
query you can inspect.

We drive the loop by hand rather than using the SDK's `client.beta.messages.tool_runner`
for two reasons: the loop is the thing being demonstrated, and we want to capture
each query/result pair to show in the UI. See README.md for the tool_runner
alternative if you would rather not own the loop.
"""

from __future__ import annotations

import json
import os

import anthropic

from .schema import schema

# Claude will not run more than this many query/answer rounds for one question.
# A grounded question normally needs 1-3; the cap stops a runaway loop.
MAX_ITERATIONS = 6

SYSTEM_PROMPT = """You are a clinical reference assistant for a medical knowledge graph.

Your knowledge of this domain comes ONLY from the knowledge graph. Follow these rules:

1. Always call `run_graphql_query` before making any factual claim about a
   condition, symptom, medication, lab test, risk factor or patient. Never answer
   from your own memory, even when you are confident you know the answer.
2. If the graph does not contain something, say so plainly ("the graph has no
   entry for X"). Do not fill the gap from general medical knowledge.
3. Cite the entity IDs you relied on, in parentheses, e.g. "Metformin (M_METFORMIN)
   is contraindicated in CKD stage 3 (C_CKD3)".
4. You may issue several queries -- start broad to find IDs, then traverse. If a
   query returns a GraphQL error, read the message and fix the query.
5. Look for connections worth flagging. If a patient takes two drugs that
   interact, or a drug contraindicated in a condition they have, say so.
6. This graph holds fictional demonstration data. Never present it as real
   medical advice; if the user seems to be asking about their own health, tell
   them to talk to a clinician.

Answer in short paragraphs or bullets. Be direct -- no preamble."""

# The tool description carries the schema SDL, so the model always sees the
# current shape of the graph. Change schema.py and this updates itself.
QUERY_TOOL = {
    "name": "run_graphql_query",
    "description": (
        "Run a GraphQL query against the medical knowledge graph and get the JSON result.\n\n"
        "Every root field accepts an optional `id` and an optional `search` (a case-insensitive "
        "substring of the name). Passing neither returns every node of that type, which is the "
        "easiest way to discover IDs when you do not know them yet. Relationship fields let you "
        "traverse several hops in a single query -- prefer one deep query over many shallow ones.\n\n"
        "The schema is:\n\n```graphql\n" + schema.as_str() + "\n```"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The GraphQL query document to execute.",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


def run_graphql_query(query: str) -> tuple[str, bool]:
    """Execute a query. Returns (result_text, is_error).

    GraphQL errors are handed back to Claude as tool errors rather than raised,
    so it can read the message and correct its own query on the next iteration.
    """
    result = schema.execute_sync(query)
    if result.errors:
        messages = "; ".join(str(e) for e in result.errors)
        return f"GraphQL error: {messages}", True
    return json.dumps(result.data, indent=2), False


def answer(messages: list[dict]) -> tuple[str, list[dict]]:
    """Answer the latest user message, grounded in the graph.

    `messages` is the full conversation so far as [{"role", "content"}, ...] --
    the API is stateless, so the client sends the whole history each time.

    Returns (answer_text, trace) where trace is the list of queries that were run
    and what each returned. The frontend renders the trace so a reader can check
    the answer against the graph.
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5")

    convo: list[dict] = [{"role": m["role"], "content": m["content"]} for m in messages]
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
            # No more queries -- Claude is answering.
            text = "\n".join(b.text for b in response.content if b.type == "text").strip()
            if not text:
                # Refusals and a few other stop reasons come back with no text.
                text = f"No answer was produced (stop_reason: {response.stop_reason})."
            return text, trace

        # Keep the assistant turn verbatim -- it carries the tool_use blocks (and
        # any thinking blocks) that the next request has to echo back.
        convo.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_uses:
            query = block.input.get("query", "")
            result_text, is_error = run_graphql_query(query)
            trace.append({"query": query, "result": result_text, "ok": not is_error})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                    "is_error": is_error,
                }
            )

        # All results for one assistant turn go back in a single user message.
        convo.append({"role": "user", "content": tool_results})

    return (
        f"I ran {len(trace)} queries but could not settle on an answer within the "
        f"{MAX_ITERATIONS}-step limit. Try asking something more specific.",
        trace,
    )
