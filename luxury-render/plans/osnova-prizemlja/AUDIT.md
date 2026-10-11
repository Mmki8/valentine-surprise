# Plan audit — OSNOVA PRIZEMLJA (ground floor)

Everything in `plan.json` is traced to pixels of `source/floorplan_ground.webp`
(see `digitize.py`). Scale is calibrated from the drawing's own dimensions
(1520 / 975 / 220 cm chains agree within 0.3 %): **1.05 cm per pixel**.
`qa/overlay_plan.py` draws the model back over the drawing — it matches.

## Rooms found

| Room | Size (approx.) | Contents on plan |
|---|---|---|
| Living (double height) | 4.9 × 6.1 m | L-sofa, 2 coffee tables, 2 armchairs, TV unit, glass east + south facades |
| Kitchen + dining | 3.4 × 5.9 m | L-kitchen (sink, cooktop, fridge `*`), island + 3 stools, table + 6 chairs |
| Entrance hall + stair | 2.2 × 7.4 m | main entrance, stair rising north, doors to mudroom/WC/spa |
| Spa | L-shaped, ~6 × 3 m | round jacuzzi ⌀170, walk-in shower, glazed slider east |
| Sauna | 1.5 × 1.7 m | two-tier bench, glass door + glass side |
| Guest WC | 1.6 × 1.7 m | wall-hung WC, long vanity with basin, high window |
| Garage | 3.3 × 6.1 m | car (drawn nose-in), low cabinets, 3 steps up to mudroom |
| Mudroom | 2.4 × 1.7 m | 2 full-height wardrobes, window |
| Laundry | 2.1 × 1.6 m | washer + dryer under worktop, exterior side door |

## Assumptions (a floor plan has no heights — confirm or correct)

| # | Assumption | Where to change |
|---|---|---|
| A1 | Ground-floor clear height **2.80 m** | `LEVELS.ceiling` in `digitize.py` |
| A2 | Double-height ceiling over living **5.60 m**, only right of the orange dashed slab edge | `LEVELS.void_ceiling` |
| A3 | Garage floor **60 cm lower** (3 treads + 4 risers drawn) | `LEVELS.garage_ffl` |
| A4 | East + south living facades are **floor-to-ceiling glass over both storeys**, transom at 2.80 m | `O_east_glazing`, `O_south_glazing` |
| ~~A5~~ | RESOLVED by the 1st-floor plan: no gallery - a plain wall rises over the living void; entry hall is double height with glass railings (UOG.1-3) | `osnova-sprat/digitize_upper.py` |
| A6 | Spa east opening is a full-height glazed slider (2.05 m) | `O_spa_glazing` |
| A7 | Mudroom + WC windows are high windows (sill 1.50 m) | `O_mud_window`, `O_wc_window` |
| A8 | Double door into dining: west leaf active, east leaf passive (dashed arc), both glazed | `O_double_door` |
| A9 | Stair modelled as straight run; the drawing shows 3 winders at the bottom | `F_stair_*` |
| A10 | `*` unit = fridge column; two small squares in kitchen corner = installation duct | furniture list |

## Open questions — I need your answer

1. **GKPL box** (65 × 105 cm, freestanding at the hall/dining boundary): chimney/fireplace, or an installation shaft? Rendered as a walnut-clad column for now. If it is a fireplace it becomes a hero element.
2. **No north arrow** on the plan → sun direction is a guess (late-afternoon sun through the big glass). Tell me which way the glass faces.
3. ~~Upper floor plan~~ — received and modelled (3 bedrooms, 3 bathrooms, landing, double-height entry).
4. Exterior view through the glass: currently left to the model (it invents hills/sea). Give me the real context (garden, city, sea…) and I'll lock it.

## Design notes (as your interior designer — the blunt version)

- **TV in front of the east glass**: solved as a freestanding walnut media wall (2.0 x 2.7 m) at the TV position - solid backing, cables hidden, glass stays clear around it.
- **Garage is tight**: 3.3 m inner width, G 63 is 1.98 m wide (2.19 m with mirrors) → ~55 cm each side. Driver door won't open fully if the low cabinets get deeper than drawn.
- **AC unit** drawn on the living north wall would sit in the middle of a 5.6 m bronze feature wall — conceal it (linear slot diffuser in the ceiling).

## First floor (OSNOVA 1. SPRATA) - assumptions
| # | Assumption |
|---|---|
| U1 | Upper finished floor +3.10 m, ceiling +5.60 m (2.50 m clear) |
| U2 | Bedroom glazing (bed 1 south, bed 2 south OG.2, bed 3 east OG.3) = full-height glazed doors to balconies |
| U3 | Railings UOG.1-3 = frameless glass, 100 cm |
| U4 | Bath 3 has no window (none drawn) |
