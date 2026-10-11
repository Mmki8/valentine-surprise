"""Design layer for house type 3 (souterrain): every fixed design decision as 3D geometry.

Design brief (client): the bedrooms follow the approved "Master Suite" of house 1 - faceted walnut
wall with glowing LED seams folding onto the ceiling over the bed, black slats, sand channel-tufted
bed with charcoal bedding, black nightstands with table lamps, white marble feature wall framed by
LED lines, pampas by the glass. Bathrooms follow the client's references (dark slate + LED ring
mirror; taupe stone + walnut + black vessel basin). Golden hour through the south glazing.

Coordinates: drawing px are converted with the same scale as digitize.py; output in plan cm.
"""
K, OX, OY = 1.313, 184, 247.5


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


def DSK(id, mat, cx, cy, cz, r, t, axis):
    return dict(id=id, shape="disc", mat=mat, center=[cx, cy, cz], r=r, t=t, axis=axis, kind="panel")


def led(id, *r):
    return B(id, "led_line", *r, kind="light", emissive=True)


D = []
H = 270


def cable(id, x, y, z0, z1):
    D.append(C(id, "cable_black", x, y, 0.6, z0, z1, kind="light"))


def lamp(tag, x, y, z=50):
    D.append(C(f"{tag}_base", "lamp_black", x, y, 5, z, z + 32, kind="light"))
    D.append(C(f"{tag}_shade", "lamp_black", x, y, 10, z + 32, z + 46, kind="light"))
    D.append(C(f"{tag}_glow", "led_line", x, y, 8.5, z + 31, z + 32, kind="light", emissive=True))


def pendant(tag, x, y, zb, zt=H):
    D.append(C(tag, "pendant_black_cyl", x, y, 4, zb, zb + 30, kind="light"))
    D.append(C(f"{tag}_glow", "led_line", x, y, 3.2, zb - 0.6, zb, kind="light", emissive=True))
    cable(f"{tag}_c", x, y, zb + 30, zt)


def pampas(tag, x, y):
    """dried pampas: tall dark vase + slender plume stems fanning out (NOT spheres - spheres read as globe lamps)"""
    D.append(C(f"{tag}_vase", "vase_dark", x, y, 9, 0, 70))
    for i, (dx, dy, dz) in enumerate([(-16, -6, 150), (11, 5, 168), (-3, 12, 176), (16, -9, 142), (1, -2, 182)]):
        D.append(dict(id=f"{tag}_plume{i}", shape="seg", mat="pampas", p0=[x, y, 68], p1=[x + dx, y + dy, dz], normal="z",
                      w=7, t=7, kind="decor", emissive=False))


# the approved master-suite facet pattern (wall: along-wall 0..1, height 0..1; canopy: along 0..1, depth 0..1)
WALL_SEAMS = [((0.00, 0.66), (0.42, 1.0)), ((0.42, 1.0), (0.57, 0.50)), ((0.57, 0.50), (0.80, 1.0)),
              ((1.00, 0.60), (0.73, 0.81)), ((0.73, 0.81), (0.57, 0.50)), ((0.21, 0.50), (0.42, 1.0))]
CANOPY_SEAMS = [((0.42, 0.0), (0.66, 0.55)), ((0.66, 0.55), (0.80, 0.0)), ((0.66, 0.55), (0.49, 1.0)),
                ((0.42, 0.0), (0.24, 1.0)), ((1.00, 0.42), (0.66, 0.55))]


