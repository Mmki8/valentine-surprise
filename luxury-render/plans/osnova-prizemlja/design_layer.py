"""Design layer for the ground floor: every fixed design decision as 3D geometry.

Why: when decor, light fittings and finishes exist only as prompt text, the
image model re-invents them for every camera (different pendants, shelves,
cushions, lighting). Modelled here, they sit at ONE position with ONE material
key, so every view sees the same object. design-system.json holds the single
description of each material key.

All coordinates in plan cm (x east, y south, z up). Written into plan.json
under "design" by digitize.py.
"""


def B(id, mat, x0, y0, x1, y1, z0, z1, kind="decor", emissive=False):
    return dict(id=id, shape="box", mat=mat, rect=[x0, y0, x1, y1], z=[z0, z1], kind=kind, emissive=emissive)


def C(id, mat, cx, cy, r, z0, z1, kind="decor", emissive=False):
    return dict(id=id, shape="cyl", mat=mat, center=[cx, cy], r=r, z=[z0, z1], kind=kind, emissive=emissive)


def S(id, mat, cx, cy, cz, r, kind="decor"):
    return dict(id=id, shape="sphere", mat=mat, center=[cx, cy, cz], r=r, kind=kind)


def T(id, mat, cx, cy, cz, R, tube, kind="light"):
    return dict(id=id, shape="torus", mat=mat, center=[cx, cy, cz], R=R, tube=tube, kind=kind)


def cable(id, x, y, z0, z1):
    return C(id, "cable_black", x, y, 0.6, z0, z1, kind="light")


D = []
# ------------------------------------------------------------------ LIVING (void x964-1457, y352-964)
# bronze feature wall: 4 x 4 large panels with fine reveals, full 5.6 m height
D.append(B("D_liv_bronze_wall", "bronze_panels", 964, 352, 1433, 355, 0, 560, kind="panel"))
for x in (1081, 1198, 1316):
    D.append(B(f"D_liv_bronze_rv{x}", "reveal_dark", x - 0.8, 355, x + 0.8, 355.6, 0, 560, kind="panel"))
for z in (140, 280, 420):
    D.append(B(f"D_liv_bronze_rh{z}", "reveal_dark", 964, 355, 1433, 355.6, z - 0.8, z + 0.8, kind="panel"))
# two interlocking crystal rings over the coffee tables
D.append(T("D_liv_ring_1", "crystal_ring", 1200, 590, 420, 75, 6))
D.append(T("D_liv_ring_2", "crystal_ring", 1260, 555, 385, 60, 5))
for i, (x, y, z) in enumerate([(1125, 590, 420), (1275, 590, 420), (1200, 515, 420), (1200, 665, 420),
                               (1200, 555, 385), (1320, 555, 385), (1260, 495, 385)]):
    D.append(cable(f"D_liv_ring_cable{i}", x, y, z, 560))
# rug under the seating group
D.append(B("D_liv_rug", "rug_sand", 1110, 500, 1395, 835, 0, 1.2))
# olive tree in the free NE corner
D.append(C("D_liv_olive_pot", "stone_pot", 1405, 395, 24, 0, 55))
D.append(C("D_liv_olive_trunk", "olive_trunk", 1405, 395, 4, 55, 140))
D.append(S("D_liv_olive_crown", "olive_foliage", 1405, 395, 175, 50))
# freestanding walnut media wall in front of the east glass (TV mounted on it, solid back)
D.append(B("D_liv_media_wall", "walnut_panel", 1440, 488, 1452, 690, 0, 270, kind="panel"))
# sheer curtains stacked at the glass ends
D.append(B("D_liv_curtain_e", "sheer_linen", 1448, 930, 1462, 975, 0, 548))
D.append(B("D_liv_curtain_s", "sheer_linen", 975, 962, 1015, 976, 0, 548))
# sofa cushions (fixed colours and places)
for i, (x, m) in enumerate([(1115, "cushion_navy"), (1170, "cushion_cognac"), (1265, "cushion_cognac"), (1320, "cushion_navy")]):
    D.append(B(f"D_liv_cushion{i}", m, x, 430, x + 45, 442, 42, 82))
D.append(B("D_liv_cushion4", "cushion_navy", 1097, 560, 1109, 605, 42, 82))
# coffee-table objects
D.append(B("D_liv_books", "books_neutral", 1170, 540, 1200, 562, 38, 44))
D.append(S("D_liv_coral", "coral_white", 1213, 553, 47, 8))
D.append(C("D_liv_bowl", "ceramic_dark", 1225, 630, 12, 32, 38))
# LED lines in the walnut void ceiling
for y in (470, 660, 850):
    D.append(B(f"D_liv_led{y}", "led_line", 985, y - 2, 1430, y + 2, 558, 559.5, kind="light", emissive=True))

