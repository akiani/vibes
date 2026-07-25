# Tehran 3D — تهران

A walkable, procedurally generated 3D model of Tehran, Iran, built with three.js in a single
self-contained HTML file. Walk the streets from the bazaar to the foot of the Alborz, fly over the
city, and pull the simulation apart with a control panel: time of day, season, air pollution,
weather, traffic and crowds.

Open `index.html` in a modern browser. No build step, no server.

```
# macOS
open tehran-3d/index.html
# Linux
xdg-open tehran-3d/index.html
```

## The city it models

Landmarks and streets are placed from **real latitude/longitude**, projected into a local metric
frame centred on Enghelab Square (35.70°N, 51.40°E). Horizontal distances are compressed ≈2.2×
(`GEO_SCALE = 0.45`) so the 30 km city is walkable in a few minutes; vertical scale is 1:1, so a
45 m tower is 45 m tall. Every landmark therefore sits at its true bearing and relative distance
from every other one.

### Geography

Tehran is built on the southern slope of the **Alborz**, and the whole city tilts: about 1,050 m
above sea level in the south, over 1,600 m in the north. The terrain here reproduces that tilt —
walking north is uphill — and closes the city with a mountain wall rising to **Mt Tochal**
(3,964 m). **Mt Damavand** (5,610 m) stands on the ENE horizon, visible only when the air is clean.

### Landmarks modelled

| Landmark | فارسی | Notes |
|---|---|---|
| Azadi Tower | برج آزادی | Hossein Amanat, 1971. Broken Sassanid vault, white marble, 45 m |
| Milad Tower | برج میلاد | 435 m, tapering octagonal shaft, 12-storey head pod, antenna |
| Tabiat Bridge | پل طبیعت | Leila Araghian, 2014. Three curving decks over Modarres Expressway |
| Grand Bazaar | بازار بزرگ | Vaulted brick lanes with domes and oculi — you can walk inside |
| Golestan Palace | کاخ گلستان | Qajar arcaded range, tiled spandrels, Shams-ol-Emareh, garden pool |
| National Museum of Iran | موزه ملی ایران | Godard's brick block with its Ctesiphon-style iwan |
| Imamzadeh Saleh | امامزاده صالح | Tajrish shrine: turquoise dome, twin minarets, arcaded courtyard |
| Museum of Contemporary Art | موزه هنرهای معاصر | Kamran Diba's concrete spiral with wind-catcher skylights |
| Azadi Stadium | ورزشگاه آزادی | The 78,000-seat bowl in the west |
| Tochal Gondola | تله‌کابین توچال | Cabins climbing from Velenjak toward the summit |

Plus the armature of the real city: **Valiasr Street** running 28 km from the south to Tajrish,
Enghelab/Azadi, Karim Khan, Motahari, Mirdamad, Shariati, the Hemmat, Modarres, Chamran, Navvab
and Resalat expressways, eleven squares (Azadi, Enghelab, Vanak, Tajrish, Imam Khomeini,
Haft-e Tir, Ferdowsi…) and eight parks (Laleh, Mellat, Ab-o-Atash, Jamshidieh, Bagh-e Ferdows…).

### The fabric between the landmarks

Everything else is generated: ~9,000 buildings placed lot-by-lot along the street network, with
district profiles that follow Tehran's real social section — low, dense and old in the south;
mid-rise brick in the centre; stone and glass towers climbing north toward Vanak, Mirdamad and
Shahrak-e Gharb; gardens at the foot of the mountains. Facades are procedurally painted canvas
textures (brick courses, balconies, air-conditioners, curtains, sun-bleached streaks) that tile
correctly whatever the building's size, with a separate emissive layer so windows light up at
night. Roofs carry water tanks, AC units, satellite dishes and stair houses. Streets get plane
trees (چنار), lamps, signals, benches, zebra crossings and the **jub** — the open water channel
that runs along Tehran's curbs.

## Controls

| | |
|---|---|
| <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> | walk / fly |
| <kbd>Shift</kbd> | run |
| <kbd>Space</kbd> / <kbd>C</kbd> | jump, crouch (up / down while flying) |
| <kbd>E</kbd> | what is this? — info on the nearest landmark |
| <kbd>F</kbd> | toggle fly mode |
| <kbd>M</kbd> | minimap · <kbd>H</kbd> hide the UI |
| <kbd>1</kbd>–<kbd>4</kbd> | dawn / noon / sunset / night |
| <kbd>Esc</kbd> | release the mouse |

Click the canvas to capture the mouse. **Orbit** mode gives you a drag-to-look camera instead.

### Simulation panel

- **Time & sky** — hour of day, time flow (up to 240 simulated minutes per second), day of year.
  The sun is computed from the real solar equations for 35.7°N, so the arc and the season are right.
- **Weather & air** — clear / haze / overcast / rain, wind, snow line on the Alborz, and an
  **air pollution** slider that runs from a rare clear day to the inversion weeks when Tehran
  closes its schools. It drives turbidity, mie scattering, fog colour and density, and exposure.
- **City life** — traffic density and speed, pedestrian density, ambient city sound (procedural
  traffic rumble and horns via Web Audio), landmark labels.
- **Graphics** — quality preset, shadows, bloom, ambient occlusion, draw distance, exposure.
- **Teleport** — fifteen vantage points, including two aerial ones.

## Technical notes

- **three.js 0.161** from unpkg (ES modules + importmap); no local copies, no bundler.
- Everything is drawn from **instanced meshes and merged geometry**: the whole city fabric is a
  handful of draw calls, one per facade style, with per-instance colour and a vertex-shader trick
  that scales UVs by each instance's dimensions so texture density stays constant.
- All textures are painted at load time onto canvases — brick, asphalt, pavement, marble, girih
  tile, plane-tree bark, roof gravel — with normal maps derived from their luminance.
- Sky, sun, moon, stars and the PMREM environment map are re-derived whenever time or weather
  changes, so reflections and ambient light always match the sky.
- Collision and building placement share one 6 m occupancy grid; the ground under your feet comes
  from the analytic terrain function, with raycasts against platforms (Tabiat Bridge, the Azadi
  plinth, palace courtyards) so you can walk up onto them.
- The sun's shadow box follows the camera, keeping crisp shadows in the ~450 m around you.

`window.tehran` exposes `{ renderer, scene, camera, state, LANDMARKS, teleport, terrainHeight, geo }`
in the console if you want to poke at the model.

## Files

- `index.html` — the whole thing: UI, styles and the simulation
- `README.md` — this file

## Caveats

It is a *portrait*, not a survey. Street geometry beyond the named arterials is invented, building
footprints are procedural, and horizontal distances are compressed. Landmark positions, heights,
street names and the north–south logic of the city are real.
