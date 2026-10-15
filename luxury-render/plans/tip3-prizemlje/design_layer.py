"""Design layer for house type 3, ground floor: every fixed design decision as 3D geometry.

Same design language as the approved floors: oak floor, warm greige plaster, walnut slatted ceiling,
hand-patinated bronze feature wall, smoked-walnut kitchen with grey-taupe marble (house 1 ground floor);
the "Master Suite" bedroom (faceted walnut wall + LED seams, white marble wall) and the bright warm
limestone bathrooms with the rough slate ONLY as one feature panel (type 3 souterrain).

Client rules for this floor: NO random light fittings - only fittings that a real house has at that
spot (two linear pendants over island and dining, the bedroom's approved facet seams + lamps, the
ring mirror in the bathroom, sauna bench backlight, one pendant in the guest WC, two linear lines in
the garage ceiling); paintings and decor on the walls; terrace visible through the living + spa glass;
a black Mercedes S-Class in the garage.

Coordinates: drawing px -> plan cm with the scale of digitize.py.
"""
K, OX, OY = 1.313, 173, 60
LO, H = -60, 280


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


def G(id, p0, p1, normal, w=1.6, t=0.4):
    return dict(id=id, shape="seg", mat="led_line", p0=list(p0), p1=list(p1), normal=normal, w=w, t=t, kind="light", emissive=True)


def DSK(id, mat, cx, cy, cz, r, t, axis, kind="panel"):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind=kind)


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


D = []


def cable(id, x, y, z0, z1):
    D.append(C(id, "cable_black", x, y, 0.6, z0, z1, kind="light"))


def lamp(tag, x, y, z=50):
    D.append(C(f"{tag}_base", "lamp_black", x, y, 5, z, z + 32, kind="light"))
    D.append(C(f"{tag}_shade", "lamp_black", x, y, 10, z + 32, z + 46, kind="light"))


def pendant(tag, x, y, zb, zt=H):
    D.append(C(tag, "pendant_black_cyl", x, y, 4, zb, zb + 30, kind="light"))
    cable(f"{tag}_c", x, y, zb + 30, zt)


def pampas(tag, x, y, z=0):
    """dried pampas: tall dark vase + slender plume stems (NOT spheres - spheres read as globe lamps)"""
    D.append(C(f"{tag}_vase", "vase_dark", x, y, 9, z, z + 70))
    for i, (dx, dy, dz) in enumerate([(-16, -6, 150), (11, 5, 168), (-3, 12, 176), (16, -9, 142), (1, -2, 182)]):
        D.append(dict(id=f"{tag}_plume{i}", shape="seg", mat="pampas", p0=[x, y, z + 68], p1=[x + dx, y + dy, z + dz], normal="z",
                      w=7, t=7, kind="decor", emissive=False))


def branches(tag, x, y, z0, h=60, r=11, reach=1.0, w=6):
    """vase with olive branches: dark ceramic cylinder + a few leafy stems (no spheres near ceilings)"""
    D.append(C(f"{tag}_vase", "ceramic_dark", x, y, r, z0, z0 + h))
    for i, (dx, dy, dz) in enumerate([(-22, -8, 70), (18, 6, 85), (-4, 16, 95), (12, -14, 64)]):
        D.append(dict(id=f"{tag}_br{i}", shape="seg", mat="olive_foliage", p0=[x, y, z0 + h - 4],
                      p1=[x + dx * reach, y + dy * reach, z0 + h + dz * reach], normal="z", w=w, t=w, kind="decor", emissive=False))


def art(id, mat, face, axis, sign, a0, a1, z0, z1):
    """framed artwork hung on a wall plane (axis 'x': plane x=face along y; 'y': plane y=face along x)"""
    lo, hi = sorted((face + sign * 1.2, face + sign * 4.2))
    if axis == "x":
        D.append(B(id, mat, lo, a0, hi, a1, z0, z1, kind="art"))
    else:
        D.append(B(id, mat, a0, lo, a1, hi, z0, z1, kind="art"))


def tree(tag, x, y, z0, pot_r=24, pot_h=55, trunk=85, crown=50):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, z0, z0 + pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 4, z0 + pot_h, z0 + pot_h + trunk))
    D.append(S(f"{tag}_crown", "olive_foliage", x, y, z0 + pot_h + trunk + crown * 0.7, crown))


