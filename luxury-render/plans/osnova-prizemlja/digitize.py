"""Digitize 'OSNOVA PRIZEMLJA' (ground floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_ground.webp
(2000x1416) so any coordinate can be checked against the drawing, then
converted to centimetres.

Scale calibration (from the drawing's own dimension chains):
  1520 cm  = structural west face (px 262) -> NE fin end (px 1708)  -> 1.0512 cm/px
   975 cm  = structural north face (py 287) -> south hall wall (py 1217) -> 1.0484 cm/px
   220 cm  = hall clear width px 622 -> 832                            -> 1.0476 cm/px
  => 1.05 cm/px, origin = structural NW corner (262, 287).

Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os

K = 1.05
OX, OY = 262, 287


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


LEVELS = {
    "ffl": 0,                 # finished floor, house
    "ceiling": 280,           # ASSUMED clear height ground floor
    "slab_top": 310,          # ASSUMED upper-floor finished level
    "void_ceiling": 560,      # ASSUMED ceiling over double-height living
    "garage_ffl": -60,        # ASSUMED: 4 risers x 15 cm down via the 3 drawn treads
}
H, VH, G = LEVELS["ceiling"], LEVELS["void_ceiling"], LEVELS["garage_ffl"]

# ---------------------------------------------------------------- walls
# rect in px, z range in cm. kind: ext (structural+insulation) | int | fin
walls = [
    # exterior envelope
    ("W_north_west",  (250, 277, 1450, 312), 0, H, "ext"),
    ("W_west",        (250, 277, 285, 1072), G, H, "ext"),
    ("W_west_fin",    (250, 1065, 290, 1125), G, H, "ext"),
    ("W_spa_east",    (1412, 287, 1450, 597), 0, H, "ext"),
    ("W_liv_north",   (1412, 585, 1665, 622), 0, VH, "ext"),   # exterior part, double height
    ("W_liv_east_n",  (1627, 585, 1665, 758), 0, VH, "ext"),
    ("W_ne_fin",      (1627, 722, 1720, 760), 0, VH, "ext"),
    ("W_se_col",      (1625, 1192, 1652, 1217), 0, VH, "ext"),
    ("W_east_glz",    (1650, 758, 1670, 1197), 0, VH, "ext"),  # fully glazed, see openings
    ("W_south_glz",   (1185, 1210, 1650, 1235), 0, VH, "ext"),  # fully glazed, see openings
    ("W_s_fin",       (1155, 1192, 1195, 1285), 0, VH, "ext"),
    ("W_south_dd",    (970, 1192, 1158, 1217), 0, H, "ext"),     # double door wall
    ("W_south_mid",   (826, 1192, 972, 1228), 0, H, "ext"),
    ("W_south_ent",   (732, 1192, 828, 1217), 0, H, "ext"),     # entrance door wall
    ("W_south_hall",  (585, 1192, 734, 1230), 0, H, "ext"),
    ("W_garage_s_e",  (585, 1065, 622, 1230), G, H, "ext"),
    ("W_garage_door", (285, 1065, 600, 1072), G, H, "ext"),     # sectional door line
    # interior
    ("W_laundry_s",   (262, 465, 495, 482), G, H, "int"),
    ("W_laundry_e",   (485, 312, 495, 465), 0, H, "int"),
    ("W_garage_e",    (600, 478, 622, 1192), G, H, "int"),
    ("W_mud_s",       (600, 478, 727, 488), 0, H, "int"),
    ("W_mud_wc",      (720, 312, 740, 488), 0, H, "int"),
    ("W_wc_s",        (727, 477, 900, 490), 0, H, "int"),
    ("W_wc_sauna",    (888, 312, 900, 487), 0, H, "int"),
    ("W_sauna_s",     (888, 477, 966, 487), 0, H, "int"),
    ("W_sauna_e",     (1042, 312, 1052, 407), 0, H, "int"),
    ("W_hall_spa",    (832, 487, 845, 597), 0, H, "int"),
    ("W_spa_s",       (832, 597, 1412, 622), 0, H, "int"),
    ("W_liv_north_up", (1180, 597, 1412, 622), H, VH, "int"),  # living feature wall above spa (double height)
    ("W_kitchen_w",   (832, 597, 858, 860), 0, H, "int"),
    ("W_sauna_glz_s", (966, 477, 1052, 487), 0, H, "int"),     # header above sauna glass door
    ("W_sauna_glz_e", (1042, 407, 1052, 487), 0, H, "int"),    # header above sauna side glass
    # ASSUMED upper-floor stairwell shell (no upper plan supplied yet)
    ("W_up_stair_w",  (600, 612, 622, 1108), H, VH, "int"),
    ("W_up_stair_e",  (720, 612, 730, 1108), H, VH, "int"),
    ("W_up_stair_n",  (600, 612, 730, 622), H, VH, "int"),
    ("W_up_stair_s",  (600, 1100, 730, 1108), H, VH, "int"),
    ("W_gkpl",        (832, 945, 898, 1050), 0, H, "box"),      # GKPL drywall box (see flags)
]

# ---------------------------------------------------------------- openings
# rect in px (cuts any wall it overlaps); sill/head cm.
openings = [
    dict(id="O_laundry_ext_door", type="door", px=(250, 380, 285, 460), sill=0, head=210,
         hinge=(262, 460), leaf="solid", note="exterior side door into laundry, opens in"),
    dict(id="O_laundry_mud_door", type="door", px=(485, 390, 495, 457), sill=0, head=210,
         hinge=(485, 437), leaf="solid", note="laundry <-> mudroom"),
    dict(id="O_mud_hall_door", type="door", px=(650, 476, 720, 490), sill=0, head=210,
         hinge=(720, 480), leaf="solid", note="mudroom <-> hall"),
    dict(id="O_wc_door", type="door", px=(750, 475, 817, 492), sill=0, head=210,
         hinge=(750, 480), leaf="solid", note="hall <-> WC"),
    dict(id="O_spa_door", type="door", px=(830, 505, 847, 585), sill=0, head=210,
         hinge=(842, 584), leaf="solid", note="hall <-> spa"),
    dict(id="O_entrance", type="door", px=(742, 1190, 828, 1219), sill=0, head=240,
         hinge=(745, 1210), leaf="solid", note="MAIN ENTRANCE into stair hall"),
    dict(id="O_double_door", type="double_door", px=(975, 1190, 1152, 1219), sill=0, head=240,
         hinge=(978, 1213), leaf="glazed", note="double door into dining: active leaf west (solid arc), passive leaf east (dashed arc)"),
    dict(id="O_garage_door", type="garage_door", px=(290, 1060, 595, 1076), sill=G, head=230,
         note="sectional garage door"),
    dict(id="O_mud_window", type="window", px=(515, 270, 575, 315), sill=150, head=230,
         note="mudroom north window (sill ASSUMED high)"),
    dict(id="O_wc_window", type="window", px=(750, 270, 810, 315), sill=150, head=230,
         note="WC north window (sill ASSUMED high)"),
    dict(id="O_spa_glazing", type="sliding", px=(1405, 392, 1455, 587), sill=0, head=250,
         note="spa east glazed opening ~205 cm (ASSUMED full-height slider)"),
    dict(id="O_east_glazing", type="curtain", px=(1645, 760, 1675, 1195), sill=0, head=VH - 10,
         mullions_px=[907, 988, 1125], transom=H, slider_px=(988, 1125),
         note="living east facade: fixed glass + lift&slide between y988-1125"),
    dict(id="O_south_glazing", type="curtain", px=(1190, 1205, 1650, 1240), sill=0, head=VH - 10,
         mullions_px=[1340, 1490], transom=H,
         note="living south facade: 3 large panels to terrace"),
    dict(id="O_sauna_glass_s", type="glass_partition", px=(966, 477, 1052, 490), sill=0, head=210,
         hinge=(970, 482), leaf="glass", note="sauna glass door, opens into spa"),
    dict(id="O_sauna_glass_e", type="glass_partition", px=(1040, 407, 1055, 487), sill=0, head=210,
         note="sauna fixed glass side"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="R_garage", name="Garage", px=[(285, 482), (600, 482), (600, 1065), (285, 1065)], floor=G, ceiling=H,
         style="garage_gallery"),
    dict(id="R_laundry", name="Laundry", px=[(285, 312), (485, 312), (485, 465), (285, 465)], floor=0, ceiling=H,
         style="service_warm"),
    dict(id="R_mudroom", name="Mudroom / wardrobe hall", px=[(495, 312), (720, 312), (720, 478), (495, 478)], floor=0,
         ceiling=H, style="service_warm"),
    dict(id="R_wc", name="Guest WC", px=[(740, 312), (888, 312), (888, 477), (740, 477)], floor=0, ceiling=H,
         style="dark_spa"),
    dict(id="R_sauna", name="Sauna", px=[(900, 312), (1042, 312), (1042, 477), (900, 477)], floor=0, ceiling=230,
         style="dark_spa"),
    dict(id="R_spa", name="Spa (jacuzzi + shower)",
         px=[(845, 487), (1052, 487), (1052, 312), (1412, 312), (1412, 597), (845, 597)], floor=0, ceiling=H,
         style="dark_spa"),
    dict(id="R_hall", name="Entrance hall + stair", px=[(622, 488), (832, 488), (832, 1192), (622, 1192)], floor=0,
         ceiling=H, style="warm_wood_luxe", ceiling_holes=[(622, 620, 720, 1100)]),
    dict(id="R_kitchen_dining", name="Kitchen + dining",
         px=[(858, 622), (1180, 622), (1180, 1192), (832, 1192), (832, 860), (858, 860)], floor=0, ceiling=H,
         style="warm_wood_luxe"),
    dict(id="R_living", name="Living (double height)", px=[(1180, 622), (1627, 622), (1627, 760), (1650, 760),
                                                           (1650, 1205), (1180, 1205)], floor=0, ceiling=VH,
         style="living_grand"),
]

# ---------------------------------------------------------------- furniture & fixtures
# box: px rect + z0/h (cm). cyl: centre px + radius cm. facing = direction user faces / front of unit.
F = []


GROUPS = {"F_l_sofa_long": "L_sofa", "F_l_sofa_return": "L_sofa",
          "F_k_run_north": "L_kitchen", "F_k_run_west": "L_kitchen"}


def box(id, kind, px, z0, h, room, facing=None, note=None):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room,
                  facing=facing, note=note, src_px=list(px), group=GROUPS.get(id)))


def cyl(id, kind, c, r_cm, z0, h, room, note=None):
    F.append(dict(id=id, kind=kind, shape="cyl", center=P(*c), r=r_cm, z0=z0, h=h, room=room,
                  note=note, src_px=list(c)))


# laundry
box("F_washer", "appliance", (362, 315, 420, 372), 0, 85, "R_laundry", "S")
box("F_dryer", "appliance", (424, 315, 481, 372), 0, 85, "R_laundry", "S")
box("F_laundry_counter", "counter", (285, 312, 485, 369), 85, 4, "R_laundry", "S", "worktop over appliances")
# mudroom
box("F_wardrobe_1", "tall_cabinet", (495, 312, 600, 369), 0, 260, "R_mudroom", "S", "X-marked = full height")
box("F_wardrobe_2", "tall_cabinet", (600, 312, 720, 369), 0, 260, "R_mudroom", "S", "X-marked = full height")
# garage steps (3 treads, 4 risers of 15) going DOWN southwards into garage
for i, (y0, y1) in enumerate([(478, 505), (505, 533), (533, 561)]):
    box(f"F_garage_step_{i+1}", "stair", (495, y0, 600, y1), G, -15 * (i + 1) - G, "R_garage")
box("F_garage_bench_1", "low_cabinet", (290, 487, 390, 545), G, 90, "R_garage", "S", "no X = low units/workbench")
box("F_garage_bench_2", "low_cabinet", (390, 487, 490, 545), G, 90, "R_garage", "S")
box("F_car", "car", (340, 617, 515, 1030), G, 197, "R_garage", "S",
    "MATTE BLACK MERCEDES G-WAGON; drawing shows hood star + windscreen at the NORTH end => parked nose-in, rear/spare wheel toward garage door")
# WC
box("F_wc_toilet", "toilet", (762, 325, 797, 377), 0, 40, "R_wc", "S", "wall-hung")
box("F_wc_vanity", "vanity", (837, 327, 888, 477), 55, 30, "R_wc", "W", "floating vanity with vessel basin")
cyl("F_wc_basin", "basin", (864, 378), 21, 85, 15, "R_wc", "vessel basin")
# sauna
box("F_sauna_bench_low", "bench", (900, 312, 966, 477), 0, 45, "R_sauna", "E")
box("F_sauna_bench_high", "bench", (900, 312, 935, 477), 45, 45, "R_sauna", "E")
# spa
cyl("F_jacuzzi", "jacuzzi", (1305, 406), 85, 0, 70, "R_spa", "round hot tub ~170 cm, raised 70 cm")
box("F_shower_tray", "shower", (1052, 312, 1152, 407), 0, 3, "R_spa", "S", "walk-in shower")
box("F_shower_glass", "glass", (1149, 312, 1153, 407), 0, 210, "R_spa", None, "fixed glass screen (east side)")
box("F_shower_rain", "fixture", (1072, 312, 1130, 330), 220, 3, "R_spa", None, "ceiling rain head")
# stair: winder + straight flight rising north from entrance
steps = 18
rise = LEVELS["slab_top"] / steps
y_top, y_bot = 720, 1185
for i in range(steps):
    ya = y_bot - (i + 1) * (y_bot - y_top) / steps
    yb = y_bot - i * (y_bot - y_top) / steps
    box(f"F_stair_{i+1:02d}", "stair", (622, ya, 718, yb), 0, round(rise * (i + 1), 1), "R_hall")
box("F_stair_balustrade", "glass", (716, 720, 720, 1185), 0, 310 + 100, "R_hall", None,
    "frameless glass balustrade on open side of stair")
# kitchen
box("F_k_duct", "box", (857, 622, 894, 643), 0, H, "R_kitchen_dining", None, "installation duct, boxed in")
box("F_k_run_north", "counter", (894, 622, 1113, 679), 0, 92, "R_kitchen_dining", "S", "base run w/ sink")
box("F_k_fridge", "tall_cabinet", (1113, 622, 1170, 679), 0, 240, "R_kitchen_dining", "S", "'*' = fridge column")
box("F_k_run_west", "counter", (857, 643, 913, 860), 0, 92, "R_kitchen_dining", "E", "base run w/ cooktop")
box("F_k_sink", "sink", (957, 625, 1012, 676), 88, 4, "R_kitchen_dining", "S")
box("F_k_cooktop", "cooktop", (865, 682, 912, 735), 92, 1, "R_kitchen_dining", "E")
box("F_k_island", "island", (999, 764, 1171, 850), 0, 92, "R_kitchen_dining", "S", "overhang on south side y821-850")
for i, x in enumerate([(1011, 1050), (1065, 1104), (1118, 1156)]):
    box(f"F_k_stool_{i+1}", "stool", (x[0], 829, x[1], 868), 0, 75, "R_kitchen_dining", "N")
# dining
box("F_d_table", "table", (1000, 960, 1170, 1035), 0, 76, "R_kitchen_dining", None)
for i, x in enumerate([(1013, 1050), (1065, 1103), (1118, 1156)]):
    box(f"F_d_chair_n{i+1}", "chair", (x[0], 930, x[1], 968), 0, 85, "R_kitchen_dining", "S")
    box(f"F_d_chair_s{i+1}", "chair", (x[0], 1025, x[1], 1064), 0, 85, "R_kitchen_dining", "N")
# living
box("F_l_sofa_long", "sofa", (1285, 675, 1560, 762), 0, 75, "R_living", "S", "L-sofa main run")
box("F_l_sofa_return", "sofa", (1285, 762, 1370, 933), 0, 75, "R_living", "E", "L-sofa chaise/return")
box("F_l_table_1", "coffee_table", (1413, 793, 1475, 850), 0, 38, "R_living", None)
box("F_l_table_2", "coffee_table", (1440, 857, 1502, 913), 0, 32, "R_living", None)
box("F_l_armchair_1", "armchair", (1357, 1002, 1430, 1078), 0, 75, "R_living", "N")
box("F_l_armchair_2", "armchair", (1452, 1002, 1530, 1078), 0, 75, "R_living", "N")
box("F_l_tv_unit", "low_cabinet", (1602, 777, 1645, 918), 0, 45, "R_living", "W", "freestanding TV unit")
box("F_l_tv", "tv", (1622, 790, 1628, 905), 75, 70, "R_living", "W", "TV facing the sofa")

plan = dict(
    meta=dict(
        name="OSNOVA PRIZEMLJA - ground floor",
        source="source/floorplan_ground.webp",
        units="cm",
        axes="x = east (drawing right), y = south (drawing down), z = up",
        scale_cm_per_px=K, origin_px=[OX, OY],
        overall_cm=[1520, 975],
    ),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px", "slider_px")},
               "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x" if o["px"][2] - o["px"][0] > o["px"][3] - o["px"][1] else "y")
                                for m in o["mullions_px"]]} if "mullions_px" in o else {}),
               **({"slider": [cm(o["slider_px"][0], "y"), cm(o["slider_px"][1], "y")]} if "slider_px" in o else {}),
               } for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=r["floor"],
                ceiling=r["ceiling"], style=r["style"],
                ceiling_holes=[R(*h) for h in r.get("ceiling_holes", [])]) for r in rooms],
    void=dict(rect=R(1180, 622, 1650, 1205), ceiling=VH,
              note="double-height over LIVING only; upper-floor slab edge = orange dashed line at px x~1180"),
    gallery_edge=dict(x=cm(1180, "x"), y0=cm(622, "y"), y1=cm(1192, "y"), z=LEVELS["slab_top"],
                      note="upper-floor slab edge overlooking living; glass balustrade ASSUMED"),
    furniture=F,
    extra_ceilings=[dict(id="CEIL_upper_stairwell", rect=R(600, 612, 730, 1108), z=VH,
                         note="ASSUMED stairwell ceiling on upper floor")],
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
with open(out, "w") as f:
    json.dump(plan, f, indent=1)
print("wrote", out, "walls", len(walls), "openings", len(openings), "furniture", len(F))
