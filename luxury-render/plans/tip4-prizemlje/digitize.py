"""Digitize 'OSNOVA PRIZEMLJA' of house type 4 (ground floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_prizemlje.png (1598x1128),
measured by pixel scans of the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  1165 cm = ticks px x 390 -> 1277 (887 px) -> 1.3134 cm/px
  1035 cm = ticks py 70 -> 857     (787 px) -> 1.3151 cm/px
   975 cm = ticks py 69 -> 811     (742 px) -> 1.3140 cm/px
  => 1.313 cm/px (same drawing scale as every sheet so far), origin = outer NW corner (381, 59).

Client: double-height ceiling ONLY over the living area (not kitchen / dining) - living void x 852-1231 px, ceiling 5.60 m.
Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 381, 59


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 280            # ASSUMED clear height
VH = 560           # living double height (client)
UP = 600           # stairwell
LEVELS = {"ffl": 0, "ceiling": H, "void_ceiling": VH, "slab_top": 310}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    ("W_west", (381, 59, 410, 822), 0, UP, "ext"),
    ("W_north", (381, 59, 1071, 88), 0, H, "ext"),             # bath window
    ("W_bed_e", (1041, 59, 1071, 316), 0, H, "ext"),           # bedroom east glazing
    ("W_liv_n", (1062, 305, 1231, 336), 0, VH, "ext"),         # living north, exterior part (double height)
    ("W_east", (1231, 305, 1248, 812), 0, VH, "ext"),          # living east glazing (double height)
    ("W_east_fin", (1248, 418, 1288, 447), 0, VH, "ext"),      # projecting fin on the east facade
    ("W_south_w", (381, 792, 866, 822), 0, H, "ext"),          # front door + double door
    ("W_south_glz", (866, 811, 1248, 825), 0, VH, "ext"),      # living south glazing (double height)
    ("W_col_se", (1211, 790, 1233, 812), 0, VH, "ext"),
    ("W_col_e", (1211, 418, 1233, 445), 0, VH, "int"),
    ("W_col_s", (838, 822, 866, 866), 0, H, "ext"),            # pier south of the double door
    # interior
    ("W_bath_s", (410, 221, 631, 229), 0, H, "int"),           # bath | hall
    ("W_bath_e", (622, 88, 631, 221), 0, H, "int"),            # bath | bedroom (door)
    ("W_hall_e", (577, 229, 585, 316), 0, H, "int"),           # hall | bedroom (door)
    ("W_bed_s", (575, 316, 1062, 336), 0, H, "int"),           # bedroom | kitchen + living
    ("W_liv_n_up", (852, 316, 1062, 336), H, VH, "int"),       # wall rising above the bedroom slab over the living void
    ("W_kit_w", (576, 336, 597, 522), 0, H, "int"),            # stair | kitchen west run
    ("W_void_w", (845, 336, 852, 811), H, VH, "int"),          # upper-floor wall closing the living void on the west
    ("W_well_e", (487, 336, 490, 560), H, UP, "int"),          # stairwell shaft above the hall ceiling
    ("W_well_s", (410, 560, 490, 563), H, UP, "int"),
    ("W_well_n", (410, 333, 490, 336), H, UP, "int"),
]

# ---------------------------------------------------------------- openings
openings = [
    dict(id="O_bath_win", type="window", px=(477, 59, 527, 88), sill=170, head=230, note="bathroom high window (north)"),
    dict(id="O_bed_glz", type="sliding", px=(1041, 152, 1071, 304), sill=0, head=250, note="bedroom east: full-height sliding glass"),
    dict(id="O_liv_e_glz", type="curtain", px=(1231, 447, 1248, 790), sill=0, head=540, transom=280,
         mullions_px=[618], note="living east: double-height glazing"),
    dict(id="O_liv_s_glz", type="curtain", px=(866, 811, 1211, 825), sill=0, head=540, transom=280,
         mullions_px=[985, 1101], note="living south: double-height glazing, sliding at the bottom"),
    dict(id="O_front_door", type="door", px=(500, 792, 571, 822), sill=0, head=230, hinge=(571, 792), leaf="solid",
         note="entrance (south-west, beside the stair)"),
    dict(id="O_double_door", type="double_door", px=(690, 792, 838, 822), sill=0, head=240, note="glazed double door (south)"),
    dict(id="O_bath_door", type="door", px=(622, 158, 631, 208), sill=0, head=210, hinge=(631, 158), leaf="solid", note="bedroom -> ensuite"),
    dict(id="O_bed_door", type="door", px=(577, 244, 585, 302), sill=0, head=210, hinge=(585, 244), leaf="solid", note="hall -> bedroom"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="G_R_bath", name="Ensuite bathroom", px=[(410, 88), (622, 88), (622, 221), (410, 221)], style="bath_dark"),
    dict(id="G_R_bed", name="Bedroom", px=[(631, 88), (1041, 88), (1041, 316), (585, 316), (585, 229), (631, 229)], style="bedroom_tray"),
    dict(id="G_R_hall", name="Hall + stair", px=[(410, 229), (577, 229), (577, 336), (576, 336), (576, 522), (597, 522), (597, 792),
                                                (410, 792)], style="hall_light", ceiling_holes=[(410, 336, 487, 560)]),
    dict(id="G_R_kitchen", name="Kitchen + dining", px=[(597, 336), (852, 336), (852, 811), (838, 811), (838, 792), (597, 792)],
         style="kitchen_oak"),
    dict(id="G_R_living", name="Living (double height)", px=[(852, 336), (1231, 336), (1231, 811), (852, 811)], style="living_void",
         ceiling=VH),
]

# ---------------------------------------------------------------- furniture
F = []


def box(id, kind, px, z0, h, room, facing=None, note=None, group=None, **kw):
    F.append(dict(id=id, kind=kind, shape="box", rect=R(*px), z0=z0, h=h, room=room, facing=facing, note=note,
                  src_px=list(px), group=group, **kw))


def rounded(x0, y0, x1, y1, r, n=6):
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


# bathroom
box("G_F_shower", "shower", (410, 88, 470, 221), 0, 3, "G_R_bath")
box("G_F_wc", "toilet", (487, 90, 516, 142), 0, 40, "G_R_bath", "S")
rbox("G_F_vanity", "vanity", (540, 88, 622, 125), 55, 30, "G_R_bath", r=6, note="floating vanity with basin")
# bedroom
box("G_F_wr1", "tall_cabinet", (631, 88, 726, 130), 0, 250, "G_R_bed", "S", "wardrobe (L, part 1)")
box("G_F_wr2", "tall_cabinet", (726, 88, 767, 240), 0, 250, "G_R_bed", "E", "wardrobe (L, part 2)")
box("G_F_bed", "bed", (838, 92, 968, 247), 0, 50, "G_R_bed", "S", "double bed, headboard on the north wall", head_h=110)
rbox("G_F_ns1", "nightstand", (802, 92, 836, 122), 0, 50, "G_R_bed", r=5)
rbox("G_F_ns2", "nightstand", (970, 92, 1004, 122), 0, 50, "G_R_bed", r=5)
# kitchen: north run + west run (cooktop), island with 3 stools, dining table for 6
box("G_F_k_duct", "box", (597, 336, 627, 357), 0, H, "G_R_kitchen", None, "installation duct (2 squares)")
box("G_F_k_run_n", "counter", (627, 336, 848, 382), 0, 92, "G_R_kitchen", "S", "north run: sink, fridge * at the end")
box("G_F_k_fridge", "tall_cabinet", (755, 336, 801, 382), 0, 240, "G_R_kitchen", "S", "fridge column (* on plan)")
box("G_F_k_run_w", "counter", (597, 382, 642, 522), 0, 92, "G_R_kitchen", "E", "west run with cooktop")
box("G_F_k_cooktop", "cooktop", (602, 384, 640, 420), 92, 1, "G_R_kitchen")
box("G_F_k_sink", "sink", (678, 340, 718, 378), 88.5, 4, "G_R_kitchen")
rbox("G_F_island", "island_x", (710, 450, 848, 507), 0, 86, "G_R_kitchen", r=6, note="island; stools on the south side")
for i, cx in enumerate((736, 779, 821)):
    cyl(f"G_F_stool{i}", "stool", cx, 516, 18, 0, 72, "G_R_kitchen")
rbox("G_F_table", "table_r", (710, 605, 848, 666), 72, 4, "G_R_kitchen", r=14, note="dining table for 6")
for i, cx in enumerate((736, 779, 821)):
    cyl(f"G_F_chair_n{i}", "chair", cx, 598, 23, 0, 46, "G_R_kitchen")
    cyl(f"G_F_chair_s{i}", "chair", cx, 673, 23, 0, 46, "G_R_kitchen")
box("G_F_gkpl", "box", (577, 595, 630, 676), 0, H, "G_R_kitchen", None, "GKPL-clad installation box (green on plan)")
# living: soft L-sofa (long side north facing south, leg west facing east), 2 coffee tables, 2 tub armchairs, TV unit
rbox("G_F_sofa", "sofa", (940, 379, 1160, 447), 0, 40, "G_R_living", r=16, group="sofa", note="L-sofa, long side")
rbox("G_F_sofa_leg", "sofa", (940, 447, 1007, 585), 0, 40, "G_R_living", r=16, group="sofa", note="L-sofa, leg")
rbox("G_F_ct1", "coffee_table", (1041, 473, 1091, 519), 0, 34, "G_R_living", r=22)
rbox("G_F_ct2", "coffee_table", (1063, 523, 1113, 570), 0, 40, "G_R_living", r=22)
cyl("G_F_arm1", "armchair", 1027, 672, 38, 0, 42, "G_R_living")
cyl("G_F_arm2", "armchair", 1104, 672, 38, 0, 42, "G_R_living")
rbox("G_F_tv_unit", "low_cabinet", (1192, 459, 1218, 573), 18, 30, "G_R_living", r=6, note="floating unit in front of the media wall")
box("G_F_tv", "tv", (1212, 470, 1215, 562), 95, 70, "G_R_living", "W", "TV on the freestanding walnut media wall")

# stair to the 1st floor: along the west wall, rises NORTH from py 710 (17 treads drawn every 22 px), glass balustrade UOG.1
SX0, SX1 = cm(410, "x"), cm(485, "x")
rise, go, n = 310 / 18, 22 * K, 17
for k in range(1, n + 1):
    yb = cm(710, "y") - go * (k - 1)
    F.append(dict(id=f"G_F_stair_{k:02d}", kind="stair", shape="box", rect=[SX0, round(yb - go, 1), SX1, round(yb, 1)],
                  z0=0, h=round(rise * k, 1), room="G_R_hall", group=None))
t = lambda py: rise * (710 - py) / 22
F.append(dict(id="G_F_uog1", kind="glass", shape="prism", axis="x", x0=cm(485, "x"), x1=cm(487.5, "x"), room="G_R_hall", group=None,
              poly=[[cm(706, "y"), round(t(706), 1)], [cm(340, "y"), round(t(340), 1)], [cm(340, "y"), round(t(340) + 100, 1)],
                    [cm(706, "y"), round(t(706) + 100, 1)]], note="UOG.1 glass balustrade"))

from design_layer import DESIGN, SITE                      # noqa: E402

plan = dict(
    meta=dict(name="OSNOVA PRIZEMLJA - house type 4, ground floor", source="source/floorplan_prizemlje.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1165, 1035]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {}),
               **({"mullions": [cm(m, "x" if (o["px"][2] - o["px"][0]) > (o["px"][3] - o["px"][1]) else "y") for m in o["mullions_px"]]}
                  if "mullions_px" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=0, ceiling=r.get("ceiling", H), style=r["style"],
                ceiling_holes=[R(*h) for h in r.get("ceiling_holes", [])]) for r in rooms],
    furniture=F,
    design=DESIGN,
    extra_ceilings=[dict(id="CEIL_stairwell", rect=R(410, 336, 487, 560), z=UP, mat="plaster_white")],
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
