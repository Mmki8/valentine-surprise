# Plan audit - OSNOVA PODRUMA (house type 4, basement)

Every element in `plan.json` is traced to pixels of `source/floorplan_podrum.png` (see `digitize.py`);
`plan_check.png` draws the model back over the drawing (walls red, openings blue, furniture green) - it matches.
Scale from the drawing's own dimension chains: 880 cm = px 395.5 -> 1065, 1105 cm = px 395.5 -> 1237, 1227 cm = py 78 -> 1012
=> **1.313 cm/px** (all chains agree within 0.1 %).

## Rooms found
| Room | Contents on plan |
|---|---|
| Spa | round jacuzzi D 168, heated bench "topla klupa" (2 seats) on the north wall, walk-in shower with a glass door, door from the corridor |
| Sauna | glass-fronted (blue), benches (purple line), between WC and shower |
| WC | wall-hung WC, basin on the west wall, ventilation pipe D 110 |
| Corridor + stair | stair to the ground floor along the west wall with glass balustrade UOG.4; doors to WC, spa, garage, middle room, laundry |
| Laundry | washer + dryer, worktop run |
| Garage | 1 car (drawn nose-in toward the north), cabinet run along the middle-room wall (purple), sectional garage door south |
| Middle room | 3.2 x 4.7 m, door from the corridor, glazed sliding door to a sunken court with planter and exterior steps - **no label, no furniture: not rendered** |

## Assumptions
| # | Assumption |
|---|---|
| B1 | Clear height 2.70 m |
| B2 | Stair rises north from py 720: 16 goings x 28.9 cm, 17 risers x 17.6 cm (only the lower treads are drawn below the cut) |
| B3 | Car = Mercedes-Benz CLE Coupe at real size (4.86 x 1.86 m), as the client asked for something smaller than a G-Wagon |
| B4 | No daylight anywhere: lighting is architectural (coves, backlit slats, step lights, under-vanity, picture lights, garage lines) |

## Open question
1. **Middle room** (between the corridor and the garage, glazed door to the sunken court): what is it - gym, cinema, wine room, guest room, hobby room? Tell me and I design + render it.
