#!/usr/bin/env python3
"""Landing page (index.html): short description + links into each section."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pzenv, pzbuild

DESC = {
 'map.html':       'Interactive isometric map — vanilla Knox County plus installed mod maps, buildings coloured by loot type.',
 'seeds.html':     'Crop growth time, water needs, sow months and yields.',
 'cars.html':      'Speed, engine, trunk and seats — base game plus Workshop mods.',
 'livestock.html': 'Animals, breeds, products and gestation.',
 'guns.html':      'Damage, range, attachments and durability.',
 'melee.html':     'Damage, DPS, reach, knockdown and durability.',
 'tools.html':     'What each tool does and how long it lasts.',
 'crafting.html':  'Recipes, XP, and the no-waste crafting cycles worth running.',
 'food.html':      'Calories, nutrition, mood effect and spoilage.',
 'foraging.html':  'What you can forage, where and when — and what is poisonous.',
 'fishing.html':   'Every fish: best bait, size and weight, and the level needed.',
 'actions.html':   'XP gained from in-world actions, by skill.',
}
sections = [(h, l) for h, l in pzbuild.NAV_TABS if h != 'index.html']
cards = '\n'.join(
    f'  <a class="card" href="{h}"><span class="ct">{l}</span>'
    f'<span class="cd">{DESC.get(h,"")}</span></a>' for h, l in sections)

META = ('Project Zomboid Build 42 reference: sortable tables for vehicles, weapons, '
        'crafting, food, farming and foraging, read straight from the game files. '
        'Game version 42.19.0 (unstable branch, 2026-06-01).')

html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project Zomboid Reference (Build 42.19.0)</title>
<meta name="description" content="{META}">
<meta name="keywords" content="Project Zomboid, Build 42, B42, reference, vehicles, weapons, crafting, food, farming, foraging">
<meta name="robots" content="index, follow">
{pzbuild.AUTHOR_META}
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Reference — Build 42.19.0">
<meta property="og:description" content="{META}">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<style>
  :root {{ --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4; --muted:#9b8f76;
    --accent:#c9a14a; --green:#6fae4f; --blue:#5a8fb0; --hdr:#241f17; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.4 "Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--txt); }}
  header {{ padding:16px 20px; border-bottom:1px solid var(--line); background:var(--panel); }}
  nav {{ margin-bottom:8px; font-size:13px; }}
  nav a {{ color:var(--muted); text-decoration:none; padding:3px 9px; border:1px solid var(--line); border-radius:6px; margin-right:6px; }}
  nav a.active {{ color:var(--accent); border-color:var(--accent); }}
  nav a:hover {{ color:var(--txt); }}
  h1 {{ margin:0 0 4px; font-size:20px; color:var(--accent); letter-spacing:.5px; }}
  .sub {{ color:var(--muted); font-size:12px; }}
  main {{ max-width:1000px; margin:0 auto; padding:22px 20px; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:12px; }}
  .card {{ display:block; background:var(--panel); border:1px solid var(--line); border-radius:8px;
           padding:13px 15px; text-decoration:none; }}
  .card:hover {{ border-color:var(--accent); }}
  .ct {{ display:block; color:var(--accent); font-weight:600; font-size:15px; }}
  .cd {{ display:block; color:var(--muted); font-size:12.5px; margin-top:4px; }}
  footer {{ max-width:1000px; margin:0 auto; padding:14px 20px 30px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); text-align:center; }}
  footer b {{ color:var(--accent); }}
  code {{ color:var(--accent); }}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid Reference</h1>
  <div class="sub">Build 42.19.0 · parsed from the game files</div>
</header>
<main>
  <div class="cards">
{cards}
  </div>
</main>
<footer>
  <div>Game data: <b>Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01.</div>
  <div style="margin-top:5px">Stats parsed from the game's <code>scripts/</code> and <code>lua/</code> files. Vehicle images from the PZ Wiki and Steam Workshop; modded vehicles link to their Workshop page.</div>
{pzbuild.TOOL_LINK}</footer>
</body></html>'''

html = html.replace('__NAV__', pzbuild.nav('index.html'))
out = pzenv.REPO + '/index.html'
open(out, 'w', encoding='utf-8').write(html)
print(f"Wrote {out} ({len(html)} bytes, {len(sections)} section links)")
