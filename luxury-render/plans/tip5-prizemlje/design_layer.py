"""Design layer for house type 5, ground floor: every fixed design decision as 3D geometry.

Client brief: the approved design language of the earlier houses (warm smoked walnut, black oak, grey-brown + brown
marble, bronze, warm LED lines, golden hour), beautiful plants, paintings on the walls, darker bedrooms with bright
details and wood details, a matte black G-Wagon in the garage, a higher ceiling over the living up to the dining table,
golden-hour sun entering through the glass; positions 100 % as drawn.
Coordinates: plan cm, origin = outer NW corner of the garage.
"""
import math

K, OX, OY = 1.313, 131, 183
H, VH, FL = 280, 590, 310
XV = 911          # px: upper slab edge / UOG.2 glass balustrade (first-floor plan)


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


def arc_back(tag, mat, cx, cy, r, z0, z1, face_deg, span=200, t=6, n=10):
    back = face_deg + 180
    for i in range(n):
        a0 = math.radians(back - span / 2 + span * i / n)
        a1 = math.radians(back - span / 2 + span * (i + 1) / n)
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0), (z0 + z1) / 2)
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1), (z0 + z1) / 2)
        D.append(dict(id=f"{tag}_back{i}", shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal="z", w=t, t=z1 - z0,
                      kind="decor", emissive=False))


def tree(tag, x, y, pot_r=26, pot_h=60, trunk=110, crown=60, foliage="olive_foliage"):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, 0, pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 5, pot_h, pot_h + trunk))
    D.append(S(f"{tag}_crown", foliage, x, y, pot_h + trunk + crown * 0.7, crown))


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
    if shape == "sphere":
        D.append(S(f"{id}_shade", mat, cx, cy, z_bottom + r, r, kind="light"))
        top = z_bottom + 2 * r
    else:
        D.append(C(f"{id}_shade", mat, cx, cy, r, z_bottom, z_bottom + h, kind="light"))
        top = z_bottom + h
    return top


def cable(id, cx, cy, z0, z1):
    D.append(C(id, "cable_black", cx, cy, 0.6, z0, z1, kind="light"))


def cove(tag, x0, y0, x1, y1, z):
    for i, r in enumerate([(x0, y0, x1, y0 + 1.6), (x0, y1 - 1.6, x1, y1), (x0, y0, x0 + 1.6, y1), (x1 - 1.6, y0, x1, y1)]):
        D.append(led(f"{tag}{i}", *r, z - 4, z - 2.5))


# ======================================================================== LIVING + DINING (double height, open to the first-floor gallery)
LN = Y(497)
# full-height fluted walnut wall behind the floating stair, the stair's step lights
D.append(B("D_liv_fluted", "walnut_fluted", X(905), LN, X(1374), LN + 2.8, 0, VH, kind="panel"))
NT = 16
rise, go = FL / (NT + 1), (1259 - 905) / NT * K
for k in range(1, NT + 1):
    xe = X(1259) - go * (k - 1)
    D.append(led(f"D_stair_led{k:02d}", xe - go + 1, LN + 2.8, xe - 1, LN + 4.4, rise * k - 8, rise * k - 6.5))
# the upper slab edge with the UOG.2 frameless glass balustrade of the first-floor gallery (no wall above the kitchen)
D.append(B("D_gal_fascia", "plaster_warm_white", X(XV) - 2, Y(573), X(XV), Y(953), H, FL, kind="panel"))
D.append(B("D_gal_fascia_st", "plaster_warm_white", X(905) - 2, Y(497), X(905), Y(573), H, FL, kind="panel"))
D.append(B("D_gal_glass", "glass", X(XV) - 1.5, Y(573), X(XV), Y(953), FL, FL + 105, kind="panel"))
D.append(B("D_gal_cap", "bronze_frame", X(XV) - 2, Y(573), X(XV) + 0.5, Y(953), FL + 105, FL + 108, kind="panel"))
# a stepped gallery of four paintings on the fluted walnut wall, rising parallel to the stair (client: add life)
for i, xc in enumerate((1580, 1460, 1340, 1220, 1100)):   # 5th: client round 4 (seen in the LIV_B view)
    zc = max(0, FL / 18 * (1 + (X(1260) - xc) / (22 * K))) + 140     # positions as approved (fixed)
    art(f"D_art_stair{i}", "art_stair_series", LN + 2.8, "y", +1, xc - 48, xc + 48, zc - 62, zc + 62)
