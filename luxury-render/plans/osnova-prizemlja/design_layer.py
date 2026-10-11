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
# Design after the client's 4 references (refs/mood/mood_bed_*, mood_bath_*):
#   master suite  = "walnut facets"  (faceted walnut wall + ceiling canopy with LED seams, black slats, marble TV wall)
#   bedrooms 1, 2 = "cove & slats"   (dark oak panelling, white tray ceiling with LED cove, slat screens, ficus, sketches)
#   master bath   = "dark ring"      (rough slate, round mirror in an LED ring, two-tone floating vanity, smoked glass)
#   baths 1, 3    = "taupe & walnut" (taupe stone, walnut counter + black vessel basin, mirror cabinet, black pendants)
U = 310


def G(id, mat, p0, p1, normal, w=1.6, t=0.4, kind="light", emissive=True):
    """thin bar from p0 to p1 (3D) lying on a surface whose plan normal axis is `normal` - LED seams"""
    return dict(id=id, shape="seg", mat=mat, p0=list(p0), p1=list(p1), normal=normal, w=w, t=t, kind=kind, emissive=emissive)


def DSK(id, mat, cx, cy, cz, r, t, axis, kind="panel"):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind=kind)


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


def lamp(tag, x, y, z):                       # small black table lamp on a nightstand
    D.append(C(f"{tag}_base", "lamp_black", x, y, 5, z, z + 32, kind="light"))
    D.append(C(f"{tag}_shade", "lamp_black", x, y, 10, z + 32, z + 46, kind="light"))
    D.append(C(f"{tag}_glow", "led_line", x, y, 8.5, z + 31, z + 32, kind="light", emissive=True))


def pendant(tag, x, y, z_bottom, z_top):      # slim black cylinder pendant on a cable
    D.append(C(f"{tag}", "pendant_black_cyl", x, y, 4, z_bottom, z_bottom + 30, kind="light"))
    D.append(C(f"{tag}_glow", "led_line", x, y, 3.2, z_bottom - 0.6, z_bottom, kind="light", emissive=True))
    D.append(cable(f"{tag}_c", x, y, z_bottom + 30, z_top))


def tray_ceiling(tag, x0, y0, x1, y1, band=35, drop=18):
    """white plaster tray: a soffit band around the room, continuous LED cove along its inner edge"""
    z = 560 - drop
    for i, r in enumerate([(x0, y0, x1, y0 + band), (x0, y1 - band, x1, y1), (x0, y0 + band, x0 + band, y1 - band), (x1 - band, y0 + band, x1, y1 - band)]):
        D.append(B(f"D_{tag}_soffit{i}", "plaster_cove_white", *r, z, 560, kind="panel"))
    a0, b0, a1, b1 = x0 + band, y0 + band, x1 - band, y1 - band
    for i, r in enumerate([(a0, b0, a1, b0 + 1), (a0, b1 - 1, a1, b1), (a0, b0, a0 + 1, b1), (a1 - 1, b0, a1, b1)]):
        D.append(led(f"D_{tag}_cove{i}", *r, z + 1, z + 4))


def ficus(tag, x, y):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, 20, U, U + 48))
    D.append(C(f"{tag}_trunk", "ficus_trunk", x, y, 4, U + 48, U + 150))
    D.append(S(f"{tag}_crown", "ficus_tree", x, y, U + 180, 34))


# ---------------- MASTER SUITE (bed3: x 659-1205, y 26-325; bed x 930-1098, headboard on the north wall)
PX0, PX1, PY = 870, 1158, 29.2                   # faceted walnut panel on the north wall
D.append(B("D_bed3_facet_wall", "walnut_facets", PX0, 26.2, PX1, PY, U, 551, kind="panel"))
D.append(B("D_bed3_facet_canopy", "walnut_facets", PX0, 26.2, PX1, 175, 551, 560, kind="panel"))
for i, ((x0, z0), (x1, z1)) in enumerate([((870, 470), (990, 551)), ((990, 551), (1035, 430)), ((1035, 430), (1100, 551)),
                                          ((1158, 455), (1080, 505)), ((1080, 505), (1035, 430)), ((930, 430), (990, 551))]):
    D.append(G(f"D_bed3_seam_w{i}", "led_line", (x0, PY + 0.3, z0), (x1, PY + 0.3, z1), "y"))
for i, ((x0, y0), (x1, y1)) in enumerate([((990, 29), (1060, 110)), ((1060, 110), (1100, 29)), ((1060, 110), (1010, 175)),
                                          ((990, 29), (940, 175)), ((1158, 90), (1060, 110))]):
    D.append(G(f"D_bed3_seam_c{i}", "led_line", (x0, y0, 550.7), (x1, y1, 550.7), "z"))
