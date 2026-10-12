"""Restyle gate: the new render must keep the ORIGINAL render's geometry (camera, walls, openings, furniture).

usage: python3 qa/restyle_check.py <original.jpg> <new.png|url> [label]
Compares large-scale structure only (materials are SUPPOSED to change):
  * edges of both images after a strong blur (fine texture - slats, veining, grain - is ignored)
  * recall  = share of the original's structural edges found again within 1.5 % of the frame width
  * precision = share of the new image's structural edges that sit on an original edge
  * shift  = global translation between the two edge maps (camera drift), fraction of the width
PASS: recall >= 0.55 and shift <= 0.03 (precision is reported - a new design legitimately adds edges).
Writes a side-by-side preview with the original edges (red) over the new image.
"""
import sys, os, json, urllib.request
import cv2, numpy as np

W = 640


def load(p):
    if p.startswith("http"):
        data = urllib.request.urlopen(p, timeout=120).read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(p, cv2.IMREAD_COLOR)
    h = round(W * img.shape[0] / img.shape[1])
    return cv2.resize(img, (W, h), interpolation=cv2.INTER_AREA)


def edges(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (0, 0), 2.2)
    v = np.median(g)
    e = cv2.Canny(g, int(max(10, 0.4 * v)), int(min(255, 0.9 * v + 30)))
    # keep only long structures: drop tiny components (texture)
    n, lab, st, _ = cv2.connectedComponentsWithStats(e, 8)
    keep = np.zeros_like(e)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 25:
            keep[lab == i] = 255
    return keep


def main(orig, new, label=""):
    a, b = load(orig), load(new)
    if a.shape != b.shape:
        b = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
    ea, eb = edges(a), edges(b)
    tol = max(3, round(0.015 * W))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * tol + 1, 2 * tol + 1))
    da, db = cv2.dilate(ea, k), cv2.dilate(eb, k)
    recall = float((ea & db).sum() / max(1, ea.sum()))
    precision = float((eb & da).sum() / max(1, eb.sum()))
    fa = cv2.GaussianBlur(ea.astype(np.float32), (0, 0), 3)
    fb = cv2.GaussianBlur(eb.astype(np.float32), (0, 0), 3)
    (dx, dy), _ = cv2.phaseCorrelate(fa, fb)
    shift = float(np.hypot(dx, dy) / W)
    ok = recall >= 0.55 and shift <= 0.03
    ov = b.copy()
    ov[ea > 0] = (0, 0, 255)
    side = np.hstack([a, ov])
    os.makedirs("/home/user/prev2", exist_ok=True)
    name = label or os.path.basename(orig).rsplit(".", 1)[0]
    cv2.imwrite(f"/home/user/prev2/{name}.jpg", side, [cv2.IMWRITE_JPEG_QUALITY, 72])
    r = dict(label=name, recall=round(recall, 3), precision=round(precision, 3), shift=round(shift, 4), pass_=ok)
    print(json.dumps(r))
    return r


if __name__ == "__main__":
    main(*sys.argv[1:4])