# ======================================================================== LIVING (floor 0)
# bronze feature wall = TV wall: south face of the spa wall, east of the column (house-1 living material)
TVF = Y(667)
D.append(B("D_liv_bronze", "bronze_panels", X(828), TVF + 1.2, X(1172), TVF + 3.0, 0, H, kind="panel"))
for x in (X(914), X(1000), X(1086)):
    D.append(B(f"D_liv_bronze_rv{int(x)}", "reveal_dark", x - 0.7, TVF + 3.0, x + 0.7, TVF + 3.4, 0, H, kind="panel"))
D.append(B("D_liv_bronze_rh", "reveal_dark", X(828), TVF + 3.0, X(1172), TVF + 3.4, 139.3, 140.7, kind="panel"))
D.append(B("D_liv_rug", "rug_sand", X(892), Y(735), X(1128), Y(1000), 0, 1.2))
# cushions along the sofa back (sofa faces south) + one on the chaise
for i, (x, m) in enumerate([(927, "cushion_cognac"), (972, "cushion_navy"), (1032, "cushion_cognac"), (1072, "cushion_navy")]):
    D.append(B(f"D_liv_cush{i}", m, X(x), Y(747), X(x) + 44, Y(747) + 12, 42, 82))
D.append(B("D_liv_cush4", "cushion_cognac", X(909), Y(835), X(909) + 12, Y(835) + 44, 42, 82))
D.append(B("D_liv_books", "books_neutral", X(992), Y(855), X(992) + 30, Y(855) + 22, 34, 40))
D.append(C("D_liv_bowl", "ceramic_dark", X(1050), Y(890), 13, 40, 47))
branches("D_liv_vase", X(1008), Y(882), 34, h=24, r=7, reach=0.4, w=2.5)
# TV floor stand (client reference: slim black screen on one dark post, light oak + linen soundbar, rectangular base)
TX, TY = X(1011.5), Y(1021.5)
D.append(B("D_tvs_base", "black_metal", TX - 45, TY - 4, TX + 45, TY + 36, 0, 3, kind="panel"))
D.append(B("D_tvs_post", "black_metal", TX - 3, TY + 3, TX + 3, TY + 8, 0, 64, kind="panel"))
D.append(B("D_tvs_bar", "oak_planks_light", TX - 62, TY - 6, TX + 62, TY + 3, 48, 60, kind="panel"))
for i, (y0, y1) in enumerate([(1053 - 7, 1053 - 1)]):
    D.append(B("D_liv_curtain_sw", "sheer_linen", X(466) + 1, Y(y0), X(484), Y(y1), 0, 272))
    D.append(B("D_liv_curtain_se", "sheer_linen", X(1153), Y(y0), X(1172) - 1, Y(y1), 0, 272))
D.append(B("D_liv_curtain_e", "sheer_linen", X(1172) - 9, Y(925), X(1172) - 1, Y(944), 0, 272))
tree("D_liv_olive", X(1148), Y(692), 0)
D.append(C("D_liv_column", "column_plaster", X(818), Y(1034), 13, 0, H, kind="panel"))
# paintings (life): large canvas over the dining (WC-block wall), portrait canvas in the upper hall
art("D_art_dining", "art_painting_large", TVF, "y", +1, X(684), X(790), 100, 215)
# big painting on the bronze wall where the TV was (client revision 2026-10-15), over the floating console
art("D_art_liv", "art_painting_monumental", TVF + 3.0, "y", +1, X(1012) - 115, X(1012) + 115, 80, 235)
art("D_art_hall", "art_painting_portrait", X(643), "x", -1, Y(574), Y(640), 95, 215)

# ======================================================================== KITCHEN + DINING
KW = X(465)
for i, (a, b) in enumerate([(687, 781), (850, 1025)]):
    D.append(B(f"D_k_backsplash{i}", "stone_backsplash", KW + 1.2, Y(a), KW + 2.6, Y(b), 92, H, kind="panel"))
