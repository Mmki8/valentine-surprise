"""Gate a whole batch of finished jobs (run where the result CDN is reachable).

usage: python3 qa/sandbox_batch.py '<json list of {"cam","label","job_id","url"}>'
Prints one summary row per camera and writes 640px previews to /home/user/prev.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jobs = json.loads(sys.argv[1])
os.makedirs("/home/user/prev", exist_ok=True)
rows = []
for j in jobs:
    plan = j.get("plan", "osnova-prizemlja")
    r = subprocess.run(["python3", "qa/record_attempt.py", f"plans/{plan}", j["cam"], j["label"], j["job_id"], j["url"]],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        rows.append((j["cam"], "ERROR", r.stderr[-200:])); continue
    log = json.load(open(os.path.join(ROOT, "output", plan, j["cam"], "qa_log.json")))
    a = log["attempts"][-1]
    d = os.path.join(ROOT, a["dir"])
    from PIL import Image
    for k, q in (("render", 72), ("overlay", 66)):
        Image.open(f"{d}/{k}.png").convert("RGB").resize((640, 360)).save(f"/home/user/prev/{j['cam']}_{a['n']:02d}_{k[0]}.jpg", quality=q)
    rows.append((j["cam"], a["n"], a["auto"]["struct_score"], a["auto"]["drift"], a["auto"]["passed"], "; ".join(a["auto"]["failures"])))
for r in rows:
    print(" | ".join(str(x) for x in r))
