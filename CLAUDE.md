# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running Projects

No build step, server, or package manager. Open any `index.html` directly in a modern browser:

```
# macOS
open calculator/index.html
open chopin-sonata/index.html
open tehran-3d/index.html

# Linux
xdg-open calculator/index.html
xdg-open chopin-sonata/index.html
xdg-open tehran-3d/index.html
```

The Chopin Sonata Player requires Web Audio API — use Chrome, Firefox, Safari, or Edge.
Tehran 3D requires WebGL 2 and a discrete or recent integrated GPU.

## Architecture

This is a portfolio of standalone browser apps. Each project is self-contained with no shared code between them.

### Calculator (`calculator/`)

Single `Calculator` class that holds state (`currentOperand`, `previousOperand`, `operation`) and exposes methods called directly from DOM event listeners wired in the same file. Display formatting (thousand separators) is handled in `getDisplayNumber()` and kept separate from compute logic.

### Chopin Sonata Player (`chopin-sonata/`)

Single `ChopinSonataPlayer` class with three responsibilities initialized in the constructor:

- **Audio** (`initAudio`): Creates a `Tone.PolySynth` with a triangle oscillator routed through a `Tone.Reverb`. Playback is sequenced with recursive `setTimeout` calls (not Tone.js Transport), so tempo changes only take effect on the next play.

- **Sheet music** (`renderSheetMusic`): Uses VexFlow 4.2.3. Notes are grouped into measures via `groupNotesByMeasure()`, then each measure is rendered as a separate `VF.Stave`. VexFlow requires pitch keys in lowercase format (e.g. `"eb4"` not `"Eb4"`) — the render method calls `note.pitch.toLowerCase()`.

- **Note data model**: Each note is `{ pitch: string, duration: string, measure: number }`. Duration strings match VexFlow notation (`'1'`, `'2'`, `'4'`, `'8'`). The `regenerateSection()` method picks from C minor scale pitches `['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'D5', 'Eb5']` — new notes should stay within this set to preserve harmonic coherence.

External libraries are loaded via CDN in `index.html` (VexFlow 4.2.3, Tone.js 14.8.49) — no local copies exist.

### Tehran 3D (`tehran-3d/`)

A procedural, walkable model of Tehran in one `index.html` (~3.6k lines) — three.js 0.161 is pulled
from unpkg via an importmap, so the inline `<script type="module">` must stay a single file (relative
module imports are blocked on `file://`). The script is organised in sections, in build order:

- **Core** — `GEO_SCALE`/`geo()` project real lat-lon into the local metric frame (origin: Enghelab
  Square). `terrainHeight(x, z)` is the single source of truth for ground elevation and is used by
  roads, buildings, agents and the player; `cityMask()` decides where the city exists and flattens
  the plain under it. All randomness goes through the seeded `mulberry32` `rnd()` — the city is
  deterministic. Canvas texture painters live here, plus two helpers everything else depends on:
  `mergeGeos()` (normalises indexed/non-indexed geometry before merging) and `uvFit()` (turns a
  primitive's 0..1 UVs into metres/tile).
- **World** — renderer, `Sky`, sun/moon from real solar equations, fog and exposure driven by
  `state.weather` + `state.smog`, terrain mesh with per-vertex colours (`paintTerrain()` is re-run
  when the snow toggle changes).
- **Streets** — named arterials as lat-lon polylines, then a background grid culled against them.
  `breaksFor()` finds junctions so sidewalks, curbs, jubs, trees and lamps stop at crossings.
  Produces `driveLanes` and `walkPaths`, which the agents consume.
- **Buildings** — a 6 m occupancy grid (`OG`, flags road/building/reserved) drives lot placement and
  doubles as player collision. Buildings snap to a 4 m bay × 3.2 m floor module so facade textures
  tile with whole numbers. Each facade style becomes an `InstancedMesh` whose material patches the
  vertex shader to scale UVs by the per-instance matrix — change that trick and every wall breaks.
- **Landmarks** — one function per monument; each calls `reserve()` (keeps generated fabric out) and
  `ogMarkRect(..., OCC_BUILD)` for its solid parts, and pushes any walkable platform to `walkables`.
- **Agents** — instanced cars/buses/motorcycles on lanes with precomputed endpoint heights (never
  call `terrainHeight` per agent per frame), pedestrians on sidewalk paths.
- **Controls / boot** — walk, fly and orbit modes; the UI panel binds directly to `state`.

`window.tehran` exposes renderer, scene, camera, state and helpers for console debugging.

## Future Enhancements (from README)

Planned but not yet built: save/load compositions, MIDI export, multiple instruments, chord accompaniment, inserting notes at arbitrary positions, visual keyboard display, recording.
