"""Design layer for house type 4, first floor: every fixed design decision as 3D geometry.

Client brief: same vibe as the approved ground floor (warm walnut, bronze, stone, LED details, golden hour) but NEW
bedroom designs; beautiful paintings and decor that bring life; bathrooms ~70 % dark with light details and nice
ambient light (client refs: refs/mood/mood_bath_dark_ring.jpg, mood4_wc_chevron.jpg, mood_bath_taupe_walnut.jpg);
light ceilings in the rooms (dark ceilings only in the two baths); no random lights - every light is a real
fitting at a real place; the view out is from the first floor (garden ~3.3 m below).
Coordinates: plan cm, origin = outer NW corner, first-floor finished floor z = 0, ground floor z = -310.
"""
import math

K, OX, OY = 1.313, 383, 173
H, FL = 280, 310


def X(px):
    return round((px - OX) * K, 1)


def Y(py):
    return round((py - OY) * K, 1)


def B(id, mat, x0, y0, x1, y1, z0, z1, kind="decor", emissive=False):
    return dict(id=id, shape="box", mat=mat, rect=[x0, y0, x1, y1], z=[z0, z1], kind=kind, emissive=emissive)


def C(id, mat, cx, cy, r, z0, z1, kind="decor", emissive=False):
    return dict(id=id, shape="cyl", mat=mat, center=[cx, cy], r=r, z=[z0, z1], kind=kind, emissive=emissive)


def S(id, mat, cx, cy, cz, r, kind="decor"):
    return dict(id=id, shape="sphere", mat=mat, center=[cx, cy, cz], r=r, kind=kind)


def DSK(id, mat, cx, cy, cz, r, t, axis, kind="decor"):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind=kind)


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


D = []


def seg(id, mat, p0, p1, w, kind="decor"):
    D.append(dict(id=id, shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal="z", w=w, t=w, kind=kind, emissive=False))


def tree(tag, x, y, pot_r=26, pot_h=60, trunk=110, crown=60, z=0):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, z, z + pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 5, z + pot_h, z + pot_h + trunk))
    D.append(S(f"{tag}_crown", "olive_foliage", x, y, z + pot_h + trunk + crown * 0.7, crown))


def pampas(tag, x, y, z=0):
    D.append(C(f"{tag}_vase", "vase_dark", x, y, 9, z, z + 70))
    for i, (dx, dy, dz) in enumerate([(-16, -6, 150), (11, 5, 168), (-3, 12, 176), (16, -9, 142), (1, -2, 182)]):
        seg(f"{tag}_plume{i}", "pampas", (x, y, z + 68), (x + dx, y + dy, z + dz), 7)


def branches(tag, x, y, z0, h=26, r=7, reach=0.45, w=2.5):
    D.append(C(f"{tag}_vase", "ceramic_dark", x, y, r, z0, z0 + h))
    for i, (dx, dy, dz) in enumerate([(-22, -8, 70), (18, 6, 85), (-4, 16, 95), (12, -14, 64)]):
        seg(f"{tag}_br{i}", "olive_foliage", (x, y, z0 + h - 4), (x + dx * reach, y + dy * reach, z0 + h + dz * reach), w)


def art(id, mat, face, axis, sign, a0, a1, z0, z1):
    lo, hi = sorted((face + sign * 1.2, face + sign * 4.2))
    D.append(B(id, mat, lo, a0, hi, a1, z0, z1, kind="art") if axis == "x" else B(id, mat, a0, lo, a1, hi, z0, z1, kind="art"))


def pendant(id, mat, cx, cy, z_bottom, r, shape="sphere", h=26):
    """a real hanging lamp: shade + thin cable to the ceiling"""
    if shape == "sphere":
        D.append(S(f"{id}_shade", mat, cx, cy, z_bottom + r, r, kind="light"))
        top = z_bottom + 2 * r
    else:
        D.append(C(f"{id}_shade", mat, cx, cy, r, z_bottom, z_bottom + h, kind="light"))
        top = z_bottom + h
    D.append(C(f"{id}_cable", "cable_black", cx, cy, 0.6, top, H, kind="light"))


def cove(tag, x0, y0, x1, y1):
    """shadow-gap LED cove all round a ceiling (inside the room rectangle)"""
    for i, r in enumerate([(x0, y0, x1, y0 + 1.6), (x0, y1 - 1.6, x1, y1), (x0, y0, x0 + 1.6, y1), (x1 - 1.6, y0, x1, y1)]):
        D.append(led(f"{tag}{i}", *r, H - 4, H - 2.5))


