# Luxury floor-plan renderer

Turns a 2D floor plan into ultra-luxury photoreal interior renders **whose
geometry is checked against the plan**, not just eyeballed.

```
floor plan ──► plan.json ──► 3D blockout ──► guide_lined.png ──► Higgsfield (GPT Image 2.5)
 (pixels)     digitize.py    engine/          (colour + edges)      "retexture pass"
                 │                                                       │
                 ▼                                                       ▼
          QA gate 0: overlay        QA gate 1: geometry_check.py  ◄── render
          plan.json back onto       (edge recall vs noise floor,      │
          the drawing               per-element recall, framing)      ▼
                                    QA gate 2: vision review vs  ──► PASS → final
                                    blockout + checklist.json        FAIL → fix cause, regenerate
```

## Why it is built this way (what the tests proved)

| Approach (same room, same camera) | Structural score |
|---|---|
| Perfect self-match (blockout vs itself) — the ceiling | 0.81 |
| Nano Banana / FLUX 3 with a design-brief prompt | 0.13–0.16 (mirrored sofa, invented windows) |
| GPT Image 2.5 with a design-brief prompt | 0.20–0.42 |
| **GPT Image 2.5, "retexture pass" prompt on the line-burned blockout** | **0.81** |

A design brief invites the model to *redesign* the room. Telling it the job
is a *material and lighting pass only* on an image that already contains every
edge locks the geometry. All taste lives in `design-system/design-system.json`;
prompts are generated from it, never hand-written.

**The automated gate isn't enough on its own.** On the production run, 3
renders passed the edge metric and were still wrong: a door invented on a blank
wall, a sauna rendered as a shower, and the G-Wagon parked backwards. Edges
can't see additions on flat surfaces or which end of a box-shaped car is the
front, so the vision review is a required gate.

## v3: consistency system (after review)

Feedback on v2: the same kitchen/decor/light looked different from view to view. Cause: decor and fittings existed only as
prompt text, so the model re-invented them per camera. Fix, in layers:
1. **Design layer** (`plans/osnova-prizemlja/design_layer.py`): pendants, chandeliers, LED lines, cushions, rug, olive tree,
   backsplash, shelf, cabinet divisions, media wall, mirrors, shower glass... modelled at fixed 3D positions.
2. **Locked material registry** (`design-system.json -> materials`): one description per material, used verbatim; the guide
   is tinted in the real colours, so it is already a colour preview of the design.
3. **Hero chaining**: one approved hero per space is IMAGE 2 for every other view of that space.
4. **Gate 3 - consistency** (`qa/consistency_check.py`): per-material colour of each view vs. its hero (mid-tones only).
5. One time of day and one exterior for the whole house.

Gates per render: geometry (auto) -> vision review (objects, openings, counts, orientation, invented items) -> consistency.

## Run it for a plan

```bash
cd luxury-render
npm --prefix engine i                                 # three + playwright-core (uses /opt/pw-browsers chromium)
pip install opencv-python-headless pillow numpy

python3 plans/<plan>/digitize.py                      # plan.json (+ opening/wall integrity check)
python3 qa/overlay_plan.py plans/<plan>/plan.json out.png   # gate 0: does the model match the drawing?
node engine/render.mjs plans/<plan>                   # blockout passes for every camera in cameras.json
python3 engine/compose_guide.py output/<plan>/*/blockout    # guide_lined.png = what the image model sees
python3 qa/build_prompt.py plans/<plan> <CAM>         # prompt.txt + checklist.json from the design system
# generate with Higgsfield (gpt_image_2_5, quality high, 2k, 16:9, image 1 = guide_lined.png)
python3 qa/record_attempt.py plans/<plan> <CAM> <label> <job_id> <url>   # gate 1 + qa_log.json
```

A new plan = new `plans/<name>/digitize.py` (pixel coordinates read off the
drawing) + `cameras.json`. The engine, QA and design system are reusable.

## Files

| Path | What |
|---|---|
| `plans/osnova-prizemlja/digitize.py` | ground floor, every element in source pixels → cm |
| `plans/osnova-prizemlja/AUDIT.md` | **assumptions + open questions — read this** |
| `plans/osnova-prizemlja/cameras.json` | 11 cameras (13 views incl. garage with/without car), per-view constraints |
| `engine/scene.js` | blockout builder + passes (guide, lines, IDs, normals, depth) |
| `qa/geometry_check.py` | gate 1 (thresholds at the top: `GATES`) |
| `qa/build_prompt.py` | prompt + checklist from plan + design system |
| `design-system/design-system.json` | palette, materials, per-room retexture maps, lighting rules |
| `output/osnova-prizemlja/review_log.json` | every generation, scores, verdicts, final URLs |

## Environment notes

This cloud container's proxy blocks `upload.higgsfield.ai` and the Higgsfield
CDN. Workaround in use: blockouts are pushed to this (public) repo and imported
with `media_import_url`. Gate 1 runs inside the Higgsfield sandbox
(`qa/sandbox_batch.py`). Allow both hosts in the environment's network settings
and everything runs locally.