# ------------------------------------------------------------------ KITCHEN (runs: north y352-412, west x626-686)
D.append(B("D_k_backsplash_n", "stone_backsplash", 663, 352, 893, 354, 92, 280, kind="panel"))
D.append(B("D_k_backsplash_w", "stone_backsplash", 626, 352, 628, 601, 92, 280, kind="panel"))
D.append(B("D_k_shelf", "walnut_shelf", 700, 354, 880, 380, 150, 155))
D.append(B("D_k_shelf_led", "led_line", 702, 360, 878, 376, 148.5, 149.5, kind="light", emissive=True))
D.append(B("D_k_counter_led", "led_line", 665, 354, 892, 358, 278, 279, kind="light", emissive=True))
# cabinet front divisions (handle-less, 60 cm modules, 3 drawers)
for x in range(723, 893, 60):
    D.append(B(f"D_k_n_split{x}", "groove_dark", x - 0.4, 412, x + 0.4, 412.6, 10, 88, kind="panel"))
for z in (35, 62):
    D.append(B(f"D_k_n_drawer{z}", "groove_dark", 663, 412, 893, 412.6, z - 0.4, z + 0.4, kind="panel"))
for y in (434, 494, 554):
    D.append(B(f"D_k_w_split{y}", "groove_dark", 686, y - 0.4, 686.6, y + 0.4, 10, 88, kind="panel"))
for z in (35, 62):
    D.append(B(f"D_k_w_drawer{z}", "groove_dark", 686, 374, 686.6, 601, z - 0.4, z + 0.4, kind="panel"))
D.append(B("D_k_fridge_split", "groove_dark", 922.6, 412, 923.4, 412.6, 10, 238, kind="panel"))
# linear pendants: island + dining
D.append(B("D_k_pendant_island", "pendant_bronze", 795, 543, 935, 549, 186, 191, kind="light"))
D.append(B("D_k_pendant_island_led", "led_line", 797, 544, 933, 548, 185.5, 186, kind="light", emissive=True))
D.append(cable("D_k_pendant_island_c1", 805, 546, 191, 280)); D.append(cable("D_k_pendant_island_c2", 925, 546, 191, 280))
D.append(B("D_d_pendant", "pendant_bronze", 788, 743, 940, 749, 166, 171, kind="light"))
D.append(B("D_d_pendant_led", "led_line", 790, 744, 938, 748, 165.5, 166, kind="light", emissive=True))
D.append(cable("D_d_pendant_c1", 798, 746, 171, 280)); D.append(cable("D_d_pendant_c2", 930, 746, 171, 280))
# kitchen ceiling LED lines
for y in (456, 680):
    D.append(B(f"D_k_led{y}", "led_line", 690, y - 2, 960, y + 2, 278, 279.5, kind="light", emissive=True))
# objects
D.append(C("D_k_lemons", "ceramic_dark", 830, 540, 14, 92, 100))
D.append(S("D_k_lemons_fruit", "lemons", 830, 540, 101, 9))
D.append(C("D_k_vase", "ceramic_light", 905, 528, 6, 92, 122))
D.append(S("D_k_vase_branches", "olive_foliage", 905, 528, 140, 18))
D.append(C("D_d_bowl", "ceramic_light", 862, 746, 18, 76, 84))          # low bowl: never blocks a view
D.append(S("D_d_bowl_fruit", "lemons", 862, 746, 85, 9))
D.append(B("D_k_board", "walnut_shelf", 760, 356, 800, 360, 92, 132))   # cutting board leaning on backsplash

# ------------------------------------------------------------------ HALL (x378-598, y211-950)
D.append(B("D_h_battens", "walnut_battens", 378, 211, 381, 950, 0, 560, kind="panel"))
D.append(B("D_h_art", "artwork_abstract", 595.5, 420, 598.5, 545, 105, 230))
D.append(T("D_h_pendant", "pendant_bronze", 430, 640, 420, 28, 2.5))
D.append(cable("D_h_pendant_c", 430, 612, 420, 560))
D.append(B("D_h_led", "led_line", 538, 230, 542, 930, 278, 279.5, kind="light", emissive=True))

# ------------------------------------------------------------------ SPA / SAUNA / WC
D.append(C("D_spa_orchid_pot", "ceramic_dark", 1185, 235, 8, 0, 20))
D.append(S("D_spa_orchid", "orchid_white", 1185, 235, 42, 15))
for i, (x, y, h) in enumerate([(1172, 252, 12), (1180, 258, 8), (1166, 246, 6)]):
    D.append(C(f"D_spa_candle{i}", "candle", x, y, 3.5, 0, h, kind="light"))
