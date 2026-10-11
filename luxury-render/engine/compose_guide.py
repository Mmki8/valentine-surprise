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
    g[e] = g[e] * 0.15 + np.array([20, 20, 20]) * 0.85
    cv2.imwrite(os.path.join(b, "guide_lined.png"), g.astype(np.uint8))
    print("guide_lined", b)
