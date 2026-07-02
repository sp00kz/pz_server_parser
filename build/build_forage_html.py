#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild

items = pzschema.records('forage')

NAV = pzbuild.nav('foraging.html')

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid foraging: natural forageables (berries, mushrooms, herbs, fruit, vegetables) with zones, seasons, level needed, amount, XP and poison flags. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, foraging, berries, mushrooms, herbs, poison, wild plants">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Foraging">
<meta property="og:description" content="Project Zomboid foraging: natural forageables (berries, mushrooms, herbs, fruit, vegetables) with zones, seasons, level needed, amount, XP and poison flags. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Foraging (Build 42.19.0)</title>
<style>
  :root { --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4; --muted:#9b8f76;
    --accent:#c9a14a; --green:#6fae4f; --red:#c5564b; --blue:#5a8fb0; --hdr:#241f17; }
  * { box-sizing:border-box; }
  html, body { height:100%; }
  body { margin:0; font:14px/1.4 "Segoe UI",system-ui,sans-serif; background:var(--bg); color:var(--txt);
         display:flex; flex-direction:column; overflow:hidden; }
  header { padding:16px 20px; border-bottom:1px solid var(--line); background:var(--panel); flex:none; }
  h1 { margin:0 0 4px; font-size:20px; color:var(--accent); letter-spacing:.5px; }
  .sub { color:var(--muted); font-size:12px; }
  nav { margin-bottom:8px; font-size:13px; }
  nav a { color:var(--muted); text-decoration:none; padding:3px 9px; border:1px solid var(--line); border-radius:6px; margin-right:6px; }
  nav a.active { color:var(--accent); border-color:var(--accent); }
  nav a:hover { color:var(--txt); }
  .controls { display:flex; gap:10px; flex-wrap:wrap; align-items:center; padding:12px 20px;
              background:var(--panel); border-bottom:1px solid var(--line); flex:none; }
  input[type=search], select { background:var(--bg); color:var(--txt); border:1px solid var(--line);
              border-radius:6px; padding:7px 10px; font-size:13px; }
  input[type=search] { min-width:180px; }
  .count { color:var(--muted); font-size:12px; margin-left:auto; }
  .wrap { flex:1; overflow:auto; padding:0 12px; }
  table { border-collapse:collapse; width:100%; min-width:920px; }
  th, td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); }
  th:hover { color:var(--txt); }
  th.sorted-asc::after { content:" \25B2"; color:var(--accent); }
  th.sorted-desc::after { content:" \25BC"; color:var(--accent); }
  tbody tr:hover { background:#241f17; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  .name { font-weight:600; }
  .poison { color:var(--red); margin-left:5px; cursor:help; }
  .tag { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; background:#2a3340; color:var(--blue); }
  .z { display:inline-block; padding:1px 6px; margin:1px 2px; border-radius:8px; font-size:11px; background:#2a3a22; color:var(--green); }
  .z.Town,.z.TrailerPark { background:#332a22; color:var(--accent); }
  .best { color:var(--green); }
  .no { color:#5a5346; }
  footer { padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Foraging</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>lua/shared/Foraging/Categories/*.lua</code>. The game's ~18 spawn zones are generalised into broad areas. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by item name…" autocomplete="off">
  <select id="cat"><option value="">All categories</option></select>
  <select id="zone"><option value="">Any area</option></select>
  <select id="lvl"><option value="">Any level</option></select>
  <label class="sub"><input type="checkbox" id="nopoison"> hide poisonous</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="tbl"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  <b>Found in</b> = generalised areas (the game's Forest/DeepForest/Birch/etc. all roll up to <b>Forest</b>; FarmLand→<b>Farmland</b>; roads/trails→<b>Roadside</b>, etc.).
  <b>Season</b> = months it can appear · <b>Best</b> = peak months · <b>Lvl</b> = Foraging level needed to find it · <b>Amount</b> per find · <b>XP</b> per item.
  ☠ = can be poisonous (identify it before eating). Town-scavenge clutter (junk, clothing, ammo) is omitted — this lists natural forageables.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
const ZONES = ['Forest','Vegetation','Farmland','Roadside','Town','Trailer Park'];
const COLS = [
  {k:'name', t:'Item', fmt:(v,d)=>`<span class="name">${wl(v)}</span>${d.poison?'<span class="poison" title="Can be poisonous">\u2620</span>':''}`},
  {k:'category', t:'Category', fmt:v=>`<span class="tag">${esc(v)}</span>`},
  {k:'zones', t:'Found in', fmt:v=>v.map(z=>`<span class="z ${esc(z).replace(' ','')}">${esc(z)}</span>`).join('')},
  {k:'season', t:'Season', fmt:v=>esc(v)||'<span class="no">\u2013</span>'},
  {k:'best', t:'Best', fmt:v=>v?`<span class="best">${esc(v)}</span>`:'<span class="no">\u2013</span>'},
  {k:'skill', t:'Lvl', num:true, fmt:v=>v||'<span class="no">any</span>'},
  {k:'_amt', t:'Amount', num:true, get:d=>d.max, fmt:(v,d)=>d.min===d.max?`${d.min}`:`${d.min}\u2013${d.max}`},
  {k:'xp', t:'XP', num:true, fmt:v=>v==null?'<span class="no">\u2013</span>':v},
];
function fill(sel,vals){vals.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});}
fill(document.getElementById('cat'), [...new Set(DATA.map(d=>d.category))].sort());
fill(document.getElementById('zone'), ZONES);
fill(document.getElementById('lvl'), Array.from({length:11},(_,i)=>i));
__TABLE_JS__
buildTable({
  data:DATA, cols:COLS, sortKey:'category', sortDir:1, countNoun:'items',
  tiebreak:(a,b)=>a.name.localeCompare(b.name),
  filters:[
    {id:'q', test:(d,v)=>!v||d.name.toLowerCase().includes(v.toLowerCase())},
    {id:'cat', test:(d,v)=>!v||d.category===v},
    {id:'zone', test:(d,v)=>!v||d.zones.includes(v)},
    {id:'lvl', test:(d,v)=>v===''||v==null||d.skill<=+v},
    {id:'nopoison', test:(d,v)=>!v||!d.poison},
  ],
});
</script></body></html>'''
data_js = pzenv.embed_json(items)
html = html.replace('__NAV__', NAV).replace('__DATA__', data_js).replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK)
open(pzenv.REPO + '/foraging.html', 'w', encoding='utf-8').write(html)
print(f"Wrote foraging.html ({len(html)} bytes, {len(items)} items)")
