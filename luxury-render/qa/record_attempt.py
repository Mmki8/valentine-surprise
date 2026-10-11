"""Record one generation attempt: download, run the geometry gate, log it.

usage: python3 qa/record_attempt.py <plan_dir> <CAM> <model> <job_id> <image_url>
  -> output/<plan>/<CAM>/attempts/NN_<model>/{render.png, geometry.json, overlay.png}
  -> appends to output/<plan>/<CAM>/qa_log.json  (auto verdict; vision verdict added by review.py)
"""
import json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry_check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(plan_dir, cam, model, job_id, url):
    base = os.path.join(ROOT, "output", os.path.basename(os.path.normpath(plan_dir)), cam)
    log_p = os.path.join(base, "qa_log.json")
    log = json.load(open(log_p)) if os.path.exists(log_p) else {"camera": cam, "attempts": []}
    n = len(log["attempts"]) + 1
    adir = os.path.join(base, "attempts", f"{n:02d}_{model}")
    os.makedirs(adir, exist_ok=True)
    raw = os.path.join(adir, "render_raw")
    subprocess.run(["curl", "-sSfL", "-o", raw, url], check=True)
    subprocess.run(["python3", "-c", f"from PIL import Image; Image.open('{raw}').convert('RGB').save('{adir}/render.png')"], check=True)
    os.remove(raw)
    geometry_check.main(os.path.join(base, "blockout"), os.path.join(adir, "render.png"), adir)
    g = json.load(open(os.path.join(adir, "geometry.json")))
    log["attempts"].append(dict(n=n, model=model, job_id=job_id, url=url, dir=os.path.relpath(adir, ROOT),
                                time=time.strftime("%Y-%m-%dT%H:%M:%S"),
                                auto=dict(passed=g["auto_pass"], struct_score=g["structural"]["score"],
                                          drift=g["alignment"]["drift"], failures=g["failures"]),
                                vision=None, final=None))
    json.dump(log, open(log_p, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:6])
