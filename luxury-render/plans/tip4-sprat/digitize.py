"""Digitize 'OSNOVA 1 SPRAT' of house type 4 (first floor) into plan.json.

Every element is entered in SOURCE PIXELS of source/floorplan_sprat.png (1598x1130), measured by pixel scans of
the wall faces (see AUDIT.md), then converted to cm.

Scale, from the drawing's own dimension chains:
  1165 cm = ticks px x 392 -> 1279 (887 px) -> 1.3134 cm/px
  1035 cm = ticks py 183 -> 971   (788 px) -> 1.3135 cm/px
  => 1.313 cm/px (same as every sheet). Origin = outer NW corner (383, 173) - the SAME point as the ground floor's
  origin (381, 59), so plan cm here and on the ground floor coincide (first floor = ground px + (2, 114)).

Level: first-floor finished floor z = 0; ground floor below at z = -310 (2.80 m clear + 0.30 m slab); garden -325.
What the drawing shows that matters:
  * the north half repeats the ground floor: ensuite bath + bedroom 1 (L wardrobe, bed head north, east glazing OG.3, TV)
  * bedroom 2 (bed head east), with an entry wardrobe, its own bath 2 (no window) and a glazed door OG.2 to a
    steel-grating balcony (IPE 100 frame, 80x50 grating) over the entrance
  * the stair arrives from the ground floor at the NORTH end of the stair (treads drawn py 450-825 = the ground-floor
    flight seen from above); the floor is OPEN over the whole stair and over the entrance hall south of UOG.3
    (glass balustrades UOG.2 + UOG.3) - a double-height entrance with tall glazing above the front door
  * the living void east of bedroom 2 is closed by plain walls (no opening into it from this floor)
Run:  python3 digitize.py  -> writes plan.json next to this file.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

K = 1.313
OX, OY = 383, 173


def cm(v, axis):
    return round((v - (OX if axis == "x" else OY)) * K, 1)


def R(x0, y0, x1, y1):
    return [cm(x0, "x"), cm(y0, "y"), cm(x1, "x"), cm(y1, "y")]


def P(x, y):
    return [cm(x, "x"), cm(y, "y")]


H = 280            # ASSUMED clear height (same as the ground floor)
FL = 310           # floor-to-floor: ground floor finished floor at z = -310
SLAB = 30
LEVELS = {"ffl": 0, "ceiling": H, "ground_ffl": -FL, "slab_bottom": -SLAB}

# ---------------------------------------------------------------- walls  (px rect, z0, z1, kind)
walls = [
    ("W_west", (383, 173, 411, 936), -FL, H, "ext"),           # runs down past the open entrance + stair
    ("W_north", (383, 173, 1072, 202), 0, H, "ext"),           # bath 1 window
    ("W_bed1_e", (1043, 173, 1072, 430), 0, H, "ext"),         # bedroom 1 east glazing OG.3
    ("W_bed1_s", (578, 430, 1072, 449), 0, H, "int"),          # bedroom 1 | hall + living void
    ("W_south_gf", (383, 906, 862, 936), -FL, -55, "ext"),     # ground-floor part: front door
    ("W_south", (383, 906, 862, 936), -55, H, "ext"),          # entrance glazing, OG.2
    ("W_void_e", (845, 449, 862, 906), 0, H, "int"),           # bath 2 + bedroom 2 | living void (closed)
    # interior
    ("W_bath1_s", (411, 335, 586, 343), 0, H, "int"),          # bath 1 | hall
    ("W_bath1_s2", (586, 335, 624, 343), 0, H, "box"),         # bath 1 | bedroom 1 (west nook); bedroom finish both sides (behind every bath view)
    ("W_bath1_e", (617, 202, 624, 335), 0, H, "int"),          # bath 1 | bedroom 1 (door)
    ("W_hall_e1", (578, 343, 586, 430), 0, H, "int"),          # hall | bedroom 1 (door)
    ("W_hall_e2", (579, 449, 598, 906), -SLAB, H, "int"),      # gallery + entrance void | bedroom 2 (door); beam below
    ("W_bath2_w", (685, 449, 693, 594), 0, H, "int"),          # bedroom 2 vestibule | bath 2 (door)
    ("W_bath2_s", (693, 586, 845, 594), 0, H, "int"),          # bath 2 | bedroom 2
]

# ---------------------------------------------------------------- openings
openings = [
    dict(id="O_bath1_win", type="window", px=(480, 173, 532, 202), sill=160, head=230, note="bath 1 high window (north)"),
    dict(id="O_bath1_door", type="door", px=(617, 270, 624, 324), sill=0, head=210, hinge=(617, 324), leaf="solid",
         note="bedroom 1 -> ensuite bath 1"),
    dict(id="O_bed1_door", type="door", px=(578, 357, 586, 417), sill=0, head=210, hinge=(586, 417), leaf="solid",
         note="hall -> bedroom 1"),
    dict(id="O_bed1_glz", type="sliding", px=(1043, 271, 1072, 416), sill=0, head=250,
         note="OG.3: bedroom 1 east, full-height sliding glass (French balcony)"),
    dict(id="O_bed2_door", type="door", px=(579, 503, 598, 571), sill=0, head=210, hinge=(598, 507), leaf="solid",
         note="gallery -> bedroom 2"),
    dict(id="O_bath2_door", type="door", px=(685, 518, 693, 578), sill=0, head=210, hinge=(693, 518), leaf="solid",
         note="bedroom 2 vestibule -> bath 2"),
    dict(id="O_bed2_glz", type="double_door", px=(689, 906, 841, 936), sill=0, head=250,
         note="OG.2: bedroom 2 south, fixed glass + glazed door to the balcony"),
    dict(id="O_entr_glz", type="window", px=(502, 906, 574, 936), sill=-50, head=260,
         note="tall glazing over the front door, lights the double-height entrance"),
    dict(id="O_front_door", type="door", px=(502, 906, 573, 936), sill=-FL, head=-FL + 230, hinge=(573, 906), leaf="solid",
         note="front door (ground floor, seen through the open entrance)"),
]

# ---------------------------------------------------------------- rooms
rooms = [
    dict(id="F_R_bath1", name="Bath 1 (ensuite)", px=[(411, 202), (617, 202), (617, 335), (411, 335)], style="bath_slate"),
    dict(id="F_R_bed1", name="Bedroom 1", px=[(624, 202), (1043, 202), (1043, 430), (586, 430), (586, 343), (624, 343)],
         style="bed_travertine"),
    dict(id="F_R_hall", name="Landing + gallery", px=[(411, 343), (579, 343), (579, 637), (491, 637), (491, 449), (411, 449)],
         style="hall_upper"),
    dict(id="F_R_bed2", name="Bedroom 2", px=[(598, 449), (685, 449), (685, 594), (845, 594), (845, 906), (598, 906)],
         style="bed_olive"),
    dict(id="F_R_bath2", name="Bath 2", px=[(693, 449), (845, 449), (845, 586), (693, 586)], style="bath_chevron"),
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


# bath 1 (same layout as the ground-floor ensuite below it)
box("F_F_shower1", "shower", (411, 202, 472, 335), 0, 3, "F_R_bath1", note="walk-in shower, glass at x 472")
box("F_F_wc1", "toilet", (489, 204, 518, 256), 0, 40, "F_R_bath1", "S")
rbox("F_F_vanity1", "vanity", (542, 202, 617, 239), 55, 30, "F_R_bath1", r=6, note="floating vanity with basin")
# bedroom 1
box("F_F_wr1", "tall_cabinet", (624, 202, 720, 244), 0, 250, "F_R_bed1", "S", "wardrobe (L, part 1)")
box("F_F_wr2", "tall_cabinet", (720, 202, 762, 343), 0, 250, "F_R_bed1", "E", "wardrobe (L, part 2)")
box("F_F_bed1", "bed", (830, 207, 961, 360), 0, 50, "F_R_bed1", "S", "double bed, headboard on the north wall", head_h=125)
rbox("F_F_ns1", "nightstand", (794, 206, 830, 237), 0, 50, "F_R_bed1", r=5)
rbox("F_F_ns2", "nightstand", (961, 206, 997, 237), 0, 50, "F_R_bed1", r=5)
box("F_F_tv1", "tv", (850, 424, 940, 427), 95, 62, "F_R_bed1", "N", "TV on the south wall, facing the bed")
# bedroom 2 (bed head EAST against the living-void wall)
box("F_F_wr3", "tall_cabinet", (598, 449, 685, 492), 0, 250, "F_R_bed2", "S", "entry wardrobe (installation duct in its corner)")
box("F_F_bed2", "bed", (687, 670, 840, 800), 0, 50, "F_R_bed2", "W", "double bed, headboard on the east wall", head_h=125)
rbox("F_F_ns3", "nightstand", (810, 632, 843, 669), 0, 50, "F_R_bed2", r=5)
rbox("F_F_ns4", "nightstand", (810, 800, 843, 836), 0, 50, "F_R_bed2", r=5)
# bath 2 (no window)
rbox("F_F_vanity2", "vanity", (695, 449, 775, 489), 55, 30, "F_R_bath2", r=4, note="floating vanity, marble basin")
box("F_F_shower2", "shower", (776, 449, 845, 518), 0, 3, "F_R_bath2", note="walk-in shower, glass along x 776")
box("F_F_wc2", "toilet", (797, 537, 845, 567), 0, 40, "F_R_bath2", "W")

# ground-floor stair seen from above (rises NORTH from py 825 at z -310 to the landing at py 450, z 0)
SX0, SX1 = cm(411, "x"), cm(487, "x")
rise, go, n = FL / 18, 22 * K, 17
for k in range(1, n + 1):
    yb = cm(825, "y") - go * (k - 1)
    F.append(dict(id=f"F_F_stair_{k:02d}", kind="stair", shape="box", rect=[SX0, round(yb - go, 1), SX1, round(yb, 1)],
                  z0=-FL, h=round(rise * k, 1), room="F_R_hall", group=None))
t = lambda py: -FL + rise * (825 - py) / 22
F.append(dict(id="F_F_uog1", kind="glass", shape="prism", axis="x", x0=cm(487, "x"), x1=cm(489.5, "x"), room="F_R_hall", group=None,
              poly=[[cm(821, "y"), round(t(821), 1)], [cm(452, "y"), round(t(452), 1)], [cm(452, "y"), round(t(452) + 100, 1)],
                    [cm(821, "y"), round(t(821) + 100, 1)]], note="UOG.1 raked glass balustrade of the stair"))
box("F_F_uog2", "glass", (495, 449, 497, 637), 0, 100, "F_R_hall", note="UOG.2 glass balustrade (gallery | stair void)")
box("F_F_uog3", "glass", (497, 636, 579, 638), 0, 100, "F_R_hall", note="UOG.3 glass balustrade (gallery | entrance void)")

from design_layer import DESIGN, SITE                      # noqa: E402

plan = dict(
    meta=dict(name="OSNOVA 1 SPRAT - house type 4, first floor", source="source/floorplan_sprat.png", units="cm",
              axes="x = east (drawing right), y = south (drawing down), z = up", scale_cm_per_px=K, origin_px=[OX, OY],
              overall_cm=[1165, 1035]),
    levels=LEVELS,
    walls=[dict(id=i, rect=R(*px), z0=z0, z1=z1, kind=k, src_px=list(px)) for i, px, z0, z1, k in walls],
    openings=[{**{k: v for k, v in o.items() if k not in ("px", "hinge", "mullions_px")}, "rect": R(*o["px"]), "src_px": list(o["px"]),
               **({"hinge": P(*o["hinge"])} if "hinge" in o else {})} for o in openings],
    rooms=[dict(id=r["id"], name=r["name"], polygon=[P(*p) for p in r["px"]], floor=0, ceiling=H, style=r["style"],
                ceiling_holes=[]) for r in rooms],
    furniture=F,
    design=DESIGN,
    # the first-floor ceiling continues over the open stair + entrance
    extra_ceilings=[dict(id="CEIL_void_stair", rect=R(411, 449, 491, 906), z=H, mat="plaster_warm_white"),
                    dict(id="CEIL_void_entr", rect=R(491, 637, 579, 906), z=H, mat="plaster_warm_white")],
    site=SITE,
)

problems = []
for o in openings:
    ox0, oy0, ox1, oy1 = o["px"]
    hits = [wid for wid, (x0, y0, x1, y1), z0, z1, _ in walls if min(x1, ox1) - max(x0, ox0) > 0.5 and min(y1, oy1) - max(y0, oy0) > 0.5
            and min(z1, o["head"]) - max(z0, o["sill"]) > 0.5]
    if len(hits) != 1:
        problems.append(f"{o['id']} cuts {hits}")
if problems:
    raise SystemExit("OPENING/WALL INTEGRITY FAILED:\n  " + "\n  ".join(problems))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
json.dump(plan, open(out, "w"), indent=1)
print("wrote", out, "walls", len(plan["walls"]), "openings", len(plan["openings"]), "furniture", len(F), "design", len(DESIGN))