def facet_suite(tag, axis, face, a0, a1, depth, sign, slat_w=24):
    """Faceted walnut headboard wall on a wall plane + canopy over the bed.
    axis 'x': wall plane x=face, runs along y a0..a1, canopy grows in +x*sign.  axis 'y': plane y=face along x."""
    zt = H - 9                                             # canopy underside
    def wp(u, v, off):                                     # wall point: along u, height v, offset from the face
        a, z = a0 + u * (a1 - a0), v * zt
        return (face + sign * off, a, z) if axis == "x" else (a, face + sign * off, z)
    def cp(u, d):                                          # canopy point: along u, depth d
        a, e = a0 + u * (a1 - a0), face + sign * d * depth
        return (e, a, zt - 0.3) if axis == "x" else (a, e, zt - 0.3)
    def rect(p0, p1, z0, z1, id, mat, **kw):              # along a/out offsets -> box
        (u0, o0), (u1, o1) = p0, p1
        if axis == "x":
            D.append(B(id, mat, min(face + sign * o0, face + sign * o1), u0, max(face + sign * o0, face + sign * o1), u1, z0, z1, **kw))
        else:
            D.append(B(id, mat, u0, min(face + sign * o0, face + sign * o1), u1, max(face + sign * o0, face + sign * o1), z0, z1, **kw))
    rect((a0, 0), (a1, 2.6), 0, zt, f"D_{tag}_facet_wall", "walnut_facets", kind="panel")
    rect((a0 - slat_w - 1, 0), (a1 + slat_w + 1, depth), zt, H, f"D_{tag}_facet_canopy", "walnut_facets", kind="panel")
    n = "x" if axis == "x" else "y"
    for i, ((u0, v0), (u1, v1)) in enumerate(WALL_SEAMS):
        D.append(G(f"D_{tag}_seam_w{i}", wp(u0, v0, 2.9), wp(u1, v1, 2.9), n))
    for i, ((u0, d0), (u1, d1)) in enumerate(CANOPY_SEAMS):
        D.append(G(f"D_{tag}_seam_c{i}", cp(u0, d0), cp(u1, d1), "z"))
    rect((a0 - slat_w - 1, depth - 1), (a1 + slat_w + 1, depth), zt - 1, zt, f"D_{tag}_canopy_edge", "led_line", kind="light", emissive=True)
    rect((a0 - 1.5, 0), (a0, 3.2), 0, zt, f"D_{tag}_panel_edge0", "led_line", kind="light", emissive=True)
    rect((a1, 0), (a1 + 1.5, 3.2), 0, zt, f"D_{tag}_panel_edge1", "led_line", kind="light", emissive=True)
    for side, start in (("l", a0 - 1 - slat_w), ("r", a1 + 1)):
        for k in range(4):
            s0 = start + k * slat_w / 4
            rect((s0 + 0.6, 0), (s0 + slat_w / 4 - 0.6, 8), 0, H, f"D_{tag}_slat_{side}{k}", "black_slats", kind="panel")


def marble_wall(tag, face, a0, a1, sign):
    """white marble feature panel on a wall at x=face, framed by two vertical LED lines (clear of the wall box overlap)"""
    lo, hi = sorted((face + sign * 1.2, face + sign * 2.7))
    llo, lhi = sorted((face + sign * 1.2, face + sign * 3.4))
    D.append(B(f"D_{tag}_marble", "marble_white_panel", lo, a0, hi, a1, 0, H, kind="panel"))
    D.append(led(f"D_{tag}_marble_led0", llo, a0 - 1.5, lhi, a0, 0, H - 4))
    D.append(led(f"D_{tag}_marble_led1", llo, a1, lhi, a1 + 1.5, 0, H - 4))


# ======================================================================== BEDROOM 1 (headboard on the west wall)
facet_suite("b1", "x", X(205), Y(546), Y(760), X(300) - X(205), +1, slat_w=8.4)   # same slim slats as bedrooms 2/3
lamp("D_b1_lamp0", X(222), Y(573.5))
lamp("D_b1_lamp1", X(222), Y(732.5))
D.append(B("D_b1_rug", "rug_sand", 60, 395, 300, 690, 0, 1.2))
marble_wall("b1", X(446), Y(560), Y(790), -1)                       # bed-facing wall
D.append(led("D_b1_wash", X(446) - 4, Y(355), X(446) - 1, Y(812), 266.5, 268.5))
D.append(B("D_b1_curtain0", "sheer_linen", X(205) + 1, Y(815) - 9, X(221) + 6, Y(815) - 1, 0, 250))
D.append(B("D_b1_curtain1", "sheer_linen", X(404) - 4, Y(815) - 9, X(404) + 14, Y(815) - 1, 0, 250))
pampas("D_b1_pampas", X(430), Y(790))

