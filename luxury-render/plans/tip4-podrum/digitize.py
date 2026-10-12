"""Digitize 'OSNOVA PODRUMA' of house type 4 (basement) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_podrum.png (1600x1130),
measured by pixel scans of the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  880 cm  = ticks px x 395.5 -> 1065   (669.5 px) -> 1.3144 cm/px
  1105 cm = ticks px x 395.5 -> 1237   (841.5 px) -> 1.3131 cm/px
  1227 cm = ticks py 78 -> 1012        (934 px)   -> 1.3137 cm/px
  => 1.313 cm/px (same drawing scale as the type 3 sheets), origin = outer NW corner (385, 68).

Basement: no windows (all walls against the earth) except the garage door and the glazed door of the
unlabelled middle room onto its sunken court. Every room is lit by architectural lighting.

Furniture is built from ROUNDED / CURVED profiles (client: "furniture looked like squares put next to each other").
Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 385, 68


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 270            # ASSUMED clear height (basement)
UP = 600           # stairwell ceiling
LEVELS = {"ffl": 0, "ceiling": H, "slab_top": 300}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    # envelope (retaining walls, insulation + waterproofing drawn pink/blue)
    ("W_west", (385, 68, 414, 1012), 0, H, "ext"),
    ("W_north", (385, 68, 1075, 98), 0, H, "ext"),
    ("W_spa_e", (1045, 68, 1075, 345), 0, H, "ext"),
    ("W_garage_n", (1045, 315, 1246, 345), 0, H, "ext"),
    ("W_garage_e", (1218, 315, 1246, 830), 0, H, "ext"),
    ("W_south", (601, 800, 1246, 830), 0, H, "ext"),            # middle-room glazed door + garage door
    ("W_laundry_e", (581, 800, 601, 1012), 0, H, "ext"),        # planter of the sunken court outside
    ("W_laundry_s", (385, 992, 601, 1012), 0, H, "ext"),
    # interior
    ("W_corr_e", (581, 236, 601, 800), 0, H, "int"),            # corridor | spa, garage, middle room (3 doors)
    ("W_corr_s", (414, 800, 581, 821), 0, H, "int"),            # corridor | laundry
    ("W_wc_s", (414, 228, 590, 236), 0, H, "int"),              # WC + sauna | corridor
    ("W_wc_e", (511, 98, 520, 228), 0, H, "int"),               # WC | sauna
    ("W_sauna_e", (627, 98, 635, 172), 0, H, "int"),            # sauna | shower
    ("W_sauna_side", (627, 172, 635, 236), 0, H, "int"),        # sauna glass side (blue)
    ("W_sauna_front", (590, 228, 627, 236), 0, H, "int"),       # sauna glass door (blue)
    ("W_spa_s", (601, 324, 1045, 345), 0, H, "int"),            # spa | garage
    ("W_mid_n", (601, 435, 864, 444), 0, H, "int"),             # middle room | garage
    ("W_mid_e", (845, 435, 864, 800), 0, H, "int"),             # middle room | garage (cabinet wall)
    # stairwell shaft above the lower ceiling (closes the opening over the stair)
    ("W_well_w", (385, 368, 414, 600), H, UP, "int"),
    ("W_well_e", (489, 368, 492, 600), H, UP, "int"),
    ("W_well_n", (414, 365, 492, 368), H, UP, "int"),
    ("W_well_s", (414, 600, 492, 603), H, UP, "int"),
]

# ---------------------------------------------------------------- openings
openings = [
    dict(id="O_wc_door", type="door", px=(445, 228, 500, 236), sill=0, head=210, hinge=(500, 228), leaf="solid", note="corridor -> WC"),
    dict(id="O_sauna_door", type="glass_partition", px=(590, 228, 627, 236), sill=0, head=210, hinge=(627, 232),
         note="sauna glass door (blue on plan)"),
    dict(id="O_sauna_side", type="glass_partition", px=(627, 172, 635, 236), sill=0, head=210, note="sauna glass side"),
    dict(id="O_spa_door", type="door", px=(581, 252, 601, 312), sill=0, head=210, hinge=(601, 312), leaf="solid", note="corridor -> spa"),
    dict(id="O_garage_in", type="door", px=(581, 363, 601, 420), sill=0, head=210, hinge=(601, 420), leaf="solid", note="corridor -> garage"),
    dict(id="O_mid_door", type="door", px=(581, 539, 601, 599), sill=0, head=210, hinge=(601, 539), leaf="solid",
         note="corridor -> middle room (unlabelled)"),
    dict(id="O_laundry_door", type="door", px=(510, 800, 567, 821), sill=0, head=210, hinge=(567, 821), leaf="solid", note="corridor -> laundry"),
    dict(id="O_mid_glz", type="sliding", px=(690, 800, 835, 830), sill=0, head=230, note="middle room: glazed sliding door to the sunken court"),
    dict(id="O_garage_door", type="garage_door", px=(913, 800, 1178, 830), sill=0, head=230, note="sectional garage door (south)"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="B_R_wc", name="WC", px=[(414, 98), (511, 98), (511, 228), (414, 228)], style="wc_dark"),
    dict(id="B_R_sauna", name="Sauna", px=[(520, 98), (627, 98), (627, 228), (520, 228)], style="sauna_timber", ceiling=215),
    dict(id="B_R_spa", name="Spa (jacuzzi, heated bench, shower)",
         px=[(635, 98), (1045, 98), (1045, 324), (601, 324), (601, 236), (631, 236), (631, 172), (635, 172)], style="spa_dark"),
    dict(id="B_R_corr", name="Corridor + stair", px=[(414, 236), (581, 236), (581, 800), (414, 800)], style="corridor_dark",
         ceiling_holes=[(414, 368, 489, 600)]),
    dict(id="B_R_laundry", name="Laundry", px=[(414, 821), (581, 821), (581, 992), (414, 992)], style="laundry_dark"),
    dict(id="B_R_mid", name="Middle room (unlabelled, no furniture)", px=[(601, 444), (845, 444), (845, 800), (601, 800)], style="corridor_dark"),
    dict(id="B_R_garage", name="Garage",
         px=[(601, 345), (1218, 345), (1218, 800), (864, 800), (864, 435), (601, 435)], style="garage_gallery"),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None, group=None, **kw):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=group, **kw))


def rounded(x0, y0, x1, y1, r, n=6):
    """plan polygon (cm) of a rectangle with radius-r corners (soft, organic furniture outlines)"""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append([round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)])
    return pts


def rbox(id, kind, px, z0, h, room, r=8, note=None, **kw):
    x0, y0, x1, y1 = R(*px)
    F.append(dict(id=id, kind=kind, shape="prism", axis="z", poly=rounded(x0, y0, x1, y1, r), z0=z0, h=h, room=room,
                  note=note, src_px=list(px), group=None, **kw))


# WC: wall-hung toilet (north wall), floating stone basin counter on the west wall
box("B_F_wc_toilet", "toilet", (467, 100, 497, 147), 0, 40, "B_R_wc", "S")
rbox("B_F_wc_vanity", "vanity", (414, 140, 446, 212), 70, 18, "B_R_wc", r=6, note="floating stone counter with integrated basin")
# sauna: upper bench along the west wall (purple line px 565), lower step
box("B_F_sauna_hi", "bench", (520, 98, 565, 228), 0, 95, "B_R_sauna", "E", "upper bench")
box("B_F_sauna_lo", "bench", (565, 98, 590, 228), 0, 45, "B_R_sauna", "E", "lower bench / step")
# spa: shower tray, round jacuzzi D 168, heated bench 'topla klupa' (two curved ergonomic seats)
box("B_F_shower", "shower", (635, 98, 715, 172), 0, 3, "B_R_spa")
F.append(dict(id="B_F_jacuzzi", kind="jacuzzi", shape="cyl", center=P(962, 218), r=round(64 * K, 1), z0=0, h=62, room="B_R_spa",
              note="round jacuzzi D 168"))
WB = cm(98, "y")


def heated_seat(id, x0px, x1px):
    """curved reclining heated bench: side profile (y, z) extruded along x - organic, not a box"""
    y = lambda py: cm(py, "y")
    prof = [(WB, 0), (WB, 100), (WB + 6, 104), (WB + 14, 98), (WB + 22, 76), (WB + 30, 56), (WB + 40, 47), (y(160) - 6, 45),
            (y(160), 41), (y(160), 14), (y(160) - 8, 8), (y(160) - 8, 0)]
    F.append(dict(id=id, kind="heated_bench", shape="prism", axis="x", x0=cm(x0px, "x"), x1=cm(x1px, "x"), poly=[list(p) for p in prof],
                  room="B_R_spa", group="heated_bench", note="heated stone bench 'topla klupa', curved reclining back"))


heated_seat("B_F_bench_w", 721, 793)
heated_seat("B_F_bench_e", 797, 858)
# garage: car (built in design_layer), cabinet run on the middle-room wall (purple on plan)
rbox("B_F_g_cab", "tall_cabinet", (864, 437, 909, 800), 0, 240, "B_R_garage", r=10, note="full-height cabinet wall")
# laundry: washer + dryer under a worktop run on the west wall, folding counter after them
box("B_F_l_washer", "appliance", (416, 822, 460, 868), 0, 85, "B_R_laundry", "E")
box("B_F_l_dryer", "appliance", (416, 870, 460, 918), 0, 85, "B_R_laundry", "E")
rbox("B_F_l_counter", "counter_r", (414, 918, 460, 992), 0, 90, "B_R_laundry", r=6, note="cabinet run")
rbox("B_F_l_top", "worktop", (414, 820, 462, 992), 88, 4, "B_R_laundry", r=4, note="worktop over washer, dryer and cabinets")

# stair to the ground floor: along the west wall, rises NORTH from py 720 (treads drawn every 22 px = 28.9 cm)
SX0, SX1 = cm(414, "x"), cm(489, "x")
rise, go, n = 300 / 17, 22 * K, 16
for k in range(1, n + 1):
    yb = cm(720, "y") - go * (k - 1)
    F.append(dict(id=f"B_F_stair_{k:02d}", kind="stair", shape="box", rect=[SX0, round(yb - go, 1), SX1, round(yb, 1)],
                  z0=0, h=round(rise * k, 1), room="B_R_corr", group=None))
# UOG.4: raked frameless glass balustrade on the open side of the lower flight (px x 489-492, py 590-697)
t = lambda py: rise * (720 - py) / 22
F.append(dict(id="B_F_uog4", kind="glass", shape="prism", axis="x", x0=cm(489, "x"), x1=cm(491.5, "x"), room="B_R_corr", group=None,
              poly=[[cm(697, "y"), round(t(697), 1)], [cm(590, "y"), round(t(590), 1)], [cm(590, "y"), round(t(590) + 100, 1)],
                    [cm(697, "y"), round(t(697) + 100, 1)]], note="UOG.4 glass balustrade"))

from design_layer import DESIGN, SITE, CAR                # noqa: E402
F.extend(CAR)

plan = dict(
    meta=dict(name="OSNOVA PODRUMA - house type 4, basement", source="source/floorplan_podrum.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1105, 1227]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=0, ceiling=r.get("ceiling", H), style=r["style"],
                ceiling_holes=[R(*h) for h in r.get("ceiling_holes", [])]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[dict(id="CEIL_stairwell", rect=R(414, 368, 489, 600), z=UP, mat="plaster_dark")],
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
