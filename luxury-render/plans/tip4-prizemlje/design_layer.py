"""Design layer for house type 4, ground floor: every fixed design decision as 3D geometry.

Client references: refs/mood/mood4g_kitchen_island.jpg (black oak + grey-brown marble kitchen, waterfall island with a
backlit bronze mesh front, black shell stools, linear black pendant), mood4g_kitchen_dining.jpg (pale oak plank ceiling,
curved leather dining chairs, sculptural linear pendants), mood4g_bedroom_tray.jpg (light tray ceiling with cove,
dark walls, line-art triptych, sculptural tree), mood4g_master_suite.jpg (the approved faceted walnut bed wall).
Client rules: golden hour, light from the windows; NOT dark ceilings everywhere; double height only over the living;
rounded, organic furniture; no random lights (every light is a real fitting at a real place).
"""
import math

K, OX, OY = 1.313, 381, 59
H, VH = 280, 560


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


def G(id, p0, p1, normal, w=1.6, t=0.4):
    return dict(id=id, shape="seg", mat="led_line", p0=list(p0), p1=list(p1), normal=normal, w=w, t=t, kind="light", emissive=True)


def DSK(id, mat, cx, cy, cz, r, t, axis, kind="decor"):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind=kind)


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


D = []


def seg(id, mat, p0, p1, w, kind="decor"):
    D.append(dict(id=id, shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal="z", w=w, t=w, kind=kind, emissive=False))


def legs(tag, cx, cy, r, z1, mat="walnut_panel", w=3):
    """four slim splayed legs under a round seat"""
    for i, a in enumerate((45, 135, 225, 315)):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        seg(f"{tag}_leg{i}", mat, (cx + dx * r * 0.55, cy + dy * r * 0.55, z1), (cx + dx * r * 0.95, cy + dy * r * 0.95, 0), w)


def arc_back(tag, mat, cx, cy, r, z0, z1, face_deg, span=200, t=6, n=10):
    """curved shell back: a thick arc (span deg) around the seat, opening towards face_deg (deg, plan: 0=+x east, 90=+y south)"""
    back = face_deg + 180
    for i in range(n):
        a0 = math.radians(back - span / 2 + span * i / n)
        a1 = math.radians(back - span / 2 + span * (i + 1) / n)
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0), (z0 + z1) / 2)
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1), (z0 + z1) / 2)
        D.append(dict(id=f"{tag}_back{i}", shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal="z", w=t, t=z1 - z0,
                      kind="decor", emissive=False))


def tree(tag, x, y, pot_r=26, pot_h=60, trunk=110, crown=60):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, 0, pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 5, pot_h, pot_h + trunk))
    D.append(S(f"{tag}_crown", "olive_foliage", x, y, pot_h + trunk + crown * 0.7, crown))


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


# ======================================================================== KITCHEN (refs 19 + 20)
KN = Y(336)
D.append(B("D_k_backsplash_n", "marble_grey_brown", X(627), KN + 1.2, X(755), KN + 2.6, 92, 150, kind="panel"))
D.append(B("D_k_backsplash_n2", "marble_grey_brown", X(801), KN + 1.2, X(848), KN + 2.6, 92, 150, kind="panel"))
D.append(B("D_k_uppers", "cabinet_greige", X(627), KN + 1.2, X(755), KN + 36, 150, H, kind="panel"))
D.append(B("D_k_uppers2", "cabinet_greige", X(801), KN + 1.2, X(848), KN + 36, 150, H, kind="panel"))
D.append(led("D_k_uppers_led", X(629), KN + 4, X(753), KN + 34, 148.5, 150))
D.append(led("D_k_uppers2_led", X(803), KN + 4, X(846), KN + 34, 148.5, 150))
KW = X(597)
D.append(B("D_k_backsplash_w", "marble_grey_brown", KW + 1.2, Y(382), KW + 2.6, Y(522), 92, 150, kind="panel"))
D.append(B("D_k_shelf_w", "walnut_shelf", KW + 2.6, Y(430), KW + 30, Y(515), 150, 155))
D.append(led("D_k_shelf_w_led", KW + 3, Y(432), KW + 28, Y(513), 148.5, 150))
D.append(B("D_k_tap", "black_metal", X(698) - 1, KN + 3, X(698) + 1, KN + 6, 92, 125))
D.append(B("D_k_board", "walnut_shelf", X(645), KN + 2.6, X(670), KN + 4.6, 92, 135))
# island: grey-brown marble top + waterfall ends, backlit bronze mesh front (south), black shell stools on walnut legs
IX0, IX1, IY0, IY1 = X(710), X(848), Y(450), Y(507)
D.append(B("D_island_top", "marble_grey_brown", IX0, IY0, IX1, IY1 + 22, 86, 92))
D.append(B("D_island_mesh", "bronze_mesh", IX0 + 12, IY1 - 0.5, IX1 - 12, IY1 + 1.0, 8, 80, kind="panel"))
D.append(led("D_island_mesh_led", IX0 + 12, IY1 + 1.0, IX1 - 12, IY1 + 3, 82, 83.5))
branches("D_island_vase", X(730), Y(470), 92)
D.append(C("D_island_bowl", "ceramic_light", X(800), Y(475), 16, 92, 100))
for i, cx in enumerate((736, 779, 821)):
    arc_back(f"D_stool{i}", "stool_black_shell", X(cx), Y(516), 18, 72, 82, 270, span=160, t=4, n=6)
    legs(f"D_stool{i}", X(cx), Y(516), 18, 64)
