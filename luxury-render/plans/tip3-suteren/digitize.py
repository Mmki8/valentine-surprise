"""Digitize 'OSNOVA SUTERENA' (house type 3, souterrain / walk-out level) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_suteren.webp (1600x1130),
measured on the drawing (pixel scans of wall faces, see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  1591 cm = ticks px x 184 -> 1396 (1212 px) -> 1.3127 cm/px
  1000 cm = ticks py 247.5 -> 1009 (761.5 px) -> 1.3132 cm/px
  => 1.313 cm/px, origin = structural NW corner (184, 247.5).
The level is dug into the slope: earth on the north, west and east (hatched); all glazing faces south.

Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 184, 247.5


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
    # envelope - north / west / east are retaining walls against the earth
    ("W_north", (184, 244, 1400, 267), 0, UP, "ext"),
    ("W_west", (184, 244, 205, 843), 0, H, "ext"),
    ("W_east", (1376, 244, 1400, 914), 0, H, "ext"),
    ("W_b1_s", (184, 815, 466, 843), 0, H, "ext"),             # bedroom 1 glazing wall
    ("W_b2_s", (466, 1004, 811, 1018), 0, H, "ext"),           # bedroom 2 glazing
    ("W_b3_s", (830, 1004, 1175, 1018), 0, H, "ext"),          # bedroom 3 glazing
    ("W_laundry_s", (1194, 895, 1400, 914), 0, H, "ext"),
    # interior
    ("W_b1_e", (446, 267, 466, 1018), 0, H, "int"),            # bedroom 1 / corridor; lower part = bedroom 2 west facade
    ("W_b3_e", (1175, 267, 1194, 1018), 0, H, "int"),          # bedroom 3 + corridor / NE room + laundry
    ("W_div", (811, 455, 830, 1018), 0, H, "int"),             # pods + bedrooms 2|3
    ("W_corr_s", (466, 455, 1175, 462), 0, H, "int"),          # GKPL wall: corridor / pods + passages
    ("W_store_s", (466, 354, 645, 362), 0, H, "int"),
    ("W_stair_w", (645, 267, 664, 362), 0, UP, "int"),
    ("W_stair_s", (645, 343, 1045, 362), 0, UP, "int"),        # wall between the stair and the corridor
    ("W_well_e", (1045, 267, 1050, 343), H, UP, "int"),        # stairwell edge above the stair foot
    ("W_bath1_e", (355, 343, 363, 440), 0, H, "int"),          # GKPL
    ("W_bath1_sh", (362, 343, 446, 350), 0, H, "int"),         # GKPL front of the shower
    ("W_bath1_s", (205, 440, 362, 449), 0, H, "int"),          # GKPL bath / wardrobe
    ("W_podL_w", (549, 462, 555, 613), 0, H, "int"),
    ("W_podL_s", (549, 592, 811, 613), 0, H, "int"),
    ("W_podL_p", (732, 462, 745, 515), 0, H, "int"),           # GKPL between vanity and WC
    ("W_podR_e", (1086, 462, 1091, 613), 0, H, "int"),
    ("W_podR_s", (830, 592, 1091, 613), 0, H, "int"),
    ("W_podR_p", (898, 462, 906, 532), 0, H, "int"),
    ("W_ne_s", (1194, 594, 1376, 613), 0, H, "int"),
]

# ---------------------------------------------------------------- openings (px rect cuts the wall it overlaps)
openings = [
    dict(id="O_b1_glz", type="sliding", px=(221, 815, 404, 843), sill=0, head=240, note="bedroom 1 south: 2-leaf sliding glass door"),
    dict(id="O_b2_glz", type="curtain", px=(466, 1004, 811, 1018), sill=0, head=250, mullions_px=[584, 703],
         note="bedroom 2 south: 3-panel glazing, middle leaf slides"),
    dict(id="O_b3_glz", type="curtain", px=(830, 1004, 1175, 1018), sill=0, head=250, mullions_px=[937, 1057],
         note="bedroom 3 south: 3-panel glazing, middle leaf slides"),
    dict(id="O_b1_door", type="door", px=(446, 373, 466, 437), sill=0, head=210, hinge=(446, 437), leaf="solid",
         note="corridor -> bedroom 1 entry hall"),
    dict(id="O_bath1_door", type="door", px=(355, 375, 363, 430), sill=0, head=210, hinge=(355, 375), leaf="solid",
         note="bedroom 1 entry hall -> bathroom 1"),
    dict(id="O_store_door", type="door", px=(481, 354, 539, 362), sill=0, head=210, hinge=(481, 354), leaf="solid",
         note="corridor -> store / technical room"),
    dict(id="O_b2_door", type="door", px=(477, 455, 540, 462), sill=0, head=210, hinge=(477, 462), leaf="solid",
         note="corridor -> bedroom 2 passage"),
    dict(id="O_b3_door", type="door", px=(1100, 455, 1165, 462), sill=0, head=210, hinge=(1165, 462), leaf="solid",
         note="corridor -> bedroom 3 passage"),
    dict(id="O_podL_door", type="door", px=(671, 592, 726, 613), sill=0, head=210, hinge=(726, 613), leaf="solid",
         note="bedroom 2 -> bathroom pod"),
    dict(id="O_podR_door", type="door", px=(915, 592, 970, 613), sill=0, head=210, hinge=(915, 613), leaf="solid",
         note="bedroom 3 -> bathroom pod"),
    dict(id="O_ne_door", type="door", px=(1175, 373, 1194, 435), sill=0, head=210, hinge=(1194, 373), leaf="solid",
         note="corridor -> north-east room (unlabelled)"),
    dict(id="O_laundry_door", type="door", px=(1236, 594, 1298, 613), sill=0, head=210, hinge=(1236, 613), leaf="solid",
         note="north-east room -> laundry"),
    dict(id="O_laundry_ext", type="door", px=(1236, 895, 1298, 914), sill=0, head=210, hinge=(1236, 895), leaf="solid",
         note="laundry exterior door (south)"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="S_R_bath1", name="Bathroom 1 (bedroom 1)", px=[(205, 267), (446, 267), (446, 343), (362, 343), (362, 440), (205, 440)],
         style="bath_greige"),
    dict(id="S_R_bed1", name="Bedroom 1 (west) incl. entry hall", px=[(205, 449), (362, 449), (362, 350), (446, 350), (446, 815), (205, 815)],
         style="bedroom_noir"),
    dict(id="S_R_store", name="Store / technical (unlabelled)", px=[(466, 267), (645, 267), (645, 354), (466, 354)], style="corridor_warm"),
    dict(id="S_R_corr", name="Corridor + stair", px=[(466, 362), (1045, 362), (1045, 343), (664, 343), (664, 267), (1175, 267),
                                                       (1175, 455), (466, 455)], style="corridor_warm",
         ceiling_holes=[(664, 267, 1045, 343)]),
    dict(id="S_R_podL", name="Bathroom 2 (pod, bedroom 2)", px=[(555, 462), (811, 462), (811, 592), (555, 592)], style="bath_taupe"),
    dict(id="S_R_podR", name="Bathroom 3 (pod, bedroom 3)", px=[(830, 462), (1086, 462), (1086, 592), (830, 592)], style="bath_taupe"),
    dict(id="S_R_bed2", name="Bedroom 2 (south, middle-west)", px=[(466, 462), (549, 462), (549, 613), (811, 613), (811, 1004), (466, 1004)],
         style="bedroom_noir"),
    dict(id="S_R_bed3", name="Bedroom 3 (south, middle-east)", px=[(1091, 462), (1175, 462), (1175, 1004), (830, 1004), (830, 613),
                                                                   (1091, 613)], style="bedroom_noir"),
    dict(id="S_R_ne", name="North-east room (unlabelled, no furniture)", px=[(1194, 267), (1376, 267), (1376, 594), (1194, 594)],
         style="corridor_warm"),
    dict(id="S_R_laundry", name="Laundry", px=[(1194, 613), (1376, 613), (1376, 895), (1194, 895)], style="laundry_warm"),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=None))


# bedroom 1 - headboard on the west wall
box("S_F_b1_bed", "bed", (207, 591, 355, 715), 0, 50, "S_R_bed1", "E", "double bed, headboard on west wall")
box("S_F_b1_ns1", "nightstand", (207, 556, 237, 591), 0, 50, "S_R_bed1")
box("S_F_b1_ns2", "nightstand", (207, 715, 237, 750), 0, 50, "S_R_bed1")
box("S_F_b1_wr", "tall_cabinet", (205, 449, 362, 495), 0, 240, "S_R_bed1", "S", "wardrobe")
# bathroom 1
box("S_F_bath1_wc", "toilet", (213, 285, 255, 315), 0, 40, "S_R_bath1", "E")
box("S_F_bath1_vanity", "vanity", (205, 368, 247, 422), 55, 30, "S_R_bath1", "E", "basin in the GKPL installation wall")
box("S_F_bath1_shower", "shower", (362, 267, 446, 343), 0, 3, "S_R_bath1")
# bathroom pods
box("S_F_podL_shower", "shower", (555, 462, 626, 592), 0, 3, "S_R_podL")
box("S_F_podL_vanity", "vanity", (626, 462, 732, 500), 80, 10, "S_R_podL", "S")
box("S_F_podL_wc", "toilet", (755, 465, 790, 515), 0, 40, "S_R_podL", "S")
box("S_F_podL_duct", "box", (747, 572, 778, 592), 0, H, "S_R_podL", None, "installation duct (green box on plan)")
box("S_F_podR_shower", "shower", (1015, 462, 1086, 592), 0, 3, "S_R_podR")
box("S_F_podR_vanity", "vanity", (906, 462, 1015, 500), 80, 10, "S_R_podR", "S")
box("S_F_podR_wc", "toilet", (840, 465, 870, 515), 0, 40, "S_R_podR", "S")
# bedrooms 2 + 3 - freestanding full-height GKPL wardrobe wall, bed against its south face
for b, (wr, bed, n1, n2) in {"b2": ((550, 684, 745, 737), (583, 739, 709, 887), (550, 739, 583, 769), (709, 739, 743, 769)),
                             "b3": ((897, 684, 1091, 737), (930, 739, 1055, 887), (897, 739, 930, 769), (1055, 739, 1091, 769))}.items():
    room = f"S_R_bed{b[1]}"
    box(f"S_F_{b}_wr", "tall_cabinet", wr, 0, H, room, "N", "full-height wardrobe wall (GKPL), doors face north (dressing zone)")
    box(f"S_F_{b}_bed", "bed", bed, 0, 50, room, "S", "double bed, headboard against the wardrobe wall")
    box(f"S_F_{b}_ns1", "nightstand", n1, 0, 50, room)
    box(f"S_F_{b}_ns2", "nightstand", n2, 0, 50, room)
# laundry
box("S_F_l_washer", "appliance", (1327, 619, 1372, 665), 0, 85, "S_R_laundry", "W")
box("S_F_l_dryer", "appliance", (1327, 668, 1372, 714), 0, 85, "S_R_laundry", "W")
box("S_F_l_counter", "counter", (1329, 714, 1376, 892), 0, 92, "S_R_laundry", "W", "worktop run with cabinets")
box("S_F_l_top_wd", "counter", (1327, 613, 1376, 714), 88, 4, "S_R_laundry", "W", "worktop over washer + dryer")
# stair - rises WEST along the north wall from the corridor (4 treads drawn solid at px 1029/1052/1075/1098, the rest
# dashed above the cut). ASSUMED 20 risers x 15 cm (floor-to-floor 300) and 19 goings of 30 cm: px 1098 -> 664, matches the drawn run.
SX_BOT, SX_TOP = cm(1098, "x"), cm(664, "x")
SY0, SY1 = cm(267, "y"), cm(343, "y")
steps, rise = 20, 300 / 20
g = (SX_BOT - SX_TOP) / (steps - 1)
for k in range(1, steps):
    F.append(dict(id=f"S_F_stair_{k:02d}", kind="stair", shape="box", rect=[round(SX_BOT - g * k, 1), SY0, round(SX_BOT - g * (k - 1), 1), SY1],
                  z0=0, h=round(rise * k, 1), room="S_R_corr", group=None))

from design_layer import DESIGN, SITE                    # noqa: E402

plan = dict(
    meta=dict(name="OSNOVA SUTERENA - house type 3, souterrain", source="source/floorplan_suteren.webp", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1591, 1000]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x") for m in o["mullions_px"]]} if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=0, ceiling=H, style=r["style"],
                ceiling_holes=[R(*h) for h in r.get("ceiling_holes", [])]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[dict(id="CEIL_stairwell", rect=R(664, 267, 1045, 343), z=UP, mat="plaster_white")],
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
