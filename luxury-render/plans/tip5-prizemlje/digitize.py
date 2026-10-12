"""Digitize 'OSNOVA PRIZEMLJA' of house type 5 (ground floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_prizemlje.png (1600x1132), measured by pixel scans of
the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chain: 1705 cm = ticks px x 140 -> 1439 (1299 px) -> 1.3125 cm/px
=> 1.313 cm/px (same as every sheet). Origin = outer NW corner of the garage (131, 183).

Client: the ceiling is HIGHER over the living room up to the dining table, normal height over the kitchen and
everything west of it. The first-floor plan (OSNOVA SPRATA, ../tip5-sprat) fixes the exact edge: the upper slab ends at
the UOG.2 glass balustrade, px x 911 on this sheet (first-floor sheet px + (1, 28)), i.e. the west edge of the dining table;
behind the glass is the first-floor gallery / office overlooking the living. No wall above the kitchen.
The first floor is modelled in this same file (level "upper", floor at FL) so both floors share one geometry.
Stair: the drawing shows the lowest treads (px x 1171-1259) and a floor-level landing east of them (1260-1374) with the
UOG.1 glass balustrade along their open south side -> the stair rises WEST along the north wall of the living to an
upper floor (the treads above the cut plane are not drawn); it arrives at the upper slab over the kitchen side.
Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 131, 183


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 280            # ASSUMED clear height (kitchen, hall, bedroom, garage, spa wing)
VH = 590           # double-height ceiling over living + dining = first-floor ceiling (FL + 280)
FL = 310           # floor-to-floor to the upper floor the stair rises to
XV = 911           # px: upper slab edge / UOG.2 glass (first-floor plan) - west edge of the dining table
LEVELS = {"ffl": 0, "ceiling": H, "high_ceiling": VH, "upper_ffl": FL, "upper_ceiling": VH}
DY1 = 28           # first-floor sheet px -> this sheet px: (x + 1, y + 28)

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    # envelope
    ("W_north", (131, 183, 1327, 212), 0, H, "ext"),            # side entrance door + bath window
    ("W_gar_w", (131, 183, 160, 497), 0, H, "ext"),             # sectional garage door (west)
    ("W_gar_s", (131, 477, 625, 497), 0, H, "ext"),             # garage | hall (west end faces the porch)
    ("W_hall_w", (253, 497, 282, 657), 0, H, "ext"),            # front door
    ("W_bed_w", (180, 657, 210, 985), 0, H, "ext"),
    ("W_south_w", (180, 954, 887, 985), 0, H, "ext"),           # bedroom sliding glass, kitchen side door
    ("W_col_s", (887, 955, 918, 1025), 0, VH, "ext"),           # pier at the south-west corner of the living
    ("W_south_glz", (918, 980, 1405, 990), 0, VH, "ext"),       # living south glazing (high)
    ("W_east_glz", (1395, 610, 1410, 990), 0, VH, "ext"),       # living east glazing (high)
    ("W_east_n", (1395, 467, 1410, 610), 0, VH, "ext"),         # east wall north of the glazing
    ("W_fin", (1374, 578, 1448, 610), 0, VH, "ext"),            # column + projecting fin on the east facade
    ("W_col_ne", (1374, 467, 1395, 497), 0, VH, "ext"),
    ("W_ne", (1327, 467, 1374, 497), 0, VH, "ext"),             # exterior wall north of the living, east of the spa
    ("W_spa_e", (1297, 183, 1327, 497), 0, VH, "ext"),           # spa east glazing (sliding)
    # interior
    ("W_gar_e", (616, 212, 624, 477), 0, H, "int"),             # garage | utility + hall (2 doors)
    ("W_util_e", (757, 212, 765, 391), 0, H, "int"),            # utility | bath
    ("W_util_s", (624, 383, 757, 391), 0, H, "int"),            # utility | hall
    ("W_bath_s", (765, 383, 887, 391), 0, H, "int"),            # bath | corridor (door)
    ("W_bath_e", (887, 212, 895, 390), 0, H, "int"),            # bath | sauna
    ("W_corr_e", (887, 390, 895, 477), 0, H, "int"),            # corridor | spa (door)
    ("W_sauna_s", (895, 382, 950, 390), 0, H, "int"),           # sauna front (glass door east of it = design)
    ("W_sauna_e", (1010, 212, 1017, 327), 0, H, "int"),         # sauna | shower (glass below = design)
    ("W_spa_s1", (762, 477, XV, 497), 0, H, "int"),             # spa wing | kitchen side
    ("W_spa_s2", (XV, 477, 1297, 497), 0, VH, "int"),           # spa wing | living (rises with the high ceiling)
    ("W_bed_n", (180, 657, 624, 676), 0, H, "int"),             # bedroom | hall (door); west end faces the porch
    ("W_bed_e", (605, 676, 624, 954), 0, H, "int"),             # bedroom | kitchen run
    ("W_bath2_n", (210, 795, 354, 804), 0, H, "int"),           # bedroom | ensuite (door)
    ("W_bath2_e", (346, 804, 354, 954), 0, H, "int"),
]

# ---------------------------------------------------------------- openings
openings = [
    dict(id="O_gar_door", type="garage_door", px=(131, 232, 160, 461), sill=0, head=240, note="sectional garage door (west)"),
    dict(id="O_side_door", type="door", px=(647, 183, 704, 212), sill=0, head=230, hinge=(704, 212), leaf="solid",
         note="side entrance (north) into the utility room"),
    dict(id="O_bath_win", type="window", px=(772, 183, 826, 212), sill=150, head=230, note="bath window (north)"),
    dict(id="O_gar_door1", type="door", px=(616, 271, 624, 326), sill=0, head=210, hinge=(624, 326), leaf="solid",
         note="garage -> utility"),
    dict(id="O_gar_door2", type="door", px=(616, 402, 624, 463), sill=0, head=210, hinge=(616, 463), leaf="solid",
         note="garage -> hall"),
    dict(id="O_bath_door", type="door", px=(777, 383, 830, 391), sill=0, head=210, hinge=(777, 383), leaf="solid",
         note="corridor -> bath"),
    dict(id="O_spa_door", type="door", px=(887, 405, 895, 466), sill=0, head=210, hinge=(895, 405), leaf="solid",
         note="corridor -> spa"),
    dict(id="O_spa_glz", type="sliding", px=(1297, 277, 1327, 470), sill=0, head=240, note="spa east: sliding glass to the garden"),
    dict(id="O_front_door", type="door", px=(253, 558, 282, 630), sill=0, head=240, hinge=(282, 628), leaf="solid",
         note="front door (west, from the covered porch)"),
    dict(id="O_bed_door", type="door", px=(373, 657, 437, 676), sill=0, head=210, hinge=(376, 676), leaf="solid",
         note="hall -> bedroom"),
    dict(id="O_bath2_door", type="door", px=(280, 795, 333, 804), sill=0, head=210, hinge=(333, 795), leaf="solid",
         note="bedroom -> ensuite"),
    dict(id="O_bed_glz", type="sliding", px=(362, 954, 516, 985), sill=0, head=240, note="bedroom south: sliding glass"),
    dict(id="O_kit_door", type="door", px=(682, 954, 745, 985), sill=0, head=230, hinge=(685, 970), leaf="solid",
         note="kitchen side door (south) to the terrace"),
    dict(id="O_liv_s_glz", type="curtain", px=(918, 980, 1395, 990), sill=0, head=VH - 20, transom=280,
         mullions_px=[1030, 1148, 1262], note="living south: high glazing"),
    dict(id="O_liv_e_glz", type="curtain", px=(1395, 610, 1410, 980), sill=0, head=VH - 20, transom=280,
         mullions_px=[725, 955], note="living east: high glazing, sliding part 795-900"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="T_R_garage", name="Garage", px=[(160, 212), (616, 212), (616, 477), (160, 477)], style="garage_walnut"),
    dict(id="T_R_util", name="Utility", px=[(624, 212), (757, 212), (757, 383), (624, 383)], style="laundry_dark"),
    dict(id="T_R_bath", name="Bath", px=[(765, 212), (887, 212), (887, 383), (765, 383)], style="bath_chevron"),
    dict(id="T_R_sauna", name="Sauna", px=[(895, 212), (1010, 212), (1010, 382), (895, 382)], style="sauna_walnut"),
    dict(id="T_R_spa", name="Spa", px=[(1017, 212), (1297, 212), (1297, 477), (895, 477), (895, 390), (1017, 390)],
         style="spa_dark"),
    dict(id="T_R_hall", name="Hall + kitchen", px=[(282, 497), (624, 497), (624, 391), (887, 391), (887, 477), (762, 477),
                                                    (762, 497), (905, 497), (905, 573), (XV, 573), (XV, 954), (624, 954), (624, 657), (282, 657)], style="kitchen_oak"),
    dict(id="T_R_living", name="Living + dining (high)", px=[(905, 497), (1395, 497), (1395, 980), (918, 980), (918, 954),
                                                              (XV, 954), (XV, 573), (905, 573)], style="living_void", ceiling=VH),
    dict(id="T_R_bed", name="Bedroom", px=[(210, 676), (605, 676), (605, 954), (354, 954), (354, 795), (210, 795)],
         style="bed_dark5"),
    dict(id="T_R_bath2", name="Ensuite", px=[(210, 804), (346, 804), (346, 954), (210, 954)], style="bath_dark"),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None, group=None, **kw):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=group, **kw))


def rounded(x0, y0, x1, y1, r, n=6):
    import math
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append([round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)])
    return pts


def rbox(id, kind, px, z0, h, room, r=10, note=None, group=None, **kw):
    x0, y0, x1, y1 = R(*px)
    F.append(dict(id=id, kind=kind, shape="prism", axis="z", poly=rounded(x0, y0, x1, y1, r), z0=z0, h=h, room=room,
                  note=note, src_px=list(px), group=group, **kw))


def cyl(id, kind, cxpx, cypx, r, z0, h, room, note=None, group=None):
    F.append(dict(id=id, kind=kind, shape="cyl", center=P(cxpx, cypx), r=r, z0=z0, h=h, room=room, note=note, group=group))


# utility
box("T_F_washer", "appliance", (625, 333, 672, 381), 0, 85, "T_R_util", "S", "washer")
box("T_F_dryer", "appliance", (672, 333, 720, 381), 0, 85, "T_R_util", "S", "dryer")
box("T_F_util_tall", "tall_cabinet", (725, 212, 757, 383), 0, 240, "T_R_util", "W", "tall cabinets (purple line)")
# bath (north)
box("T_F_wc", "toilet", (785, 212, 812, 262), 0, 40, "T_R_bath", "S")
rbox("T_F_vanity", "vanity", (847, 272, 887, 352), 55, 30, "T_R_bath", r=5, note="floating vanity on the east wall")
# sauna + spa
box("T_F_sauna_b1", "bench", (895, 212, 947, 382), 0, 45, "T_R_sauna", note="lower sauna bench")
box("T_F_sauna_b2", "bench", (895, 212, 922, 382), 45, 45, "T_R_sauna", note="upper sauna bench")
box("T_F_shower", "shower", (1017, 212, 1097, 287), 0, 3, "T_R_spa", note="walk-in shower")
cyl("T_F_jacuzzi", "jacuzzi", 1214, 288, 85, 0, 62, "T_R_spa", note="round jacuzzi D 1.70 m")
# hall
box("T_F_hall_wr", "tall_cabinet", (282, 497, 624, 540), 0, 250, "T_R_hall", "S", "hall wardrobe, 4 bays")
# bedroom
box("T_F_wr1", "tall_cabinet", (210, 676, 255, 795), 0, 250, "T_R_bed", "E", "wardrobe (L, west)")
box("T_F_wr2", "tall_cabinet", (255, 676, 355, 710), 0, 250, "T_R_bed", "S", "wardrobe (L, north)")
box("T_F_bed", "bed", (450, 750, 602, 880), 0, 50, "T_R_bed", "W", "double bed, headboard on the east wall", head_h=125)
rbox("T_F_ns1", "nightstand", (572, 715, 605, 750), 0, 50, "T_R_bed", r=5)
rbox("T_F_ns2", "nightstand", (572, 880, 605, 917), 0, 50, "T_R_bed", r=5)
# ensuite
rbox("T_F_vanity2", "vanity", (210, 817, 247, 882), 55, 30, "T_R_bath2", r=4, note="floating vanity on the west wall")
box("T_F_shower2", "shower", (210, 885, 277, 952), 0, 3, "T_R_bath2", note="walk-in shower")
box("T_F_wc2", "toilet", (297, 900, 327, 954), 0, 40, "T_R_bath2", "N")
# kitchen: tall run (with fridge *) + base run with sink along the bedroom wall, island with the cooktop at its south end
box("T_F_k_tall", "tall_cabinet", (624, 657, 670, 795), 0, 240, "T_R_hall", "E", "tall units + fridge (*)")
box("T_F_k_run", "counter", (624, 795, 670, 952), 0, 92, "T_R_hall", "E", "base run with sink")
box("T_F_k_sink", "sink", (628, 827, 667, 867), 88.5, 4, "T_R_hall")
rbox("T_F_island", "island_x", (762, 658, 830, 898), 0, 92, "T_R_hall", r=5, note="island, cooktop at the south end")
box("T_F_k_cooktop", "cooktop", (766, 831, 805, 875), 92, 1, "T_R_hall")
# dining (under the high ceiling): table for 6
rbox("T_F_table", "table_r", (912, 720, 973, 853), 72, 4, "T_R_living", r=12, note="dining table for 6")
for i, cy in enumerate((743, 785, 828)):
    cyl(f"T_F_chair_w{i}", "chair", 905, cy, 22, 0, 46, "T_R_living")
    cyl(f"T_F_chair_e{i}", "chair", 981, cy, 22, 0, 46, "T_R_living")
# living: 3-seat sofa facing east, 2 coffee tables, 2 armchairs facing north, TV
rbox("T_F_sofa", "sofa", (1071, 652, 1139, 857), 0, 40, "T_R_living", r=16, note="3-seat sofa facing east")
rbox("T_F_ct1", "coffee_table", (1195, 700, 1243, 747), 0, 36, "T_R_living", r=12)
rbox("T_F_ct2", "coffee_table", (1215, 752, 1262, 798), 0, 30, "T_R_living", r=12)
rbox("T_F_arm1", "armchair", (1175, 869, 1233, 930), 0, 42, "T_R_living", r=18)
rbox("T_F_arm2", "armchair", (1252, 869, 1312, 930), 0, 42, "T_R_living", r=18)
box("T_F_tv", "tv", (1372, 620, 1375, 712), 95, 68, "T_R_living", "W", "TV on a freestanding walnut media wall (plan: TV stand at the glass)")

# stair: rises WEST along the north wall from the floor-level landing (px 1260-1374). The first-floor plan draws the whole
# flight: 16 treads from px 1259 to the upper slab at px 905 (17 risers of FL/17).
NT = 16
rise, go = FL / (NT + 1), (1259 - 905) / NT * K
SY0, SY1 = cm(497, "y"), cm(573, "y")
for k in range(1, NT + 1):
    xe = cm(1259, "x") - go * (k - 1)
    F.append(dict(id=f"T_F_stair_{k:02d}", kind="stair", shape="box", rect=[round(xe - go, 1), SY0, round(xe, 1), SY1],
                  z0=round(rise * k - 6, 1), h=6, room="T_R_living", group=None))
xs, xt = cm(1259, "x"), cm(1259, "x") - go * NT
F.append(dict(id="T_F_uog1", kind="glass", shape="prism", axis="y", y0=cm(573, "y"), y1=cm(575, "y"), room="T_R_living", group=None,
              poly=[[round(xs - go, 1), round(rise, 1)], [round(xt, 1), round(rise * NT, 1)], [round(xt, 1), round(rise * NT + 100, 1)],
                    [round(xs - go, 1), round(rise + 100, 1)]], note="UOG.1 raked glass balustrade"))

# ======================================================================== FIRST FLOOR (OSNOVA SPRATA, level "upper")
# All px below are already shifted onto this sheet: first-floor sheet px + (1, 28). Floor at FL, ceiling at VH.
U = FL
walls_up = [
    ("V_W_north", (131, 183, 1297, 213), "ext"),            # bath windows
    ("V_W_west1", (131, 213, 161, 478), "ext"),             # OG.4 french window (bedroom 1)
    ("V_W_s1", (131, 478, 623, 497), "int"),                # bedroom 1 | master + walk-in
    ("V_W_b1w", (516, 213, 521, 386), "int"),               # bedroom 1 | bath 1
    ("V_W_b1s", (521, 378, 723, 386), "int"),               # bath 1 south (door from the bedroom-1 alcove)
    ("V_W_b12", (723, 213, 732, 386), "int"),               # bath 1 | bath 2
    ("V_W_b2s", (732, 378, 941, 386), "int"),               # bath 2 south (door from the bedroom-2 alcove)
    ("V_W_b2e", (933, 213, 941, 386), "int"),               # bath 2 | bedroom 2 wardrobe
    ("V_W_bed1e", (616, 386, 623, 478), "int"),             # bedroom 1 door
    ("V_W_bed2w", (834, 386, 841, 478), "int"),             # bedroom 2 door
    ("V_W_corr_s", (762, 478, XV, 497), "int"),             # corridor / bedroom 2 | landing + stair top
    ("V_W_mw", (180, 497, 209, 953), "ext"),                # master west
    ("V_W_south", (180, 953, 887, 983), "ext"),             # OG.1 (master), OG.2 (gallery)
    ("V_W_me", (603, 497, 623, 953), "int"),                # master | gallery (master door)
    ("V_W_wic", (459, 497, 467, 645), "int"),               # walk-in partition
    ("V_W_wics", (406, 638, 467, 645), "int"),
    ("V_W_mbn", (209, 638, 346, 645), "int"),               # ensuite north (door)
    ("V_W_mbe", (336, 645, 346, 894), "int"),               # ensuite | bedroom (TV on its east face); glass below 894 = design
]
openings += [
    dict(id="O_u_bath1_win", type="window", px=(656, 183, 706, 213), sill=U + 120, head=U + 220, note="bath 1 window (north)"),
    dict(id="O_u_bath2_win", type="window", px=(773, 183, 823, 213), sill=U + 120, head=U + 220, note="bath 2 window (north)"),
    dict(id="O_u_og4", type="sliding", px=(131, 231, 161, 456), sill=U, head=U + 240, note="OG.4 bedroom 1: full-height french window (west)"),
    dict(id="O_u_og3", type="sliding", px=(1297, 278, 1327, 463), sill=U, head=U + 240, note="OG.3 bedroom 2: full-height window (east)"),
    dict(id="O_u_og1", type="sliding", px=(361, 953, 516, 983), sill=U, head=U + 240, note="OG.1 master: sliding glass (south)"),
    dict(id="O_u_og2", type="sliding", px=(676, 953, 745, 983), sill=U, head=U + 240, note="OG.2 gallery: glazed door (south)"),
    dict(id="O_u_bed1_door", type="door", px=(616, 406, 623, 468), sill=U, head=U + 210, hinge=(616, 468), leaf="solid", note="landing -> bedroom 1"),
    dict(id="O_u_bed2_door", type="door", px=(834, 406, 841, 468), sill=U, head=U + 210, hinge=(841, 468), leaf="solid", note="landing -> bedroom 2"),
    dict(id="O_u_bath1_door", type="door", px=(538, 378, 591, 386), sill=U, head=U + 210, hinge=(591, 378), leaf="solid", note="bedroom 1 -> bath 1"),
    dict(id="O_u_bath2_door", type="door", px=(858, 378, 915, 386), sill=U, head=U + 210, hinge=(915, 378), leaf="solid", note="bedroom 2 -> bath 2"),
    dict(id="O_u_master_door", type="door", px=(603, 550, 623, 613), sill=U, head=U + 210, hinge=(603, 613), leaf="solid", note="gallery -> master"),
    dict(id="O_u_ens_door", type="door", px=(271, 638, 326, 645), sill=U, head=U + 210, hinge=(326, 645), leaf="solid", note="master -> ensuite"),
]
rooms += [
    dict(id="V_R_bed1", name="Bedroom 1", px=[(161, 213), (516, 213), (516, 386), (616, 386), (616, 478), (161, 478)],
         style="bed_olive5", level="upper"),
    dict(id="V_R_bath1", name="Bath 1", px=[(521, 213), (723, 213), (723, 378), (521, 378)], style="bath_verde5", level="upper"),
    dict(id="V_R_bath2", name="Bath 2", px=[(732, 213), (933, 213), (933, 378), (732, 378)], style="bath_emperador5", level="upper"),
    dict(id="V_R_bed2", name="Bedroom 2", px=[(941, 213), (1297, 213), (1297, 478), (841, 478), (841, 386), (941, 386)],
         style="bed_charcoal5", level="upper"),
    dict(id="V_R_hall", name="Landing + gallery office", px=[(623, 386), (834, 386), (834, 478), (762, 478), (762, 497), (905, 497),
                                                             (905, 573), (XV, 573), (XV, 953), (623, 953)], style="gallery5", level="upper"),
    dict(id="V_R_master", name="Master bedroom + walk-in", px=[(209, 497), (603, 497), (603, 953), (346, 953), (346, 645), (209, 645)],
         style="bed_espresso5", level="upper"),
    dict(id="V_R_mbath", name="Master ensuite", px=[(209, 645), (336, 645), (336, 953), (209, 953)], style="bath_master5", level="upper"),
]
for r in rooms:
    if r.get("level") == "upper":
        r["floor"], r["ceiling"] = U, VH


def rot_poly(cxpx, cypx, wpx, hpx, deg):
    import math
    a = math.radians(deg)
    pts = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        dx, dy = sx * wpx / 2, sy * hpx / 2
        pts.append(P(cxpx + dx * math.cos(a) - dy * math.sin(a), cypx + dx * math.sin(a) + dy * math.cos(a)))
    return pts


def rprism(id, kind, cxpx, cypx, wpx, hpx, deg, z0, h, room, note=None):
    F.append(dict(id=id, kind=kind, shape="prism", axis="z", poly=rot_poly(cxpx, cypx, wpx, hpx, deg), z0=z0, h=h, room=room,
                  note=note, group=None))


# bedroom 1 (NW): bed head north, wardrobe east, TV on the south wall
box("V_F_bed1", "bed", (263, 216, 393, 368), U, 50, "V_R_bed1", "S", "double bed, head north", head_h=125)
rbox("V_F_b1ns1", "nightstand", (226, 213, 263, 246), U, 50, "V_R_bed1", r=4)
rbox("V_F_b1ns2", "nightstand", (393, 213, 429, 246), U, 50, "V_R_bed1", r=4)
box("V_F_b1wr", "tall_cabinet", (468, 213, 513, 386), U, 250, "V_R_bed1", "W", "wardrobe")
box("V_F_b1tv", "tv", (276, 474, 371, 478), U + 95, 60, "V_R_bed1", "N", "TV on the south wall")
# bath 1
box("V_F_bath1_sh", "shower", (522, 213, 619, 273), U, 3, "V_R_bath1", note="walk-in shower NW")
box("V_F_bath1_wc", "toilet", (666, 213, 696, 263), U, 40, "V_R_bath1", "S")
rbox("V_F_bath1_van", "vanity", (643, 340, 721, 378), U + 55, 30, "V_R_bath1", r=4, note="vanity on the south wall")
# bath 2
box("V_F_bath2_wc", "toilet", (770, 213, 800, 265), U, 40, "V_R_bath2", "S")
box("V_F_bath2_sh", "shower", (836, 213, 933, 273), U, 3, "V_R_bath2", note="walk-in shower NE")
rbox("V_F_bath2_van", "vanity", (732, 339, 813, 378), U + 55, 30, "V_R_bath2", r=4, note="vanity on the south wall")
# bedroom 2 (NE)
box("V_F_b2wr", "tall_cabinet", (943, 213, 989, 386), U, 250, "V_R_bed2", "E", "wardrobe")
box("V_F_bed2", "bed", (1080, 215, 1211, 369), U, 50, "V_R_bed2", "S", "double bed, head north", head_h=125)
rbox("V_F_b2ns1", "nightstand", (1043, 213, 1080, 246), U, 50, "V_R_bed2", r=4)
rbox("V_F_b2ns2", "nightstand", (1211, 213, 1247, 246), U, 50, "V_R_bed2", r=4)
box("V_F_b2tv", "tv", (1096, 474, 1191, 478), U + 95, 60, "V_R_bed2", "N", "TV on the south wall")
# master (SW): walk-in wardrobes, bed head east, TV on the ensuite partition
box("V_F_mwr1", "tall_cabinet", (209, 497, 459, 539), U, 250, "V_R_master", "S", "walk-in wardrobe north")
box("V_F_mwr2", "tall_cabinet", (467, 497, 603, 539), U, 250, "V_R_master", "S", "wardrobe north")
box("V_F_mwr3", "tall_cabinet", (209, 539, 250, 638), U, 250, "V_R_master", "E", "walk-in wardrobe west")
box("V_F_mwr4", "tall_cabinet", (413, 539, 459, 638), U, 250, "V_R_master", "W", "walk-in wardrobe island side")
rbox("V_F_mpouf", "ottoman", (472, 582, 503, 634), U, 45, "V_R_master", r=6, note="dressing pouf")
box("V_F_mbed", "bed", (448, 729, 603, 860), U, 50, "V_R_master", "W", "king bed, head east", head_h=130)
rbox("V_F_mns1", "nightstand", (572, 694, 603, 729), U, 50, "V_R_master", r=4)
rbox("V_F_mns2", "nightstand", (572, 860, 603, 897), U, 50, "V_R_master", r=4)
box("V_F_mtv", "tv", (346, 745, 349, 840), U + 95, 65, "V_R_master", "E", "TV on the ensuite partition")
# master ensuite
rbox("V_F_mb_van", "vanity", (209, 645, 247, 788), U + 55, 30, "V_R_mbath", r=4, note="double vanity on the west wall")
box("V_F_mb_wc", "toilet", (221, 830, 263, 863), U, 40, "V_R_mbath", "E")
box("V_F_mb_sh", "shower", (209, 884, 336, 953), U, 3, "V_R_mbath", note="walk-in shower south")
# gallery office (desk angled 30 deg, desk chair, two lounge chairs)
rprism("V_F_desk", "desk", 762, 846.6, 121, 54, 30.2, U + 72, 4, "V_R_hall", note="writing desk")
rprism("V_F_desk_base", "desk", 762, 846.6, 100, 40, 30.2, U, 72, "V_R_hall")
rprism("V_F_dchair", "chair", 745, 878, 40, 40, 30.2, U, 48, "V_R_hall", note="desk chair")
rprism("V_F_lc1", "armchair", 791, 749, 56, 56, 30.2, U, 42, "V_R_hall", note="lounge chair")
rprism("V_F_lc2", "armchair", 847, 787, 56, 56, 30.2, U, 42, "V_R_hall", note="lounge chair")

from design_layer import DESIGN, SITE, CAR                 # noqa: E402
import design_upper                                          # noqa: E402,F401  (appends the first-floor design to DESIGN)
F += CAR

wall_rows = []
for i, px, z0, z1, k in walls:
    if i in ("W_spa_s2", "W_spa_e"):              # walls shared with first-floor rooms: upper part samples the upper rooms
        wall_rows += [(i, px, z0, FL, k, "ground"), (i + "_up", px, FL, z1, k, "upper")]
    else:
        wall_rows.append((i, px, z0, z1, k, "ground"))
wall_rows += [(i, px, U, VH, k, "upper") for i, px, k in walls_up]

plan = dict(
    meta=dict(name="OSNOVA PRIZEMLJA + OSNOVA SPRATA - house type 5, ground + first floor", source="source/floorplan_prizemlje.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1705, 1025]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, level=lv, src_px=list(px)) for i, px, z0, z1, k, lv in wall_rows],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x" if (o["px"][2] - o["px"][0]) > (o["px"][3] - o["px"][1]) else "y") for m in o["mullions_px"]]}
                  if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=r.get("floor", 0), ceiling=r.get("ceiling", H),
                style=r["style"], level=r.get("level", "ground"), ceiling_holes=[]) for r in rooms],
    furniture=F,
    design=DESIGN,
    site=SITE,
)

problems = []
for o in openings:
    ox0, oy0, ox1, oy1 = o["px"]
    hits = [wid for wid, (x0, y0, x1, y1), z0, z1, _, _ in wall_rows if min(x1, ox1) - max(x0, ox0) > 0.5 and min(y1, oy1) - max(y0, oy0) > 0.5
            and min(z1, o["head"]) - max(z0, o["sill"]) > 0.5]
    if len(hits) != 1:
        problems.append(f"{o['id']} cuts {hits}")
if problems:
    raise SystemExit("OPENING/WALL INTEGRITY FAILED:\n  " + "\n  ".join(problems))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
json.dump(plan, open(out, "w"), indent=1)
print("wrote", out, "walls", len(plan["walls"]), "openings", len(plan["openings"]), "furniture", len(F), "design", len(DESIGN))