D.append(B("D_k_shelf", "walnut_shelf", KW + 2.6, Y(940), KW + 30, Y(1018), 150, 155))
D.append(C("D_k_shelf_jar0", "ceramic_light", X(474), Y(960), 6, 155, 175))
D.append(C("D_k_shelf_jar1", "ceramic_dark", X(474), Y(985), 8, 155, 168))
D.append(B("D_k_board", "walnut_shelf", KW + 2.6, Y(860), KW + 4.6, Y(873), 92, 130))
D.append(B("D_k_island_top", "marble_island", X(586), Y(803), X(655), Y(972), 86, 92))
D.append(B("D_k_tap", "black_metal", X(472), Y(902), X(476), Y(904), 92, 122))
# linear bronze pendants: one along the island, one along the dining table
IX = X(609)
D.append(B("D_k_pend_island", "pendant_bronze", IX - 3, Y(828), IX + 3, Y(948), 182, 187, kind="light"))
cable("D_k_pend_island_c0", IX, Y(834), 187, H); cable("D_k_pend_island_c1", IX, Y(942), 187, H)
DY = Y(880.5)
D.append(B("D_d_pend", "pendant_bronze", X(676), DY - 3, X(772), DY + 3, 160, 165, kind="light"))
cable("D_d_pend_c0", X(682), DY, 165, H); cable("D_d_pend_c1", X(766), DY, 165, H)
D.append(C("D_d_bowl", "ceramic_light", X(723), DY, 18, 76, 84))
D.append(S("D_d_lemons", "lemons", X(723), DY, 85, 9))
branches("D_k_vase", X(608), Y(828), 92, h=26, r=7, reach=0.45, w=2.5)

# ======================================================================== ENTRY + STAIR + CORRIDOR (floor -60)
D.append(B("D_e_battens", "walnut_battens", X(663), Y(397) - 3.4, X(1023), Y(397) - 1.2, LO, 600, kind="panel"))
art("D_art_corr", "art_relief", Y(416), "y", +1, X(684), X(770), LO + 100, LO + 215)
branches("D_e_vase", X(620), Y(343), LO, h=70, r=13, reach=0.9, w=3.5)
D.append(B("D_e_bench", "walnut_counter", X(523), Y(325), X(590), Y(325) + 38, LO + 40, LO + 45))
D.append(B("D_e_bench_leg0", "walnut_counter", X(523), Y(325), X(523) + 4, Y(325) + 38, LO, LO + 40))
D.append(B("D_e_bench_leg1", "walnut_counter", X(590) - 4, Y(325), X(590), Y(325) + 38, LO, LO + 40))

# ======================================================================== GUEST WC (bright limestone; slate only behind the vanity)
WF = X(776)
D.append(B("D_wc_slate", "slate_feature", WF - 3.4, Y(505), WF - 1.2, Y(627), LO, H, kind="panel"))
D.append(C("D_wc_basin", "basin_black_vessel", X(752), Y(546), 19, LO + 90, LO + 104))
D.append(DSK("D_wc_mirror", "mirror_round", WF - 4.4, Y(546), LO + 160, 30, 1.6, "x"))
pendant("D_wc_pend", X(752), Y(512), LO + 130)
D.append(B("D_wc_flush", "black_metal", X(690), Y(648) - 2.9, X(702), Y(648) - 1.1, LO + 92, LO + 108, kind="panel"))
art("D_wc_art", "art_sketch", X(663), "x", +1, Y(530), Y(585), LO + 110, LO + 190)
D.append(B("D_wc_towels", "towels_charcoal", X(760), Y(600), X(774), Y(620), LO + 90, LO + 98))

# ======================================================================== SPA (bright limestone, walnut ceiling) + SAUNA
SN = Y(416)
D.append(B("D_spa_bench", "walnut_counter", X(855), SN + 1.2, X(1000), SN + 42, LO + 40, LO + 45))
for i, x in enumerate((X(855), X(1000) - 4)):
    D.append(B(f"D_spa_bench_leg{i}", "walnut_counter", x, SN + 1.2, x + 4, SN + 42, LO, LO + 40))
D.append(B("D_spa_towels", "towels_charcoal", X(965), SN + 4, X(990), SN + 38, LO + 45, LO + 60))
art("D_spa_art", "art_relief", SN, "y", +1, X(870), X(985), LO + 120, LO + 235)
D.append(C("D_spa_orchid_pot", "ceramic_dark", X(1150), Y(560), 9, LO, LO + 22))
D.append(S("D_spa_orchid", "orchid_white", X(1150), Y(560), LO + 46, 15))
for i, (dx, dy, h) in enumerate([(-14, 10, 12), (-6, 18, 8), (-20, 20, 6)]):
    D.append(C(f"D_spa_candle{i}", "candle", X(1150) + dx, Y(560) + dy, 3.5, LO, LO + h))