# monumental three-tier chandelier, centrepiece of the double-height void (bottom at 3.0 m, visible from every living view)
CH_X, CH_Y = X(1050), Y(660)
for i, (r, z0, z1) in enumerate([(75, 300, 322), (58, 342, 362), (42, 382, 400)]):
    D.append(C(f"D_chand_t{i}", "chandelier_crystal", CH_X, CH_Y, r, z0, z1, kind="light"))
for i in range(3):
    a = math.radians(90 + 120 * i)
    cable(f"D_chand_c{i}", CH_X + 30 * math.cos(a), CH_Y + 30 * math.sin(a), 400, VH)
# monumental painting on the high wall above the kitchen side (faces east into the living)
art("D_art_mono", "art_painting_monumental", X(623), "x", +1, Y(705), Y(865), FL + 45, FL + 245)   # gallery back wall
# freestanding walnut media wall in front of the east glass with the TV, floating console (plan: TV stand at the glass)
D.append(B("D_media_wall", "walnut_panel", X(1376), Y(600), X(1384), Y(735), 0, 265, kind="panel"))
D.append(B("D_media_console", "walnut_console", X(1350), Y(616), X(1376), Y(717), 18, 46))
# sofa: rounded back + cushions on the west side; armchairs with curved backs facing north
D.append(B("D_sofa_back", "boucle_ivory", X(1071) + 2, Y(656), X(1084), Y(853), 40, 78))
for i, (y, m) in enumerate([(680, "cushion_cognac"), (725, "cushion_charcoal"), (785, "cushion_cognac"), (822, "cushion_charcoal")]):
    D.append(B(f"D_sofa_cush{i}", m, X(1084), Y(y), X(1084) + 12, Y(y) + 40, 40, 74))
for i, cx in enumerate((1204, 1282)):
    arc_back(f"D_arm{i}", "boucle_ivory", X(cx), Y(900), 37, 42, 76, 270, span=220, t=12, n=10)
D.append(B("D_liv_rug", "rug_dark_wool", X(1100), Y(668), X(1325), Y(862), 0, 1.2))
branches("D_liv_vase", X(1219), Y(722), 36, h=24, r=7, reach=0.35, w=2)
D.append(B("D_liv_books", "books_neutral", X(1232), Y(765), X(1232) + 26, Y(765) + 18, 30, 36))
# plants: olive tree in the glass corner, a tall fig between the dining and the sofa
tree("D_liv_olive", X(1362), Y(952), pot_r=28, pot_h=60, trunk=170, crown=80)
tree("D_liv_fig", X(1035), Y(948), pot_r=24, pot_h=55, trunk=120, crown=55, foliage="fig_foliage")
# dining: two long bronze linear pendants from the high ceiling over the table
for i, x in enumerate((942.5,)):   # one bronze pendant over the dining table (client)
    D.append(B(f"D_d_pend{i}", "pendant_bronze", X(x) - 1.5, Y(735), X(x) + 1.5, Y(838), 182, 186, kind="light"))
    for y in (735, 838):
        cable(f"D_d_pend{i}_c{y}", X(x), Y(y), 186, VH)
D.append(B("D_d_base", "marble_grey_brown", X(930), Y(745), X(955), Y(828), 0, 72))
for i, cy in enumerate((743, 785, 828)):
    arc_back(f"D_chw{i}", "leather_brown_chair", X(905), Y(cy), 21, 46, 80, 0, span=170, t=5, n=6)
    arc_back(f"D_che{i}", "leather_brown_chair", X(981), Y(cy), 21, 46, 80, 180, span=170, t=5, n=6)
D.append(S("D_d_fruit", "lemons", X(942), Y(786), 80, 8))
# curtains at the glass, warm cove around the high ceiling
for i, (y0, y1) in enumerate([(612, 628), (958, 976)]):
    D.append(B(f"D_liv_curtain_e{i}", "sheer_linen", X(1395) - 10, Y(y0), X(1395) - 2, Y(y1), 0, VH - 22))
D.append(B("D_liv_curtain_s", "sheer_linen", X(920), Y(980) - 10, X(936), Y(980) - 2, 0, VH - 22))
cove("D_liv_cove", X(XV), LN + 2.8, X(1395), Y(980), VH)

