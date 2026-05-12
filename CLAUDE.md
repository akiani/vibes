# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running Projects

No build step, server, or package manager. Open any `index.html` directly in a modern browser:

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

This is a portfolio of standalone browser apps. Each project is self-contained with no shared code between them.

### Calculator (`calculator/`)

Single `Calculator` class that holds state (`currentOperand`, `previousOperand`, `operation`) and exposes methods called directly from DOM event listeners wired in the same file. Display formatting (thousand separators) is handled in `getDisplayNumber()` and kept separate from compute logic.

### Chopin Sonata Player (`chopin-sonata/`)

Single `ChopinSonataPlayer` class with three responsibilities initialized in the constructor:

- **Audio** (`initAudio`): Creates a `Tone.PolySynth` with a triangle oscillator routed through a `Tone.Reverb`. Playback is sequenced with recursive `setTimeout` calls (not Tone.js Transport), so tempo changes only take effect on the next play.

- **Sheet music** (`renderSheetMusic`): Uses VexFlow 4.2.3. Notes are grouped into measures via `groupNotesByMeasure()`, then each measure is rendered as a separate `VF.Stave`. VexFlow requires pitch keys in lowercase format (e.g. `"eb4"` not `"Eb4"`) — the render method calls `note.pitch.toLowerCase()`.

- **Note data model**: Each note is `{ pitch: string, duration: string, measure: number }`. Duration strings match VexFlow notation (`'1'`, `'2'`, `'4'`, `'8'`). The `regenerateSection()` method picks from C minor scale pitches `['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4', 'C5', 'D5', 'Eb5']` — new notes should stay within this set to preserve harmonic coherence.

External libraries are loaded via CDN in `index.html` (VexFlow 4.2.3, Tone.js 14.8.49) — no local copies exist.

## Future Enhancements (from README)

Planned but not yet built: save/load compositions, MIDI export, multiple instruments, chord accompaniment, inserting notes at arbitrary positions, visual keyboard display, recording.