# walk-in shower: rough slate ONLY on its back wall, one fixed clear glass panel, black rain head
D.append(B("D_spa_sh_slate", "slate_feature", X(906), Y(648) - 3.4, X(986), Y(648) - 1.2, LO, H, kind="panel"))
D.append(B("D_spa_sh_glass", "glass", X(986) - 0.6, Y(584), X(986) + 0.6, Y(648) - 1.2, LO, LO + 205, kind="panel"))
D.append(C("D_spa_rain", "black_metal", X(946), Y(612), 15, H - 2, H, kind="light"))
# sauna: backlight under the upper bench (real sauna detail), stove with stones in the corner
D.append(led("D_sauna_bench_led", X(814) - 1.2, Y(508), X(814), Y(645), LO + 86, LO + 87.5))
D.append(B("D_sauna_stove", "sauna_stove", X(878), Y(624), X(898), Y(646), LO, LO + 72))

# ======================================================================== BATHROOM (bedroom wing)
BN = Y(564)
D.append(B("D_bath_slate", "slate_feature", X(275), BN + 1.2, X(350), BN + 3.4, 0, H, kind="panel"))
D.append(B("D_bath_drawer", "vanity_walnut_drawer", X(284), BN + 3.4, X(341), Y(598), 25, 48))
D.append(C("D_bath_basin", "basin_black_vessel", X(312.5), Y(582), 19, 90, 104))
D.append(DSK("D_bath_mirror", "mirror_round", X(312.5), BN + 4.4, 160, 33, 1.6, "y"))
D.append(T("D_bath_ring", "ring_led", X(312.5), BN + 6.6, 160, 38, 1.3, "y"))
D.append(B("D_bath_sh_glass", "glass", X(270) - 0.6, BN + 1.2, X(270) + 0.6, Y(616), 0, 205, kind="panel"))
D.append(C("D_bath_rain", "black_metal", X(236), Y(598), 15, H - 2, H, kind="light"))
D.append(B("D_bath_flush", "black_metal", X(201) + 1.2, Y(661), X(201) + 3.0, Y(679), 92, 108, kind="panel"))
D.append(B("D_bath_towels", "towels_charcoal", X(290), BN + 6, X(306), BN + 20, 92, 100))

# ======================================================================== BEDROOM ("Master Suite", headboard on the west wall)
WALL_SEAMS = [((0.00, 0.66), (0.42, 1.0)), ((0.42, 1.0), (0.57, 0.50)), ((0.57, 0.50), (0.80, 1.0)),
              ((1.00, 0.60), (0.73, 0.81)), ((0.73, 0.81), (0.57, 0.50)), ((0.21, 0.50), (0.42, 1.0))]
CANOPY_SEAMS = [((0.42, 0.0), (0.66, 0.55)), ((0.66, 0.55), (0.80, 0.0)), ((0.66, 0.55), (0.49, 1.0)),
                ((0.42, 0.0), (0.24, 1.0)), ((1.00, 0.42), (0.66, 0.55))]


def facet_suite(tag, face, a0, a1, depth, slat_w=8.4):
    """approved faceted walnut wall on the plane x=face (bed wall) folding onto the ceiling as a canopy (+x)"""
    zt = H - 9
    def wp(u, v, off):
        return (face + off, a0 + u * (a1 - a0), v * zt)
    def cp(u, d):
        return (face + d * depth, a0 + u * (a1 - a0), zt - 0.3)
    def rect(p0, p1, z0, z1, id, mat, **kw):
        (u0, o0), (u1, o1) = p0, p1
        D.append(B(id, mat, face + min(o0, o1), u0, face + max(o0, o1), u1, z0, z1, **kw))
    rect((a0, 0), (a1, 2.6), 0, zt, f"D_{tag}_facet_wall", "walnut_facets", kind="panel")
    rect((a0 - slat_w - 1, 0), (a1 + slat_w + 1, depth), zt, H, f"D_{tag}_facet_canopy", "walnut_facets", kind="panel")
    for i, ((u0, v0), (u1, v1)) in enumerate(WALL_SEAMS):
        D.append(G(f"D_{tag}_seam_w{i}", wp(u0, v0, 2.9), wp(u1, v1, 2.9), "x"))
    for i, ((u0, d0), (u1, d1)) in enumerate(CANOPY_SEAMS):
        D.append(G(f"D_{tag}_seam_c{i}", cp(u0, d0), cp(u1, d1), "z"))
    rect((a0 - slat_w - 1, depth - 1), (a1 + slat_w + 1, depth), zt - 1, zt, f"D_{tag}_canopy_edge", "led_line", kind="light", emissive=True)
    for side, start in (("l", a0 - 1 - slat_w), ("r", a1 + 1)):
        for k in range(4):
            s0 = start + k * slat_w / 4
            rect((s0 + 0.6, 0), (s0 + slat_w / 4 - 0.6, 8), 0, H, f"D_{tag}_slat_{side}{k}", "black_slats", kind="panel")


