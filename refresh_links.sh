#!/usr/bin/env bash
# Re-audit pzwiki links (NETWORK). Incremental: validate.py/resolve_*.py skip
# items already cached in work/resolved.json, so only NEW items are queried.
# Produces work/linkmap.json consumed by the builders.
set -euo pipefail
cd "$(dirname "$0")"; source ./config.sh
$PY links/extract_universe.py
$PY links/validate.py
$PY links/resolve_misses.py
$PY links/resolve_variants.py
$PY build/build_linkmap.py
echo "[links] linkmap refreshed"
