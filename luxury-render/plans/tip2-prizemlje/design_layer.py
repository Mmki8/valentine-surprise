"""Design layer for house type 2 (ground floor), used by the top-down 3D floor plan.

Follows the approved type-2 ground-floor renders (output/tip2-restyle): warm polished stone floors, cream plaster, a
walnut slatted TV wall, ivory boucle L-sofa, dark smoked-walnut kitchen columns with a marble island, sand
channel-tufted bed with a walnut panel wall and glass-front wardrobe, dark marble bathrooms, walnut-slatted garage
with the black G-Wagon. Only floor-level objects that complete the drawn furniture are modelled (rug, round column).
Coordinates: drawing px are converted with the same scale as digitize.py; output in plan cm.
"""
K, OX, OY = 1.313, 161, 235
LV = -51


def X(px):
    return round((px - OX) * K, 1)


def Y(py):
    return round((py - OY) * K, 1)


def B(id, mat, x0, y0, x1, y1, z0, z1, kind="decor"):
    return dict(id=id, shape="box", mat=mat, rect=[X(x0), Y(y0), X(x1), Y(y1)], z=[z0, z1], kind=kind, emissive=False)


def C(id, mat, cx, cy, r, z0, z1, kind="decor"):
    return dict(id=id, shape="cyl", mat=mat, center=[X(cx), Y(cy)], r=r, z=[z0, z1], kind=kind, emissive=False)


DESIGN = [
    B("D_liv_rug", "rug_sand", 900, 712, 1060, 880, LV, LV + 1.2),
    C("D_liv_column", "cut_cap", 821, 968, 13, LV, 280, kind="panel"),          # round structural column drawn on the plan
    B("D_bed_rug", "rug_sand", 985, 470, 1135, 560, 0, 1.2),
]
SITE = []