# linear black pendant over the island (ref 19)
D.append(B("D_k_pend", "pendant_black_linear", X(718), Y(476) - 3, X(840), Y(476) + 3, 185, 190, kind="light"))
D.append(led("D_k_pend_led", X(720), Y(476) - 1.5, X(838), Y(476) + 1.5, 184.4, 185))
for x in (X(730), X(828)):
    D.append(C(f"D_k_pend_c{int(x)}", "cable_black", x, Y(476), 0.6, 190, H, kind="light"))
# dining: round-cornered walnut-and-marble table on two pedestals, curved leather shells, sculptural linear pendants (ref 20)
for i, x in enumerate((X(735), X(823))):
    D.append(C(f"D_table_ped{i}", "walnut_panel", x, Y(635.5), 9, 0, 72))
for i, cx in enumerate((736, 779, 821)):
    for row, cy, face in (("n", 598, 90), ("s", 673, 270)):
        arc_back(f"D_chair_{row}{i}", "leather_brown_chair", X(cx), Y(cy), 23, 46, 82, face, span=190, t=5, n=8)
        legs(f"D_chair_{row}{i}", X(cx), Y(cy), 23, 44, mat="black_metal", w=2.4)
for i, ((x0, y0), (x1, y1)) in enumerate([((716, 625), (790, 640)), ((768, 646), (842, 630))]):
    seg(f"D_d_pend{i}", "pendant_bronze", (X(x0), Y(y0), 168), (X(x1), Y(y1), 168), 4, kind="light")
    D.append(C(f"D_d_pend{i}_c0", "cable_black", X(x0) + 3, Y(y0), 0.6, 168, H, kind="light"))
    D.append(C(f"D_d_pend{i}_c1", "cable_black", X(x1) - 3, Y(y1), 0.6, 168, H, kind="light"))
D.append(C("D_d_bowl", "ceramic_dark", X(779), Y(635), 15, 76, 84))
D.append(S("D_d_fruit", "lemons", X(779), Y(635), 85, 8))

# ======================================================================== LIVING (double height 5.6 m)
LN = Y(336)
D.append(B("D_liv_fluted", "walnut_fluted", X(860), LN + 1.2, X(1225), LN + 4.0, 0, VH, kind="panel"))
for i, x in enumerate((X(860) - 1.6, X(1225))):
    D.append(led(f"D_liv_fluted_led{i}", x, LN + 1.2, x + 1.6, LN + 4.6, 0, VH - 4))
# freestanding walnut media wall in front of the east glass (the plan puts the TV against the glazing)
D.append(B("D_liv_media", "walnut_panel", X(1215), Y(452), X(1222), Y(580), 0, 270, kind="panel"))
# soft sofa: rounded back cushions along the north side and the west side of the leg, loose cushions
D.append(B("D_sofa_back_n", "boucle_ivory", X(944), Y(379), X(1156), Y(392), 40, 76))
D.append(B("D_sofa_back_w", "boucle_ivory", X(940), Y(392), X(953), Y(581), 40, 76))
for i, (x, m) in enumerate([(985, "cushion_cognac"), (1030, "cushion_charcoal"), (1090, "cushion_cognac"), (1128, "cushion_charcoal")]):
    D.append(B(f"D_sofa_cush{i}", m, X(x), Y(392), X(x) + 44, Y(392) + 12, 40, 76))
