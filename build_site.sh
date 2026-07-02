#!/usr/bin/env bash
# Generate every HTML page (+ thumbnails + service worker) into the repo.
# Uses the EXISTING work/linkmap.json (run refresh_links.sh first if items changed).
set -euo pipefail
cd "$(dirname "$0")"; source ./config.sh
[ -f "$WORK/linkmap.json" ] || { echo "!! work/linkmap.json missing — run refresh_links.sh first"; exit 1; }
for b in build_html build_cars_html build_livestock_html build_guns_html build_melee_html \
         build_tools_html build_crafting build_food_html build_forage_html build_xp_html build_fishing_html; do
  printf "  build %s\n" "$b"; $PY "build/$b.py" >/dev/null
done
$PY build/build_thumbs.py
$PY build/build_sw.py
python3 build_index.py
$PY build_sitemap.py
echo "[build] site written to $REPO"
