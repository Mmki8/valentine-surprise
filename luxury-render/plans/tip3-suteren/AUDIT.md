# Plan audit - OSNOVA SUTERENA (house type 3, souterrain / walk-out level)

Every element in `plan.json` is traced to pixels of `source/floorplan_suteren.webp` (see `digitize.py`).
Scale from the drawing's own dimension ticks: 1591 cm = px 184 -> 1396, 1000 cm = py 247.5 -> 1009
=> **1.313 cm/px** (both chains agree within 0.04 %). Wall faces were measured by pixel scans along rows/columns.

## Rooms found
| Room | Size (approx.) | Contents on plan |
|---|---|---|
| Bedroom 1 (west) | 3.2 x 4.9 m + entry hall | double bed (headboard west wall), 2 nightstands, wardrobe, 2-leaf sliding glass door south |
| Bathroom 1 | L-shape 3.2 x 2.3 m | wall-hung WC, basin in a GKPL installation wall, walk-in shower (no window) |
| Bedroom 2 / 3 (mirror pair) | 4.5 x 5.2 m each | full-height GKPL wardrobe wall with the bed against it, 2 nightstands, 3-panel south glazing, side passage from the corridor |
| Bathroom pods 2 / 3 | 3.4 x 1.7 m each | shower, vanity + basin, WC behind a GKPL partition (no window) |
| Corridor + stair | 1.2 m wide | stair rising west along the north wall behind a wall (4 treads drawn, rest dashed) |
| Laundry | 2.4 x 3.8 m | washer + dryer under a worktop run, exterior door south |
| North-east room | 2.4 x 4.2 m | **no furniture, no label** - not rendered |
| Small store | 2.4 x 1.1 m | duct box, door from corridor - not rendered |

## Assumptions (a floor plan has no heights)
| # | Assumption |
|---|---|
| S1 | Clear height **2.70 m**; floor-to-floor 3.00 m |
| S2 | Stair: **20 risers x 15 cm, 19 goings x 30 cm** - fits the drawn run px 1098 -> 664 exactly |
| S3 | North, west and east walls are retaining walls against the earth (hatching) - no windows |
| S4 | South glazing full height (2.40 / 2.50 m), bedrooms 2/3 middle leaf slides |
| S5 | Outside the glazing: stone terrace (dashed outline) then garden at the same level (walk-out) |

## Open questions
1. **North-east room** (2.4 x 4.2 m, no window, door from corridor and to the laundry): what is it? (gym, cinema, wine cellar, guest room, technical?) - tell me and I will design + render it.
2. Same north/sun question as house 1: sun assumed from the south-west.
