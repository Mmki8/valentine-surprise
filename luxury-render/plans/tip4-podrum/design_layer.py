"""Design layer for house type 4, basement: every fixed design decision as 3D geometry.

Client brief: the dark design they love (refs/mood/mood4_bath_croc.jpg, mood4_vanity_basalt.jpg, mood4_wc_chevron.jpg):
dark basalt / dark stone, croc-textured black stone tub, warm oak slats with backlit edges, wood accents in the spa,
sauna and WC, beautiful plants; NO windows, so architectural lighting everywhere - but every light is a real fitting
at a real place (coves, step lights, under-vanity strips, backlit panels, picture lights, sauna bench backlight).
Furniture is soft and rounded (see digitize.py), never a row of boxes.
"""
K, OX, OY = 1.313, 385, 68
H = 270


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


def T(id, mat, cx, cy, cz, R, tube, axis, kind="light"):
    return dict(id=id, shape="torus", mat=mat, center=[cx, cy, cz], R=R, tube=tube, axis=axis, kind=kind)


def DSK(id, mat, cx, cy, cz, r, t, axis, kind="decor"):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind=kind)


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


D = []


def seg(id, mat, p0, p1, w, kind="decor"):
    D.append(dict(id=id, shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal="z", w=w, t=w, kind=kind, emissive=False))


def tree(tag, x, y, pot_r=24, pot_h=55, trunk=85, crown=48):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, 0, pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 4, pot_h, pot_h + trunk))
    D.append(S(f"{tag}_crown", "olive_foliage", x, y, pot_h + trunk + crown * 0.7, crown))


def fern(tag, x, y, r=26):
    D.append(C(f"{tag}_pot", "vase_dark", x, y, r * 0.75, 0, 42))
    D.append(S(f"{tag}_leaves", "fern_foliage", x, y, 62, r))


def blossom(tag, x, y, z0=0, h=75, reach=1.0):
    """tall dark vase with flowering cherry branches (as in the client's reference)"""
    D.append(C(f"{tag}_vase", "vase_dark", x, y, 11, z0, z0 + h))
    for i, (dx, dy, dz) in enumerate([(-30, -8, 70), (26, 10, 88), (-6, 22, 100), (18, -18, 62), (-22, 16, 80)]):
        seg(f"{tag}_br{i}", "blossom", (x, y, z0 + h - 4), (x + dx * reach, y + dy * reach, z0 + h + dz * reach), 5)


def art(id, mat, face, axis, sign, a0, a1, z0, z1, light=True):
    """framed artwork on a wall plane + a slim bronze picture light above it (a real fitting)"""
    lo, hi = sorted((face + sign * 1.2, face + sign * 4.2))
    if axis == "x":
        D.append(B(id, mat, lo, a0, hi, a1, z0, z1, kind="art"))
    else:
        D.append(B(id, mat, a0, lo, a1, hi, z0, z1, kind="art"))
    if light:
        m0, m1 = (a0 + a1) / 2 - (a1 - a0) * 0.3, (a0 + a1) / 2 + (a1 - a0) * 0.3
        l0, l1 = sorted((face + sign * 1.2, face + sign * 12))
        if axis == "x":
            D.append(B(f"{id}_plight", "picture_light", l0, m0, l1, m1, z1 + 8, z1 + 12, kind="light"))
        else:
            D.append(B(f"{id}_plight", "picture_light", m0, l0, m1, l1, z1 + 8, z1 + 12, kind="light"))


def cove(tag, pts, z=H - 3):
    """warm LED cove: a light line 4 cm off each listed wall face, just under the ceiling"""
    for i, (x0, y0, x1, y1) in enumerate(pts):
        D.append(led(f"D_{tag}_cove{i}", x0, y0, x1, y1, z - 1.5, z))


# ======================================================================== SPA (dark basalt, oak slats, croc-stone jacuzzi, moss wall)
NW = Y(98)
# warm oak slat feature wall behind the curved heated bench, backlit at both ends
D.append(B("D_spa_slats", "oak_slats_h", X(718), NW + 1.2, X(862), NW + 4.0, 0, H, kind="panel"))
for i, x in enumerate((X(718) - 1.6, X(862))):
    D.append(led(f"D_spa_slats_led{i}", x, NW + 1.2, x + 1.6, NW + 4.6, 0, H - 2))
