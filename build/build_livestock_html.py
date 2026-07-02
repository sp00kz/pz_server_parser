#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild

animals = pzschema.records('animals')

NAV = pzbuild.nav('livestock.html')

EMOJI = {'cow':'🐄','pig':'🐖','sheep':'🐑','chicken':'🐔','turkey':'🦃','rabbit':'🐇'}
import re as _re, urllib.parse as _up, html as _html
def esc(x):
    return _html.escape(str(x)) if x is not None else x
_LINKMAP = json.load(open(pzenv.WORK + '/linkmap.json'))
def wl(v):
    # Python port of pzbuild.WL_FN's wl(): LINKMAP before the '/' split.
    if not v: return v
    s = str(v)
    key = s.strip()
    if key.endswith(')'):
        pi = key.rfind('(')
        if pi > 0: key = key[:pi].strip()
    if key in _LINKMAP:
        url = _LINKMAP[key]
    elif '/' in s:
        return ' / '.join(wl(p.strip()) for p in s.split('/'))
    else:
        url = 'https://pzwiki.net/wiki/' + _up.quote(key.replace(' ', '_'))
    if not url: return esc(v)
    return f'<a class="wk" target="_blank" rel="noopener" href="{url}">{esc(v)}</a>'
def pct(rng):
    if not rng: return '<span class="no">–</span>'
    return f'{round(rng[0]*100)}–{round(rng[1]*100)}%'
def prod_badges(ps):
    return ''.join(f'<span class="prod p{p}">{p}</span>' for p in ps)

GENE_COLS = [('meatRatio','Meat ratio'),('maxMilk','Milk'),('maxWeight','Weight'),('maxWool','Wool')]

rows = []
for s in animals:
    em = EMOJI.get(s['key'],'')
    gest = (f"{s['gestation']} d" if s['gestation'] else ('Lays eggs' if 'Eggs' in s['products'] else '–'))
    breed_names = ', '.join(wl(b['name']) for b in s['breeds'])
    # species genes when breeds share genes
    sp_genes = s['breeds'][0]['genes'] if (not s['breedsDiffer'] and s['breeds'] and s['breeds'][0]['genes']) else None
    note = '' if s['breedsDiffer'] else (f'<div class="bn">Breeds: {breed_names}</div>' if breed_names else '')
    gene_cells = ''.join(f'<td class="num">{pct(sp_genes.get(g) if sp_genes else None)}</td>' for g,_ in GENE_COLS)
    rows.append(f'''<tr class="sp">
      <td><span class="name">{em} {wl(s['name'])}</span>{note}</td>
      <td>{prod_badges(s['products'])}</td>
      <td class="num">{s['matures']} d</td>
      <td class="num">{gest}</td>
      <td class="num">{s['trailer']}</td>
      <td>{esc(s['temperament'])}</td>
      {gene_cells}
    </tr>''')
    if s['breedsDiffer']:
        for b in s['breeds']:
            gc = ''.join(f'<td class="num">{pct(b["genes"].get(g))}</td>' for g,_ in GENE_COLS)
            rows.append(f'''<tr class="breed">
      <td><span class="bname">↳ {wl(b['name'])}</span></td>
      <td colspan="5" class="bd">breed variant — gene tendencies →</td>
      {gc}
    </tr>''')

THEAD = '<tr><th>Animal</th><th>Products</th><th>Matures</th><th>Gestation</th><th>Trailer size</th><th>Temperament</th>' + ''.join(f'<th class="r">{t}</th>' for _,t in GENE_COLS) + '</tr>'

