#!/usr/bin/env bash
# Run the geometry gate for a finished Higgsfield job INSIDE the Higgsfield
# sandbox (it can reach the result CDN). Prints the verdict and writes small
# JPEG previews (render + overlay) for visual review.
#   bash qa/sandbox_check.sh <CAM> <label> <job_id> <result_url>
set -euo pipefail
cd "$(dirname "$0")/.."
CAM=$1; LABEL=$2; JOB=$3; URL=$4
python3 qa/record_attempt.py plans/osnova-prizemlja "$CAM" "$LABEL" "$JOB" "$URL" \
 | python3 -c "import json,sys; d=json.load(sys.stdin); print('ALIGN',d['alignment']); print('STRUCT',d['structural']); print('PASS',d['auto_pass']); [print(' -',f) for f in d['failures']]"
A=$(ls -d output/osnova-prizemlja/$CAM/attempts/* | tail -1)
python3 - "$A" "$CAM" <<'EOF'
import sys
from PIL import Image
a, cam = sys.argv[1], sys.argv[2]
n = a.rstrip('/').split('/')[-1]
Image.open(f"{a}/render.png").convert("RGB").resize((800, 450)).save(f"/home/user/prev/{cam}_{n}_r.jpg", quality=72)
Image.open(f"{a}/overlay.png").convert("RGB").resize((800, 450)).save(f"/home/user/prev/{cam}_{n}_o.jpg", quality=68)
print("PREVIEW", f"/home/user/prev/{cam}_{n}_r.jpg", f"/home/user/prev/{cam}_{n}_o.jpg")
EOF
