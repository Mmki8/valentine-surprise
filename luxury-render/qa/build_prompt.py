"""Compose the generation prompt + the QA checklist for one camera.

Both come from the same data, so what we ask for is exactly what we check:
  plan.json (what exists) + blockout surface_ids (what this camera sees)
  + design-system.json (how it should look).

usage: python3 qa/build_prompt.py <plan_dir> <CAM_ID[_variant]>
writes output/<plan>/<CAM>/prompt.txt and checklist.json
"""
import json, os, re, sys
from collections import defaultdict
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry_check import base_id

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {
    "sofa": "L-shaped sofa", "armchair": "lounge armchair", "coffee_table": "coffee table", "table": "dining table",
    "chair": "dining chair", "stool": "bar stool", "island": "kitchen island", "counter": "L-shaped kitchen base-cabinet run",
    "tall_cabinet": "full-height cabinet column", "low_cabinet": "low cabinet", "appliance": "washer/dryer",
    "tv": "TV", "toilet": "wall-hung toilet", "vanity": "floating vanity", "basin": "vessel basin",
    "bench": "sauna bench", "jacuzzi": "round jacuzzi hot tub", "shower": "walk-in shower",
    "stair": "staircase", "car": "car (matte black Mercedes G-Wagon)", "cooktop": "cooktop", "sink": "sink",
    "box": "boxed column",
}
OPEN_NAMES = {"window": "window", "door": "door (closed)", "double_door": "glazed double door (closed)",
              "sliding": "full-height glazed sliding door", "curtain": "floor-to-ceiling glass facade",
              "garage_door": "sectional garage door (closed)", "glass_partition": "glass partition/door"}


def where(x0, x1, W):
    c = (x0 + x1) / 2 / W
    return "left" if c < 0.33 else ("right" if c > 0.67 else "centre")


