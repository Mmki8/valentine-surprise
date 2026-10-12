# House type 5, first floor: plan audit

Source: `source/floorplan_sprat.png` (client sheet 27.png, OSNOVA SPRATA, 1645 + 60 × 1000 + 85 cm).
Model: the same model as the ground floor (`../tip5-prizemlje/digitize.py` + `design_upper.py`). First-floor elements
have level `upper`, a floor at 310 cm and a ceiling at 590 cm. `digitize.py` here rebuilds it and copies `plan.json`.
Check: `plan_check.png` overlays every modelled first-floor wall, opening and furniture piece on the drawing.

## Registration with the ground floor
The two sheets share the scale (1.313 cm/px) and have identical outer walls. The first-floor sheet px + (1, 28) lands on
the ground sheet. Verified on the north wall (185 → 213), the south wall (925 → 953), the master/bedroom party wall
(602–622 = ground 605–624) and the stair (469–546 → 497–574).

## As drawn (modelled 1:1)
| Zone | Plan | Model |
|---|---|---|
| Bedroom 1 (NW) | bed head north, nightstands, wardrobe east, TV south, OG.4 full-height french window west | as drawn, glass Juliet rail outside |
| Bath 1 / Bath 2 | ensuites of bedrooms 1/2 (doors from the alcoves), shower, WC north under a high window, basin on the south wall | as drawn |
| Bedroom 2 (NE) | mirror of bedroom 1, OG.3 full-height window east | as drawn |
| Corridor + landing | doors to bedrooms 1/2, open to the gallery | as drawn |
| Gallery office | angled desk (30°), desk chair, 2 lounge chairs; UOG.2 glass balustrade at the slab edge; OG.2 glazed door south | as drawn |
| Stair | 16 treads from px 1259 to the slab at px 905 (17 risers of 18.2 cm), UOG.1 glass | ground model corrected to match |
| Master (SW) | walk-in (wardrobes N + W + island), door from the gallery, bed head east, TV on the ensuite wall, OG.1 sliding south | as drawn |
| Master ensuite | 2 basins west, WC, walk-in shower south, door from the walk-in | as drawn |

## Consequences for the ground floor
- The high-ceiling edge is the upper slab edge with the UOG.2 glass (ground px 911 = the west edge of the dining table),
  not px 875. There is no wall above the kitchen. Ground views 01/02 were edited to show the open gallery.
- The large abstract painting moved from that wall to the gallery's back wall (master east wall), where it is
  still seen from the living.
- Double-height ceiling = first-floor ceiling = 5.9 m (310 + 280).

## Assumptions
1. First-floor clear height 2.8 m (not drawn).
2. OG.1–OG.4 are full-height glazed doors/windows. Because there is no balcony on the plan, each has a frameless glass Juliet rail.
3. The west slatted element outside the master (px 75–179) is an exterior pergola. It is not visible from inside.
