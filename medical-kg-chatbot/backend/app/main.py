"""FastAPI application: the chat endpoint plus a GraphQL playground.

Two things are served here:

  POST /api/chat  -- the grounded chatbot the React frontend talks to
  /graphql        -- the same schema the agent uses, with GraphiQL, for humans

Being able to open /graphql and run the agent's queries by hand is the fastest
way to convince yourself the answers are really coming from the graph.
"""

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

# Load backend/.env before anything reads ANTHROPIC_API_KEY.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from . import agent  # noqa: E402 -- must come after load_dotenv
from .schema import schema  # noqa: E402

app = FastAPI(title="Medical KG Chatbot")

# The Vite dev server runs on 5173 and proxies /api, but we allow the origin
# directly too so you can point any frontend at this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(GraphQLRouter(schema), prefix="/graphql")


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class TraceEntry(BaseModel):
    query: str
    result: str
    ok: bool


class ChatResponse(BaseModel):
    answer: str
    trace: list[TraceEntry]


@app.get("/api/health")
def health() -> dict:
    """Cheap readiness check that also reports whether an API key is configured."""
    return {"status": "ok", "api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY"))}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")

    # The most common first-run problem, reported in plain words rather than
    # as an opaque 500 from deep inside the SDK.
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="No ANTHROPIC_API_KEY set. Copy backend/.env.example to backend/.env, "
            "add your key, and restart the server.",
        )

    try:
        answer_text, trace = agent.answer([m.model_dump() for m in request.messages])
    except anthropic.AuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="Claude rejected the API key. Check ANTHROPIC_API_KEY in backend/.env.",
        )
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limited by the Claude API. Try again shortly.")
    except anthropic.APIStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Claude API error ({exc.status_code}): {exc.message}")
    except anthropic.APIConnectionError:
        raise HTTPException(status_code=502, detail="Could not reach the Claude API. Check your network.")

    return ChatResponse(answer=answer_text, trace=[TraceEntry(**t) for t in trace])
