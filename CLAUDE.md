# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running Projects

Most projects have no build step, server, or package manager — open any
`index.html` directly in a modern browser. The exception is
`medical-kg-chatbot/`, which is a Python + React app with its own setup steps in
`medical-kg-chatbot/README.md`.

```
# macOS
open calculator/index.html
open chopin-sonata/index.html

# Linux
xdg-open calculator/index.html
xdg-open chopin-sonata/index.html
```

The Chopin Sonata Player requires Web Audio API — use Chrome, Firefox, Safari, or Edge.

## Architecture

This is a portfolio of standalone apps. Each project is self-contained with no shared code between them.

### Calculator (`calculator/`)

Single `Calculator` class that holds state (`currentOperand`, `previousOperand`, `operation`) and exposes methods called directly from DOM event listeners wired in the same file. Display formatting (thousand separators) is handled in `getDisplayNumber()` and kept separate from compute logic.

### Chopin Sonata Player (`chopin-sonata/`)

Single `ChopinSonataPlayer` class with three responsibilities initialized in the constructor:

- **Audio** (`initAudio`): Creates a `Tone.PolySynth` with a triangle oscillator routed through a `Tone.Reverb`. Playback is sequenced with recursive `setTimeout` calls (not Tone.js Transport), so tempo changes only take effect on the next play.

- **Sheet music** (`renderSheetMusic`): Uses VexFlow 4.2.3. Notes are grouped into measures via `groupNotesByMeasure()`, then each measure is rendered as a separate `VF.Stave`. VexFlow requires pitch keys in lowercase format (e.g. `"eb4"` not `"Eb4"`) — the render method calls `note.pitch.toLowerCase()`.

- **Note data model**: Each note is `{ pitch: string, duration: string, measure: number }`. Duration strings match VexFlow notation (`'1'`, `'2'`, `'4'`, `'8'`). The `regenerateSection()` method picks from C minor scale pitches `['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'D5', 'Eb5']` — new notes should stay within this set to preserve harmonic coherence.

External libraries are loaded via CDN in `index.html` (VexFlow 4.2.3, Tone.js 14.8.49) — no local copies exist.

### Medical KG Chatbot (`medical-kg-chatbot/`)

The only project with a backend. A Claude agent answers questions grounded in a
medical knowledge graph, and cannot answer from its own recall — see
`medical-kg-chatbot/README.md` for setup.

- **Grounding loop** (`backend/app/agent.py`): a manual Claude tool-use loop with
  a single tool, `run_graphql_query`. The tool's description embeds the SDL from
  `schema.as_str()`, so changing the GraphQL schema updates what the agent knows
  it can ask for — never hand-write a second description of the graph. The loop
  collects a `trace` of every query and result, which the frontend renders.

- **Data flow** (`data.py` → `graph.py` → `schema.py`): `data.py` holds `NODES`
  and `EDGES` as plain dicts; `graph.py` builds adjacency indices at import time
  and is the only module that touches storage; `schema.py` exposes Strawberry
  types whose relationship fields resolve through `graph.neighbors()`. Adding an
  entity type means editing those three files in that order.

- Relations listed in `EDGES` are directed. `INTERACTS_WITH` is declared once and
  symmetrised in `graph.py` via `SYMMETRIC_RELATIONS` — do not add both
  directions to `data.py`.

- `backend/smoke_test.py` exercises the graph and GraphQL layers without an API
  key, and asserts the two multi-hop findings the demo relies on (a patient on
  two interacting drugs, and a patient taking a drug contraindicated by their own
  condition). Run it after any change to `data.py`.

## Future Enhancements (from README)

Planned but not yet built: save/load compositions, MIDI export, multiple instruments, chord accompaniment, inserting notes at arbitrary positions, visual keyboard display, recording.
