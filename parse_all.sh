#!/usr/bin/env bash
# Snapshot the previous data, then re-parse all datasets from the game files.
set -euo pipefail
cd "$(dirname "$0")"; source ./config.sh
echo "[parse] snapshot previous -> work/prev/"
mkdir -p "$WORK/prev"; cp "$WORK"/*.json "$WORK/prev/" 2>/dev/null || true
for k in seeds vehicles animals guns melee tools recipes food forage xp fishing; do
  printf "  parse %-9s -> %s.json\n" "$k" "$k"
  $PY "parse/parse_$k.py" > "$WORK/$k.json.tmp" && mv "$WORK/$k.json.tmp" "$WORK/$k.json"
done
echo "[parse] validating against pzschema"
$PY "$TOOLS/validate_schema.py" || { echo "!! schema validation FAILED — a dataset shape changed; update pzschema/schema.py"; exit 1; }
echo "[parse] done"