# ======================================================================== BEDROOM 1  "travertine + cognac"
BN = Y(202)
# floor-to-ceiling honed travertine bed wall from the wardrobe to the east wall, washed by a ceiling slot
D.append(B("D_b1_trav", "travertine_wall", X(762), BN, X(1043), BN + 2.6, 0, H, kind="panel"))
D.append(led("D_b1_trav_slot", X(763), BN + 2.6, X(1042), BN + 5.0, H - 2, H - 0.5))
# wide cognac-leather channel headboard panel spanning bed + nightstands
D.append(B("D_b1_headpanel", "headboard_cognac_channel", X(790), BN + 2.6, X(1001), BN + 7.0, 0, 128, kind="panel"))
art("D_b1_art", "art_painting_bed1", BN + 2.6, "y", +1, X(843), X(948), 158, 236)
# smoked-glass globe pendants over the nightstands
for i, x in enumerate((812, 979)):
    pendant(f"D_b1_pend{i}", "pendant_glass", X(x), Y(222), 112, 11)
D.append(B("D_b1_rug", "rug_ivory", X(795), Y(275), X(1000), Y(412), 0, 1.2))
# TV wall: walnut panel with a floating walnut console and a few objects
BS1 = Y(430)
D.append(B("D_b1_tvpanel", "walnut_panel", X(822), BS1 - 2.6, X(968), BS1 - 1.2, 0, H, kind="panel"))
D.append(B("D_b1_console", "walnut_console", X(836), BS1 - 34, X(954), BS1 - 2.6, 24, 52))
branches("D_b1_vase", X(944), BS1 - 18, 52, h=30, r=8)
D.append(B("D_b1_books", "books_neutral", X(845), BS1 - 26, X(845) + 30, BS1 - 8, 52, 60))
# sculptural olive tree in the south-west corner, sheer + linen curtains at the east glass, French-balcony glass guard
tree("D_b1_tree", X(700), Y(402), pot_r=24, pot_h=55, trunk=120, crown=55)
for i, (y0, y1) in enumerate([(272, 290), (398, 416)]):
    D.append(B(f"D_b1_curtain{i}", "sheer_linen", X(1043) - 10, Y(y0), X(1043) - 2, Y(y1), 0, 272))
D.append(B("D_b1_guard", "glass", X(1072) + 1, Y(271), X(1072) + 2.2, Y(416), 0, 100, kind="panel"))

# ======================================================================== BEDROOM 2  "olive velvet + walnut"
BE = X(845)
# olive velvet channel headboard wall, walnut picture ledge, a pair of paintings, alabaster pendants
D.append(B("D_b2_velvet", "velvet_olive_channel", BE - 4.4, Y(622), BE - 1.2, Y(846), 0, 128, kind="panel"))
D.append(B("D_b2_ledge", "walnut_shelf", BE - 14, Y(616), BE - 1.2, Y(852), 128, 132))
art("D_b2_art0", "art_painting_pair", BE, "x", -1, Y(681), Y(729), 150, 232)
art("D_b2_art1", "art_painting_pair", BE, "x", -1, Y(741), Y(789), 150, 232)
D.append(led("D_b2_slot", BE - 5, Y(595), BE - 2.6, Y(905), H - 2, H - 0.5))
for i, y in enumerate((650, 818)):
    pendant(f"D_b2_pend{i}", "pendant_alabaster", X(826), Y(y), 108, 8, shape="cyl", h=24)
D.append(B("D_b2_rug", "rug_sand", X(662), Y(648), X(812), Y(822), 0, 1.2))
# large painting on the north wall, olive tree in the south-west corner, curtains at the balcony glass
art("D_b2_art2", "art_painting_wide", Y(594), "y", +1, X(712), X(812), 120, 196)
tree("D_b2_tree", X(628), Y(868), pot_r=24, pot_h=55, trunk=120, crown=55)
for i, (x0, x1) in enumerate([(689, 704), (826, 841)]):
    D.append(B(f"D_b2_curtain{i}", "sheer_linen", X(x0), Y(906) - 10, X(x1), Y(906) - 2, 0, 272))