for i, cx in enumerate((1027, 1104)):
    arc_back(f"D_arm{i}", "boucle_ivory", X(cx), Y(672), 37, 42, 74, 270, span=230, t=12, n=10)
D.append(B("D_liv_rug", "rug_dark_wool", X(960), Y(455), X(1180), Y(712), 0, 1.2))
D.append(B("D_liv_books", "books_neutral", X(1048), Y(482), X(1048) + 28, Y(482) + 20, 34, 40))
branches("D_liv_vase", X(1095), Y(545), 40, h=20, r=6, reach=0.35, w=2)
D.append(C("D_liv_bowl", "ceramic_dark", X(1074), Y(498), 11, 34, 40))
tree("D_liv_tree", X(1190), Y(765), pot_r=30, pot_h=60, trunk=150, crown=75)
for i, (y0, y1) in enumerate([(452, 470), (770, 788)]):
    D.append(B(f"D_liv_curtain_e{i}", "sheer_linen", X(1231) - 10, Y(y0), X(1231) - 2, Y(y1), 0, 538))
D.append(B("D_liv_curtain_s", "sheer_linen", X(868), Y(811) - 10, X(888), Y(811) - 2, 0, 538))
art("D_art_void", "art_painting_large", X(852), "x", +1, Y(470), Y(680), 330, 500)
# client: paintings on the fluted walnut wall - a triptych centred over the sofa (no picture lights: lit by the sun)
for i, a in enumerate((710, 825, 940)):     # cm: 3 x 100 cm canvases, 15 cm gaps, centred on the sofa (x 875)
    art(f"D_art_trip{i}", "art_painting_tall", LN + 4.0, "y", +1, a, a + 100, 115, 265)

# ======================================================================== HALL + STAIR
WW = X(410)
D.append(B("D_stair_battens", "walnut_battens", WW + 1.2, Y(336), WW + 4.0, Y(710), 0, 270, kind="panel"))
# the open stair + entrance (first-floor plan): gallery slab edges, glass balustrades UOG.2 / UOG.3, the monumental
# painting on the double-height wall, three smoked-glass globe pendants dropping into the entrance
for i, r in enumerate([(X(487), Y(335), X(489), Y(523)), (X(489), Y(523), X(577), Y(525)), (X(409), Y(333), X(487), Y(335))]):
    D.append(B(f"D_slab_edge{i}", "plaster_warm_white", *r, H, H + 30, kind="panel"))
D.append(B("D_uog2", "glass", X(493), Y(335), X(495), Y(523), H + 30, H + 130, kind="panel"))
D.append(B("D_uog3", "glass", X(495), Y(522), X(577), Y(524), H + 30, H + 130, kind="panel"))
art("D_art_mono", "art_painting_monumental", WW, "x", +1, Y(461), Y(601), 290, 535)
for i, (x, y, z) in enumerate([(520, 658, 350), (546, 686, 318), (526, 718, 286)]):
    D.append(S(f"D_entr_pend{i}_shade", "pendant_glass", X(x), Y(y), z + 13, 13, kind="light"))
    D.append(C(f"D_entr_pend{i}_cable", "cable_black", X(x), Y(y), 0.6, z + 26, 590, kind="light"))
for k in range(1, 18):
    yb = Y(710) - 22 * K * (k - 1)
    D.append(led(f"D_stair_led{k:02d}", WW + 4, yb - 2.2, X(483), yb - 1.2, 310 / 18 * k - 2.2, 310 / 18 * k - 1.2))
for i, (a, b) in enumerate([(430, 470), (480, 520), (530, 570)]):
    art(f"D_art_hall{i}", "art_sketch", Y(229), "y", +1, X(a), X(b), 115, 175)
pampas("D_hall_pampas", X(560), Y(305))

# ======================================================================== BEDROOM (approved Master Suite + light tray ceiling)
WALL_SEAMS = [((0.00, 0.66), (0.42, 1.0)), ((0.42, 1.0), (0.57, 0.50)), ((0.57, 0.50), (0.80, 1.0)),
              ((1.00, 0.60), (0.73, 0.81)), ((0.73, 0.81), (0.57, 0.50)), ((0.21, 0.50), (0.42, 1.0))]
