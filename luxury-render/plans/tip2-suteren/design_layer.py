"""Design layer for house type 2 (souterrain), used by the top-down 3D floor plan.

Follows the approved type-2 souterrain renders (output/tip2-restyle): warm walnut floors and walnut panelling, cream
plaster, cognac channel-tufted headboards and leather bed benches, olive-green bedding in the east suite, dark marble
bathrooms, dark stone spa with a round jacuzzi and a walnut sauna. Only floor-level objects are modelled here (rugs,
benches): nothing that is not on the client's plan. The plan is seen from straight above, so ceiling fittings are irrelevant.
Coordinates: drawing px are converted with the same scale as digitize.py; output in plan cm.
"""
K, OX, OY = 1.313, 170, 220


def X(px):
    return round((px - OX) * K, 1)


def Y(py):
    return round((py - OY) * K, 1)


def B(id, mat, x0, y0, x1, y1, z0, z1, kind="decor"):
    return dict(id=id, shape="box", mat=mat, rect=[X(x0), Y(y0), X(x1), Y(y1)], z=[z0, z1], kind=kind, emissive=False)


def C(id, mat, cx, cy, r, z0, z1, kind="decor"):
    return dict(id=id, shape="cyl", mat=mat, center=[X(cx), Y(cy)], r=r, z=[z0, z1], kind=kind, emissive=False)


def S(id, mat, cx, cy, cz, r, kind="decor"):
    return dict(id=id, shape="sphere", mat=mat, center=[X(cx), Y(cy), cz], r=r, kind=kind, emissive=False)


DESIGN = []
for b, (rug, bench) in {"1": ((572, 790, 737, 935), (600, 868, 709, 888)),
                        "2": ((919, 790, 1084, 935), (947, 868, 1056, 888))}.items():
    DESIGN.append(B(f"D_bed{b}_rug", "rug_sand", *rug, 0, 1.2))
    DESIGN.append(B(f"D_bed{b}_bench", "leather_cognac", *bench, 0, 45, kind="panel"))
SITE = []