D.append(B("D_spa_towels", "towels_charcoal", 1150, 300, 1190, 322, 0, 30))
D.append(B("D_sauna_led_low", "led_line", 737, 30, 739, 195, 40, 41, kind="light", emissive=True))
D.append(B("D_sauna_led_high", "led_line", 704, 30, 706, 195, 86, 87, kind="light", emissive=True))
D.append(B("D_wc_mirror", "mirror_backlit", 653.5, 62, 656, 180, 110, 200, kind="panel"))
D.append(B("D_wc_mirror_led", "led_line", 656, 59, 656.8, 183, 107, 203, kind="light", emissive=True))  # glow BEHIND the mirror
D.append(C("D_wc_orchid_pot", "ceramic_dark", 645, 75, 5, 85, 97))
D.append(S("D_wc_orchid", "orchid_white", 645, 75, 112, 10))

# ------------------------------------------------------------------ GARAGE (x24-355, y205-817, floor -60)
for x in (110, 270):
    D.append(B(f"D_g_led_x{x}", "led_line", x - 2, 215, x + 2, 805, 278, 279.5, kind="light", emissive=True))
for y in (330, 520, 710):
    D.append(B(f"D_g_led_y{y}", "led_line", 30, y - 2, 350, y + 2, 278, 279.5, kind="light", emissive=True))
for i, (y, z) in enumerate([(229, -18), (258, -33), (288, -48)]):   # under each nosing
    D.append(B(f"D_g_step_led{i}", "led_line", 247, y - 1, 353, y, z - 1, z, kind="light", emissive=True))

# ------------------------------------------------------------------ EXTERIOR (hidden from QA passes)
for i, r in enumerate([(-800, 1000, 2400, 2200), (1480, -800, 2400, 1000), (-800, -800, 1480, -40), (-800, -40, -40, 1000)]):
    D.append(B(f"X_lawn{i}", "lawn", *r, -1.5, -0.5, kind="exterior"))   # around, never through, the house
D.append(B("X_hedge_s", "hedge", 900, 1230, 1700, 1290, 0, 110, kind="exterior"))
D.append(B("X_hedge_e", "hedge", 1640, 300, 1700, 1290, 0, 110, kind="exterior"))
for i, (x, y) in enumerate([(1150, 1450), (1500, 1500), (1900, 700), (1950, 1100)]):
    D.append(C(f"X_tree_trunk{i}", "olive_trunk", x, y, 8, 0, 180, kind="exterior"))
    D.append(S(f"X_tree_crown{i}", "olive_foliage", x, y, 260, 110, kind="exterior"))

DESIGN = D

# ------------------------------------------------------------------ UPPER FLOOR (FFL 310, ceiling 560)
U = 310
def _bedroom(tag, panel, pendants, rug, curtains):
    D.append(B(f"D_{tag}_headwall", "walnut_panel", *panel, U, 560, kind="panel"))
    for i, (x, y) in enumerate(pendants):
        D.append(S(f"D_{tag}_pend{i}", "pendant_glass", x, y, U + 125, 11, kind="light"))
        D.append(cable(f"D_{tag}_pend{i}_c", x, y, U + 136, 560))
    D.append(B(f"D_{tag}_rug", "rug_sand", *rug, U, U + 1.2))
    for i, c in enumerate(curtains):
        D.append(B(f"D_{tag}_curtain{i}", "sheer_linen", *c, U, 540))

_bedroom("bed1", (26.2, 470, 28.6, 717), [(46, 483), (46, 701)], (110, 470, 330, 720), [(30, 795, 62, 803), (318, 795, 350, 803)])
_bedroom("bed3", (880, 26.2, 1150, 28.6), [(906, 51), (1122, 51)], (900, 150, 1130, 300), [(1190, 98, 1203, 126)])
_bedroom("bed2", (938.2, 600, 940.6, 850), [(918, 616), (918, 832)], (700, 620, 900, 830), [(745, 944, 777, 952)])
for tag, (x0, x1), y, in [("bath1", (60, 180), 26.2), ("bath2", (555, 635), 26.2), ("bath3", (760, 830), 351)]:
    D.append(B(f"D_{tag}_mirror", "mirror_backlit", x0, y + 0.3, x1, y + 2.6, U + 110, U + 200, kind="panel"))
    D.append(B(f"D_{tag}_mirror_led", "led_line", x0 - 3, y, x1 + 3, y + 0.3, U + 107, U + 203, kind="light", emissive=True))
# upper showers: frameless glass screen + ceiling rain head (modelled so every view shows the same shower)
for tag, glass, head in [("bath3", (861, 351, 862.2, 445), (902, 398)),
                         ("bath2", (551.5, 26.2, 552.7, 180), (442, 100)),
                         ("bath1", (26.2, 207.5, 150, 208.7), (90, 245))]:
    D.append(B(f"D_{tag}_shower_glass", "glass", *glass, U, U + 205, kind="panel"))
    D.append(C(f"D_{tag}_rainhead", "black_metal", head[0], head[1], 15, U + 238, U + 240, kind="light"))