D.append(led("D_bed3_canopy_edge_s", PX0, 174, PX1, 175, 550, 551))
for x in (PX0 - 1.5, PX1):
    D.append(led(f"D_bed3_panel_edge{int(x)}", x, 26.2, x + 1.5, PY + 0.4, U, 551))
for side, xs in (("l", 845), ("r", 1161)):                 # black slats either side of the walnut
    for k in range(4):
        D.append(B(f"D_bed3_slat_{side}{k}", "black_slats", xs + k * 6, 26.2, xs + k * 6 + 4, 36, U, 560, kind="panel"))
lamp("D_bed3_lamp0", 906, 51, U + 50)
lamp("D_bed3_lamp1", 1122, 51, U + 50)
D.append(B("D_bed3_rug", "rug_sand", 895, 140, 1135, 300, U, U + 1.2))
# TV wall: white marble framed by two vertical LED lines
D.append(B("D_bed3_marble", "marble_white_panel", 890, 322.4, 1134, 323.9, U, 560, kind="panel"))
for x in (888.5, 1134):
    D.append(led(f"D_bed3_marble_led{int(x)}", x, 321.4, x + 1.5, 323.9, U, 556))
D.append(led("D_bed3_cove_s", 612, 320.5, 1203, 323.9, 557.5, 559.5))     # wall-washer line along the TV wall
D.append(B("D_bed3_curtain0", "sheer_linen", 1190, 30, 1203, 100, U, 540))
D.append(C("D_bed3_vase", "vase_dark", 1194, 106, 9, U, U + 70))           # pampas between the curtain stack and the glass
for i, (dx, dy, dz) in enumerate([(-4, -3, 120), (5, 2, 140), (-2, 5, 158)]):
    D.append(S(f"D_bed3_pampas{i}", "pampas", 1194 + dx, 106 + dy, U + dz, 13))

# ---------------- BEDROOM 1 (x 26-354, y 308-803 main; bed headboard on the west wall)
tray_ceiling("bed1", 26.2, 307.9, 353.7, 803.0)
for y in (452, 731):                                                         # LED lines framing the bed wall
    D.append(led(f"D_bed1_wall_led{y}", 26.2, y, 28.8, y + 1.5, U, 542))
pendant("D_bed1_pend0", 46, 483, U + 102, 542)
pendant("D_bed1_pend1", 46, 701, U + 102, 542)
D.append(B("D_bed1_rug", "rug_charcoal", 105, 470, 300, 720, U, U + 1.2))
for i, (y0, y1) in enumerate([(470, 505), (675, 710)]):                     # slat screens flanking the TV
    D.append(B(f"D_bed1_screen{i}", "slat_screen_black", 350, y0, 353.7, y1, U, 542, kind="panel"))
for i, c in enumerate([(30, 795, 62, 803), (318, 795, 350, 803)]):
    D.append(B(f"D_bed1_curtain{i}", "sheer_linen", *c, U, 540))
ficus("D_bed1_ficus", 100, 758)

# ---------------- BEDROOM 2 (x 610-941, y 541-954 main; bed headboard on the east wall)
tray_ceiling("bed2", 610.5, 541.0, 940.6, 953.7)
for y in (586, 860):
    D.append(led(f"D_bed2_wall_led{y}", 938.0, y, 940.6, y + 1.5, U, 542))
pendant("D_bed2_pend0", 918, 616, U + 102, 542)
pendant("D_bed2_pend1", 918, 832, U + 102, 542)
D.append(B("D_bed2_rug", "rug_charcoal", 690, 600, 905, 850, U, U + 1.2))
D.append(B("D_bed2_bench", "bench_tufted_cream", 692, 662, 736, 787, U, U + 45))
for i, y in enumerate((645, 700, 755)):                                     # three line-art sketches facing the bed
    D.append(B(f"D_bed2_art{i}", "art_sketch", 610.5, y, 613, y + 45, U + 135, U + 195))
for i, c in enumerate([(745, 944, 777, 952)]):
    D.append(B(f"D_bed2_curtain{i}", "sheer_linen", *c, U, 540))
ficus("D_bed2_ficus", 650, 912)