CANOPY_SEAMS = [((0.42, 0.0), (0.66, 0.55)), ((0.66, 0.55), (0.80, 0.0)), ((0.66, 0.55), (0.49, 1.0)),
                ((0.42, 0.0), (0.24, 1.0)), ((1.00, 0.42), (0.66, 0.55))]


def facet_suite(tag, face, a0, a1, depth, slat_w=8.4):
    """faceted walnut wall on the plane y=face (north wall) folding onto the ceiling as a canopy (+y)"""
    zt = H - 9
    def wp(u, v, off):
        return (a0 + u * (a1 - a0), face + off, v * zt)
    def cp(u, d):
        return (a0 + u * (a1 - a0), face + d * depth, zt - 0.3)
    D.append(B(f"D_{tag}_facet_wall", "walnut_facets", a0, face, a1, face + 2.6, 0, zt, kind="panel"))
    D.append(B(f"D_{tag}_facet_canopy", "walnut_facets", a0 - slat_w - 1, face, a1 + slat_w + 1, face + depth, zt, H, kind="panel"))
    for i, ((u0, v0), (u1, v1)) in enumerate(WALL_SEAMS):
        D.append(G(f"D_{tag}_seam_w{i}", wp(u0, v0, 2.9), wp(u1, v1, 2.9), "y"))
    for i, ((u0, d0), (u1, d1)) in enumerate(CANOPY_SEAMS):
        D.append(G(f"D_{tag}_seam_c{i}", cp(u0, d0), cp(u1, d1), "z"))
    D.append(led(f"D_{tag}_canopy_edge", a0 - slat_w - 1, face + depth - 1, a1 + slat_w + 1, face + depth, zt - 1, zt))
    for side, start in (("l", a0 - 1 - slat_w), ("r", a1 + 1)):
        for k in range(4):
            s0 = start + k * slat_w / 4
            D.append(B(f"D_{tag}_slat_{side}{k}", "black_slats", s0 + 0.6, face, s0 + slat_w / 4 - 0.6, face + 8, 0, H, kind="panel"))


facet_suite("bed", Y(88), X(800), X(1005), Y(205) - Y(88))
for i, x in enumerate((819, 987)):
    D.append(C(f"D_bed_lamp{i}_base", "lamp_black", X(x), Y(105), 5, 50, 82, kind="light"))
    D.append(C(f"D_bed_lamp{i}_shade", "lamp_black", X(x), Y(105), 10, 82, 96, kind="light"))
D.append(B("D_bed_rug", "rug_sand", X(818), Y(170), X(990), Y(300), 0, 1.2))
# white marble wall facing the bed (south wall), framed by two LED lines
BS = Y(316)
D.append(B("D_bed_marble", "marble_white_panel", X(790), BS - 2.7, X(1035), BS - 1.2, 0, H - 30, kind="panel"))
for i, x in enumerate((X(790) - 1.5, X(1035))):
    D.append(led(f"D_bed_marble_led{i}", x, BS - 3.4, x + 1.5, BS - 1.2, 0, H - 34))
# light tray ceiling with a warm cove (ref 21): dropped plaster band on the south, east and west sides
for i, r in enumerate([(X(631), BS - 32, X(1041), BS, H - 30, H), (X(1041) - 32, Y(205), X(1041), BS - 32, H - 30, H),
                       (X(767), Y(205), X(767) + 32, BS - 32, H - 30, H)]):
    D.append(B(f"D_bed_tray{i}", "plaster_white", *r, kind="panel"))
D.append(led("D_bed_cove_s", X(767) + 32, BS - 33.5, X(1041) - 32, BS - 32, H - 31.5, H - 30))
D.append(led("D_bed_cove_e", X(1041) - 33.5, Y(205), X(1041) - 32, BS - 32, H - 31.5, H - 30))
D.append(led("D_bed_cove_w", X(767) + 32, Y(205), X(767) + 33.5, BS - 32, H - 31.5, H - 30))
pampas("D_bed_pampas", X(1022), Y(135))
D.append(B("D_bed_curtain0", "sheer_linen", X(1041) - 10, Y(152), X(1041) - 2, Y(170), 0, 270))
D.append(B("D_bed_curtain1", "sheer_linen", X(1041) - 10, Y(290), X(1041) - 2, Y(308), 0, 270))