D.append(led("D_spa_bench_glow", X(723), Y(160) - 9, X(856), Y(160) - 7, 4, 5.5))          # toe-kick glow under the bench
# living moss wall on the spa side of the garage wall, grazed by a warm line above
SW = Y(324)
D.append(B("D_spa_moss", "moss_wall", X(690), SW - 4.0, X(880), SW - 1.2, 30, 235, kind="panel"))
D.append(led("D_spa_moss_led", X(690), SW - 8, X(880), SW - 6, 246, 247.5))
# jacuzzi: soft glow ring at its plinth
D.append(T("D_spa_jac_glow", "led_line", X(962), Y(218), 4, 64 * K - 3, 1.4, "z"))
for i, (dx, dy) in enumerate([(0, 0), (-12, 8), (10, 10)]):
    D.append(C(f"D_spa_candle{i}", "candle", X(880) + dx, Y(300) + dy, 3.5, 0, 14 - 4 * i, kind="light"))
D.append(C("D_spa_orchid_pot", "ceramic_dark", X(868), Y(305), 8, 0, 22))
for i, (dx, dy, dz) in enumerate([(-9, 2, 52), (7, -3, 58), (1, 8, 48)]):
    seg(f"D_spa_orchid{i}", "orchid_white", (X(868), Y(305), 22), (X(868) + dx, Y(305) + dy, dz), 3.5)
tree("D_spa_olive", X(1024), Y(122))
D.append(B("D_spa_towels", "towels_charcoal", X(845), Y(108), X(856), Y(150), 47, 58))
# shower: glass door + fixed glass (south), glass side (east), black rain head, lit niche in the back wall
D.append(B("D_sh_glass_s", "glass", X(637), Y(172) - 0.6, X(715), Y(172) + 0.6, 0, 205, kind="panel"))
D.append(B("D_sh_glass_e", "glass", X(715) - 0.6, NW + 1.2, X(715) + 0.6, Y(172), 0, 205, kind="panel"))
D.append(C("D_sh_rain", "black_metal", X(675), Y(135), 15, H - 2, H, kind="light"))
D.append(B("D_sh_niche", "niche_lit", X(650), NW + 1.2, X(700), NW + 3.6, 100, 130, kind="panel"))
D.append(led("D_sh_niche_led", X(650), NW + 1.2, X(700), NW + 3.9, 128.5, 130))
cove("spa", [(X(722), NW + 3, X(1045) - 3, NW + 5), (X(1045) - 5, NW + 3, X(1045) - 3, SW - 3), (X(601) + 3, SW - 5, X(1045) - 3, SW - 3)])
# sauna: backlight under both benches, stove with stones
D.append(led("D_sauna_hi_led", X(565) - 1.4, Y(100), X(565), Y(226), 86, 87.5))
D.append(led("D_sauna_lo_led", X(590) - 1.4, Y(100), X(590), Y(226), 36, 37.5))
D.append(B("D_sauna_stove", "sauna_stove", X(600), Y(101), X(624), Y(124), 0, 72))

# ======================================================================== WC (dark chevron stone, marble trough, bronze mirror, oak behind the WC)
WW = X(414)
D.append(B("D_wc_oak", "oak_slats_h", X(452), NW + 1.2, X(511) - 0.5, NW + 3.6, 0, H, kind="panel"))
D.append(B("D_wc_flush", "black_metal", X(476), NW + 3.6, X(488), NW + 5.0, 92, 108, kind="panel"))
D.append(B("D_wc_drawer", "vanity_walnut_drawer", WW + 1.2, Y(146), X(444), Y(206), 42, 70))
D.append(led("D_wc_vanity_led", WW + 2, Y(148), X(442), Y(204), 40.5, 41.5))
D.append(B("D_wc_mirror", "mirror_bronze", WW + 1.2, Y(148), WW + 4.5, Y(204), 110, 195, kind="panel"))
D.append(led("D_wc_lightbar", WW + 1.2, Y(212), WW + 4.2, Y(215), 115, 190))
D.append(B("D_wc_tap", "black_metal", WW + 1.2, Y(175) - 1, WW + 14, Y(175) + 1, 100, 103))
blossom("D_wc_blossom", X(438), Y(152), 88, h=18, reach=0.35)
cove("wc", [(WW + 3, NW + 3, X(511) - 3, NW + 5)])

