"""guide_lined.png = guide pass with the true geometric edges burned in as thin
dark lines. Gives the image model an unambiguous 'technical drawing' of every
wall, opening and furniture edge on top of the material/colour intent.
usage: python3 engine/compose_guide.py <blockout_dir> [...]
"""
import os, sys
import cv2
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "qa"))
import gt_edges

for b in sys.argv[1:]:
    gt = os.path.join(b, "gt_edges.png")
    gt_edges.run(b)          # always: a gt_edges.png left from an earlier render would burn stale geometry into the guide
    g = cv2.imread(os.path.join(b, "guide.png")).astype(np.float32)
    e = cv2.imread(gt, cv2.IMREAD_GRAYSCALE) < 128
    e = cv2.dilate(e.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)
    # dark outlines on light surfaces, LIGHT outlines on dark surfaces (slate, black glass): an edge must always be visible
    luma = g[:, :, :3].mean(axis=2)
    dark_bg = cv2.blur(luma, (9, 9)) < 70
    ed, el = e & ~dark_bg, e & dark_bg
    g[ed] = g[ed] * 0.15 + np.array([20, 20, 20]) * 0.85
    g[el] = g[el] * 0.25 + np.array([215, 215, 215]) * 0.75
    cv2.imwrite(os.path.join(b, "guide_lined.png"), g.astype(np.uint8))
    print("guide_lined", b)
