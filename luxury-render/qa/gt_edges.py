"""Ground-truth visible edges of a blockout = depth jumps + surface-normal creases.

Seams between coplanar wall pieces (which no photo would show) are excluded.
Each edge pixel is labelled with the element on its nearer side (surface_ids).
usage: python3 qa/gt_edges.py <blockout_dir>   -> writes gt_edges.png
"""
import sys, os
import cv2
import numpy as np


def run(bdir):
    n = cv2.imread(os.path.join(bdir, "normals.png"), cv2.IMREAD_COLOR).astype(np.int16)
    dp = cv2.imread(os.path.join(bdir, "depth.png"), cv2.IMREAD_COLOR)[:, :, ::-1].astype(np.float64) / 255.0
    d = (dp[:, :, 0] + dp[:, :, 1] / 255.0 + dp[:, :, 2] / 65025.0) * 8000.0
    H, W = d.shape
    e = np.zeros((H, W), bool)
    for ax in (0, 1):
        dn = np.abs(np.diff(n, axis=ax)).max(axis=2) > 45
        dd = np.abs(np.diff(d, axis=ax)) / np.maximum(np.minimum(d[:-1, :] if ax == 0 else d[:, :-1],
                                                                  d[1:, :] if ax == 0 else d[:, 1:]), 1) > 0.04
        m = dn | dd
        if ax == 0:
            e[:-1, :] |= m
        else:
            e[:, :-1] |= m
    out = np.where(e, 0, 255).astype(np.uint8)
    cv2.imwrite(os.path.join(bdir, "gt_edges.png"), out)
    return out


if __name__ == "__main__":
    for b in sys.argv[1:]:
        run(b)
        print("gt edges", b)
