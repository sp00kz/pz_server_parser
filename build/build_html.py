#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild


seeds = pzschema.records('seeds')
data_js = pzenv.embed_json(seeds)

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid seed and crop reference: growth time, water needs, sow/best/risk months and yields for every crop. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, seeds, crops, farming, growth time, yield, sow months">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Seeds & Crops">
<meta property="og:description" content="Project Zomboid seed and crop reference: growth time, water needs, sow/best/risk months and yields for every crop. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Seed / Crop Table (Build 42.19.0)</title>
<style>
  :root {
    --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4;
    --muted:#9b8f76; --accent:#c9a14a; --green:#6fae4f; --red:#c5564b;
    --blue:#5a8fb0; --hdr:#241f17;
  }
  * { box-sizing:border-box; }
  html, body { height:100%; }
  body { margin:0; font:14px/1.4 "Segoe UI",system-ui,sans-serif;
         background:var(--bg); color:var(--txt);
         display:flex; flex-direction:column; overflow:hidden; }
  header { padding:16px 20px; border-bottom:1px solid var(--line); background:var(--panel); flex:none; }
  h1 { margin:0 0 4px; font-size:20px; color:var(--accent); letter-spacing:.5px; }
  .sub { color:var(--muted); font-size:12px; }
  nav { margin-bottom:8px; font-size:13px; }
  nav a { color:var(--muted); text-decoration:none; padding:3px 9px; border:1px solid var(--line); border-radius:6px; margin-right:6px; }
  nav a.active { color:var(--accent); border-color:var(--accent); }
  nav a:hover { color:var(--txt); }
  .controls { display:flex; gap:10px; flex-wrap:wrap; align-items:center;
              padding:12px 20px; background:var(--panel); border-bottom:1px solid var(--line);
              flex:none; }
  input[type=search], select { background:var(--bg); color:var(--txt);
              border:1px solid var(--line); border-radius:6px; padding:7px 10px; font-size:13px; }
  input[type=search] { min-width:220px; }
  .count { color:var(--muted); font-size:12px; margin-left:auto; }
  .wrap { flex:1; overflow:auto; padding:0 12px; }
  table { border-collapse:collapse; width:100%; min-width:1100px; }
  th, td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted);
       box-shadow:inset 0 -1px 0 var(--line); }
  th:hover { color:var(--txt); }
  th.sorted-asc::after  { content:" \25B2"; color:var(--accent); }
  th.sorted-desc::after { content:" \25BC"; color:var(--accent); }
  tbody tr:hover { background:#241f17; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  .name { font-weight:600; color:var(--txt); }
  .tag { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; }
  .tag.Vegetable { background:#2a3a22; color:var(--green); }
  .tag.Herb { background:#2a3340; color:var(--blue); }
  .mon { font-size:11px; color:var(--muted); }
  .mon b { color:var(--green); }       /* best */
  .mon i { color:var(--accent); font-style:normal; }  /* risk */
  .yes { color:var(--green); font-weight:600; }
  .no { color:#5a5346; }
  .bar { display:inline-block; height:8px; background:var(--accent); border-radius:2px; vertical-align:middle; opacity:.7; }
  footer { padding:14px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style>
</head>
<body>
<header>
  __NAV__
  <h1>Project Zomboid — Seed &amp; Crop Reference</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>farming_vegetableconf_*.lua</code> · growth/rot at default <code>FarmingSpeedNew=1</code>, well-watered. Click any column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by name, seed, produce, month…" autocomplete="off">
  <select id="cat">
    <option value="">All categories</option>
    <option value="Vegetable">Vegetables</option>
    <option value="Herb">Herbs</option>
  </select>
  <select id="month">
    <option value="">Sowable any month</option>
  </select>
  <label class="mon"><input type="checkbox" id="coldOnly"> cold-hardy only</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap">
  <table id="tbl">
    <thead><tr id="hrow"></tr></thead>
    <tbody></tbody>
  </table>
</div>
<footer>
  Months: <b style="color:var(--green)">green=best</b> · <i style="color:var(--accent)">amber=risk</i> · grey=other sow months.
  Growth days = stages &times; timeToGrow &divide; 24. Rot window = (rotTime or timeToGrow/2) &divide; 24.
  Yield is the base min–max veg before skill/sandbox modifiers.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
const COLS = [
  {k:'name', t:'Name', cls:'name', fmt:v=>wl(v)},
  {k:'category', t:'Type', fmt:v=>`<span class="tag ${esc(v)}">${esc(v)}</span>`},
  {k:'seed', t:'Seed item'},
  {k:'produce', t:'Produce'},
  {k:'yield', t:'Yield', num:true, get:d=>d.yieldMin, fmt:(v,d)=>`${d.yieldMin}\u2013${d.yieldMax}`},
  {k:'growthDays', t:'Growth (days)', num:true, fmt:(v,d)=>{if(v==null)return '\u2013';const w=Math.round(40*v/maxGrowth);return `${v} <span class="bar" style="width:${w}px"></span>`;}},
  {k:'stages', t:'Stages', num:true},
  {k:'timeToGrow', t:'h/stage', num:true},
  {k:'rotDays', t:'Rot win (d)', num:true, fmt:v=>v==null?'\u2013':v},
  {k:'waterLvl', t:'Water lvl', num:true},
  {k:'sow', t:'Sow months', get:d=>d.sow.length?monthIdx(d.sow[0]):99, fmt:(v,d)=>monthsHtml(d)},
  {k:'coldHardy', t:'Cold-hardy', get:d=>d.coldHardy?1:0, fmt:v=>v?'<span class="yes">\u2713</span>':'<span class="no">\u00b7</span>'},
  {k:'scythe', t:'Scythe', get:d=>d.scythe?1:0, fmt:v=>v?'<span class="yes">\u2713</span>':'<span class="no">\u00b7</span>'},
];
const MO = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const MO_FULL = ['January','February','March','April','May','June','July','August','September','October','November','December'];
function monthIdx(m){return MO.indexOf(m);}
const monthSel=document.getElementById('month');
MO.forEach((m,i)=>{const o=document.createElement('option');o.value=m;o.textContent='Sowable in '+MO_FULL[i];monthSel.appendChild(o);});
function monthsHtml(d){
  if(!d.sow.length) return '<span class="mon">\u2013</span>';
  const best=new Set(d.best), risk=new Set(d.risk);
  return '<span class="mon">'+d.sow.map(m=>{
    if(best.has(m)) return '<b>'+m+'</b>';
    if(risk.has(m)) return '<i>'+m+'</i>';
    return m;
  }).join(' ')+'</span>';
}
const maxGrowth=Math.max(...DATA.map(d=>d.growthDays||0));
__TABLE_JS__
buildTable({
  data:DATA, cols:COLS, sortKey:'name', sortDir:1, countNoun:'seeds', pickDir:()=>1,
  filters:[
    {id:'q', test:(d,v)=>{if(!v)return true;const mw=d.sow.map(m=>m+' '+MO_FULL[monthIdx(m)]).join(' ');return (d.name+' '+d.seed+' '+d.produce+' '+mw).toLowerCase().includes(v.toLowerCase());}},
    {id:'cat', test:(d,v)=>!v||d.category===v},
    {id:'month', test:(d,v)=>!v||d.sow.includes(v)},
    {id:'coldOnly', test:(d,v)=>!v||d.coldHardy},
  ],
});
</script>
</body>
</html>'''

html = html.replace('__DATA__', data_js).replace('__NAV__', pzbuild.nav('seeds.html')).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__WLJS__', pzbuild.WL_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK)
out = pzenv.REPO + '/seeds.html'
open(out, 'w', encoding='utf-8').write(html)
print(f'Wrote {out} ({len(html)} bytes, {len(seeds)} seeds)')
