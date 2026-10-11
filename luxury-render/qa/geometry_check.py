"""QA gate 1 - automated geometry check of an AI render against its blockout.

The blockout is the ground truth (built from plan.json). For every edge the 3D
model says must be visible from this camera, we ask: is there an image edge in
the AI render within a few pixels of it?

  * global alignment search (shift/scale) -> detects camera drift / reframing
  * structural score (walls, openings, slab) vs. a shifted-lines noise floor,
    so busy textures (wood grain, marble) cannot fake a pass
  * per-element recall -> names the exact window/door/furniture that moved,
    vanished or was invented over

usage: python3 qa/geometry_check.py <blockout_dir> <render.png> <out_dir>
writes <out_dir>/geometry.json and <out_dir>/overlay.png
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np

STRUCT_PREFIX = ("W_", "O_", "SLAB", "GALLERY", "CEIL_void")
GATES = dict(
    max_drift=0.02,            # best-fit shift must stay within 2% of frame
    max_scale_dev=0.03,        # and scale within 3%
    min_struct_score=0.45,     # normalised structural recall (0 = noise, 1 = perfect)
    min_element_recall=0.35,   # every sizeable structural element must be found
    min_element_px=250,        # ... if it has at least this many edge pixels
    min_furniture_recall=0.30,
)


def load_render(path, W, H):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    a_t, a_r = W / H, w / h
    if abs(a_r - a_t) > 0.01:  # centre-crop to blockout aspect
        if a_r > a_t:
            nw = int(h * a_t); x0 = (w - nw) // 2; im = im[:, x0:x0 + nw]
        else:
            nh = int(w / a_t); y0 = (h - nh) // 2; im = im[y0:y0 + nh]
    return cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)


def edges(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 1.2)
    e = cv2.Canny(g, 12, 36)
    return e


def warp_pts(pts, dx, dy, s, W, H):
    cx, cy = W / 2, H / 2
    x = (pts[:, 0] - cx) * s + cx + dx
    y = (pts[:, 1] - cy) * s + cy + dy
    return x, y


def recall(dist, pts, dx, dy, s, tol, W, H):
    x, y = warp_pts(pts, dx, dy, s, W, H)
    ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
    if ok.sum() == 0:
        return 0.0
    d = dist[y[ok].astype(int), x[ok].astype(int)]
    return float((d <= tol).mean())


def base_id(eid):
    eid = re.sub(r"_(s|sill|head)\d+$", "", eid)
    eid = re.sub(r"_(fl|fr|ft|fb|tr|mid|kick|m[\d.]+|g[-\d.]+)$", "", eid)
    eid = re.sub(r"_(back|leg|arm[NSEW]|top|plinth|base|cabin|wheel|water)$", "", eid)
    return eid


def main(bdir, render_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    meta = json.load(open(os.path.join(bdir, "passes.json")))
    gt = os.path.join(bdir, "gt_edges.png")
    if not os.path.exists(gt):
        import gt_edges; gt_edges.run(bdir)
    lines = cv2.imread(gt, cv2.IMREAD_GRAYSCALE)
    eids = cv2.imread(os.path.join(bdir, "surface_ids.png"), cv2.IMREAD_COLOR)[:, :, ::-1]
    H, W = lines.shape
    tol = max(3, round(W * 0.005))
    img = load_render(render_path, W, H)
    e = edges(img)
    dist = cv2.distanceTransform(255 - e, cv2.DIST_L2, 3)

    # element membership of every blockout edge pixel
    lut = {tuple(l["rgb"]): l for l in meta["legend"]}
    ys, xs = np.nonzero(lines < 128)
    rgb = eids[ys, xs]
    keys = [tuple(int(c) for c in p) for p in rgb]
    pts = np.stack([xs, ys], 1).astype(np.float32)
    elem = np.array([base_id(lut[k]["id"]) if k in lut else "?" for k in keys])
    kind = np.array([lut[k]["kind"] if k in lut else "?" for k in keys])
    is_struct = np.array([el.startswith(STRUCT_PREFIX) for el in elem])

    # 1. alignment search on structural edges
    sp = pts[is_struct] if is_struct.sum() > 500 else pts
    best = (-1, 0, 0, 1)
    for s in (0.97, 0.985, 1.0, 1.015, 1.03):
        for dx in np.linspace(-0.03 * W, 0.03 * W, 13):
            for dy in np.linspace(-0.03 * H, 0.03 * H, 9):
                r = recall(dist, sp[::4], dx, dy, s, tol, W, H)
                if r > best[0]:
                    best = (r, dx, dy, s)
    _, dx, dy, s = best
    # refine
    for s2 in np.linspace(s - 0.008, s + 0.008, 5):
        for dx2 in np.linspace(dx - 0.004 * W, dx + 0.004 * W, 5):
            for dy2 in np.linspace(dy - 0.004 * H, dy + 0.004 * H, 5):
                r = recall(dist, sp[::2], dx2, dy2, s2, tol, W, H)
                if r > best[0]:
                    best = (r, dx2, dy2, s2)
    _, dx, dy, s = best

    # 2. noise floor: same lines, deliberately misplaced
    offs = [(0.08 * W, 0), (-0.08 * W, 0), (0, 0.08 * H), (0, -0.08 * H), (0.06 * W, 0.06 * H)]
    floor = float(np.mean([recall(dist, sp[::2], dx + ox, dy + oy, s, tol, W, H) for ox, oy in offs]))
    raw = recall(dist, sp, dx, dy, s, tol, W, H)
    struct_score = (raw - floor) / max(1e-6, 1 - floor)

    # 3. per element
    per = {}
    for el in np.unique(elem):
        m = elem == el
        n = int(m.sum())
        if n < 60 or el in ("?",) or el.startswith(("FLOOR_", "CEIL_R", "EXT_")):
            continue
        r = recall(dist, pts[m], dx, dy, s, tol, W, H)
        per[el] = dict(px=n, recall=round(r, 3), structural=bool(el.startswith(STRUCT_PREFIX)),
                       kind=str(kind[m][0]))
    drift = float(np.hypot(dx / W, dy / H))
    fails = []
    if drift > GATES["max_drift"]:
        fails.append(f"camera drift {drift:.3f} > {GATES['max_drift']}")
    if abs(s - 1) > GATES["max_scale_dev"]:
        fails.append(f"framing scale {s:.3f}")
    if struct_score < GATES["min_struct_score"]:
        fails.append(f"structural score {struct_score:.2f} < {GATES['min_struct_score']}")
    for el, v in per.items():
        if v["px"] < GATES["min_element_px"]:
            continue
        lim = GATES["min_element_recall"] if v["structural"] else GATES["min_furniture_recall"]
        if v["recall"] < lim:
            fails.append(f"{el} ({v['kind']}) recall {v['recall']:.2f} < {lim}")

    # 4. overlay: render + blockout edges (green = matched, red = missing)
    ov = (img * 0.75).astype(np.uint8)
    x, y = warp_pts(pts, dx, dy, s, W, H)
    ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
    xi, yi = x[ok].astype(int), y[ok].astype(int)
    hit = dist[yi, xi] <= tol
    ov[yi[hit], xi[hit]] = (60, 230, 60)
    ov[yi[~hit], xi[~hit]] = (40, 40, 255)
    ov = cv2.dilate(ov, np.ones((1, 1), np.uint8))
    for i, f in enumerate(fails[:12]):
        cv2.putText(ov, f, (12, 28 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imwrite(os.path.join(out_dir, "overlay.png"), ov)
    cv2.imwrite(os.path.join(out_dir, "render_edges.png"), e)

    res = dict(
        render=render_path, size=[W, H], tol_px=tol,
        alignment=dict(dx_frac=round(dx / W, 4), dy_frac=round(dy / H, 4), scale=round(s, 4), drift=round(drift, 4)),
        structural=dict(raw_recall=round(raw, 3), noise_floor=round(floor, 3), score=round(struct_score, 3)),
        gates=GATES, auto_pass=not fails, failures=fails,
        elements=dict(sorted(per.items(), key=lambda kv: kv[1]["recall"])),
    )
    json.dump(res, open(os.path.join(out_dir, "geometry.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("alignment", "structural", "auto_pass", "failures")}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
