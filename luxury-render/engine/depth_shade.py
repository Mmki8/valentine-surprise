"""Top-down plans of an upper floor: darken everything below that floor by its height, from the surface-ID pass.

Through the stair hole and the double-height voids the camera sees the floor below. In a flat-lit guide that floor
has the same colour as the upper floor, so the opening does not read. Shading by real height fixes it: the upper floor
stays at full brightness, the lower floor is dimmed, and each stair tread gets a brightness set by its own height,
so the flight visibly climbs to the landing.
usage: python3 engine/depth_shade.py plans/<plan> output/<plan>/<CAM>/blockout [floor_z] [stair_top_z]
With floor_z 0 (a lowest level) only the stair is graded, from LOW at its foot to full brightness at stair_top_z.
"""
import json, sys
import numpy as np
from PIL import Image

plan_dir, bdir = sys.argv[1], sys.argv[2]
FZ = float(sys.argv[3]) if len(sys.argv) > 3 else 310.0
TOP = float(sys.argv[4]) if len(sys.argv) > 4 else FZ
LOW = 0.42                                           # brightness of the lower floor

plan = json.load(open(f"{plan_dir}/plan.json"))
legend = json.load(open(f"{bdir}/passes.json"))["legend"]


def top(d):
    if "z" in d: return d["z"][1]
    if "h" in d and "z0" in d: return d["z0"] + d["h"]
    if "center" in d and len(d["center"]) > 2: return d["center"][2] + d.get("r", d.get("R", 0))
    if "p0" in d: return max(d["p0"][2], d["p1"][2])
    return None


ztop = {d["id"]: top(d) for d in plan["furniture"] + plan["design"]}


def factor(e):
    i, k = e["id"], e["kind"]
    if FZ <= 0:                                      # lowest level: grade the stair only, the rest stays as rendered
        return LOW + (1 - LOW) * min(ztop.get(i) or 0, TOP) / TOP if k == "stair" else 1.0
    if i.startswith(("U_", "FLOOR_U_")) or i.endswith("_cap"): return 1.0
    if k == "floor": return LOW
    if i == "F_stair_balustrade": return 0.8
    if i.startswith("F_stair_"):
        return LOW + (1 - LOW) * min(ztop.get(i) or 0, FZ) / FZ
    if k in ("wall", "frame"): return 0.6               # side faces of walls seen down the void
    z = ztop.get(i)
    if z is None: return 1.0
    return 1.0 if z >= FZ - 10 else LOW


sid = np.asarray(Image.open(f"{bdir}/surface_ids.png").convert("RGB")).astype(np.int32)
key = (sid[..., 0] << 16) | (sid[..., 1] << 8) | sid[..., 2]
f = np.ones(key.shape, np.float32)
for e in legend:
    r, g, b = e["rgb"]
    f[key == ((r << 16) | (g << 8) | b)] = factor(e)
for name in ("guide.png", "guide_lined.png"):
    im = np.asarray(Image.open(f"{bdir}/{name}").convert("RGB")).astype(np.float32)
    Image.fromarray(np.clip(im * f[..., None], 0, 255).astype(np.uint8)).save(f"{bdir}/{name}")
print("shaded", bdir, "lower-floor pixels:", int((f < 0.99).sum()))
