# Plan audit - OSNOVA 1 SPRAT (house type 4, first floor)

Every element in `plan.json` is traced to pixels of `source/floorplan_sprat.png` (see `digitize.py`);
`plan_check.png` draws the model back over the drawing (walls red, openings blue, furniture green) - it matches.
Scale from the drawing's own dimension ticks: 1165 cm = px 392 -> 1279, 1035 cm = py 183 -> 971 => **1.313 cm/px**.
Origin = outer NW corner (383, 173) = the ground floor's origin, so plan cm coincide on both floors.

## Rooms found
| Room | Contents on plan |
|---|---|
| Bath 1 (ensuite) | walk-in shower with glass, wall-hung WC, vanity, high window north, vent pipe D110; door from bedroom 1 |
| Bedroom 1 | L wardrobe, bed head north + 2 nightstands, TV on the south wall, full-height sliding glass OG.3 east |
| Landing + gallery | stair arrives from the ground floor at its north end; gallery strip between glass balustrades UOG.2 / UOG.3 to bedroom 2 |
| Bedroom 2 | entry wardrobe (installation duct in its corner), bed head east + 2 nightstands, glazed door OG.2 to a steel balcony |
| Bath 2 (no window) | vanity, walk-in shower with shower column, wall-hung WC |
| Open to below | the whole stair + the entrance south of UOG.3 = double height; tall glazing above the front door |
| Living void | closed by plain walls (bedroom 1 south, bedroom 2 east) - no opening from this floor |

## Assumptions
| # | Assumption |
|---|---|
| F1 | Clear height 2.80 m; floor-to-floor 3.10 m; garden 3.25 m below the first floor |
| F2 | Balcony: steel grating (IPE 100 frame, 80x50 grating) as drawn; a frameless glass guard is ADDED (none drawn, required at 3 m) |
| F3 | OG.3 (bedroom 1 east) is a French balcony: frameless glass guard added in the opening |
| F4 | Entrance glazing above the front door: z -0.50 to +2.60 m (first-floor level) |
| F5 | Ground floor corrected to match this sheet: the hall ceiling is open over the whole stair and the entrance (was modelled with a ceiling) |
| F6 | New bedroom designs per the brief; baths ~70 % dark per the client's bath references |
