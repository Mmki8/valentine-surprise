"""Digitize 'OSNOVA PRIZEMLJA' of house type 3 (ground floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_prizemlje.png (1596x1130),
measured by pixel scans of the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains (same drawing scale as the souterrain sheet):
  1326 cm = ticks px x 182 -> 1192 (1010 px)  -> 1.3129 cm/px
  1000 cm = ticks py 301 -> 1063  (762 px)    -> 1.3123 cm/px
  1365 cm = ticks py 69 -> 1108   (1039 px)   -> 1.3138 cm/px
  => 1.313 cm/px, origin = outer NW corner of the garage (173, 60).

SPLIT LEVEL (read off the drawing): 4 risers (lines py 497/520/543/565, 3 treads of 30 cm) across the
whole hall width, and the SAME 4 risers outside on the terrace (py 648/671/693/716). The north half
(garage, entry, stair, guest WC, spa, sauna) is LOWER; the south half (living, kitchen, dining,
bedroom wing) is HIGHER - the souterrain bedrooms sit under the living and need the extra height.
  living level  = 0      entry/spa level = -60 (4 x 15 cm)

Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 173, 60


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


LO = -60          # entry / spa / garage level (4 risers x 15 cm below the living)
H = 280           # ceiling (one flat slab): living 2.80 m clear, entry + spa 3.40 m clear
UP = 600          # stairwell ceiling (stair to the 1st floor)
LEVELS = {"ffl": 0, "ffl_low": LO, "ceiling": H, "slab_top": 310}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    # envelope
    ("W_west", (173, 60, 201, 1034), LO, H, "ext"),                # garage + bedroom wing west facade
    ("W_garage_n", (173, 60, 473, 88), LO, H, "ext"),              # garage door wall
    ("W_garage_e", (445, 60, 473, 292), LO, H, "ext"),
    ("W_north", (465, 292, 1202, 320), LO, UP, "ext"),             # entrance facade: front door, stair glazing, back door
    ("W_east", (1172, 292, 1202, 1072), LO, H, "ext"),             # spa + living glazing to the terrace
    ("W_south", (465, 1053, 1172, 1066), LO, H, "ext"),            # living south glazing OG.1 (two sliding sets)
    ("W_sw_fin", (433, 1025, 465, 1115), LO, H, "ext"),            # SW pier projecting past the glass
    ("W_bed_s", (173, 1005, 445, 1034), LO, H, "ext"),             # bedroom glazing OG.2
    # interior
    ("W_core_w", (445, 292, 465, 1043), LO, H, "int"),             # garage + bedroom wing | entry, hall, kitchen
    ("W_garage_s", (201, 545, 445, 564), LO, H, "int"),            # garage | bath + lobby
    ("W_bath_e", (353, 564, 361, 705), 0, H, "int"),               # bath | lobby (GKPL)
    ("W_bath_s", (201, 705, 361, 712), 0, H, "int"),               # bath | wardrobe (GKPL)
    ("W_stair_s", (643, 397, 1172, 416), LO, UP, "int"),           # stair + back vestibule | corridor + spa
    ("W_stair_e", (1023, 320, 1043, 397), LO, UP, "int"),          # head of the stair | back vestibule
    ("W_spa_door", (777, 416, 784, 497), LO, H, "int"),            # door frame corridor | spa
    ("W_wc_n", (643, 497, 838, 505), LO, H, "int"),                # corridor | guest WC + sauna
    ("W_wc_w", (643, 497, 663, 667), LO, H, "int"),                # guest WC | steps + hall
    ("W_wc_e", (776, 505, 784, 648), LO, H, "int"),                # guest WC | sauna
    ("W_sauna_n", (838, 497, 906, 503), LO, H, "int"),             # sauna glass front
    ("W_sauna_e", (900, 503, 906, 565), LO, H, "int"),             # sauna glass side
    ("W_shower_w", (897, 565, 906, 648), LO, H, "int"),            # sauna | spa shower
    ("W_spa_s", (643, 648, 1172, 667), LO, H, "int"),              # WC + sauna + spa | dining + living (TV wall)
    ("W_kit_n", (465, 648, 510, 667), LO, H, "int"),               # stub at the head of the kitchen run
]

# ---------------------------------------------------------------- openings (px rect cuts the wall it overlaps)
openings = [
    dict(id="O_garage_door", type="garage_door", px=(205, 60, 441, 88), sill=LO, head=LO + 230, note="sectional garage door (north)"),
    dict(id="O_garage_win", type="window", px=(173, 432, 201, 485), sill=LO + 110, head=LO + 220, note="garage west window"),
    dict(id="O_bath_win", type="window", px=(173, 643, 201, 690), sill=110, head=220, note="bathroom west window (over the WC)"),
    dict(id="O_bed_glz", type="sliding", px=(221, 1005, 400, 1034), sill=0, head=250, note="bedroom south: sliding glass door OG.2"),
    dict(id="O_front_door", type="door", px=(519, 292, 586, 320), sill=LO, head=LO + 250, hinge=(519, 320), leaf="solid",
         note="main entrance (north)"),
    dict(id="O_stair_glz", type="curtain", px=(595, 292, 805, 320), sill=LO, head=LO + 300, mullions_px=[663, 735],
         note="full-height glazing beside the front door, lighting the entry and the stair"),
    dict(id="O_back_door", type="door", px=(1048, 292, 1115, 320), sill=LO, head=LO + 230, hinge=(1048, 320), leaf="solid",
         note="back door (north) into the spa vestibule"),
    dict(id="O_vest_glz", type="sliding", px=(1043, 397, 1172, 416), sill=LO, head=LO + 230, note="glass sliding door vestibule | spa"),
    dict(id="O_spa_glz", type="sliding", px=(1172, 426, 1202, 641), sill=LO, head=260, note="spa east: full-height sliding glass to the terrace"),
    dict(id="O_liv_e_glz", type="sliding", px=(1172, 731, 1202, 944), sill=0, head=260, note="living east: full-height sliding glass to the terrace"),
    dict(id="O_liv_s_glz", type="curtain", px=(465, 1053, 1172, 1066), sill=0, head=260, mullions_px=[582, 701, 818, 937, 1055],
         note="living south: 6-panel glazing, two sliding sets (OG.1), glass railing outside"),
    dict(id="O_garage_entry", type="door", px=(445, 418, 465, 484), sill=LO, head=LO + 210, hinge=(458, 418), leaf="solid",
         note="garage -> entry hall"),
    dict(id="O_lobby_door", type="door", px=(445, 576, 465, 640), sill=0, head=210, hinge=(450, 576), leaf="solid",
         note="hall -> bedroom wing lobby"),
    dict(id="O_bath_door", type="door", px=(353, 640, 361, 692), sill=0, head=210, hinge=(353, 692), leaf="solid",
         note="lobby -> bathroom"),
    dict(id="O_spa_door", type="door", px=(777, 427, 784, 489), sill=LO, head=LO + 210, hinge=(784, 427), leaf="solid",
         note="corridor -> spa"),
    dict(id="O_wc_door", type="door", px=(673, 497, 730, 505), sill=LO, head=LO + 210, hinge=(673, 505), leaf="solid",
         note="corridor -> guest WC"),
    dict(id="O_sauna_front", type="glass_partition", px=(838, 497, 906, 503), sill=LO, head=LO + 210, hinge=(841, 497),
         note="sauna glass front with glass door"),
    dict(id="O_sauna_side", type="glass_partition", px=(900, 503, 906, 565), sill=LO, head=LO + 210, note="sauna glass side"),
]

# ---------------------------------------------------------------- rooms  (floor = level, all ceilings on one slab)
rooms = [
    dict(id="P_R_garage", name="Garage", px=[(201, 88), (445, 88), (445, 545), (201, 545)], floor=LO, style="garage_gallery"),
    dict(id="P_R_entry", name="Entry hall + corridor + steps",
         px=[(510, 320), (663, 320), (663, 416), (777, 416), (777, 497), (643, 497), (643, 565),
             (465, 565), (465, 406), (510, 406)], floor=LO, style="entry_warm"),
    dict(id="P_R_stair", name="Stairwell down to the souterrain", px=[(663, 320), (1023, 320), (1023, 397), (663, 397)],
         floor=LO - 300, style="entry_warm"),
    dict(id="P_R_vest", name="Back vestibule", px=[(1043, 320), (1172, 320), (1172, 397), (1043, 397)], floor=LO, style="entry_warm"),
    dict(id="P_R_wc", name="Guest WC", px=[(663, 505), (776, 505), (776, 648), (663, 648)], floor=LO, style="bath_greige"),
    dict(id="P_R_sauna", name="Sauna", px=[(784, 505), (900, 505), (900, 648), (784, 648)], floor=LO, ceiling=LO + 220,
         style="sauna_timber"),
    dict(id="P_R_spa", name="Spa (jacuzzi + shower)", px=[(784, 416), (1172, 416), (1172, 648), (906, 648), (906, 503), (784, 503)],
         floor=LO, style="spa_greige"),
    dict(id="P_R_living", name="Living + kitchen + dining + upper hall",
         px=[(465, 565), (643, 565), (643, 667), (1172, 667), (1172, 1053), (465, 1053)], floor=0, style="living_warm"),
    dict(id="P_R_bath", name="Bathroom (bedroom wing)", px=[(201, 564), (353, 564), (353, 705), (201, 705)], floor=0, style="bath_greige"),
    dict(id="P_R_bed", name="Bedroom incl. lobby",
         px=[(361, 564), (445, 564), (445, 1005), (201, 1005), (201, 712), (361, 712)], floor=0, style="bedroom_noir"),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None, group=None, **kw):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=group, **kw))


# living - CLIENT REVISION 2026-10-15: the L-sofa is turned to face the south panorama glazing (plan drawing had it
# facing east); the TV moves off the bronze wall onto a freestanding floor stand in front of the south glass, facing the
# sofa; a large painting takes the TV's place on the bronze wall; armchairs stay on the east side (U-shaped group)
box("P_F_sofa", "sofa", (907, 745, 1117, 814), 0, 78, "P_R_living", "S", "L-sofa, long side centred in front of the painting, back to the bronze wall, facing the south glass", group="sofa")
box("P_F_sofa_chaise", "sofa", (907, 814, 976, 883), 0, 78, "P_R_living", "E", "L-sofa, chaise at the west end pointing south", group="sofa")
box("P_F_arm1", "armchair", (1082, 862, 1142, 920), 0, 75, "P_R_living", "W")
box("P_F_arm2", "armchair", (1082, 940, 1142, 998), 0, 75, "P_R_living", "W")
box("P_F_ct1", "coffee_table", (985, 845, 1031, 895), 0, 34, "P_R_living")
box("P_F_ct2", "coffee_table", (1027, 865, 1072, 915), 0, 40, "P_R_living")
box("P_F_tv_unit", "low_cabinet", (955, 670, 1070, 705), 18, 28, "P_R_living", "S", "floating walnut console under the painting")
box("P_F_tv", "tv", (956, 1020, 1067, 1023), 62, 82, "P_R_living", "N", "TV on a freestanding floor stand in front of the south glass, facing the sofa")
# round structural column by the south glass (px 808-828, py 1024-1044): modelled in design_layer (straight cylinder)
# kitchen (single run on the west wall, island with cooktop, dining table joined to the island)
box("P_F_k_duct", "box", (465, 667, 495, 687), 0, H, "P_R_living", None, "installation duct (2 small squares)")
box("P_F_k_run1", "counter", (465, 687, 510, 781), 0, 92, "P_R_living", "E")
box("P_F_k_fridge", "tall_cabinet", (465, 781, 510, 850), 0, 240, "P_R_living", "E", "fridge column (* on plan)")
box("P_F_k_run2", "counter", (465, 850, 510, 1025), 0, 92, "P_R_living", "E", "sink run")
box("P_F_k_sink", "sink", (470, 882, 503, 924), 88.5, 4, "P_R_living")
box("P_F_island", "island_x", (586, 803, 631, 972), 0, 86, "P_R_living", "W", "island with cooktop; marble top runs on to px 655 (overhang) in design_layer")
box("P_F_cooktop", "cooktop", (591, 896, 630, 940), 92, 1, "P_R_living")
box("P_F_table", "table", (655, 850, 792, 911), 0, 76, "P_R_living", None, "dining table joined to the island")
for i, (x0, x1) in enumerate([(665, 696), (708, 738), (750, 781)]):
    box(f"P_F_chair_n{i}", "chair", (x0, 827, x1, 858), 0, 82, "P_R_living", "S")
    box(f"P_F_chair_s{i}", "chair", (x0, 903, x1, 934), 0, 82, "P_R_living", "N")
# bedroom (headboard on the west wall) + wardrobe
box("P_F_bed", "bed", (205, 828, 353, 953), 0, 50, "P_R_bed", "E", "double bed, headboard on the west wall", head_h=110)
box("P_F_ns1", "nightstand", (205, 794, 236, 828), 0, 50, "P_R_bed")
box("P_F_ns2", "nightstand", (205, 953, 236, 987), 0, 50, "P_R_bed")
box("P_F_wr", "tall_cabinet", (201, 712, 361, 758), 0, 250, "P_R_bed", "S", "wardrobe, 2 modules")
# bathroom
box("P_F_bath_shower", "shower", (201, 564, 270, 633), 0, 3, "P_R_bath")
box("P_F_bath_vanity", "vanity", (282, 564, 343, 600), 80, 10, "P_R_bath", "S", "basin on the north wall")
box("P_F_bath_wc", "toilet", (210, 650, 255, 690), 0, 40, "P_R_bath", "E", "wall-hung WC under the window")
# guest WC
box("P_F_wc_toilet", "toilet", (681, 600, 711, 642), LO, 40, "P_R_wc", "N")
box("P_F_wc_vanity", "vanity", (740, 508, 776, 626), LO + 80, 10, "P_R_wc", "W", "long counter with basin on the east wall")
box("P_F_wc_duct", "box", (745, 627, 776, 648), LO, H - LO, "P_R_wc", None, "installation duct (box on plan)")
# spa
F.append(dict(id="P_F_jacuzzi", kind="jacuzzi", shape="cyl", center=P(1096, 575), r=round(65 * K, 1), z0=LO, h=62,
              room="P_R_spa", note="round jacuzzi D 170"))
box("P_F_spa_shower", "shower", (906, 572, 986, 648), LO, 3, "P_R_spa")
box("P_F_sauna_bench_hi", "bench", (784, 505, 814, 648), LO, 95, "P_R_sauna", "E", "upper bench")
box("P_F_sauna_bench_lo", "bench", (814, 505, 836, 648), LO, 48, "P_R_sauna", "E", "lower bench / step")
# shaft by the front door
box("P_F_shaft", "box", (465, 320, 510, 406), LO, H - LO, "P_R_entry", None, "installation shaft (X on plan)")
# car: S-Class built as a side-profile prism in design_layer (kind car)

# steps between the levels: 4 risers rising SOUTH, 3 treads of 30 cm (lines py 497 / 520 / 543 / 565)
for k, (y0, y1) in enumerate([(497, 520), (520, 543), (543, 565)]):
    box(f"P_F_step_{k + 1}", "stair", (465, y0, 643, y1), LO, 15 * (k + 1), "P_R_entry")
# stair DOWN to the souterrain (corrected): it lies exactly over the souterrain stair, which rises west and arrives here
# at the west end (px 663). The treads are drawn solid over the whole run (all below the cut) = a stair going down.
# 16 goings of 23 px (30 cm) visible in the stairwell, risers of 15 cm (souterrain: 20 risers over 300 cm).
SX0, SX1 = cm(663, "x"), cm(1023, "x")
SY0, SY1 = cm(320, "y"), cm(397, "y")
n_go, rise = 16, 15
g = (SX1 - SX0) / n_go
for k in range(n_go):
    F.append(dict(id=f"P_F_stair_{k + 1:02d}", kind="stair", shape="box", rect=[round(SX0 + g * k, 1), SY0, round(SX0 + g * (k + 1), 1), SY1],
                  z0=LO - 300, h=300 - rise * (k + 1), room="P_R_stair", group=None))

from design_layer import DESIGN, SITE, CAR                # noqa: E402
F.extend(CAR)

plan = dict(
    meta=dict(name="OSNOVA PRIZEMLJA - house type 3, ground floor", source="source/floorplan_prizemlje.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1326, 1365]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x") for m in o["mullions_px"]]} if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=r["floor"], ceiling=r.get("ceiling", H),
                style=r["style"], ceiling_holes=[R(*h) for h in r.get("ceiling_holes", [])]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[dict(id="CEIL_stairwell", rect=R(663, 320, 1023, 397), z=UP, mat="plaster_white")],
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