# ======================================================================== KITCHEN + HALL (normal height, pale oak ceiling)
KW = X(624)
D.append(B("D_k_backsplash", "marble_grey_brown", KW, Y(795), KW + 2.4, Y(952), 92, 150, kind="panel"))
D.append(B("D_k_shelf", "walnut_shelf", KW, Y(805), KW + 26, Y(945), 158, 162))
D.append(led("D_k_shelf_led", KW + 1.6, Y(805), KW + 24, Y(945), 156.5, 158))
D.append(B("D_k_worktop", "marble_grey_brown", KW, Y(795), X(670) + 1, Y(952), 92, 95, kind="panel"))
D.append(B("D_k_island_top", "marble_grey_brown", X(762), Y(658), X(830), Y(898), 92, 96, kind="panel"))
D.append(B("D_k_pend", "pendant_black_linear", X(796) - 2.5, Y(690), X(796) + 2.5, Y(860), 182, 186, kind="light"))
for y in (690, 860):
    cable(f"D_k_pend_c{y}", X(796), Y(y), 186, H)
branches("D_k_vase", X(796), Y(700), 96, h=26, r=7)
# hall: painting on the bedroom wall (faces the hall), pampas by the kitchen, a slim LED line in the hall ceiling
art("D_art_hall", "art_painting_wide", Y(657), "y", -1, X(445), X(598), 118, 198)
pampas("D_hall_pampas", X(608), Y(636))
D.append(led("D_hall_line", X(300), Y(574), X(600), Y(575.5), H - 1.5, H))

# ======================================================================== BEDROOM (darker, wood, bright details)
BE = X(605)
# bed wall: smoked walnut slats full width + a backlit honey-onyx panel behind the ivory headboard (the bright detail)
D.append(B("D_b_slats", "walnut_slats_v", BE - 2.8, Y(676), BE, Y(954), 0, H, kind="panel"))
D.append(B("D_b_onyx", "onyx_backlit", BE - 4.2, Y(752), BE - 2.8, Y(878), 0, 230, kind="panel"))
D.append(led("D_b_onyx_top", BE - 4.4, Y(752), BE - 2.8, Y(878), 230, 231.5))
for i, y in enumerate((732, 898)):
    top = pendant(f"D_b_pend{i}", "pendant_alabaster", BE - 22, Y(y), 112, 8, shape="cyl", h=24)
    cable(f"D_b_pend{i}_c", BE - 22, Y(y), top, H)
D.append(B("D_b_rug", "rug_ivory", X(430), Y(730), X(560), Y(900), 0, 1.2))
art("D_art_bed", "art_painting_pair", Y(676), "y", +1, X(455), X(590), 120, 205)
tree("D_b_plant", X(588), Y(937), pot_r=16, pot_h=45, trunk=95, crown=40, foliage="fig_foliage")
D.append(B("D_b_curtain0", "sheer_linen", X(362), Y(954) - 10, X(378), Y(954) - 2, 0, 270))
D.append(B("D_b_curtain1", "sheer_linen", X(500), Y(954) - 10, X(516), Y(954) - 2, 0, 270))
cove("D_b_cove", X(210), Y(676), BE - 2.8, Y(954), H)

# ======================================================================== ENSUITE (70 % dark, cream marble details)
D.append(B("D_e_shower_wall", "marble_warm_veined", X(210), Y(885), X(210) + 2.4, Y(952), 0, H - 4.5, kind="panel"))
D.append(B("D_e_glass", "glass", X(277) - 0.6, Y(885), X(277) + 0.6, Y(952), 0, 205, kind="panel"))
D.append(C("D_e_rain", "black_metal", X(243), Y(918), 13, H - 2, H))
D.append(B("D_e_mirror", "mirror_backlit", X(210), Y(822), X(210) + 1.8, Y(877), 110, 190, kind="panel"))
D.append(led("D_e_vanity_led", X(210), Y(818), X(246), Y(881), 53.5, 55))
D.append(C("D_e_basin", "basin_black_vessel", X(229), Y(850), 15, 85, 97))
D.append(B("D_e_flush", "black_metal", X(306), Y(954) - 1.4, X(318), Y(954), 92, 106, kind="panel"))
cove("D_e_cove", X(210), Y(804), X(346), Y(954), H)

