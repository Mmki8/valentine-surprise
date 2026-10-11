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
    "box": "boxed column", "bed": "bed", "nightstand": "nightstand",
}
OPEN_NAMES = {"window": "window", "door": "door (closed)", "double_door": "glazed double door (closed)",
              "sliding": "full-height glazed sliding door", "curtain": "floor-to-ceiling glass facade",
              "garage_door": "sectional garage door (closed)", "glass_partition": "glass partition/door"}


def where(x0, x1, W):
    c = (x0 + x1) / 2 / W
    return "left" if c < 0.33 else ("right" if c > 0.67 else "centre")


def hero_for(cam_full, plan_dir):
    c = json.load(open(os.path.join(plan_dir, "cameras.json")))
    cam = next(x for x in c["cameras"] if cam_full.startswith(x["id"]))
    h = c.get("heroes", {}).get(cam.get("space"))
    return h if h and h != cam_full else None


def mood_for(cam_full, plan_dir):
    """the client's mood reference for this space - used as IMAGE 2 only by the hero (nothing approved yet to chain to)"""
    c = json.load(open(os.path.join(plan_dir, "cameras.json")))
    cam = next(x for x in c["cameras"] if cam_full.startswith(x["id"]))
    if c.get("heroes", {}).get(cam.get("space")) != cam_full:
        return None
    return c.get("moods", {}).get(cam.get("space"))


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
    # ---- materials this camera actually sees (material-ID pass), each with its ONE locked text
    mimg = cv2.imread(os.path.join(out, "blockout", "mat_ids.png"), cv2.IMREAD_COLOR)[:, :, ::-1]
    mcodes = (mimg[:, :, 0].astype(np.int64) << 16) | (mimg[:, :, 1].astype(np.int64) << 8) | mimg[:, :, 2]
    mlut = {(l["rgb"][0] << 16) | (l["rgb"][1] << 8) | l["rgb"][2]: l["mat"] for l in meta["mat_legend"]}
    mu, mc = np.unique(mcodes, return_counts=True)
    seen = sorted(((mlut[k], n) for k, n in zip(mu, mc) if k in mlut), key=lambda t: -t[1])
    skip = {"reveal_dark", "groove_dark", "cable_black", "unknown", "lawn", "hedge"}
    if not car_on:
        skip.add("car_g63")
    mat_lines = [ds["materials"][m]["text"] for m, n in seen if m not in skip and m in ds["materials"] and n > W * H * 0.0008]
    inv = ", ".join(f"{n} x {NAMES.get(k, k)}" for k, n in sorted(counts.items()))
    if any(i["name"] == "staircase" for i in items):
        inv = (inv + ", " if inv else "") + "1 x staircase"
    open_txt = "; ".join(f"{o['name']} at frame {o['where']}" for o in openings) or "none"
    hero = hero_for(cam_full, plan_dir)
    mood = mood_for(cam_full, plan_dir)
    upper = cam["room"].startswith("U_")
    car_line = " The garage is EMPTY: no car anywhere." if (cam["room"] == "R_garage" and not car_on) else ""
    g = ds["global"]
    prompt = (
        "Turn IMAGE 1 into a photorealistic ultra-luxury architectural photograph WITHOUT changing its geometry. "
        "IMAGE 1 is a colour-coded 3D model of the real house, already showing the final design: every wall, opening, "
        "furniture piece, light fitting and decor object is modelled at its exact place, in its real colour, with every edge "
        "drawn as a thin dark line. Keep the identical camera, framing and perspective and keep every line at exactly the same "
        "pixel position, size and count. This is a material and lighting pass only: make every surface real, do not redesign, "
        "do not add or remove anything. Closed doors stay closed; glass only where the light-blue panes are." + car_line + "\n\n"
        + (f"IMAGE 2 is the approved render of this same space from another camera. Every object, material, colour, fitting and "
           f"the light must look EXACTLY like in IMAGE 2 (same pendants, same cabinet fronts, same stone, same cushions, same "
           f"time of day). Take geometry and camera ONLY from IMAGE 1, never from IMAGE 2."
           + (" IMAGE 2 shows a parked car - ignore it: this view has NO car." if (cam["room"] == "R_garage" and not car_on) else "")
           + "\n\n" if hero else "")
        + ("IMAGE 2 is the client's MOOD REFERENCE for this room: copy ONLY its look - the material character, colour palette, "
           "finish quality and the warm LED lighting mood. NEVER copy its layout, furniture, objects, windows, camera or proportions: "
           "every object and its position come ONLY from IMAGE 1.\n\n" if mood else "")
        + f"Locked and visible: openings: {open_txt}; furniture: {inv or 'none'}.\n"
        f"Materials, as coloured in IMAGE 1 (identical in every view of this house): {'; '.join(mat_lines)}.\n"
        + ("Light fittings: ONLY those modelled in IMAGE 1 - every thin glowing white line is a warm 2700K LED (seams between the walnut "
           "facets, coves, wall lines, under-counter strips), a white ring on a wall is a slim circular LED ring around a round mirror, "
           "black cylinders hanging on cables are slim black pendants, black cylinders on the nightstands are small table lamps. Add no "
           "other fittings, no spotlights, no downlights, no track lights. Decor: only the modelled objects (beige spheres = dried pampas "
           "plumes, green sphere on a trunk = sculptural ficus tree, small white spheres = dried gypsophila); add no new objects.\n"
           if upper else
           "Light fittings: ONLY those modelled in IMAGE 1 - the glowing white lines are warm 2700K LED lines, the white rings are "
           "crystal ring chandeliers, the thin bars hanging on cables are linear bronze pendants. Add no other fittings, no spotlights, "
           "no track lights. Decor: only the modelled objects (green spheres = olive foliage/branches, white small spheres = orchids or "
           "coral, yellow = lemons); add no new objects.\n") +
        f"Time of day: {g['time_of_day_upper'] if upper else g['time_of_day']}. Room mood: {room['retexture']['light']}.\n"
        f"Exterior: {g['exterior_upper'] if upper else g['exterior']}\n"
        + (f"Specific to this view: {cam['notes']}\n" if cam.get("notes") and not (cam["room"] == "R_garage" and not car_on) else "") +
        "High-end interior photography, 24mm tilt-shift, perfectly vertical verticals, photorealistic global illumination, "
        "real material micro-detail. No people, no text, no extra furniture, no extra openings."
    )
    checklist = dict(camera=cam_full, room=cam["room"], hero=hero, mood=mood, materials=[m for m, n in seen if n > W * H * 0.0008], car=car_on if cam["room"] == "R_garage" else None,
                     openings=openings, furniture_counts=dict(counts), items=items,
                     manual_checks=[
                         "camera position/angle/framing identical to blockout (compare overlay)",
                         "every opening listed is present, same position/size; NO extra window/door",
                         "every furniture count matches exactly; positions & orientation match",
                         "ceiling heights match (double height only over living)",
                         "daylight comes from the visible openings only, direction consistent",
                         "style matches design system for this room; photoreal, no AI artefacts",
                         "CONSISTENCY: every shared object/material/fitting/light matches the hero render of this space",
                         "no light fittings or decor objects beyond those modelled",
                     ])
    open(os.path.join(out, "prompt.txt"), "w").write(prompt)
    json.dump(checklist, open(os.path.join(out, "checklist.json"), "w"), indent=1)
    print(prompt)
    print("\nCHECKLIST counts:", dict(counts), "| openings:", [o["id"] for o in openings])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
