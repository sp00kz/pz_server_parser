#!/usr/bin/env bash
# Quick offline regen: re-parse game files + rebuild the site (reuses the
# existing work/linkmap.json — run ./refresh_links.sh first if items changed).
set -euo pipefail
cd "$(dirname "$0")"
./parse_all.sh
./build_site.sh
echo "[rebuild] done — review with: ./pz diff  (then git status in the repo)"