# ======================================================================== BATH (north, 70 % dark chevron, Carrara details)
D.append(B("D_ba_mirror", "mirror_bronze", X(887) - 2.2, Y(282), X(887), Y(342), 108, 190, kind="panel"))
D.append(led("D_ba_bar", X(887) - 2.4, Y(276), X(887), Y(278), 108, 190))
D.append(led("D_ba_bar2", X(887) - 2.4, Y(346), X(887), Y(348), 108, 190))
D.append(led("D_ba_vanity_led", X(848), Y(272), X(886), Y(352), 53.5, 55))
D.append(B("D_ba_flush", "black_metal", X(793), Y(212), X(805), Y(212) + 1.4, 92, 106, kind="panel"))
branches("D_ba_vase", X(870), Y(340), 85, h=18, r=5, reach=0.3, w=1.6)
cove("D_ba_cove", X(765), Y(212), X(887), Y(383), H)

# ======================================================================== SAUNA + SPA (dark basalt, walnut, warm light)
D.append(B("D_sauna_glass_s", "glass_bronze", X(950), Y(384), X(1012), Y(385.5), 0, 215, kind="panel"))
D.append(B("D_sauna_glass_e", "glass_bronze", X(1012), Y(327), X(1013.5), Y(385), 0, 215, kind="panel"))
D.append(B("D_sauna_fascia", "walnut_panel", X(895), Y(390), X(1017), Y(390) + 2.4, 215, H, kind="panel"))
D.append(B("D_sauna_head", "walnut_panel", X(950), Y(382), X(1017), Y(390), 215, H, kind="panel"))
D.append(B("D_sauna_east_clad", "walnut_panel", X(1017), Y(287), X(1017) + 2.4, Y(327), 0, H, kind="panel"))
D.append(B("D_sauna_front", "walnut_panel", X(895), Y(390), X(950), Y(390) + 2.4, 0, 215, kind="panel"))
D.append(B("D_sauna_stove", "sauna_stove", X(985), Y(214), X(1008), Y(240), 0, 80))
D.append(led("D_sauna_led", X(947), Y(214), X(948.5), Y(380), 40, 42))
D.append(B("D_spa_glass", "glass", X(1097) - 0.6, Y(212), X(1097) + 0.6, Y(287), 0, 205, kind="panel"))
D.append(C("D_spa_rain", "black_metal", X(1057), Y(248), 16, H - 2, H))
D.append(B("D_spa_niche", "niche_lit", X(1017) + 0.5, Y(225), X(1017) + 3.2, Y(275), 100, 128, kind="panel"))
D.append(C("D_spa_ring_led", "led_line", X(1214), Y(288), 92, H - 3, H - 2, kind="light", emissive=True))
D.append(C("D_spa_ring_ceil", "walnut_slats", X(1214), Y(288), 90, H - 2, H))
D.append(B("D_spa_moss", "moss_wall", X(1102), Y(212), X(1245), Y(212) + 3, 75, 245, kind="panel"))
D.append(led("D_spa_moss_led", X(1102), Y(212), X(1245), Y(212) + 3.5, 245, 246.5))
art("D_art_spa0", "art_spa_pair", Y(477), "y", -1, X(960), X(1040), 115, 205)
art("D_art_spa1", "art_spa_pair", Y(477), "y", -1, X(1060), X(1140), 115, 205)

# ======================================================================== GARAGE (walnut slats, dark stone, LED lines)
D.append(B("D_g_slats", "walnut_slats_v", X(165), Y(477) - 2.8, X(612), Y(477), 0, H, kind="panel"))
D.append(led("D_g_slats_led", X(165), Y(477) - 6, X(612), Y(477) - 4.5, H - 2, H - 0.5))
for i, y in enumerate((260, 340, 420)):
    D.append(led(f"D_g_line{i}", X(175), Y(y) - 1.5, X(605), Y(y) + 1.5, H - 1.5, H))
D.append(B("D_g_wallbox", "black_metal", X(616) - 3, Y(350), X(616), Y(372), 110, 145, kind="panel"))

DESIGN = D

# ======================================================================== CAR: Mercedes-AMG G 63, matte black, nose EAST as drawn
CXR, CXF = X(386) - 243.5, X(386) + 243.5          # rear (west) / front (east), 487 cm
CY0, CY1 = Y(340) - 98, Y(340) + 98                # 196 cm wide


def prof(pts):
    return [[round(CXR + u, 1), round(z, 1)] for u, z in pts]