# steel-grating balcony in front of OG.2 and the entrance glazing (IPE 100 frame) - frameless glass guard (ASSUMED)
D.append(B("D_balc_deck", "steel_grating", X(507), Y(936), X(834), Y(1040), -6, 0, kind="panel"))
D.append(B("D_balc_frame", "black_metal", X(507), Y(1032), X(834), Y(1040), -18, -6, kind="panel"))
for i, r in enumerate([(X(507), Y(1036), X(834), Y(1037.5)), (X(507), Y(936), X(508.5), Y(1040)), (X(832.5), Y(936), X(834), Y(1040))]):
    D.append(B(f"D_balc_guard{i}", "glass", *r, 0, 100, kind="panel"))

# ======================================================================== BATH 1  "riven slate + walnut + travertine" (ref: dark ring)
WB = X(411)
D.append(B("D_ba1_glass", "glass", X(472) - 0.6, BN + 1, X(472) + 0.6, Y(333), 0, 205, kind="panel"))
D.append(B("D_ba1_niche", "niche_trav", WB + 1.2, Y(228), WB + 4.0, Y(305), 100, 128, kind="panel"))
D.append(led("D_ba1_niche_led", WB + 1.2, Y(228), WB + 4.3, Y(305), 126.5, 128))
D.append(C("D_ba1_rain", "black_metal", X(441), Y(268), 14, H - 2, H))
# WC installation ledge with a travertine top, flush plate
D.append(B("D_ba1_ledge", "slate_rough", X(472), BN, X(535), BN + 15, 0, 105, kind="panel"))
D.append(B("D_ba1_ledge_top", "travertine_top", X(472), BN, X(535), BN + 16, 105, 108, kind="panel"))
D.append(B("D_ba1_flush", "black_metal", X(497), BN + 15, X(510), BN + 16.4, 80, 95, kind="panel"))
# vanity: dark stone, travertine vessel basin, walnut shelf below, LED glow; round mirror in a warm LED ring
D.append(C("D_ba1_basin", "basin_travertine", X(578), Y(220), 17, 85, 99))
D.append(B("D_ba1_shelf", "walnut_shelf", X(545), BN, X(615), Y(236), 22, 26))
D.append(led("D_ba1_vanity_led", X(544), BN + 3, X(616), Y(237), 53.5, 55))
D.append(DSK("D_ba1_ring", "ring_led", X(578), BN + 1.3, 158, 41, 1.0, "y", kind="light"))
D.append(DSK("D_ba1_mirror", "mirror_round", X(578), BN + 2.6, 158, 38, 1.4, "y", kind="panel"))
D.append(B("D_ba1_towels", "towels_charcoal", X(590), BN + 2, X(612), Y(234), 26, 36))
cove("D_ba1_cove", WB, BN, X(617), Y(335))
D.append(B("D_ba1_skin_s", "slate_rough", X(586), Y(335) - 1.0, X(617), Y(335), 0, H - 4.5, kind="panel"))   # slate on the bath side of the short nook wall

# ======================================================================== BATH 2  "dark chevron + light marble" (ref: chevron WC)
B2N = Y(449)
D.append(B("D_ba2_drawer", "vanity_walnut_drawer", X(697), B2N, X(773), Y(487), 40, 55))
D.append(led("D_ba2_vanity_led", X(697), B2N + 3, X(773), Y(488), 38.5, 40))
D.append(B("D_ba2_mirror", "mirror_bronze", X(704), B2N + 1.2, X(764), B2N + 3.4, 108, 192, kind="panel"))
D.append(led("D_ba2_bar", X(768), B2N + 1.2, X(770), B2N + 3.6, 108, 192))
D.append(B("D_ba2_glass", "glass", X(776) - 0.6, B2N + 1, X(776) + 0.6, Y(518), 0, 205, kind="panel"))
D.append(B("D_ba2_column", "black_metal", X(845) - 4, Y(458), X(845) - 1.2, Y(504), 30, 200, kind="panel"))
D.append(B("D_ba2_niche", "niche_lit", X(785), B2N + 1.2, X(832), B2N + 4.0, 100, 126, kind="panel"))
D.append(led("D_ba2_niche_led", X(785), B2N + 1.2, X(832), B2N + 4.3, 124.5, 126))
D.append(B("D_ba2_flush", "black_metal", X(845) - 1.4, Y(545), X(845), Y(559), 92, 106, kind="panel"))
D.append(B("D_ba2_towels", "towels_charcoal", X(700), B2N + 3, X(722), Y(484), 85, 95))
branches("D_ba2_vase", X(758), Y(470), 85, h=18, r=5, reach=0.3, w=1.6)
cove("D_ba2_cove", X(693), B2N, BE, Y(586))