facet_suite("bed", X(201), Y(786), Y(995), X(300) - X(201))
lamp("D_bed_lamp0", X(220), Y(811))
lamp("D_bed_lamp1", X(220), Y(970))
D.append(B("D_bed_rug", "rug_sand", X(262), Y(800), X(418), Y(985), 0, 1.2))
MF = X(445)
D.append(B("D_bed_marble", "marble_white_panel", MF - 2.7, Y(772), MF - 1.2, Y(996), 0, H, kind="panel"))
D.append(led("D_bed_marble_led0", MF - 3.4, Y(772) - 1.5, MF - 1.2, Y(772), 0, H - 4))
D.append(led("D_bed_marble_led1", MF - 3.4, Y(996), MF - 1.2, Y(996) + 1.5, 0, H - 4))
D.append(B("D_bed_curtain0", "sheer_linen", X(201) + 1, Y(1005) - 9, X(221) + 6, Y(1005) - 1, 0, 250))
D.append(B("D_bed_curtain1", "sheer_linen", X(400) - 4, Y(1005) - 9, X(400) + 14, Y(1005) - 1, 0, 250))
pampas("D_bed_pampas", X(214), Y(776))
art("D_art_lobby", "art_sketch", Y(564), "y", +1, X(372), X(436), 100, 195)

# ======================================================================== GARAGE (floor -60): car gallery
for x in (X(262), X(384)):
    D.append(led(f"D_g_led{int(x)}", x - 1.5, Y(100), x + 1.5, Y(530), H - 1.5, H))
art("D_g_art", "art_photo_bw", X(445), "x", -1, Y(150), Y(330), LO + 105, LO + 215)

DESIGN = D

# ======================================================================== CAR: Mercedes-Benz S-Class (long saloon, black), nose-in
# side-profile prisms (plan y, z) extruded across the car's width; drawn car centre px x 315, nose toward the south wall
CX0, CX1 = X(315) - 96, X(315) + 96              # 192 cm wide
CY0 = Y(125)                                     # rear bumper; length 518 cm -> nose at Y(519.5)
L = 518


def prof(pts):
    return [[round(CY0 + u, 1), round(LO + z, 1)] for u, z in pts]


CAR = [
    dict(id="P_F_car", kind="car", shape="prism", axis="x", x0=CX0, x1=CX1, room="P_R_garage", group=None,
         poly=prof([(2, 22), (0, 62), (6, 92), (40, 101), (112, 104), (396, 106), (470, 96), (508, 82), (L, 60), (L - 2, 22)]),
         note="black Mercedes-Benz S-Class, parked nose-in exactly where the car is drawn"),
    dict(id="P_F_car_glass", kind="car_glass", shape="prism", axis="x", x0=CX0 + 9, x1=CX1 - 9, room="P_R_garage", group=None,
         poly=prof([(110, 103), (182, 146), (322, 148), (400, 105)])),
]
for i, u in enumerate((92, 404)):                # wheelbase 312 cm
    for s, x, o in (("l", CX0, -1), ("r", CX1, +1)):
        D.append(DSK(f"D_car_tyre{i}{s}", "car_tyre", x, CY0 + u, LO + 36, 36, 22, "x", kind="decor"))
        D.append(DSK(f"D_car_wheel{i}{s}", "car_wheel", x + o * 11.6, CY0 + u, LO + 36, 26, 1.2, "x", kind="decor"))

