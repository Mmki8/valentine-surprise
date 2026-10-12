# Plan audit - OSNOVA PRIZEMLJA (house type 4, ground floor)

Every element in `plan.json` is traced to pixels of `source/floorplan_prizemlje.png` (see `digitize.py`);
`plan_check.png` draws the model back over the drawing (walls red, openings blue, furniture green) - it matches.
Scale **1.313 cm/px** (same sheet series as the basement, checked on the dimension chains).

## Rooms found
| Room | Contents on plan |
|---|---|
| Living | L-sofa, 2 armchairs, 2 round coffee tables, TV, glass walls east + south (2 mullions), double height |
| Dining + kitchen | table for 6, island with 3 stools, north run, west run with cooktop + sink, fridge column, plasterboard box (GKPL) by the stair |
| Hall + stair | front door (south), stair to the first floor with raked glass balustrade UOG.1, doors to bathroom and bedroom |
| Master bedroom | bed head north, 2 nightstands, L wardrobe, sliding glazing east |
| Bathroom | walk-in shower, wall-hung WC, vanity, small window north |

## Assumptions
| # | Assumption |
|---|---|
| G1 | Clear height 2.80 m everywhere except the living room: void 5.60 m over the living area only (client: "just living room, not kitchen and dining"); void edge = the wall line at px 852 |
| G2 | Stair rises north from py 710: 17 treads / 18 risers |
| G3 | The plan draws the TV against the east glass; it sits on a freestanding walnut media wall just in front of it (a TV cannot hang on glass) |
| G4 | South double door + front door modelled as drawn; the GKPL box is clad in fluted walnut |
| G6 | Revision 2: triptych (3 x 100 x 150 cm) centred over the sofa on the fluted walnut wall; ensuite 70 % dark (Nero Marquina, dark floor + ceiling, perimeter cove), warm cream marble only on the shower wall + vanity top |
| G5 | Golden hour, sun low through the living + bedroom glazing; light ceilings everywhere except a walnut canopy over the bed (part of the client's Master Suite ref) |

## Open questions
1. AC unit symbol on the north living wall - not modelled (hidden in the fluted walnut wall).
2. North arrow / real sun direction - golden hour light is placed for the best look, not the true orientation.