# ---------------- MASTER BATH (bath2: x 380-646, y 26-200; shower west, WC + window north, vanity NE)
D.append(B("D_bath2_shower_glass", "smoked_glass", 458.0, 26.2, 459.2, 150, U, U + 205, kind="panel"))
D.append(C("D_bath2_rainhead", "black_metal", 419, 105, 15, 548, 550, kind="light"))
D.append(B("D_bath2_niche", "niche_lit", 379.9, 50, 382.6, 175, U + 100, U + 130, kind="panel"))
D.append(led("D_bath2_niche_led", 379.9, 50, 382.9, 175, U + 128.5, U + 130))
D.append(DSK("D_bath2_mirror", "mirror_round", 593.4, 27.4, 470, 36, 1.6, "y"))
D.append(T("D_bath2_ring", "ring_led", 593.4, 30.5, 470, 41, 1.3))
D[-1]["axis"] = "y"
D.append(B("D_bath2_drawer", "vanity_walnut_drawer", 548, 28, 640, 74, U + 25, U + 48))
D.append(led("D_bath2_vanity_under", 548, 30, 640, 72, U + 23.5, U + 24.5))
D.append(B("D_bath2_flush", "black_metal", 489, 26.2, 514, 28.4, U + 92, U + 108, kind="panel"))
for y in (70, 150):
    D.append(led(f"D_bath2_slot{y}", 390, y - 1.2, 640, y + 1.2, 558.5, 559.6))
D.append(C("D_bath2_diffuser", "ceramic_dark", 632, 44, 3.5, U + 85, U + 101))

# ---------------- BATHS 1 + 3 ("taupe & walnut")
def taupe_bath(tag, cx0, cy0, cx1, cy1, basin_x, wall_y, pend_xy, vase_xy):
    """counter (furniture) spans cx0..cx1 / cy0..cy1 at 390-400; wall_y = wall behind it"""
    D.append(B(f"D_{tag}_shelf", "walnut_counter", cx0, cy0 + 2, cx1, cy1 - 4, U + 52, U + 55))
    D.append(B(f"D_{tag}_drawers", "cabinet_taupe", cx0, cy0 + 4, cx1, cy1 - 4, U + 8, U + 34))
    D.append(led(f"D_{tag}_under", cx0 + 2, cy0 + 6, cx1 - 2, cy1 - 6, U + 6.5, U + 7.5))
    D.append(B(f"D_{tag}_basin", "basin_black_vessel", basin_x - 24, cy0 + 8, basin_x + 24, cy1 - 10, U + 90, U + 104))
    D.append(B(f"D_{tag}_mirror", "mirror_cabinet", cx0 + 8, wall_y, cx1 - 6, wall_y + 13, U + 118, U + 222, kind="panel"))
    D.append(led(f"D_{tag}_mirror_led", cx0 + 8, wall_y + 1, cx1 - 6, wall_y + 12, U + 116.5, U + 117.5))
    D.append(led(f"D_{tag}_wash", cx0, wall_y, cx1, wall_y + 2.5, 556.5, 558.5))
    for i, (x, y, zb) in enumerate(pend_xy):
        pendant(f"D_{tag}_pend{i}", x, y, U + zb, 560)
    D.append(C(f"D_{tag}_vase", "ceramic_dark", *vase_xy, 6, U + 90, U + 116))
    for i, (dx, dy, dz) in enumerate([(-5, 0, 124), (5, 3, 128), (0, -3, 136)]):     # airy cloud of dried gypsophila
        D.append(S(f"D_{tag}_gyps{i}", "gypsophila", vase_xy[0] + dx, vase_xy[1] + dy, U + dz, 8))


taupe_bath("bath1", 39.3, 30.1, 203.1, 85.2, 152, 26.2, [(62, 66, 128), (76, 74, 112)], (186, 62))
D.append(B("D_bath1_shower_glass", "glass", 26.2, 207.5, 150, 208.7, U, U + 205, kind="panel"))
D.append(C("D_bath1_rainhead", "black_metal", 90, 250, 15, 548, 550, kind="light"))
D.append(B("D_bath1_niche", "niche_lit", 26.2, 220, 28.9, 285, U + 95, U + 125, kind="panel"))
D.append(led("D_bath1_niche_led", 26.2, 220, 29.2, 285, U + 123.5, U + 125))

taupe_bath("bath3", 750.6, 357.6, 835.8, 403.5, 793, 351.1, [(846, 375, 128), (853, 389, 112)], (822, 372))
D.append(B("D_bath3_shower_glass", "glass", 861.0, 351.1, 862.2, 405, U, U + 205, kind="panel"))
D.append(C("D_bath3_rainhead", "black_metal", 902, 398, 15, 548, 550, kind="light"))
D.append(B("D_bath3_niche", "niche_lit", 937.9, 365, 940.6, 430, U + 95, U + 125, kind="panel"))
D.append(led("D_bath3_niche_led", 937.6, 365, 940.6, 430, U + 123.5, U + 125))
D.append(B("D_bath3_ladder", "towel_ladder", 790, 516, 840, 521.4, U + 60, U + 180, kind="panel"))

# ---------------- UPPER LANDING (kept in the ground-hall finishes it is seen with from below)
D.append(B("D_uh_art", "art_relief", 597.0, 395, 600.0, 560, U + 85, U + 205))
D.append(led("D_uh_led", 538, 225, 542, 590, 558, 559.5))