# ======================================================================== CORRIDOR + STAIR (smoked walnut, dark plaster, B&W photographs)
CE = X(581)
art("D_art_c0", "art_photo_portrait_bw", CE, "x", -1, Y(438), Y(530), 105, 205)
art("D_art_c1", "art_photo_portrait_bw", CE, "x", -1, Y(622), Y(690), 110, 200)
art("D_art_c2", "art_photo_portrait_bw", CE, "x", -1, Y(712), Y(780), 110, 200)
for k in range(1, 17):                                                   # warm LED under every stair nosing
    yb = Y(720) - 22 * K * (k - 1)
    D.append(led(f"D_stair_led{k:02d}", WW + 2, yb - 2.2, X(487), yb - 1.2, 300 / 17 * k - 2.2, 300 / 17 * k - 1.2))
D.append(B("D_stair_wall_slats", "walnut_battens", WW + 1.2, Y(368), WW + 4.0, Y(720), 0, H, kind="panel"))
tree("D_corr_olive", X(440), Y(772), pot_r=20)
fern("D_corr_fern", X(562), Y(256), r=20)
cove("corr", [(WW + 3, Y(240), WW + 5, Y(368)), (CE - 5, Y(240), CE - 3, Y(796))])

# ======================================================================== LAUNDRY (walnut + marble, open shelf with LED under)
D.append(B("D_l_shelf", "walnut_shelf", WW + 1.2, Y(830), X(436), Y(990), 150, 154))
D.append(led("D_l_shelf_led", WW + 2, Y(832), X(434), Y(988), 148.5, 149.5))
D.append(B("D_l_basket", "rattan_basket", WW + 3, Y(930), X(434), Y(955), 154, 172))
D.append(B("D_l_towels", "towels_charcoal", WW + 3, Y(962), X(434), Y(985), 154, 166))
D.append(C("D_l_plant_pot", "ceramic_dark", X(437), Y(965), 7, 92, 108))
D.append(S("D_l_plant", "fern_foliage", X(437), Y(965), 118, 11))
cove("laundry", [(WW + 3, Y(824), WW + 5, Y(990)), (X(581) - 5, Y(824), X(581) - 3, Y(990))])

# ======================================================================== GARAGE (car gallery: dark, walnut cabinet wall, two linear lines)
for x in (X(1010), X(1100)):
    D.append(led(f"D_g_led{int(x)}", x - 1.5, Y(360), x + 1.5, Y(790), H - 1.5, H))
D.append(led("D_g_cab_niche", X(909), Y(560), X(910.5), Y(680), 100, 101.5))
D.append(B("D_g_cab_niche_back", "oak_slats_h", X(905), Y(560), X(909), Y(680), 100, 160, kind="panel"))
art("D_g_art", "art_photo_bw", Y(345), "y", +1, X(940), X(1180), 105, 215, light=False)

DESIGN = D

# ======================================================================== CAR: Mercedes-Benz CLE Coupe (black), nose NORTH as drawn
CX0, CX1 = X(1055) - 93, X(1055) + 93            # 186 cm wide
YN = Y(395)                                      # nose; length 486 cm -> rear at py ~765
LO = 0


def prof(pts):
    return [[round(YN + u, 1), round(z, 1)] for u, z in pts]


CAR = [
    dict(id="B_F_car", kind="car", shape="prism", axis="x", x0=CX0, x1=CX1, room="B_R_garage", group=None,
         poly=prof([(2, 22), (0, 58), (10, 74), (90, 88), (170, 97), (420, 104), (470, 100), (486, 88), (486, 58), (484, 22)]),
         note="black Mercedes-Benz CLE Coupe, nose-in as drawn"),
    dict(id="B_F_car_glass", kind="car_glass", shape="prism", axis="x", x0=CX0 + 10, x1=CX1 - 10, room="B_R_garage", group=None,
         poly=prof([(168, 95), (250, 137), (330, 139), (425, 102)])),
]
for i, u in enumerate((85, 372)):
    for s, x, o in (("l", CX0, -1), ("r", CX1, +1)):
        D.append(DSK(f"D_car_tyre{i}{s}", "car_tyre", x, YN + u, 34, 34, 22, "x"))
        D.append(DSK(f"D_car_wheel{i}{s}", "car_wheel", x + o * 11.6, YN + u, 34, 25, 1.2, "x"))

SITE = [dict(id="EXT_ground", mat="lawn", rect=[-600, -600, 2000, 2000], z=[-2, -1])]