def main(plan_dir, cam_full):
    plan = json.load(open(os.path.join(plan_dir, "plan.json")))
    ds = json.load(open(os.path.join(ROOT, "design-system", "design-system.json")))
    cams = json.load(open(os.path.join(plan_dir, "cameras.json")))["cameras"]
    cam = next(c for c in cams if cam_full.startswith(c["id"]))
    out = os.path.join(ROOT, "output", os.path.basename(os.path.normpath(plan_dir)), cam_full)
    meta = json.load(open(os.path.join(out, "blockout", "passes.json")))
    sid = cv2.imread(os.path.join(out, "blockout", "surface_ids.png"), cv2.IMREAD_COLOR)[:, :, ::-1]
    H, W = sid.shape[:2]
    codes = (sid[:, :, 0].astype(np.int64) << 16) | (sid[:, :, 1].astype(np.int64) << 8) | sid[:, :, 2]
    lut = {(l["rgb"][0] << 16) | (l["rgb"][1] << 8) | l["rgb"][2]: l for l in meta["legend"]}
    vis = defaultdict(lambda: dict(px=0, x0=W, x1=0))
    u, cnt = np.unique(codes, return_counts=True)
    for code, n in zip(u, cnt):
        if code not in lut:
            continue
        b = base_id(lut[code]["id"])
        ys, xs = np.nonzero(codes == code)
        v = vis[b]; v["px"] += int(n); v["x0"] = min(v["x0"], int(xs.min())); v["x1"] = max(v["x1"], int(xs.max()))
    frac = {k: v["px"] / (W * H) for k, v in vis.items()}

    furn = {f["id"]: f for f in plan["furniture"]}
    opens = {o["id"]: o for o in plan["openings"]}
    car_on = meta["variant"].get("opts", {}).get("car", True)
    items, counts, openings, seen_groups = [], defaultdict(int), [], set()
    for k, fr in sorted(frac.items(), key=lambda kv: -kv[1]):
        if fr < 0.002:
            continue
        if k in furn:
            f = furn[k]
            if f["kind"] in ("glass", "fixture"):
                continue
            if f["kind"] == "stair":
                k2 = "staircase"
                if k2 in [i["id"] for i in items]:
                    continue
                items.append(dict(id=k2, name="staircase", where=where(vis[k]["x0"], vis[k]["x1"], W), share=round(fr, 3)))
                continue
            if f.get("group"):
                if f["group"] in seen_groups:
                    continue
                seen_groups.add(f["group"])
            counts[f["kind"]] += 1
            items.append(dict(id=k, name=NAMES.get(f["kind"], f["kind"]), where=where(vis[k]["x0"], vis[k]["x1"], W),
                              share=round(fr, 3), note=f.get("note")))
        elif k in opens:
            o = opens[k]
            openings.append(dict(id=k, name=OPEN_NAMES[o["type"]], where=where(vis[k]["x0"], vis[k]["x1"], W),
                                 share=round(fr, 3), note=o.get("note")))
    if not car_on:
        counts.pop("car", None)

    room = ds["rooms"][cam["room"]]
    rt = room["retexture"]
    others = sorted({furn[i["id"]]["room"] for i in items if i["id"] in furn} - {cam["room"]})
    look = ds["blockout_look"]
    kinds = ["floor", "ceiling", "wall"] + [k for k in counts] + \
            [k for k in ("door", "glass", "frame", "slab_edge") if any(v.startswith(("O_", "SLAB", "GALLERY")) and
             (k != "slab_edge" or v.startswith("SLAB")) for v in vis)]
    if any(i["name"] == "staircase" for i in items):
        kinds.append("stair")
    # materials of neighbouring rooms seen through openings
    mp = {}
    for r in [cam["room"]] + others:
        for k, v in ds["rooms"].get(r, {}).get("retexture", {}).get("map", {}).items():
            mp.setdefault(k, v)
    pairs = []
    for k in dict.fromkeys(kinds):
        if k in mp and k in look:
            pairs.append(f"{look[k]} = {mp[k]}")
    inv = ", ".join(f"{n} x {NAMES.get(k, k)}" for k, n in sorted(counts.items()))
    if any(i["name"] == "staircase" for i in items):
        inv = (inv + ", " if inv else "") + "1 x staircase"
    open_txt = "; ".join(f"{o['name']} at frame {o['where']}" for o in openings) or "none"
    car_line = ""
    if cam["room"] == "R_garage" and not car_on:
        car_line = " The garage is EMPTY: no car anywhere."
    prompt = (
        "Turn IMAGE 1 into a photorealistic ultra-luxury architectural photograph WITHOUT changing its geometry. "
        "IMAGE 1 is a colour-coded 3D blockout of the real floor plan with every edge drawn as a thin dark line; keep the identical camera, "
        "framing and perspective, and keep every line - every wall, ceiling height, opening, column, stair and furniture piece - at exactly "
        "the same pixel position, size and count. This is a material and lighting pass only: retexture the surfaces, do not redesign the space. "
        "Do not add windows or doors; closed doors stay closed; glass only where the light-blue panes are." + car_line + "\n\n"
        f"Locked and visible: openings: {open_txt}; furniture: {inv or 'none'}.\n"
        f"Retexture as: {'; '.join(pairs)}.\n"
        f"Add only: {rt['add']}.\n"
        f"Light: {rt['light']}.\n"
        + (f"Specific to this view: {cam['notes']}\n" if cam.get("notes") else "") +
        "High-end interior photography, 24mm tilt-shift, perfectly vertical verticals, photorealistic global illumination, "
        "real material micro-detail. No people, no text, no extra furniture, no extra openings."
    )
    checklist = dict(camera=cam_full, room=cam["room"], car=car_on if cam["room"] == "R_garage" else None,
                     openings=openings, furniture_counts=dict(counts), items=items,
                     manual_checks=[
                         "camera position/angle/framing identical to blockout (compare overlay)",
                         "every opening listed is present, same position/size; NO extra window/door",
                         "every furniture count matches exactly; positions & orientation match",
                         "ceiling heights match (double height only over living)",
                         "daylight comes from the visible openings only, direction consistent",
                         "style matches design system for this room; photoreal, no AI artefacts",
                     ])
    open(os.path.join(out, "prompt.txt"), "w").write(prompt)
    json.dump(checklist, open(os.path.join(out, "checklist.json"), "w"), indent=1)
    print(prompt)
    print("\nCHECKLIST counts:", dict(counts), "| openings:", [o["id"] for o in openings])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
