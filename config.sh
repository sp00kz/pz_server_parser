#!/usr/bin/env bash
# Central config for the PZ reference build tooling (lives OUTSIDE the published
# repo on purpose). Everything auto-detects with portable defaults; override any
# value by exporting it before you run, e.g.  export PZ_MEDIA=/path/to/.../media
#
# Python scripts resolve the same values via pzenv.py (these exports take
# precedence over its auto-detection).

# This tooling dir + its intermediates (auto: relative to this file)
export TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WORK="${WORK:-$TOOLS/work}"

# The published site (git repo). Default: sibling "pz_server"; override with PZ_REPO.
export REPO="${PZ_REPO:-$(cd "$TOOLS/.." && pwd)/pz_server}"
export PZ_REPO="$REPO"

# Installed game media dir (Steam). Auto-detect common Linux / WSL locations.
if [ -z "${PZ_MEDIA:-}" ]; then
  for c in \
    /mnt/*/"program files (x86)"/steam/steamapps/common/ProjectZomboid/media \
    /mnt/*/"Program Files (x86)"/Steam/steamapps/common/ProjectZomboid/media \
    /mnt/*/SteamLibrary/steamapps/common/ProjectZomboid/media \
    "$HOME"/.steam/steam/steamapps/common/ProjectZomboid/media \
    "$HOME"/.local/share/Steam/steamapps/common/ProjectZomboid/media ; do
    [ -d "$c" ] && export PZ_MEDIA="$c" && break
  done
fi
case "${PZ_MEDIA:-}" in
  */steamapps/*) export PZ_STEAMAPPS="${PZ_MEDIA%%/steamapps/*}/steamapps"
                 export PZ_WORKSHOP="$PZ_STEAMAPPS/workshop/content/108600" ;;
esac

# Browser UA needed to pass pzwiki's Cloudflare for the link audit
export PZ_UA="${PZ_UA:-Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36}"

export PY="${PY:-python3}"
