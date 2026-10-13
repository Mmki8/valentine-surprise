# Plan audit - OSNOVA PRIZEMLJA (house type 3, ground floor)

Every element in `plan.json` is traced to pixels of `source/floorplan_prizemlje.png` (see `digitize.py`);
`plan_check.png` draws the model back over the drawing (walls red, openings blue, furniture green) - it matches.
Scale from the drawing's own dimension chains: 1326 cm = px 182 -> 1192, 1000 cm = py 301 -> 1063, 1365 cm = py 69 -> 1108
=> **1.313 cm/px** (all three agree within 0.1 %; the same scale as the souterrain sheet).

## Rooms found
| Room | Contents on plan | Level |
|---|---|---|
| Garage | 1 car (drawn nose-in), sectional door north, small west window, door to the entry | entry level |
| Entry hall + corridor | front door + full-height glazing (north), installation shaft, stair to the 1st floor along the north wall, 4 wide steps up to the living level | entry level |
| Guest WC | wall-hung WC, long counter with basin, duct box | entry level |
| Spa | round jacuzzi D 170, walk-in shower, glass-fronted sauna, full-height glass to the east terrace, glass door to the back vestibule | entry level |
| Back vestibule | back door (north) | entry level |
| Living + kitchen + dining | L-sofa, 2 armchairs, 2 coffee tables, TV unit on the spa wall, kitchen run (fridge `*`, sink), island with cooktop joined to a table for 6, round column, south glazing OG.1 (2 sliding sets), east glazing to the terrace | living level |
| Bedroom + lobby | double bed (headboard west), 2 nightstands, 2-module wardrobe, sliding glass door south (OG.2) | living level |
| Bathroom | shower, basin, WC under a small west window | living level |
| East terrace | entry-level part by the spa, 4 steps, living-level part with glass railings OG.3 / OG.4 | both |

## Assumptions (a floor plan has no heights)
| # | Assumption |
|---|---|
| P1 | **Split level** - 4 risers drawn across the hall (py 497/520/543/565) and the same 4 risers outside on the terrace (py 648-716): the entry / spa / garage side sits **60 cm lower** than the living / bedroom side. Direction (living higher) chosen because the souterrain bedrooms lie under the living and need the height. |
| P2 | One flat ceiling at +2.80 (living 2.80 m clear, entry and spa 3.40 m) |
| P3 | Stair DOWN to the souterrain (corrected): it lies exactly over the souterrain stair and its treads are drawn solid over the whole run; 16 goings of 30 cm visible, risers of 15 cm, descending east |
| P4 | OG.1 / OG.2 / OG.3 / OG.4 = frameless glass railings (OG = ograda). The south glass is a French balcony; the garden lies a full storey below (souterrain walk-out). |
| P5 | Car modelled at the real size of a Mercedes S-Class LWB (5.18 x 1.92 m) - longer than the drawn symbol; it fits with ~48 cm behind and ~33 cm in front |
| P6 | Double line between the back vestibule and the spa read as a glass sliding door |

## Open questions
1. Is the living side really the higher one (P1)? If the entry side is higher, the steps flip - tell me and I re-render the two hall views.
2. North direction still assumed (sun from the south-west through the living glass).