CAR = [
    dict(id="T_F_car", kind="car", shape="prism", axis="y", y0=CY0, y1=CY1, room="T_R_garage", group=None,
         poly=prof([(2, 28), (0, 48), (0, 152), (8, 190), (300, 196), (338, 190), (368, 128), (470, 120), (485, 108),
                    (487, 62), (485, 28)]), note="matte black Mercedes-AMG G 63, nose-in (east) as drawn"),
    dict(id="T_F_car_glass", kind="car_glass", shape="prism", axis="y", y0=CY0 + 8, y1=CY1 - 8, room="T_R_garage", group=None,
         poly=prof([(22, 132), (22, 182), (300, 187), (334, 182), (358, 132)])),
]
for i, u in enumerate((82, 372)):
    for s, y, o in (("l", CY0, -1), ("r", CY1, +1)):
        D.append(DSK(f"D_car_tyre{i}{s}", "car_tyre", CXR + u, y, 40, 40, 26, "y"))
        D.append(DSK(f"D_car_wheel{i}{s}", "car_wheel", CXR + u, y + o * 13.6, 40, 28, 1.2, "y"))
D.append(DSK("D_car_spare", "car_tyre", CXR - 8, (CY0 + CY1) / 2, 112, 38, 16, "x"))

# ALTERNATIVE CAR (opts.car_alt, used by the 3D floor plans): black Mercedes-Benz S-Class saloon (W223), 518 x 192 cm,
# same drawn centre, nose EAST as drawn
SXR = X(386) - 259
SY0, SY1 = Y(340) - 96, Y(340) + 96


def sprof(pts):
    return [[round(SXR + u, 1), round(z, 1)] for u, z in pts]


CAR += [
    dict(id="T_F_carS", kind="car", alt=True, shape="prism", axis="y", y0=SY0, y1=SY1, room="T_R_garage", group=None,
         poly=sprof([(5, 25), (0, 60), (2, 95), (10, 105), (100, 110), (200, 148), (320, 150), (405, 112), (505, 100),
                     (518, 75), (516, 30)]), note="black Mercedes-Benz S-Class saloon, nose-in (east) as drawn"),
    dict(id="T_F_carS_glass", kind="car_glass", alt=True, shape="prism", axis="y", y0=SY0 + 10, y1=SY1 - 10, room="T_R_garage",
         group=None, poly=sprof([(110, 112), (200, 144), (320, 146), (398, 113)])),
]
for i, u in enumerate((98, 409)):
    for s_, y, o in (("l", SY0, -1), ("r", SY1, +1)):
        # tyres tucked under the body (outer face 4 cm inside the body line): from straight above no wheel may stick out
        D.append(DSK(f"D_carS_tyre{i}{s_}", "car_tyre", SXR + u, y - o * 16, 36, 36, 24, "y"))
        D.append(DSK(f"D_carS_wheel{i}{s_}", "car_wheel", SXR + u, y - o * 4.6, 36, 26, 1.2, "y"))

# ======================================================================== SITE (golden-hour garden at garden level)
G = -15
SITE = [
    dict(id="EXT_lawn", mat="lawn", rect=[-900, -900, 3000, 3000], z=[G - 1, G]),
    dict(id="EXT_terrace_s", mat="terrace_stone", rect=[X(180), Y(985), X(1460), Y(1110)], z=[G, -2]),
    dict(id="EXT_terrace_e", mat="terrace_stone", rect=[X(1410), Y(460), X(1530), Y(1110)], z=[G, -2]),
    dict(id="EXT_drive", mat="terrace_stone", rect=[X(20), Y(212), X(131), Y(477)], z=[G, -2]),
    dict(id="EXT_hedge_s", mat="hedge", rect=[-300, 1950, 2900, 2010], z=[G, 120]),
    dict(id="EXT_hedge_e", mat="hedge", rect=[2450, -300, 2510, 2010], z=[G, 120]),
]
for i, (x, y) in enumerate([(900, 1500), (1450, 1700), (2000, 1450), (2200, 900), (2150, 350), (300, 1600), (1700, 1150)]):
    SITE.append(dict(id=f"EXT_tree_trunk{i}", mat="olive_trunk", cyl=[x, y, 9], z=[G, 180]))
    SITE.append(dict(id=f"EXT_tree_crown{i}", mat="olive_foliage", sphere=[x, y, 270, 115]))