html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid livestock reference: products, maturation, gestation, trailer size, temperament and breed gene tendencies. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, livestock, animals, cow, pig, sheep, chicken, breeds, farming">
<meta name="robots" content="index, follow">
{pzbuild.AUTHOR_META}
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Livestock">
<meta property="og:description" content="Project Zomboid livestock reference: products, maturation, gestation, trailer size, temperament and breed gene tendencies. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Livestock (Build 42.19.0)</title>
<style>
  :root {{ --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4; --muted:#9b8f76;
    --accent:#c9a14a; --green:#6fae4f; --blue:#5a8fb0; --hdr:#241f17; }}
  * {{ box-sizing:border-box; }}
  html, body {{ height:100%; }}
  body {{ margin:0; font:14px/1.4 "Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--txt);
         display:flex; flex-direction:column; overflow:hidden; }}
  header {{ padding:16px 20px; border-bottom:1px solid var(--line); background:var(--panel); flex:none; }}
  h1 {{ margin:0 0 4px; font-size:20px; color:var(--accent); letter-spacing:.5px; }}
  .sub {{ color:var(--muted); font-size:12px; }}
  nav {{ margin-bottom:8px; font-size:13px; }}
  nav a {{ color:var(--muted); text-decoration:none; padding:3px 9px; border:1px solid var(--line); border-radius:6px; margin-right:6px; }}
  nav a.active {{ color:var(--accent); border-color:var(--accent); }}
  nav a:hover {{ color:var(--txt); }}
  .wrap {{ flex:1; overflow:auto; padding:8px 16px 30px; }}
  table {{ border-collapse:collapse; width:100%; min-width:900px; }}
  th, td {{ padding:8px 12px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }}
  th {{ position:sticky; top:0; background:var(--hdr); font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); }}
  th.r {{ text-align:right; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  tr.sp {{ background:#1b1711; }}
  tr.sp td {{ border-top:2px solid var(--line); }}
  tr.breed td {{ background:#161310; color:var(--muted); }}
  .name {{ font-weight:700; font-size:15px; }}
  .bname {{ color:var(--blue); padding-left:14px; }}
  .bn {{ color:var(--muted); font-size:11px; margin-top:2px; }}
  .bd {{ color:#6f6450; font-size:11px; font-style:italic; }}
  .prod {{ display:inline-block; padding:1px 7px; margin:1px 2px; border-radius:10px; font-size:11px; background:#2a3340; color:var(--blue); }}
  .prod.pMeat {{ background:#3a2422; color:#d08a7a; }}
  .prod.pMilk {{ background:#2f3340; color:#cdd6e6; }}
  .prod.pEggs {{ background:#3a3422; color:var(--accent); }}
  .prod.pWool {{ background:#2a3a2a; color:var(--green); }}
  .prod.pLeather {{ background:#332a22; color:#c9a14a; }}
  .prod.pFeathers {{ background:#2a3340; color:var(--blue); }}
  .prod.pManure {{ background:#26221c; color:#8a7a5a; }}
  .no {{ color:#5a5346; }}
  .wk {{ color:inherit; text-decoration:none; border-bottom:1px dotted #6b5f48; }}
  .wk:hover {{ color:var(--accent); border-bottom-color:var(--accent); }}
  footer {{ padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }}
  code {{ color:var(--accent); }}
</style></head><body>
<header>{NAV}
  <h1>Project Zomboid — Livestock</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>lua/shared/Definitions/animal/*Definitions.lua</code>. Breeds shown as sub-rows only when their stats differ.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="wrap"><table><thead>{THEAD}</thead><tbody>
{''.join(rows)}
</tbody></table></div>
<footer>
  <b>Matures</b> = days for a newborn to reach adult size · <b>Gestation</b> = pregnancy length (birds lay eggs instead) ·
  <b>Trailer size</b> = space an adult occupies in an animal trailer (bigger = fewer fit) ·
  <b>Meat ratio / Milk / Weight / Wool</b> = breed gene tendencies (relative %, higher = more). Breeds with identical genes are listed on the species row.
{pzbuild.TOOL_LINK}</footer>
</body></html>'''
open(pzenv.REPO + '/livestock.html','w',encoding='utf-8').write(html)
print(f"Wrote livestock.html ({len(html)} bytes, {len(animals)} species, {sum(1 for s in animals if s['breedsDiffer'])} with breed sub-rows)")