# ======================================================================== BEDROOMS 2 + 3 (headboard on the wardrobe wall)
for b, (wx0, wx1, ns1, ns2, mface, msign, cur, pam, rug) in {
        "b2": (550, 745, 566.5, 726, X(811), -1, (466, 811), 492, (500, 715)),
        "b3": (897, 1091, 913.5, 1073, X(830), +1, (830, 1175), 1150, (955, 1170))}.items():
    facet_suite(b, "y", Y(737), X(wx0) + 9.4, X(wx1) - 9.4, Y(840) - Y(737), +1, slat_w=8.4)
    lamp(f"D_{b}_lamp0", X(ns1), Y(754))
    lamp(f"D_{b}_lamp1", X(ns2), Y(754))
    D.append(B(f"D_{b}_rug", "rug_sand", rug[0], 700, rug[1], 905, 0, 1.2))
    marble_wall(b, mface, Y(735), Y(975), msign)                    # side wall beside the bed
    D.append(led(f"D_{b}_wash", min(mface + msign * 1, mface + msign * 4), Y(613) + 2, max(mface + msign * 1, mface + msign * 4), Y(1004) - 2, 266.5, 268.5))
    D.append(B(f"D_{b}_curtain0", "sheer_linen", X(cur[0]) + 1, Y(1004) - 9, X(cur[0]) + 21, Y(1004) - 1, 0, 255))
    D.append(B(f"D_{b}_curtain1", "sheer_linen", X(cur[1]) - 21, Y(1004) - 9, X(cur[1]) - 1, Y(1004) - 1, 0, 255))
    pampas(f"D_{b}_pampas", X(pam), Y(978))

# ======================================================================== BATHROOM 1 ("dark ring": slate, ring mirror)
D.append(B("D_bath1_drawer", "vanity_walnut_drawer", X(207), Y(371), X(245), Y(419), 25, 48))
D.append(led("D_bath1_vanity_under", X(207), Y(373), X(245), Y(417), 23.5, 24.5))
D.append(DSK("D_bath1_mirror", "mirror_round", X(205) + 2.0, Y(395), 160, 33, 1.6, "x"))
D.append(T("D_bath1_ring", "ring_led", X(205) + 4.2, Y(395), 160, 38, 1.3, "x"))
D.append(B("D_bath1_flush", "black_metal", X(205) + 1.2, Y(289), X(205) + 3, Y(311), 92, 108, kind="panel"))
D.append(B("D_bath1_shower_glass", "smoked_glass", X(362) - 0.6, Y(267) + 1, X(362) + 0.6, Y(322), 0, 205, kind="panel"))
D.append(C("D_bath1_rainhead", "black_metal", X(404), Y(305), 15, 266, 268, kind="light"))
D.append(B("D_bath1_niche", "niche_lit", X(372), Y(267) + 1.1, X(436), Y(267) + 3.6, 95, 125, kind="panel"))
D.append(led("D_bath1_niche_led", X(372), Y(267) + 1.1, X(436), Y(267) + 3.9, 123.5, 125))
for i, (y, x0, x1) in enumerate([(Y(290), X(210), X(440)), (Y(400), X(250), X(350))]):
    D.append(led(f"D_bath1_slot{i}", x0, y - 1.2, x1, y + 1.2, 268.5, 269.6))
D.append(C("D_bath1_diffuser", "ceramic_dark", X(214), Y(410), 3.5, 85, 101))

