"""Top-down plan of an upper floor whose model leaves out the open-to-below areas (double-height voids, entrance voids).

Fills every pixel of the upper-floor guide that shows plain background, but where the floor below has something,
with the floor below rendered from the matching camera (raised by the storey height, so the scale matches). The
lower floor is dimmed so the voids read as open to below; its walls stay at full brightness because they rise
through the void to the upper floor.
usage: python3 engine/compose_open_below.py <upper blockout dir> <lower blockout dir> [dim]
"""
import json, sys
import numpy as np
from PIL import Image

up, lo = sys.argv[1], sys.argv[2]
DIM = float(sys.argv[3]) if len(sys.argv) > 3 else 0.55


def ids(d):
    a = np.asarray(Image.open(f"{d}/surface_ids.png").convert("RGB")).astype(np.int32)
    return (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]


BG = (255 << 16) | (255 << 8) | 255
iu, il = ids(up), ids(lo)
fill = (iu == BG) & (il != BG)
f = np.full(il.shape, DIM, np.float32)
for e in json.load(open(f"{lo}/passes.json"))["legend"]:
    if e["kind"] in ("wall", "frame") or e["id"].endswith("_cap"):
        r, g, b = e["rgb"]
        f[il == ((r << 16) | (g << 8) | b)] = 1.0
for name in ("guide.png", "guide_lined.png"):
    a = np.asarray(Image.open(f"{up}/{name}").convert("RGB")).astype(np.float32)
    b = np.asarray(Image.open(f"{lo}/{name}").convert("RGB")).astype(np.float32) * f[..., None]
    a[fill] = b[fill]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f"{up}/{name}")
print("filled", int(fill.sum()), "px from", lo)
