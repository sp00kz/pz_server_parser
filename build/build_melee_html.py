#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild

melee = pzschema.records('melee')

NAV = pzbuild.nav('melee.html')

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid melee weapons: damage, DPS, reach, swing speed, crit, knockdown and durability. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, melee weapons, damage, dps, reach, durability">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Melee Weapons">
<meta property="og:description" content="Project Zomboid melee weapons: damage, DPS, reach, swing speed, crit, knockdown and durability. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Melee Weapons (Build 42.19.0)</title>
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
  input[type=search] { min-width:200px; }
  .count { color:var(--muted); font-size:12px; margin-left:auto; }
  .wrap { flex:1; overflow:auto; padding:0 12px; }
  table { border-collapse:collapse; width:100%; min-width:1050px; }
  th, td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); }
  th:hover { color:var(--txt); }
  th.sorted-asc::after { content:" \25B2"; color:var(--accent); }
  th.sorted-desc::after { content:" \25BC"; color:var(--accent); }
  tbody tr:hover { background:#241f17; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  .name { font-weight:600; }
  .tag { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; background:#2a3340; color:var(--blue); }
  .tag.Axe { background:#3a2a22; color:var(--accent); }
  .tag.LongBlade,.tag.ShortBlade { background:#2a3a22; color:var(--green); }
  .tag.LongBlunt,.tag.ShortBlunt { background:#3a2a40; color:#b98fd0; }
  .tag.Spear { background:#22323a; color:var(--blue); }
  .tag.Improvised,.tag.Unarmed { background:#2a2620; color:var(--muted); }
  .bar { display:inline-block; height:8px; background:var(--accent); border-radius:2px; vertical-align:middle; opacity:.7; margin-left:4px; }
  .yes { color:var(--green); } .no { color:#5a5346; }
  footer { padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Melee Weapons</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>scripts/generated/items/weapon.txt</code>. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by weapon name…" autocomplete="off">
  <select id="cat"><option value="">All types</option></select>
  <label class="sub"><input type="checkbox" id="noimp"> hide improvised</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="tbl"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  <b>Damage</b> min–max per hit · <b>DPS</b> = avg damage ÷ swing time (higher = better) · <b>Range</b> reach in tiles ·
  <b>Swing</b> seconds per attack (lower = faster; drops toward its minimum as your skill rises) · <b>Hits</b> max zombies per swing ·
  <b>Crit%</b> critical chance · <b>Knock</b> knockdown modifier · <b>Durab</b> ≈ hits before breaking (ConditionMax × condition-loss rarity) ·
  <b>Door / Tree</b> damage to doors / trees · <b>2H</b> two-handed. Damage is base, before the matching skill bonus.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
const f = v => v==null ? '<span class="no">–</span>' : (Number.isInteger(v) ? v : Math.round(v*100)/100);
const COLS = [
  {k:'name', t:'Weapon', fmt:v=>`<span class="name">${wl(v)}</span>`},
  {k:'category', t:'Type', fmt:v=>`<span class="tag ${esc(v).replace(' ','')}">${esc(v)}</span>`},
  {k:'maxDmg', t:'Damage', num:true, fmt:(v,d)=>{let h=`${f(d.minDmg)}\u2013${f(d.maxDmg)}`;if(v!=null){const w=Math.round(40*v/maxDmg);h+=`<span class="bar" style="width:${w}px"></span>`;}return h;}},
  {k:'dps', t:'DPS', num:true, fmt:f},
  {k:'range', t:'Range', num:true, fmt:f},
  {k:'swing', t:'Swing', num:true, fmt:f},
  {k:'hits', t:'Hits', num:true, fmt:f},
  {k:'crit', t:'Crit %', num:true, fmt:f},
  {k:'knock', t:'Knock', num:true, fmt:f},
  {k:'durab', t:'Durab', num:true, fmt:f},
  {k:'door', t:'Door', num:true, fmt:f},
  {k:'tree', t:'Tree', num:true, fmt:f},
  {k:'twoH', t:'2H', fmt:v=>v?'<span class="yes">\u2713</span>':'<span class="no">\u2013</span>'},
  {k:'weight', t:'Wt', num:true, fmt:f},
];
const maxDmg=Math.max(...DATA.map(d=>d.maxDmg||0));
function fill(sel,vals){vals.forEach(v=>{if(v==null)return;const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});}
fill(document.getElementById('cat'), [...new Set(DATA.map(d=>d.category))].sort());
__TABLE_JS__
buildTable({
  data:DATA, cols:COLS, sortKey:'avg', sortDir:-1, countNoun:'weapons',
  filters:[
    {id:'q', test:(d,v)=>!v||d.name.toLowerCase().includes(v.toLowerCase())},
    {id:'cat', test:(d,v)=>!v||d.category===v},
    {id:'noimp', test:(d,v)=>!v||d.category!=='Improvised'},
  ],
});
</script></body></html>'''
data_js = pzenv.embed_json(melee)
html = html.replace('__NAV__', NAV).replace('__DATA__', data_js).replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK)
open(pzenv.REPO + '/melee.html', 'w', encoding='utf-8').write(html)
print(f"Wrote melee.html ({len(html)} bytes, {len(melee)} weapons)")
