"""QA gate 0 - digitization check.

Draws every digitized wall / opening / furniture element of plan.json back onto
the source floor plan so a human (or Claude vision) can confirm the 3D model is
built from exactly what is drawn. Red = walls, cyan = openings, green =
furniture, orange = double-height void.

usage: python3 qa/overlay_plan.py plans/<plan>/plan.json out.png
"""
import json, os, sys
from PIL import Image, ImageDraw

plan_path, out = sys.argv[1], sys.argv[2]
plan = json.load(open(plan_path))
src = os.path.join(os.path.dirname(plan_path), plan["meta"]["source"])
K = plan["meta"]["scale_cm_per_px"]
OX, OY = plan["meta"]["origin_px"]
S = 2  # supersample for legibility

im = Image.open(src).convert("RGB")
im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
base = im.copy()
ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)


def px(x, y):
    return ((x / K + OX) * S, (y / K + OY) * S)


def rect(r, fill, outline):
    a, b = px(r[0], r[1]), px(r[2], r[3])
    d.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=fill, outline=outline, width=2)


v = plan["void"]["rect"]
rect(v, (255, 140, 0, 30), (255, 140, 0, 255))
for w in plan["walls"]:
    rect(w["rect"], (255, 0, 0, 70), (200, 0, 0, 255))
for o in plan["openings"]:
    rect(o["rect"], (0, 200, 255, 140), (0, 120, 255, 255))
for f in plan["furniture"]:
    if f["shape"] == "box":
        rect(f["rect"], (0, 220, 0, 50), (0, 150, 0, 255))
    elif f["shape"] == "prism":
        if f["axis"] == "z":
            d.polygon([px(*q) for q in f["poly"]], fill=(0, 220, 0, 50), outline=(0, 150, 0, 255))
    else:
        cx, cy = px(*f["center"])
        r = f["r"] / K * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 220, 0, 50), outline=(0, 150, 0, 255), width=2)
for r in plan["rooms"]:
    pts = [px(*p) for p in r["polygon"]]
    d.line(pts + [pts[0]], fill=(160, 0, 255, 255), width=2)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    d.text((cx - 30, cy), r["name"], fill=(120, 0, 200, 255))

Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB").save(out)
print("wrote", out)
