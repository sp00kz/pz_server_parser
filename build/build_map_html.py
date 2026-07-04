#!/usr/bin/env python3
"""Map page (map.html): embeds the interactive PZ map, pre-loaded with the mod maps
detected among the *already-parsed* installed mods.

Detection adds no new directory walk — it reuses pzmods.mod_media_roots() (the mod
media dirs the parser already enumerates) and only does a sub-dir check for `maps/`,
matching the mod by its Workshop id (taken from the WORKSHOP/<id>/... path). Maps whose
Workshop id is in SUPPORTED (the set whose tiles map.projectzomboid.com hosts) are
enabled in the embedded viewer via its ?mods= parameter."""
import os, sys, glob
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import pzenv, pzbuild

MAP_URL = 'https://sp00kz.github.io/pz_map/'
# Workshop id -> map id in the hosted viewer (the mod maps whose tiles the PZ map CDN serves).
SUPPORTED = {
    '3484263516': 'RavenCreek', '2463499011': 'Grapeseed', '3037854728': 'Tikitown',
    '3480990544': 'Constown', '3476333350': 'EchoCreekMB', '3134394569': 'Taylorsville',
    '3493916941': 'Ashenwood', '2934132344': 'LVQZ', '3644794945': 'Maplewood',
    '3666180085': 'Dawntown',
}


def _has_map(moddir):
    """True if an installed mod contains a rendered map — a `maps/` dir (any case, any media
    layout) holding a cell .lotheader. Prunes before descending the large tile tree."""
    for root, dirs, _ in os.walk(moddir):
        if os.path.basename(root).lower() == 'maps':
            hit = any(glob.glob(os.path.join(root, d, '*.lotheader')) for d in dirs)
            dirs[:] = []          # don't walk into the map's huge lotheader/tile contents
            if hit:
                return True
    return False


def detected_maps():
    """Viewer map ids for supported mod maps that are installed — a bounded `maps/` sub-dir
    check inside each supported mod's already-parsed Workshop folder (WORKSHOP/<id>/...)."""
    ws = pzenv.WORKSHOP
    found = []
    if not ws or not os.path.isdir(ws):
        return found
    for wsid, mid in SUPPORTED.items():
        mod = os.path.join(ws, wsid)
        if os.path.isdir(mod) and _has_map(mod):
            found.append(mid)
    return found


mods = detected_maps()
src = MAP_URL + ('?mods=' + ','.join(mods) if mods else '')
sub = (f'Vanilla Knox County + {len(mods)} detected mod map{"" if len(mods) == 1 else "s"}: '
       + ', '.join(mods)) if mods else 'Vanilla Knox County — no supported mod maps installed'

html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project Zomboid — Interactive Map</title>
<meta name="description" content="Interactive isometric Project Zomboid map (Build 42): vanilla Knox County plus installed mod maps, with buildings coloured by loot type.">
{pzbuild.AUTHOR_META}
<style>
  :root {{ --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4; --muted:#9b8f76; --accent:#c9a14a; }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; height:100%; }}
  body {{ display:flex; flex-direction:column; font:14px/1.4 "Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--txt); }}
  header {{ padding:16px 20px; border-bottom:1px solid var(--line); background:var(--panel); flex:none; }}
  nav {{ margin-bottom:8px; font-size:13px; }}
  nav a {{ color:var(--muted); text-decoration:none; padding:3px 9px; border:1px solid var(--line); border-radius:6px; margin-right:6px; }}
  nav a.active {{ color:var(--accent); border-color:var(--accent); }}
  nav a:hover {{ color:var(--txt); }}
  h1 {{ margin:0 0 4px; font-size:20px; color:var(--accent); letter-spacing:.5px; }}
  .sub {{ color:var(--muted); font-size:12px; }}
  iframe {{ flex:1; width:100%; border:none; background:#0c0e11; }}
</style></head><body>
<header>__NAV__
  <h1>Interactive Map</h1>
  <div class="sub">{sub}</div>
</header>
<iframe src="{src}" title="Project Zomboid interactive map" loading="lazy"></iframe>
</body></html>'''

html = html.replace('__NAV__', pzbuild.nav('map.html'))
out = pzenv.REPO + '/map.html'
os.makedirs(pzenv.REPO, exist_ok=True)
open(out, 'w', encoding='utf-8').write(html)
print(f"Wrote {out} ({len(html)} bytes) — detected maps: {mods or 'none'}")
