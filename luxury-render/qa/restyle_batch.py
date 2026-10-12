"""Run the restyle gate on many renders at once.
usage: python3 qa/restyle_batch.py <jobs.json>   (list of {label, src, url})
Prints one JSON line per render, writes side-by-sides to /home/user/prev2/<label>.jpg and a contact sheet
/home/user/prev2/_sheet_<n>.jpg (4 per sheet, small enough to inspect)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restyle_check import main as check
import cv2, numpy as np

jobs = json.load(open(sys.argv[1]))
res = []
for j in jobs:
    try:
        res.append(check(j["src"], j["url"], j["label"]))
    except Exception as e:
        print(json.dumps(dict(label=j["label"], error=str(e))))
for i in range(0, len(res), 4):
    tiles = [cv2.imread(f"/home/user/prev2/{r['label']}.jpg") for r in res[i:i + 4]]
    tiles = [cv2.resize(t, (960, round(960 * t.shape[0] / t.shape[1]))) for t in tiles]
    cv2.imwrite(f"/home/user/prev2/_sheet_{i // 4}.jpg", np.vstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 70])