# ======================================================================== BATH (70 % dark nero marble; warm cream marble as the details; ambient light)
BN = Y(88)
BS, BW, BE = Y(221), X(410), X(622)
# warm marble details: full-height shower back wall + vanity top
D.append(B("D_bath_shower_wall", "marble_warm_veined", BW + 0.2, BN + 0.2, BW + 1.2, BS - 0.2, 0, H - 0.2, kind="panel"))
D.append(B("D_bath_vanity_top", "marble_warm_veined", X(541), BN + 0.2, X(621), Y(124), 85, 87.5, kind="panel"))
# perimeter shadow-gap cove all round the dark ceiling
for i, r in enumerate([(BW + 0.2, BN + 0.2, BE - 0.2, BN + 1.8), (BW + 0.2, BS - 1.8, BE - 0.2, BS - 0.2),
                       (BW + 1.2, BN + 0.2, BW + 2.8, BS - 0.2), (BE - 1.8, BN + 0.2, BE - 0.2, BS - 0.2)]):
    D.append(led(f"D_bath_cove{i}", *r, H - 4, H - 2.5))
D.append(B("D_bath_mirror", "mirror_backlit", X(545), BN + 1.2, X(618), BN + 3.0, 110, 200, kind="panel"))
D.append(led("D_bath_mirror_glow", X(543), BN + 1.2, X(620), BN + 3.4, 201, 202.5))
D.append(led("D_bath_vanity_led", X(542), BN + 3, X(620), Y(123), 53.5, 55))
D.append(C("D_bath_basin", "basin_black_vessel", X(581), Y(106), 18, 87.5, 100))
D.append(B("D_bath_glass", "glass", X(470) - 0.6, BN + 1.2, X(470) + 0.6, Y(215), 0, 205, kind="panel"))
D.append(C("D_bath_rain", "black_metal", X(440), Y(150), 15, H - 2, H, kind="light"))
D.append(B("D_bath_niche", "niche_lit", X(410) + 1.2, Y(110), X(410) + 3.6, Y(170), 100, 130, kind="panel"))
D.append(led("D_bath_niche_led", X(410) + 1.2, Y(110), X(410) + 3.9, Y(170), 128.5, 130))
D.append(B("D_bath_flush", "black_metal", X(495), BN + 1.2, X(508), BN + 3.0, 92, 108, kind="panel"))
D.append(B("D_bath_towels", "towels_charcoal", X(600), Y(98), X(615), Y(118), 85, 95))

DESIGN = D

# ======================================================================== SITE (golden-hour garden seen through the glass)
SITE = [
    dict(id="EXT_lawn", mat="lawn", rect=[-900, -900, 2900, 2900], z=[-16, -15]),
    dict(id="EXT_terrace_sw", mat="terrace_stone", rect=[X(290), Y(822), X(866), Y(1000)], z=[-15, -2]),
    dict(id="EXT_terrace_s", mat="terrace_stone", rect=[X(866), Y(825), X(1248), Y(940)], z=[-15, -2]),
    dict(id="EXT_terrace_e", mat="terrace_stone", rect=[X(1248), Y(336), X(1360), Y(940)], z=[-15, -2]),
    dict(id="EXT_planter0", mat="stone_pot", rect=[X(395), Y(940), X(590), Y(1000)], z=[-2, 45]),
    dict(id="EXT_planter0_green", mat="hedge", rect=[X(400), Y(944), X(585), Y(996)], z=[45, 90]),
    dict(id="EXT_hedge_s", mat="hedge", rect=[-300, 2500, 2700, 2560], z=[-15, 110]),
    dict(id="EXT_hedge_e", mat="hedge", rect=[2400, -300, 2460, 2560], z=[-15, 110]),
]
for i, (x, y) in enumerate([(900, 1750), (1450, 1950), (2000, 1650), (2150, 1000), (2100, 400), (400, 1900)]):
    SITE.append(dict(id=f"EXT_tree_trunk{i}", mat="olive_trunk", cyl=[x, y, 9], z=[-15, 180]))
    SITE.append(dict(id=f"EXT_tree_crown{i}", mat="olive_foliage", sphere=[x, y, 270, 115]))
