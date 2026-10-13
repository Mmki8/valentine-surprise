"""Digitize 'OSNOVA SUTERENA' (house type 2, souterrain) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_suteren.png (client sheet 33.webp, 1598x1132),
measured by pixel scans of the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  1621 cm = ticks px x 170 -> 1405 (1235 px) -> 1.3126 cm/px
  1000 cm = ticks py 222 -> 983 (761 px)     -> 1.3141 cm/px
  => 1.313 cm/px, origin = structural outer face NW (170, 220).
The level is dug into the slope: earth on the north, west and east (hatched); bedrooms and spa glaze to the south.

Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 170, 220


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 270          # ASSUMED clear height (souterrain)
UP = 570         # ASSUMED ceiling of the ground floor above the stairwell (floor-to-floor 300)
LEVELS = {"ffl": 0, "ceiling": H, "slab_top": 300}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    # envelope - north, west and east are retaining walls against the earth
    ("W_north", (452, 219, 1405, 241), 0, UP, "ext"),
    ("W_west_up", (452, 219, 475, 337), 0, H, "ext"),          # main block west wall north of the spa wing
    ("W_spa_n", (170, 317, 452, 337), 0, H, "ext"),
    ("W_spa_w", (170, 317, 190, 842), 0, H, "ext"),
    ("W_spa_s", (170, 823, 455, 842), 0, H, "ext"),             # spa glazing wall (sliding door 215-398)
    ("W_main_w", (455, 337, 475, 1037), 0, H, "int"),          # spa | corridor + bedroom 1; south part = facade fin
    ("W_east", (1386, 219, 1405, 889), 0, H, "ext"),
    ("W_east_in", (1184, 241, 1204, 985), 0, H, "int"),        # corridor + bedroom 2 | east room + laundry
    ("W_south", (475, 978, 1184, 994), 0, H, "ext"),           # full glazing of both bedrooms
    ("W_laundry_s", (1204, 869, 1386, 889), 0, H, "ext"),
    # interior
    ("W_stair_s", (475, 317, 1092, 336), 0, UP, "int"),        # store + stair | corridor (stair foot open 1092-1184)
    ("W_corr_s", (475, 428, 1184, 437), 0, H, "int"),          # GKPL: corridor | bedroom vestibules + bathrooms
    ("W_mid", (820, 437, 840, 978), 0, H, "int"),              # bathroom 1 | 2, bedroom 1 | 2
    ("W_podL_w", (557, 437, 564, 567), 0, H, "int"),
    ("W_podL_s", (557, 567, 820, 587), 0, H, "int"),
    ("W_podL_p", (742, 437, 752, 505), 0, H, "int"),           # GKPL between basin and WC
    ("W_podR_e", (1095, 437, 1102, 567), 0, H, "int"),
    ("W_podR_s", (840, 567, 1102, 587), 0, H, "int"),
    ("W_podR_p", (907, 437, 915, 495), 0, H, "int"),
    ("W_er_s", (1204, 567, 1386, 587), 0, H, "int"),           # east room | laundry
    ("W_wc_s", (190, 420, 342, 429), 0, H, "int"),             # GKPL WC | sauna
    ("W_wc_e", (342, 337, 350, 550), 0, H, "int"),             # WC + sauna front (glass part below 482)
    ("W_sauna_s", (190, 542, 342, 550), 0, H, "int"),
]

# ---------------------------------------------------------------- openings (px rect cuts the wall it overlaps)
openings = [
    dict(id="O_spa_glz", type="sliding", px=(215, 823, 398, 842), sill=0, head=H, note="spa south: 2-leaf sliding glass door"),
    dict(id="O_b1_glz", type="curtain", px=(476, 978, 830, 994), sill=0, head=H, mullions_px=[593, 710],
         note="bedroom 1 south: glazing, middle leaf slides"),
    dict(id="O_b2_glz", type="curtain", px=(830, 978, 1184, 994), sill=0, head=H, mullions_px=[947, 1065],
         note="bedroom 2 south: glazing, middle leaf slides"),
    dict(id="O_spa_door", type="door", px=(455, 345, 475, 410), sill=0, head=210, hinge=(465, 410), leaf="solid",
         note="corridor -> spa"),
    dict(id="O_store_door", type="door", px=(487, 317, 547, 336), sill=0, head=210, hinge=(487, 336), leaf="solid",
         note="corridor -> store under the stair landing"),
    dict(id="O_b1_door", type="door", px=(485, 428, 550, 437), sill=0, head=210, hinge=(487, 437), leaf="solid",
         note="corridor -> bedroom 1 vestibule"),
    dict(id="O_b2_door", type="door", px=(1110, 428, 1174, 437), sill=0, head=210, hinge=(1172, 437), leaf="solid",
         note="corridor -> bedroom 2 vestibule"),
    dict(id="O_podL_door", type="door", px=(677, 567, 737, 587), sill=0, head=210, hinge=(737, 587), leaf="solid",
         note="bedroom 1 -> bathroom 1"),
    dict(id="O_podR_door", type="door", px=(921, 567, 982, 587), sill=0, head=210, hinge=(921, 587), leaf="solid",
         note="bedroom 2 -> bathroom 2 (no leaf drawn)"),
    dict(id="O_er_door", type="door", px=(1184, 345, 1204, 410), sill=0, head=210, hinge=(1194, 347), leaf="solid",
         note="corridor -> east room"),
    dict(id="O_laundry_door", type="door", px=(1236, 567, 1302, 587), sill=0, head=210, hinge=(1238, 587), leaf="solid",
         note="east room -> laundry"),
    dict(id="O_laundry_ext", type="door", px=(1236, 869, 1302, 889), sill=0, head=210, hinge=(1238, 869), leaf="solid",
         note="laundry exterior door (south)"),
    dict(id="O_wc_door", type="door", px=(342, 347, 350, 404), sill=0, head=210, hinge=(342, 347), leaf="solid",
         note="spa -> WC"),
    dict(id="O_sauna_glass", type="glass_partition", px=(342, 482, 350, 550), sill=0, head=210,
         note="sauna glass front with glass door"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="T2_R_wc", name="WC", px=[(190, 337), (342, 337), (342, 420), (190, 420)], style="wc_dark"),
    dict(id="T2_R_sauna", name="Sauna", px=[(190, 429), (342, 429), (342, 542), (190, 542)], style="sauna_walnut"),
    dict(id="T2_R_spa", name="Spa (jacuzzi, shower)", px=[(350, 337), (455, 337), (455, 823), (190, 823), (190, 550), (350, 550)],
         style="spa_dark"),
    dict(id="T2_R_store", name="Store under the stair landing", px=[(475, 241), (657, 241), (657, 317), (475, 317)], style="corridor_warm"),
    dict(id="T2_R_stair", name="Stair", px=[(657, 241), (1184, 241), (1184, 317), (657, 317)], style="corridor_warm"),
    dict(id="T2_R_corr", name="Corridor", px=[(475, 336), (1184, 336), (1184, 428), (475, 428)], style="corridor_warm"),
    dict(id="T2_R_bed1", name="Bedroom 1 (south-west) incl. vestibule",
         px=[(475, 437), (557, 437), (557, 587), (820, 587), (820, 978), (475, 978)], style="bedroom_luxe"),
    dict(id="T2_R_bath1", name="Bathroom 1", px=[(564, 437), (820, 437), (820, 567), (564, 567)], style="bath_dark"),
    dict(id="T2_R_bath2", name="Bathroom 2", px=[(840, 437), (1095, 437), (1095, 567), (840, 567)], style="bath_dark"),
    dict(id="T2_R_bed2", name="Bedroom 2 (south-east) incl. vestibule",
         px=[(1102, 437), (1184, 437), (1184, 978), (840, 978), (840, 587), (1102, 587)], style="bedroom_luxe"),
    dict(id="T2_R_east", name="East room (unlabelled, no furniture)", px=[(1204, 241), (1386, 241), (1386, 567), (1204, 567)],
         style="corridor_warm"),
    dict(id="T2_R_laundry", name="Laundry", px=[(1204, 587), (1386, 587), (1386, 869), (1204, 869)], style="laundry_warm"),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=None))


# WC: toilet on the west wall, basin on the GKPL wall facing north
box("T2_F_wc_toilet", "toilet", (200, 350, 242, 378), 0, 40, "T2_R_wc", "E")
box("T2_F_wc_vanity", "vanity", (255, 395, 300, 420), 55, 30, "T2_R_wc", "N")
# sauna: deep lower bench along the WC wall, upper bench behind it
box("T2_F_sauna_bench1", "bench", (190, 429, 342, 481), 0, 45, "T2_R_sauna", "S", "lower bench, edge = magenta line py 481")
box("T2_F_sauna_bench2", "bench", (190, 429, 342, 455), 0, 90, "T2_R_sauna", "S", "upper bench")
# spa: shower tray in the north-west corner of the open part, round jacuzzi
box("T2_F_spa_shower", "shower", (190, 550, 265, 630), 0, 3, "T2_R_spa")
F.append(dict(id="T2_F_jacuzzi", kind="jacuzzi", shape="cyl", center=P(262, 723), r=round(65 * K, 1), z0=0, h=62,
              room="T2_R_spa", note="round jacuzzi D 1.70 m"))
# bathroom 1 (left pod): walk-in shower west, basin counter, WC east of the GKPL partition
box("T2_F_b1_shower", "shower", (564, 437, 635, 567), 0, 3, "T2_R_bath1")
box("T2_F_b1_vanity", "vanity", (635, 437, 715, 475), 80, 10, "T2_R_bath1", "S")
box("T2_F_b1_duct", "box", (715, 437, 742, 447), 0, H, "T2_R_bath1", None, "installation box (black square on plan)")
box("T2_F_b1_wc", "toilet", (767, 447, 797, 487), 0, 40, "T2_R_bath1", "S")
# bathroom 2 (right pod, mirrored)
box("T2_F_b2_wc", "toilet", (850, 447, 880, 487), 0, 40, "T2_R_bath2", "S")
box("T2_F_b2_vanity", "vanity", (915, 437, 1025, 475), 80, 10, "T2_R_bath2", "S")
box("T2_F_b2_shower", "shower", (1025, 437, 1095, 567), 0, 3, "T2_R_bath2")
box("T2_F_b2_ledge", "box", (840, 555, 907, 567), 0, 110, "T2_R_bath2", None, "GKPL ledge with floor drain (green on plan)")
# bedrooms: freestanding full-height GKPL wardrobe wall, bed against its south face
for b, (wr, bed, n1, n2) in {"1": ((558, 658, 754, 711), (592, 715, 717, 862), (558, 713, 592, 744), (717, 713, 751, 744)),
                             "2": ((905, 658, 1101, 711), (939, 715, 1064, 862), (905, 713, 939, 744), (1064, 713, 1098, 744))}.items():
    room = f"T2_R_bed{b}"
    box(f"T2_F_bed{b}_wr", "tall_cabinet", wr, 0, H, room, "N", "full-height wardrobe wall (GKPL), doors face north")
    box(f"T2_F_bed{b}_bed", "bed", bed, 0, 50, room, "S", "double bed, headboard against the wardrobe wall")
    box(f"T2_F_bed{b}_ns1", "nightstand", n1, 0, 50, room)
    box(f"T2_F_bed{b}_ns2", "nightstand", n2, 0, 50, room)
# laundry
box("T2_F_l_washer", "appliance", (1336, 592, 1381, 638), 0, 85, "T2_R_laundry", "W")
box("T2_F_l_dryer", "appliance", (1336, 640, 1381, 688), 0, 85, "T2_R_laundry", "W")
box("T2_F_l_counter", "counter", (1338, 688, 1386, 867), 0, 92, "T2_R_laundry", "W", "worktop run with cabinets (magenta edge)")
# stair - rises WEST along the north wall from the corridor (3 treads drawn solid at px 1092/1069/1046, the rest dashed
# above the cut, arrow pointing west). 20 risers x 15 cm (floor-to-floor 300 ASSUMED), 19 goings: px 1092 -> 657.
SX_BOT, SX_TOP = cm(1092, "x"), cm(657, "x")
SY0, SY1 = cm(241, "y"), cm(317, "y")
steps, rise = 20, 300 / 20
g = (SX_BOT - SX_TOP) / (steps - 1)
for k in range(1, steps):
    F.append(dict(id=f"T2_F_stair_{k:02d}", kind="stair", shape="box",
                  rect=[round(SX_BOT - g * k, 1), SY0, round(SX_BOT - g * (k - 1), 1), SY1],
                  z0=0, h=round(rise * k, 1), room="T2_R_stair", group=None))

from design_layer import DESIGN, SITE                    # noqa: E402

plan = dict(
    meta=dict(name="OSNOVA SUTERENA - house type 2, souterrain", source="source/floorplan_suteren.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1621, 1060]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x") for m in o["mullions_px"]]} if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=0, ceiling=H, style=r["style"],
                ceiling_holes=[]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[],
    site=SITE,
)

# ---- integrity: every opening cuts exactly one wall
problems = []
for o in openings:
    ox0, oy0, ox1, oy1 = o["px"]
    hits = [wid for wid, (x0, y0, x1, y1), *_ in walls if min(x1, ox1) - max(x0, ox0) > 0.5 and min(y1, oy1) - max(y0, oy0) > 0.5]
    if len(hits) != 1:
        problems.append(f"{o['id']} cuts {hits}")
if problems:
    raise SystemExit("OPENING/WALL INTEGRITY FAILED:\n  " + "\n  ".join(problems))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
json.dump(plan, open(out, "w"), indent=1)
print("wrote", out, "walls", len(plan["walls"]), "openings", len(plan["openings"]), "furniture", len(F), "design", len(DESIGN))
