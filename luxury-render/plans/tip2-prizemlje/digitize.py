"""Digitize 'OSNOVA PRIZEMLJA' (house type 2, ground floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_prizemlje.png (client sheet 34.png, 1600x1130),
measured by pixel scans of the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  1356 cm = ticks px x 161 -> 1194 (1033 px) -> 1.3127 cm/px
  1060 cm = ticks py 235 -> 1042 (807 px)    -> 1.3135 cm/px
  => 1.313 cm/px, origin = structural outer face NW of the garage / north wall (161, 235).
Same frame as the souterrain (plans/tip2-suteren): the main west wall lands at 375-402 cm on both sheets.
Split level: the entrance hall, bedroom wing and garage are at +0; three steps lead down (51 cm) to kitchen + living.
The stair to the souterrain starts at the west end of the stairwell and descends EAST.

Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 161, 235


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 280          # ASSUMED clear height of the upper level
LV = -51         # living + kitchen level: 3 risers of 17 cm down from the hall (render H3 shows 3 steps)
Z0 = LV          # walls start at the lowest finished floor
LEVELS = {"ffl": 0, "living": LV, "ceiling": H}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    ("W_gar_w", (161, 330, 181, 856), Z0, H, "ext"),
    ("W_gar_n", (161, 330, 447, 350), Z0, H, "ext"),            # long strip window 187-416
    ("W_gar_s", (161, 837, 447, 856), Z0, H, "ext"),            # sectional garage door 207-390
    ("W_west", (447, 235, 467, 1050), Z0, H, "int"),            # garage | house; south part = facade fin
    ("W_north", (447, 235, 1202, 254), Z0, H, "ext"),           # entrance door, stair glazing, NE door + window
    ("W_east", (1175, 235, 1202, 1005), Z0, H, "ext"),          # bedroom window, living sliding door
    ("W_south", (467, 990, 1175, 1005), Z0, H, "ext"),          # full sliding glazing OG.1
    ("W_stair_s", (625, 330, 1015, 350), Z0, H, "int"),         # stairwell | corridor
    ("W_stair_e", (995, 254, 1003, 330), Z0, H, "int"),         # stairwell | NE vestibule
    ("W_ne_s", (1015, 341, 1175, 351), Z0, H, "int"),           # NE vestibule | bedroom (light partition)
    ("W_hall_e", (625, 350, 645, 582), Z0, H, "int"),           # hall | bedroom corridor + bathroom 1
    ("W_bath_n", (645, 429, 878, 440), Z0, H, "int"),
    ("W_bath12", (729, 440, 737, 582), Z0, H, "int"),
    ("W_bath2_e", (867, 430, 878, 582), Z0, H, "int"),
    ("W_liv_n", (625, 581, 1175, 601), Z0, H, "int"),           # bedroom wing | living
    ("W_hall_sw", (467, 581, 512, 601), Z0, H, "int"),          # end of the hall wardrobe
]

# ---------------------------------------------------------------- openings (px rect cuts the wall it overlaps)
openings = [
    dict(id="O_gar_win", type="window", px=(187, 330, 416, 350), sill=120, head=220, note="garage north: long strip window"),
    dict(id="O_gar_door", type="garage_door", px=(207, 837, 390, 856), sill=0, head=240, note="garage south: sectional door"),
    dict(id="O_gar_house", type="door", px=(447, 361, 467, 425), sill=0, head=210, hinge=(447, 361), leaf="solid",
         note="garage -> entrance hall"),
    dict(id="O_entry", type="door", px=(517, 235, 588, 254), sill=0, head=230, hinge=(521, 254), leaf="solid",
         note="front door (north)"),
    dict(id="O_stair_glz", type="curtain", px=(588, 235, 809, 254), sill=0, head=H, note="glazing over the hall and stairwell"),
    dict(id="O_ne_door", type="door", px=(1016, 235, 1090, 254), sill=0, head=210, hinge=(1020, 254), leaf="solid",
         note="north-east vestibule exterior door"),
    dict(id="O_ne_win", type="window", px=(1090, 235, 1175, 254), sill=90, head=220, note="north-east vestibule window"),
    dict(id="O_bed_win", type="curtain", px=(1175, 360, 1202, 577), sill=0, head=H, note="bedroom east glazing"),
    dict(id="O_liv_e", type="sliding", px=(1175, 662, 1202, 880), sill=0, head=H, note="living east sliding door"),
    dict(id="O_liv_s", type="sliding", px=(467, 990, 1175, 1005), sill=0, head=H, mullions_px=[702, 820, 939, 1057],
         note="living south: sliding glazing OG.1"),
    dict(id="O_bz_door", type="door", px=(625, 361, 645, 425), sill=0, head=210, hinge=(637, 425), leaf="solid",
         note="hall -> bedroom corridor"),
    dict(id="O_b1_door", type="door", px=(625, 447, 645, 505), sill=0, head=210, hinge=(645, 450), leaf="solid",
         note="hall -> bathroom 1 (guest)"),
    dict(id="O_b2_door", type="door", px=(812, 429, 867, 440), sill=0, head=210, hinge=(867, 440), leaf="solid",
         note="bedroom corridor -> bathroom 2 (en-suite)"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="P2_R_garage", name="Garage", px=[(181, 350), (447, 350), (447, 837), (181, 837)], floor=0, style="garage_walnut"),
    dict(id="P2_R_hall", name="Entrance hall", floor=0, style="hall_light",
         px=[(467, 254), (649, 254), (649, 330), (625, 330), (625, 532), (512, 532), (512, 581), (467, 581)]),
    dict(id="P2_R_stair", name="Stairwell (down to the souterrain)", px=[(649, 254), (995, 254), (995, 330), (649, 330)],
         floor=-300, style="hall_light"),
    dict(id="P2_R_ne", name="North-east vestibule (exterior door)", px=[(1003, 254), (1175, 254), (1175, 341), (1003, 341)],
         floor=0, style="hall_light"),
    dict(id="P2_R_bed", name="Bedroom incl. corridor", floor=0, style="bedroom_luxe",
         px=[(645, 350), (1175, 350), (1175, 581), (878, 581), (878, 429), (645, 429)]),
    dict(id="P2_R_bath1", name="Bathroom 1 (guest WC)", px=[(645, 440), (729, 440), (729, 581), (645, 581)], floor=0, style="wc_dark"),
    dict(id="P2_R_bath2", name="Bathroom 2 (en-suite)", px=[(737, 440), (867, 440), (867, 581), (737, 581)], floor=0, style="bath_dark"),
    dict(id="P2_R_living", name="Kitchen + dining + living (3 steps down)", floor=LV, style="living_warm",
         px=[(467, 601), (512, 601), (512, 532), (625, 532), (625, 601), (1175, 601), (1175, 990), (467, 990)]),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=None))


# entrance hall: walnut wardrobes north + along the west wall, steps down to the living
box("P2_F_hall_wr_n", "tall_cabinet", (467, 254, 513, 340), 0, 240, "P2_R_hall", "E", "wardrobe by the front door")
box("P2_F_hall_wr_w", "tall_cabinet", (467, 427, 512, 581), 0, 240, "P2_R_hall", "E", "full-height walnut wardrobe wall")
box("P2_F_step1", "stair", (512, 532, 625, 555), LV, -17 - LV, "P2_R_living", None, "step 1 (top -17)")
box("P2_F_step2", "stair", (512, 555, 625, 580), LV, -34 - LV, "P2_R_living", None, "step 2 (top -34)")
# garage: the car drawn nose south (towards the sectional door)
box("P2_F_car", "car", (245, 420, 385, 750), 0, 195, "P2_R_garage", "S", "car as drawn, nose south")
# bathroom 1 (guest): basin on the east wall, WC on the south wall
box("P2_F_b1_vanity", "vanity", (695, 467, 728, 512), 80, 10, "P2_R_bath1", "W")
box("P2_F_b1_wc", "toilet", (665, 527, 695, 570), 0, 40, "P2_R_bath1", "N")
box("P2_F_b1_duct", "box", (705, 441, 729, 460), 0, 110, "P2_R_bath1", None, "installation box")
# bathroom 2 (en-suite): basin west, walk-in shower south-west, WC south
box("P2_F_b2_vanity", "vanity", (739, 453, 774, 500), 80, 10, "P2_R_bath2", "E")
box("P2_F_b2_shower", "shower", (737, 512, 805, 581), 0, 3, "P2_R_bath2")
box("P2_F_b2_wc", "toilet", (829, 528, 859, 570), 0, 40, "P2_R_bath2", "N")
# bedroom: wardrobe against the en-suite, bed with its head on the south wall
box("P2_F_bed_wr", "tall_cabinet", (886, 430, 932, 582), 0, 240, "P2_R_bed", "E", "wardrobe (glass fronts in the render)")
box("P2_F_bed", "bed", (997, 435, 1122, 582), 0, 50, "P2_R_bed", "N", "double bed, headboard on the south wall")
box("P2_F_bed_ns1", "nightstand", (962, 552, 997, 582), 0, 50, "P2_R_bed")
box("P2_F_bed_ns2", "nightstand", (1122, 552, 1155, 582), 0, 50, "P2_R_bed")
# kitchen (living level): tall units + counter run on the west wall, island with cooktop
box("P2_F_k_tall", "tall_cabinet", (467, 602, 512, 715), LV, 240, "P2_R_living", "E", "fridge + oven column")
box("P2_F_k_counter", "counter", (467, 715, 512, 958), LV, 92, "P2_R_living", "E", "counter run with sink")
box("P2_F_k_sink", "sink", (470, 815, 510, 857), LV + 88, 6, "P2_R_living", "E")
box("P2_F_k_island", "island", (587, 715, 657, 882), LV, 92, "P2_R_living", "E")
box("P2_F_k_cooktop", "cooktop", (590, 805, 622, 852), LV + 92, 1, "P2_R_living")
# dining: table attached east of the island, 3 + 3 chairs
box("P2_F_table", "table", (657, 761, 794, 822), LV, 75, "P2_R_living")
for i, x in enumerate((667, 710, 752)):
    box(f"P2_F_chair_n{i}", "chair", (x, 737, x + 30, 768), LV, 85, "P2_R_living", "S")
    box(f"P2_F_chair_s{i}", "chair", (x, 814, x + 30, 845), LV, 85, "P2_R_living", "N")
# living: L-sofa facing east, two coffee tables, two armchairs facing west, TV console on the north wall
box("P2_F_sofa", "sofa", (871, 690, 941, 912), LV, 80, "P2_R_living", "E", "L-sofa, main run")
box("P2_F_sofa_chaise", "sofa", (941, 842, 1010, 912), LV, 80, "P2_R_living", "N", "L-sofa, chaise")
box("P2_F_ct1", "coffee_table", (966, 759, 1012, 808), LV, 35, "P2_R_living")
box("P2_F_ct2", "coffee_table", (997, 731, 1043, 780), LV, 40, "P2_R_living")
box("P2_F_arm1", "armchair", (1070, 704, 1131, 765), LV, 80, "P2_R_living", "W")
box("P2_F_arm2", "armchair", (1070, 783, 1131, 845), LV, 80, "P2_R_living", "W")
box("P2_F_tv", "low_cabinet", (957, 604, 1072, 639), LV, 50, "P2_R_living", "S", "TV console")
# stair down to the souterrain: starts at the west end of the stairwell, descends east (souterrain stair rises west
# to x 639 cm on its own sheet = the same line here). 15 treads drawn px 649 -> 992, each 30.1 cm, rise 15 cm.
SX0 = cm(649, "x")
g = 30.1
SY0, SY1 = cm(254, "y"), cm(330, "y")
for k in range(15):
    top = -15 * (k + 1)
    F.append(dict(id=f"P2_F_stair_{k + 1:02d}", kind="stair", shape="box", rect=[round(SX0 + g * k, 1), SY0, round(SX0 + g * (k + 1), 1), SY1],
                  z0=-300, h=300 + top, room="P2_R_stair", group=None))

from design_layer import DESIGN, SITE                    # noqa: E402

plan = dict(
    meta=dict(name="OSNOVA PRIZEMLJA - house type 2, ground floor", source="source/floorplan_prizemlje.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1356, 1060]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x") for m in o["mullions_px"]]} if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=r["floor"], ceiling=H, style=r["style"],
                ceiling_holes=[]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[],
    site=SITE,
)

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
