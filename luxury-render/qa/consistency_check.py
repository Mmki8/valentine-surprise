"""QA gate 3 - cross-view consistency.

The same material must look the same in every view of the house. For each
render we know, per pixel, which locked material should be there (material-ID
pass, mapped into the render with the alignment found by geometry_check). We
sample the render's colour for every material and compare each view against
the hero view of its space:

  * chroma difference (a*, b* in CIELAB) catches a different stone, wood or
    fabric colour - e.g. walnut fronts in one view, black lacquer in another;
  * lightness is compared loosely (lighting changes between viewpoints are real).

usage: python3 qa/consistency_check.py <plan_dir> CAM1 CAM2 ...   (uses each camera's latest attempt)
prints a table and writes output/<plan>/consistency.json
"""
import json, os, sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_DCHROMA = 14.0      # ~ clearly different colour / material
MAX_DL = 32.0           # very loose: viewpoints legitimately differ in brightness
MIN_PX = 1500
IGNORE = {"glass", "led_line", "reveal_dark", "groove_dark", "cable_black", "unknown", "lawn", "hedge",
          "crystal_ring", "water", "mirror_backlit", "black_metal"}


def stats(base, att):
    meta = json.load(open(os.path.join(base, "blockout", "passes.json")))
    g = json.load(open(os.path.join(att, "geometry.json")))
    mimg = cv2.imread(os.path.join(base, "blockout", "mat_ids.png"))[:, :, ::-1]
    H, W = mimg.shape[:2]
    img = cv2.imread(os.path.join(att, "render.png"))
    h, w = img.shape[:2]
    if abs(w / h - W / H) > 0.01:
        if w / h > W / H:
            nw = int(h * W / H); img = img[:, (w - nw) // 2:(w - nw) // 2 + nw]
        else:
            nh = int(w * H / W); img = img[(h - nh) // 2:(h - nh) // 2 + nh]
    img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:, :, 0] *= 100 / 255; lab[:, :, 1] -= 128; lab[:, :, 2] -= 128
    al = g["alignment"]; s = al["scale"]; dx = al["dx_frac"] * W; dy = al["dy_frac"] * H
    A = np.float32([[s, 0, W / 2 * (1 - s) + dx], [0, s, H / 2 * (1 - s) + dy]])
    out = {}
    for l in meta["mat_legend"]:
        if l["mat"] in IGNORE:
            continue
        m = np.all(mimg == np.array(l["rgb"], np.uint8), axis=2).astype(np.uint8) * 255
        m = cv2.warpAffine(m, A, (W, H), flags=cv2.INTER_NEAREST)
        m = cv2.erode(m, np.ones((9, 9), np.uint8))
        n = int((m > 0).sum())
        if n < MIN_PX:
            continue
        px = lab[m > 0]
        out[l["mat"]] = dict(px=n, L=float(np.median(px[:, 0])), a=float(np.median(px[:, 1])), b=float(np.median(px[:, 2])))
    return out


def latest(plan, cam):
    log = json.load(open(os.path.join(ROOT, "output", plan, cam, "qa_log.json")))
    return os.path.join(ROOT, log["attempts"][-1]["dir"])


def main(plan_dir, cams):
    plan = os.path.basename(os.path.normpath(plan_dir))
    cfg = json.load(open(os.path.join(plan_dir, "cameras.json")))
    space = {c["id"]: c.get("space") for c in cfg["cameras"]}
    S = {cam: stats(os.path.join(ROOT, "output", plan, cam), latest(plan, cam)) for cam in cams}
    report = {}
    for cam in cams:
        sp = next(v for k, v in space.items() if cam.startswith(k))
        hero = cfg["heroes"].get(sp)
        if not hero or hero == cam or hero not in S:
            continue
        rows = []
        for m, v in S[cam].items():
            if m not in S[hero]:
                continue
            h = S[hero][m]
            dc = float(np.hypot(v["a"] - h["a"], v["b"] - h["b"])); dl = abs(v["L"] - h["L"])
            rows.append(dict(mat=m, d_chroma=round(dc, 1), d_L=round(dl, 1), ok=dc <= MAX_DCHROMA and dl <= MAX_DL))
        bad = [r for r in rows if not r["ok"]]
        report[cam] = dict(hero=hero, compared=len(rows), passed=not bad, failures=bad)
        print(f"{cam:12s} vs {hero:10s}  materials compared {len(rows):2d}  "
              + ("PASS" if not bad else "FAIL " + "; ".join(f"{r['mat']} dC={r['d_chroma']} dL={r['d_L']}" for r in bad)))
    json.dump(dict(stats=S, report=report), open(os.path.join(ROOT, "output", plan, "consistency.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
