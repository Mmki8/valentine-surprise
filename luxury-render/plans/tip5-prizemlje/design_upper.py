"""First floor (OSNOVA SPRATA) of house type 5: every fixed design decision as 3D geometry, appended to DESIGN.

Brief: the same language as the ground floor (dark, woody, warm LED, golden hour, bright details) but each room a new
variation, never a copy: master in espresso walnut boiserie + cognac leather, bedroom 1 olive + walnut slats, bedroom 2
charcoal + ribbed smoked oak with rust accents, baths 70 % dark (verde marble, emperador + calacatta, charcoal stone +
travertine). The gallery office overlooks the living through the UOG.2 glass.
Coordinates: plan cm (same frame as the ground floor), px on the ground sheet (first-floor sheet px + (1, 28)).
"""
import design_layer as dl
from design_layer import B, C, S, X, Y, led, art, branches, pendant, cable, cove, seg

D = dl.D
U, VH, XV = dl.FL, dl.VH, dl.XV


def tree_z(tag, x, y, z, pot_r=22, pot_h=55, trunk=110, crown=55, foliage="fig_foliage"):
    D.append(C(f"{tag}_pot", "stone_pot", x, y, pot_r, z, z + pot_h))
    D.append(C(f"{tag}_trunk", "olive_trunk", x, y, 4, z + pot_h, z + pot_h + trunk))
    D.append(S(f"{tag}_crown", foliage, x, y, z + pot_h + trunk + crown * 0.7, crown))


def curtain_x(tag, xface, sign, y0, y1):          # gathered sheer at both jambs of an opening in a wall along y
    lo, hi = sorted((xface + sign * 2, xface + sign * 10))
    D.append(B(f"{tag}0", "sheer_linen", lo, y0, hi, y0 + 16, U, VH - 12))
    D.append(B(f"{tag}1", "sheer_linen", lo, y1 - 16, hi, y1, U, VH - 12))


def curtain_y(tag, yface, sign, x0, x1):
    lo, hi = sorted((yface + sign * 2, yface + sign * 10))
    D.append(B(f"{tag}0", "sheer_linen", x0, lo, x0 + 16, hi, U, VH - 12))
    D.append(B(f"{tag}1", "sheer_linen", x1 - 16, lo, x1, hi, U, VH - 12))


def globe(tag, x, y, z):                          # opal glass globe on a slim brass rod
    D.append(S(f"{tag}_shade", "pendant_opal_globe", x, y, z + 13, 13, kind="light"))
    cable(f"{tag}_c", x, y, z + 26, VH)


# ======================================================================== GALLERY OFFICE + LANDING (overlooks the living)
D.append(B("D_gal_rug", "rug_dark_wool", X(680), Y(705), X(895), Y(925), U, U + 1.2))
top = pendant("D_gal_pend", "pendant_alabaster", X(762), Y(846), U + 172, 14, shape="cyl", h=28)
cable("D_gal_pend_c", X(762), Y(846), top, VH)
branches("D_gal_vase", X(780), Y(835), U + 76, h=22, r=6, reach=0.35, w=1.8)
D.append(B("D_gal_books", "books_neutral", X(740), Y(845), X(740) + 24, Y(845) + 17, U + 76, U + 83))
tree_z("D_gal_fig", X(648), Y(925), U, pot_r=24, pot_h=55, trunk=125, crown=58)
cove("D_gal_cove", X(623), Y(497), X(XV), Y(953), VH)
# landing: walnut console + a painting on the corridor wall facing the stair arrival
D.append(B("D_land_console", "walnut_console", X(766), Y(497), X(830), Y(497) + 35, U + 18, U + 80))
art("D_art_land", "art_painting_portrait", Y(497), "y", +1, X(775), X(822), U + 120, U + 205)

# ======================================================================== MASTER (espresso walnut boiserie, cognac, cream + brass details)
MW = X(603)                                        # bed wall (east)
D.append(B("D_m_boiserie", "walnut_boiserie_brass", MW - 3, Y(645), MW, Y(951), U, VH - 6, kind="panel"))
art("D_m_art", "art_cream_texture", MW - 3, "x", -1, Y(737), Y(852), U + 150, U + 232)
globe("D_m_globe0", MW - 20, Y(711), U + 112)
globe("D_m_globe1", MW - 20, Y(878), U + 112)
D.append(B("D_m_rug", "rug_ivory", X(425), Y(705), X(560), Y(886), U, U + 1.2))
D.append(B("D_m_tvwall", "walnut_panel", X(346), Y(700), X(346) + 2.4, Y(888), U, VH - 6, kind="panel"))
curtain_y("D_m_curt", Y(953), -1, X(361), X(516))
tree_z("D_m_olive", X(586), Y(930), U, pot_r=17, pot_h=48, trunk=95, crown=42, foliage="olive_foliage")
cove("D_m_cove", X(346), Y(645), MW - 3, Y(953), VH)
cove("D_m_cove_n", X(209), Y(497), X(603), Y(645), VH)
D.append(led("D_m_wic_glow", X(250), Y(539) - 1.5, X(459), Y(539), U + 2, U + 3.5))

# ======================================================================== MASTER ENSUITE (charcoal stone, calacatta shower wall, travertine)
D.append(B("D_mb_shwall", "marble_calacatta_gold", X(209), Y(953) - 2.4, X(336), Y(953), U, VH - 6, kind="panel"))
D.append(B("D_mb_glass", "glass", X(209), Y(884) - 0.6, X(300), Y(884) + 0.6, U, U + 205, kind="panel"))
D.append(B("D_mb_glass_e", "glass", X(340) - 0.6, Y(894), X(340) + 0.6, Y(953), U, VH - 6, kind="panel"))
D.append(C("D_mb_rain", "black_metal", X(272), Y(920), 13, VH - 2, VH))
for i, (y0, y1) in enumerate([(652, 702), (712, 762)]):
    D.append(B(f"D_mb_mirror{i}", "mirror_backlit", X(209), Y(y0), X(209) + 1.8, Y(y1), U + 110, U + 192, kind="panel"))