# ======================================================================== SITE (seen through the glass; hidden from the QA passes)
SITE = [
    dict(id="EXT_north_yard", mat="lawn", rect=[-900, -900, 2600, Y(320)], z=[LO - 3, LO - 2]),
    dict(id="EXT_drive", mat="terrace_stone", rect=[X(201), -400, X(445), Y(60)], z=[LO - 2, LO - 1]),
    dict(id="EXT_east_lawn", mat="lawn", rect=[X(1390), Y(320), 2600, Y(716)], z=[LO - 3, LO - 2]),
    dict(id="EXT_east_slope", mat="lawn", rect=[X(1390), Y(716), 2600, Y(1066)], z=[-200, -199]),
    dict(id="EXT_west_lawn", mat="lawn", rect=[-900, Y(320), X(173), Y(1034)], z=[LO - 3, LO - 2]),
    dict(id="EXT_garden", mat="lawn", rect=[-900, Y(1066), 2600, 3200], z=[-362, -361]),
    dict(id="EXT_low_terrace", mat="terrace_stone", rect=[X(173), Y(1066), X(1202), Y(1066) + 190], z=[-361, -360]),
    dict(id="EXT_hedge", mat="hedge", rect=[-300, 2520, 2300, 2590], z=[-360, -240]),
    # raised east terrace: spa part at the entry level, 4 steps, living part at the living level
    dict(id="EXT_terrace_spa", mat="terrace_stone", rect=[X(1202), Y(300), X(1390), Y(648)], z=[LO - 20, LO]),
    dict(id="EXT_terrace_liv", mat="terrace_stone", rect=[X(1202), Y(716), X(1390), Y(966)], z=[-30, 0]),
]
for k, (a, b) in enumerate([(648, 671), (671, 693), (693, 716)]):
    SITE.append(dict(id=f"EXT_terrace_step{k + 1}", mat="terrace_stone", rect=[X(1202), Y(a), X(1390), Y(b)], z=[LO - 20, LO + 15 * (k + 1)]))
for i, (x, y, z) in enumerate([(250, 2050, -360), (820, 2250, -360), (1350, 2000, -360), (1900, 1800, -360), (-350, 1600, -360),
                               (2050, 450, LO), (2150, 1000, -200)]):
    SITE.append(dict(id=f"EXT_tree_trunk{i}", mat="olive_trunk", cyl=[x, y, 9], z=[z, z + 190]))
    SITE.append(dict(id=f"EXT_tree_crown{i}", mat="olive_foliage", sphere=[x, y, z + 280, 120]))

# terrace furniture + glass railings (OG.1 - OG.4) as exterior design objects (glass needs the design-layer transparency)
EXT = [
    B("X_rail_og1", "glass", X(465), Y(1069), X(1172), Y(1071.5), 0, 100, kind="exterior"),
    B("X_rail_og2", "glass", X(221), Y(1036), X(400), Y(1038.5), 0, 100, kind="exterior"),
    B("X_rail_og3", "glass", X(1205), Y(962), X(1390), Y(964.5), 0, 100, kind="exterior"),
    B("X_rail_og4", "glass", X(1386.5), Y(831), X(1389), Y(964), 0, 100, kind="exterior"),
    B("X_lounger0", "lounger_teak", X(1250), Y(440), X(1250) + 70, Y(440) + 190, LO, LO + 32, kind="exterior"),
    B("X_lounger0_back", "lounger_teak", X(1250), Y(440), X(1250) + 70, Y(440) + 12, LO + 32, LO + 80, kind="exterior"),
    B("X_lounger1", "lounger_teak", X(1250) + 100, Y(440), X(1250) + 170, Y(440) + 190, LO, LO + 32, kind="exterior"),
    B("X_lounger1_back", "lounger_teak", X(1250) + 100, Y(440), X(1250) + 170, Y(440) + 12, LO + 32, LO + 80, kind="exterior"),
    C("X_side_table", "outdoor_table", X(1250) + 85, Y(440) + 40, 14, LO, LO + 40, kind="exterior"),
    B("X_out_sofa", "outdoor_sofa", X(1222), Y(905), X(1372), Y(905) + 82, 0, 40, kind="exterior"),
    B("X_out_sofa_back", "outdoor_sofa", X(1222), Y(905) + 66, X(1372), Y(905) + 82, 40, 75, kind="exterior"),
    B("X_out_table", "outdoor_table", X(1262), Y(840), X(1332), Y(840) + 60, 0, 36, kind="exterior"),
    C("X_planter0", "stone_pot", X(1365), Y(740), 28, 0, 60, kind="exterior"),
    C("X_planter0_trunk", "olive_trunk", X(1365), Y(740), 5, 60, 150, kind="exterior"),
    S("X_planter0_crown", "olive_foliage", X(1365), Y(740), 190, 50, kind="exterior"),
    C("X_planter1", "stone_pot", X(1365), Y(330), 28, LO, LO + 60, kind="exterior"),
    C("X_planter1_trunk", "olive_trunk", X(1365), Y(330), 5, LO + 60, LO + 150, kind="exterior"),
    S("X_planter1_crown", "olive_foliage", X(1365), Y(330), LO + 190, 50, kind="exterior"),
]
DESIGN.extend(EXT)
