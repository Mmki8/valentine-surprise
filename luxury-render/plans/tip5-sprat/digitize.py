"""House type 5, first floor (OSNOVA SPRATA, source/floorplan_sprat.png = client sheet 27.png).

Both floors of type 5 live in ONE model, built by ../tip5-prizemlje/digitize.py (first-floor elements: level "upper",
floor at FL = 310 cm, ceiling 590 cm; sheet px shifted by (+1, +28) onto the ground sheet - the two sheets share the
1.313 cm/px scale, the outer walls, the stair and the master/bedroom party wall). This script rebuilds that model and
copies plan.json here so the first-floor cameras render against exactly the same geometry as the ground floor.
"""
import os, shutil, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
ground = os.path.join(here, "..", "tip5-prizemlje")
subprocess.run([sys.executable, "digitize.py"], cwd=ground, check=True)
shutil.copy(os.path.join(ground, "plan.json"), os.path.join(here, "plan.json"))
print("copied plan.json (ground + first floor) ->", here)