D.append(led("D_mb_van_led", X(209), Y(645), X(247), Y(788), U + 53.5, U + 55))
D.append(B("D_mb_flush", "black_metal", X(209), Y(840), X(209) + 1.4, Y(853), U + 92, U + 106, kind="panel"))
cove("D_mb_cove", X(209), Y(645), X(336), Y(953), VH)

# ======================================================================== BEDROOM 1 (olive plaster, walnut slats, olive velvet, cream details)
D.append(B("D_b1_slats", "walnut_slats_v", X(170), Y(213), X(462), Y(213) + 2.8, U, VH - 6, kind="panel"))
D.append(led("D_b1_slat_wash", X(170), Y(213) + 2.8, X(462), Y(213) + 4.3, VH - 9, VH - 7.5))
globe("D_b1_globe0", X(245), Y(232), U + 105)
globe("D_b1_globe1", X(411), Y(232), U + 105)
D.append(B("D_b1_rug", "rug_ivory", X(240), Y(300), X(416), Y(425), U, U + 1.2))
D.append(B("D_b1_tvwall", "walnut_panel", X(250), Y(478) - 2.4, X(397), Y(478), U, VH - 6, kind="panel"))
curtain_x("D_b1_curt", X(161), +1, Y(231), Y(456))
tree_z("D_b1_fig", X(184), Y(222), U, pot_r=15, pot_h=45, trunk=100, crown=40)
cove("D_b1_cove", X(161), Y(213), X(516), Y(478), VH)

# ======================================================================== BATH 1 (70 % dark verde marble, travertine + brass details)
D.append(B("D_ba1_glass", "glass", X(522), Y(273) - 0.6, X(600), Y(273) + 0.6, U, U + 205, kind="panel"))
D.append(C("D_ba1_rain", "brass_brushed", X(570), Y(243), 12, VH - 2, VH))
D.append(B("D_ba1_mirror", "mirror_round_backlit", X(657), Y(378) - 1.8, X(707), Y(378), U + 108, U + 186, kind="panel"))
D.append(led("D_ba1_van_led", X(643), Y(340), X(721), Y(378), U + 53.5, U + 55))
D.append(B("D_ba1_flush", "brass_brushed", X(674), Y(213), X(688), Y(213) + 1.4, U + 92, U + 106, kind="panel"))
D.append(B("D_ba1_niche", "niche_lit", X(521), Y(225), X(521) + 2.7, Y(262), U + 100, U + 128, kind="panel"))
cove("D_ba1_cove", X(521), Y(213), X(723), Y(378), VH)

# ======================================================================== BATH 2 (70 % dark emperador marble, calacatta shower wall)
D.append(B("D_ba2_shwall", "marble_calacatta_gold", X(836), Y(213), X(933), Y(213) + 2.4, U, VH - 6, kind="panel"))
D.append(B("D_ba2_glass", "glass", X(855), Y(273) - 0.6, X(933), Y(273) + 0.6, U, U + 205, kind="panel"))
D.append(C("D_ba2_rain", "black_metal", X(885), Y(243), 12, VH - 2, VH))
D.append(B("D_ba2_mirror", "mirror_backlit", X(745), Y(378) - 1.8, X(800), Y(378), U + 108, U + 186, kind="panel"))
D.append(led("D_ba2_van_led", X(732), Y(339), X(813), Y(378), U + 53.5, U + 55))
D.append(B("D_ba2_flush", "black_metal", X(778), Y(213), X(792), Y(213) + 1.4, U + 92, U + 106, kind="panel"))
cove("D_ba2_cove", X(732), Y(213), X(933), Y(378), VH)

# ======================================================================== BEDROOM 2 (charcoal plaster, ribbed smoked oak, sand linen, rust)
D.append(B("D_b2_ribbed", "oak_ribbed_smoked", X(995), Y(213), X(1290), Y(213) + 2.8, U, VH - 6, kind="panel"))
for i, x in enumerate((1062, 1229)):
    t = pendant(f"D_b2_pend{i}", "pendant_alabaster", X(x), Y(232), U + 108, 8, shape="cyl", h=24)
    cable(f"D_b2_pend{i}_c", X(x), Y(232), t, VH)
D.append(B("D_b2_rug", "rug_ivory", X(1055), Y(300), X(1236), Y(425), U, U + 1.2))
D.append(B("D_b2_tvwall", "oak_ribbed_smoked", X(1070), Y(478) - 2.4, X(1217), Y(478), U, VH - 6, kind="panel"))
curtain_x("D_b2_curt", X(1297), -1, Y(278), Y(463))
tree_z("D_b2_fig", X(1281), Y(470), U, pot_r=14, pot_h=45, trunk=95, crown=38)
cove("D_b2_cove", X(941), Y(213), X(1297), Y(478), VH)

# ======================================================================== JULIET GLASS at the full-height first-floor windows
D.append(B("D_jul_og4", "glass", X(131) - 3, Y(231), X(131) - 1.5, Y(456), U, U + 100, kind="panel"))
D.append(B("D_jul_og3", "glass", X(1327) + 1.5, Y(278), X(1327) + 3, Y(463), U, U + 100, kind="panel"))
D.append(B("D_jul_og1", "glass", X(361), Y(983) + 1.5, X(516), Y(983) + 3, U, U + 100, kind="panel"))
D.append(B("D_jul_og2", "glass", X(676), Y(983) + 1.5, X(745), Y(983) + 3, U, U + 100, kind="panel"))