# ======================================================================== LANDING + GALLERY + the open stair / entrance below
# monumental painting on the double-height west wall over the stair (seen from both floors)
art("D_art_mono", "art_painting_monumental", WB, "x", +1, Y(575), Y(715), -20, 225)
# ground-floor part of that wall: walnut battens + step lights along the stair (as approved on the ground floor)
D.append(B("D_stair_battens", "walnut_battens", WB + 1.2, Y(450), WB + 4.0, Y(825), -FL, -40, kind="panel"))
for k in range(1, 18):
    yb = Y(825) - 22 * K * (k - 1)
    zt = -FL + FL / 18 * k
    D.append(led(f"D_stair_led{k:02d}", WB + 4, yb - 2.2, X(483), yb - 1.2, zt - 2.2, zt - 1.2))
# slab edges at the gallery and the landing
for i, r in enumerate([(X(489), Y(449), X(491), Y(637)), (X(491), Y(637), X(579), Y(639)), (X(411), Y(447), X(489), Y(449))]):
    D.append(B(f"D_slab_edge{i}", "plaster_warm_white", *r, -30, 0, kind="panel"))
# three smoked-glass globe pendants dropping into the double-height entrance
for i, (x, y, z) in enumerate([(522, 772, 40), (548, 800, 8), (528, 832, -24)]):
    pendant(f"D_entr_pend{i}", "pendant_glass", X(x), Y(y), z, 13)
# landing: wide painting on the bath wall, pampas in the corner
art("D_art_landing", "art_painting_wide", Y(343), "y", +1, X(440), X(552), 118, 192)
pampas("D_land_pampas", X(424), Y(358))
# ground floor below the open part: honed brown marble floor, the GKPL box clad in fluted walnut
D.append(B("D_gf_floor", "marble_brown_floor", X(411), Y(449), X(720), Y(906), -FL - 2, -FL, kind="panel"))
D.append(B("D_gf_gkpl", "walnut_fluted", X(579), Y(709), X(632), Y(790), -FL, -30))

DESIGN = D

# ======================================================================== SITE (golden-hour garden seen from 3.3 m up)
G = -FL - 15          # garden level
SITE = [
    dict(id="EXT_lawn", mat="lawn", rect=[-900, -900, 2900, 2900], z=[G - 1, G]),
    dict(id="EXT_terrace_sw", mat="terrace_stone", rect=[X(290), Y(936), X(866), Y(1114)], z=[G, G + 13]),
    dict(id="EXT_terrace_s", mat="terrace_stone", rect=[X(866), Y(939), X(1250), Y(1054)], z=[G, G + 13]),
    dict(id="EXT_terrace_e", mat="terrace_stone", rect=[X(1250), Y(450), X(1362), Y(1054)], z=[G, G + 13]),
    dict(id="EXT_terrace_ne", mat="terrace_stone", rect=[X(1072), Y(173), X(1180), Y(450)], z=[G, G + 13]),
    dict(id="EXT_planter0", mat="stone_pot", rect=[X(397), Y(1054), X(592), Y(1114)], z=[G + 13, G + 60]),
    dict(id="EXT_planter0_green", mat="hedge", rect=[X(402), Y(1058), X(587), Y(1110)], z=[G + 60, G + 105]),
    dict(id="EXT_hedge_s", mat="hedge", rect=[-300, 2500, 2700, 2560], z=[G, G + 125]),
    dict(id="EXT_hedge_e", mat="hedge", rect=[2400, -300, 2460, 2560], z=[G, G + 125]),
]
for i, (x, y) in enumerate([(900, 1750), (1450, 1950), (2000, 1650), (2150, 1000), (2100, 400), (400, 1900), (1700, 300)]):
    SITE.append(dict(id=f"EXT_tree_trunk{i}", mat="olive_trunk", cyl=[x, y, 9], z=[G, G + 195]))
    SITE.append(dict(id=f"EXT_tree_crown{i}", mat="olive_foliage", sphere=[x, y, G + 285, 115]))
