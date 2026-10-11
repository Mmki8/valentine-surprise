"""Digitize 'OSNOVA 1. SPRATA' (first floor) in SOURCE PIXELS of
source/floorplan_first.png (1600x1130) and convert to the SAME house cm frame
as the ground floor (origin = structural NW corner, x east, y south).

Scale: 1520 cm = px 202 -> 1365 (1.307), 975 cm = py 217 -> 960 (1.312)
=> 1.31 cm/px, origin (202, 217). Cross-check with the ground floor:
void west wall 940px -> 967 cm (ground 964), void north 485px -> 351 cm
(ground 352), stair hole west 492px -> 380 cm (ground 378).

Imported by plans/osnova-prizemlja/digitize.py so the whole house is one model.
Upper finished floor = 310 cm, upper ceiling = 560 cm.
"""
K = 1.31
OX, OY = 202, 217
FFL, CEIL = 310, 560


def cm(v, a):
    return round((v - (OX if a == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


Z0 = 283            # above the ground ceilings (280) incl. the 1 cm wall overlap: no coplanar z-fighting
WALLS = [
    # exterior
    ("U_W_north", (192, 210, 1152, 237), Z0, CEIL, "ext"),
    ("U_W_west", (192, 210, 222, 850), Z0, CEIL, "ext"),
    ("U_W_east_bed3", (1122, 237, 1152, 465), Z0, CEIL, "ext"),
    ("U_W_bed3_s_ext", (1122, 455, 1310, 485), Z0, CEIL, "ext"),
    ("U_W_bed1_s", (222, 830, 472, 850), Z0, CEIL, "ext"),        # glazed, see openings
    ("U_W_entry_s", (472, 940, 668, 962), Z0, CEIL, "ext"),       # upper window over entrance
    ("U_W_bed2_s", (660, 945, 930, 965), Z0, CEIL, "ext"),        # glazed door to balcony
    # interior
    ("U_W_bath1_e", (357, 237, 366, 452), Z0, CEIL, "int"),
    ("U_W_bath1_s", (222, 442, 366, 452), Z0, CEIL, "int"),
    ("U_W_bed1_e", (472, 237, 492, 850), Z0, CEIL, "int"),         # bedroom 1 / stairwell
    ("U_W_bath2_s", (492, 370, 705, 380), Z0, CEIL, "int"),
    ("U_W_bath2_e", (695, 237, 705, 380), Z0, CEIL, "int"),
    ("U_W_bed3_w", (660, 380, 668, 485), Z0, CEIL, "int"),
    ("U_W_bed3_s", (640, 465, 1122, 485), Z0, CEIL, "int"),
    ("U_W_bed2_w", (660, 485, 668, 945), Z0, CEIL, "int"),          # bedroom 2 / landing + entry void
    ("U_W_bath3_w", (765, 485, 775, 625), Z0, CEIL, "int"),
    ("U_W_bath3_s", (765, 615, 930, 630), Z0, CEIL, "int"),
    ("U_W_void_w", (920, 485, 940, 960), Z0, CEIL, "int"),          # = ground W_void_west_up (plain wall over living)
]

OPENINGS = [
    dict(id="U_O_bath1_win", type="window", px=(192, 292, 222, 360), sill=FFL + 110, head=FFL + 220, note="bathroom 1 west window"),
    dict(id="U_O_bath2_win", type="window", px=(562, 210, 610, 237), sill=FFL + 120, head=FFL + 220, note="bathroom 2 north window"),
    dict(id="U_O_bed3_win", type="sliding", px=(1118, 302, 1156, 455), sill=FFL, head=FFL + 230, note="bedroom 3 east glazed door (OG.3)"),
    dict(id="U_O_bed1_glz", type="sliding", px=(225, 826, 467, 854), sill=FFL, head=FFL + 230, note="bedroom 1 south glazing with door to balcony"),
    dict(id="U_O_bed2_glz", type="sliding", px=(770, 941, 915, 969), sill=FFL, head=FFL + 230, note="bedroom 2 south glazed door (OG.2)"),
    dict(id="U_O_entry_win", type="window", px=(580, 936, 657, 966), sill=FFL + 20, head=FFL + 230, note="tall window lighting the double-height entry"),
    dict(id="U_O_bath1_door", type="door", px=(355, 300, 368, 355), sill=FFL, head=FFL + 210),
    dict(id="U_O_bed1_door", type="door", px=(470, 393, 494, 455), sill=FFL, head=FFL + 210),
    dict(id="U_O_bath2_door", type="door", px=(693, 300, 707, 352), sill=FFL, head=FFL + 210),
    dict(id="U_O_bed3_door", type="door", px=(658, 392, 670, 455), sill=FFL, head=FFL + 210),
    dict(id="U_O_bed2_door", type="door", px=(658, 540, 670, 605), sill=FFL, head=FFL + 210),
    dict(id="U_O_bath3_door", type="door", px=(763, 555, 777, 610), sill=FFL, head=FFL + 210),
]

ROOMS = [
    dict(id="U_R_bath1", name="Bathroom 1 (bedroom 1)", px=[(222, 237), (357, 237), (357, 442), (222, 442)], style="bath_taupe"),
    dict(id="U_R_bed1", name="Bedroom 1 (south-west)", px=[(366, 237), (472, 237), (472, 830), (222, 830), (222, 452), (366, 452)], style="bedroom_cove"),
    dict(id="U_R_bath2", name="Bathroom 2 (en-suite bedroom 3)", px=[(492, 237), (695, 237), (695, 370), (492, 370)], style="bath_slate"),
    dict(id="U_R_hall", name="Upper landing", px=[(492, 380), (660, 380), (660, 672), (572, 672), (572, 485), (492, 485)], style="warm_wood_luxe"),
    dict(id="U_R_bed3", name="Bedroom 3 (north-east, master)", px=[(705, 237), (1122, 237), (1122, 465), (668, 465), (668, 380), (705, 380)], style="bedroom_noir"),
    dict(id="U_R_bath3", name="Bathroom 3 (bedroom 2)", px=[(775, 485), (920, 485), (920, 615), (775, 615)], style="bath_taupe"),
    dict(id="U_R_bed2", name="Bedroom 2 (south)", px=[(668, 485), (765, 485), (765, 630), (920, 630), (920, 945), (668, 945)], style="bedroom_cove"),
]
# open to below: stair hole + double-height entry (railings UOG.1-3)
VOIDS = [R(492, 485, 572, 945), R(572, 672, 660, 945)]

FURN = []


def box(id, kind, px, z0, h, room, facing=None, note=None):
    FURN.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=FFL + z0, h=h, room=room, facing=facing, note=note,
                     src_px=list(px), group=None))


# bedroom 1
box("U_F_bed1", "bed", (222, 605, 377, 735), 0, 50, "U_R_bed1", "E", "double bed, headboard on west wall")
box("U_F_bed1_ns1", "nightstand", (222, 567, 252, 605), 0, 50, "U_R_bed1")
box("U_F_bed1_ns2", "nightstand", (222, 735, 252, 770), 0, 50, "U_R_bed1")
box("U_F_bed1_tvunit", "low_cabinet", (442, 610, 470, 725), 0, 45, "U_R_bed1", "W")
box("U_F_bed1_tv", "tv", (466, 625, 470, 710), 100, 70, "U_R_bed1", "W")
box("U_F_bed1_wr1", "tall_cabinet", (222, 452, 366, 495), 0, 240, "U_R_bed1", "S", "wardrobes")
box("U_F_bed1_wr2", "tall_cabinet", (366, 237, 472, 280), 0, 240, "U_R_bed1", "S", "wardrobes")
# bathroom 1
box("U_F_bath1_vanity", "vanity", (232, 240, 357, 282), 80, 10, "U_R_bath1", "S")
box("U_F_bath1_wc", "toilet", (232, 325, 275, 355), 0, 40, "U_R_bath1", "E")
box("U_F_bath1_shower", "shower", (222, 375, 357, 442), 0, 3, "U_R_bath1")
# bathroom 2
box("U_F_bath2_shower", "shower", (492, 237, 552, 370), 0, 3, "U_R_bath2")
box("U_F_bath2_wc", "toilet", (570, 247, 600, 290), 0, 40, "U_R_bath2", "S")
box("U_F_bath2_vanity", "vanity", (615, 237, 695, 277), 55, 30, "U_R_bath2", "S")
# bedroom 3 (master)
box("U_F_bed3", "bed", (912, 242, 1040, 397), 0, 50, "U_R_bed3", "S", "king bed, headboard on north wall")
box("U_F_bed3_ns1", "nightstand", (875, 240, 912, 272), 0, 50, "U_R_bed3")
box("U_F_bed3_ns2", "nightstand", (1040, 240, 1077, 272), 0, 50, "U_R_bed3")
box("U_F_bed3_wr1", "tall_cabinet", (705, 237, 800, 280), 0, 240, "U_R_bed3", "S", "wardrobes")
box("U_F_bed3_wr2", "tall_cabinet", (800, 237, 842, 380), 0, 240, "U_R_bed3", "E", "wardrobes")
box("U_F_bed3_tvunit", "low_cabinet", (927, 450, 1022, 465), 0, 45, "U_R_bed3", "N")
box("U_F_bed3_tv", "tv", (935, 461, 1015, 465), 100, 55, "U_R_bed3", "N")
# bathroom 3
box("U_F_bath3_vanity", "vanity", (775, 490, 840, 525), 80, 10, "U_R_bath3", "S")
box("U_F_bath3_shower", "shower", (860, 485, 920, 560), 0, 3, "U_R_bath3")
box("U_F_bath3_wc", "toilet", (870, 570, 915, 605), 0, 40, "U_R_bath3", "N")
# bedroom 2
box("U_F_bed2", "bed", (770, 705, 920, 835), 0, 50, "U_R_bed2", "W", "double bed, headboard on east wall")
box("U_F_bed2_ns1", "nightstand", (885, 670, 920, 705), 0, 50, "U_R_bed2")
box("U_F_bed2_ns2", "nightstand", (885, 835, 920, 870), 0, 50, "U_R_bed2")
box("U_F_bed2_closet", "tall_cabinet", (680, 485, 765, 550), 0, 240, "U_R_bed2", "S")
# railings (UOG.1/2/3), frameless glass 100 cm
# UOG.1 (px 567-572, y 672-945) is the stair's own raked glass balustrade - modelled with the stair (ground digitize.py)
box("U_F_rail2", "glass", (570, 485, 575, 672), 0, 100, "U_R_hall", None, "UOG.2")
box("U_F_rail3", "glass", (572, 670, 660, 675), 0, 100, "U_R_hall", None, "UOG.3")


def export():
    walls = [dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px), level="upper") for i, px, z0, z1, k in WALLS]
    ops = [{**{k: v for k, v in o.items() if k != "px"}, "rect": R(*o["px"]), "src_px": list(o["px"]), "level": "upper"} for o in OPENINGS]
    rooms = [dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=FFL, ceiling=CEIL, style=r["style"], level="upper")
             for r in ROOMS]
    return walls, ops, rooms, FURN, VOIDS