# ======================================================================== BATHROOM PODS ("taupe & walnut")
def pod(tag, vx0, vx1, wall_y, basin_x, pend, vase, glass_x, rain, niche_face, niche_side, flush_x):
    cy0, cy1 = Y(462), Y(500)
    x0, x1 = X(vx0), X(vx1)
    D.append(B(f"D_{tag}_shelf", "walnut_counter", x0, cy0 + 2, x1, cy1 - 4, 52, 55))
    D.append(B(f"D_{tag}_drawers", "cabinet_taupe", x0, cy0 + 4, x1, cy1 - 4, 8, 34))
    D.append(led(f"D_{tag}_under", x0 + 2, cy0 + 6, x1 - 2, cy1 - 6, 6.5, 7.5))
    D.append(B(f"D_{tag}_basin", "basin_black_vessel", X(basin_x) - 24, cy0 + 8, X(basin_x) + 24, cy1 - 10, 90, 104))
    D.append(B(f"D_{tag}_mirror", "mirror_cabinet", x0 + 8, wall_y + 1.1, x1 - 6, wall_y + 13, 118, 222, kind="panel"))
    D.append(led(f"D_{tag}_mirror_led", x0 + 8, wall_y + 1.5, x1 - 6, wall_y + 12, 116.5, 117.5))
    D.append(led(f"D_{tag}_wash", x0, wall_y + 1.1, x1, wall_y + 3.5, 266.5, 268.5))
    for i, (px, py, zb) in enumerate(pend):
        pendant(f"D_{tag}_pend{i}", X(px), Y(py), zb)
    D.append(C(f"D_{tag}_vase", "ceramic_dark", X(vase[0]), Y(vase[1]), 6, 90, 116))
    for i, (dx, dy, dz) in enumerate([(-5, 0, 124), (5, 3, 128), (0, -3, 136)]):
        D.append(S(f"D_{tag}_gyps{i}", "gypsophila", X(vase[0]) + dx, Y(vase[1]) + dy, dz, 8))
    gx = X(glass_x)
    D.append(B(f"D_{tag}_shower_glass", "glass", gx - 0.6, Y(462) + 1, gx + 0.6, Y(560), 0, 205, kind="panel"))
    D.append(C(f"D_{tag}_rainhead", "black_metal", X(rain[0]), Y(rain[1]), 15, 266, 268, kind="light"))
    n0, n1 = sorted((niche_face + niche_side * 1.2, niche_face + niche_side * 3.7))
    D.append(B(f"D_{tag}_niche", "niche_lit", n0, Y(490), n1, Y(560), 95, 125, kind="panel"))
    D.append(led(f"D_{tag}_niche_led", n0, Y(490), n1 + (0.3 if niche_side > 0 else 0), Y(560), 123.5, 125))
    D.append(B(f"D_{tag}_flush", "black_metal", X(flush_x) - 12, wall_y + 1.1, X(flush_x) + 12, wall_y + 2.9, 92, 108, kind="panel"))


pod("podL", 626, 732, Y(462), 679, [(637, 476, 118), (643, 485, 102)], (722, 474), 626, (590, 527), X(555), +1, 772.5)
pod("podR", 906, 1015, Y(462), 960, [(1004, 476, 118), (998, 485, 102)], (916, 474), 1015, (1050, 527), X(1086), -1, 855)

# ======================================================================== CORRIDOR + STAIR
D.append(B("D_c_battens", "walnut_battens", X(645), Y(362) + 1.1, X(1045), Y(362) + 4, 0, H, kind="panel"))
D.append(led("D_c_led", X(475), Y(408) - 1.5, X(1170), Y(408) + 1.5, 267.5, 269.5))
for i, (a, b) in enumerate([(600, 740), (903, 1043)]):
    D.append(B(f"D_c_art{i}", "art_relief", X(a), Y(455) - 4.1, X(b), Y(455) - 1.1, 95, 195))
D.append(led("D_stair_led", X(668), Y(267) + 1.1, X(1098), Y(267) + 2.5, 8, 9))     # low wall-washer along the treads

# ======================================================================== LAUNDRY
D.append(B("D_l_uppers", "walnut_cabinet", X(1350), Y(640), X(1376) - 1.1, Y(888), 150, 235, kind="panel"))
D.append(led("D_l_uppers_led", X(1352), Y(642), X(1376) - 1.5, Y(886), 148.5, 149.5))
D.append(led("D_l_led", X(1240), Y(630), X(1244), Y(880), 267.5, 269.5))

DESIGN = D

# ======================================================================== SITE (exterior seen through the south glazing)
SITE = [
    dict(id="EXT_ground", mat="lawn", rect=[-800, -400, 2400, 2600], z=[-2, -1]),
    dict(id="EXT_terrace_b1", mat="stone_pot", rect=[X(184), Y(843), X(466), Y(980)], z=[-1, 0]),
    dict(id="EXT_terrace", mat="stone_pot", rect=[X(437), Y(1018), X(1205), Y(1065)], z=[-1, 0]),
    dict(id="EXT_hedge", mat="hedge", rect=[-200, 1500, 2000, 1560], z=[0, 110]),
]
for i, (x, y) in enumerate([(300, 1330), (760, 1420), (1150, 1300), (1500, 1450), (-150, 1200)]):
    SITE.append(dict(id=f"EXT_tree_trunk{i}", mat="olive_trunk", cyl=[x, y, 8], z=[0, 180]))
    SITE.append(dict(id=f"EXT_tree_crown{i}", mat="olive_foliage", sphere=[x, y, 260, 110]))
