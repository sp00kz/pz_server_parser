#!/usr/bin/env bash
# Full update after a game patch: detect version, re-parse, refresh wiki links,
# rebuild the site, then show what changed. Does NOT commit/push — you review first.
set -euo pipefail
cd "$(dirname "$0")"; source ./config.sh
echo "=== version ==="; $PY version_check.py || true
echo "=== parse ===";   ./parse_all.sh
echo "=== images ==="; $PY fetch_images.py
echo "=== links ===";   ./refresh_links.sh
echo "=== build ===";   ./build_site.sh
echo "=== changes ==="; $PY diff_data.py
cat <<MSG

Review the diff above and spot-check the pages in $REPO.
If good:
  python3 $TOOLS/version_check.py --record     # record the new version
  cd $REPO && git add -A && git commit -m "Update to Build <ver>" && git push
MSG
