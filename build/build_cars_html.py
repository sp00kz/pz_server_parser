#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild


cars = pzschema.records('vehicles')
imgmap = json.load(open(pzenv.WORK+'/images_map.json'))          # mod source -> img
vmap   = json.load(open(pzenv.WORK+'/vanilla_images_map.json'))  # vanilla script -> img
for c in cars:
    c['img'] = imgmap.get(c['source']) or vmap.get(c['script'])
    import os as _os
    c['thumb'] = None
    if c['img']:
        _t = c['img'].replace('images/', 'images/thumbs/', 1)
        if _os.path.exists(pzenv.REPO + '/' + _t): c['thumb'] = _t
data_js = pzenv.embed_json(cars)

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid vehicle stats: top speed, engine power and quality, mass, seats, trunk capacity and crash protection for the base game plus Workshop mods. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, vehicles, cars, vehicle stats, trunk capacity, engine, Workshop mods">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Vehicles">
<meta property="og:description" content="Project Zomboid vehicle stats: top speed, engine power and quality, mass, seats, trunk capacity and crash protection for the base game plus Workshop mods. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Vehicle / Car Stats (Build 42.19.0 + mods)</title>
<style>
  :root { --bg:#14110d; --panel:#1d1913; --line:#3a3024; --txt:#e8dcc4;
    --muted:#9b8f76; --accent:#c9a14a; --green:#6fae4f; --red:#c5564b; --blue:#5a8fb0; --hdr:#241f17; }
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
  .controls { display:flex; gap:10px; flex-wrap:wrap; align-items:center;
              padding:12px 20px; background:var(--panel); border-bottom:1px solid var(--line); flex:none; }
  input[type=search], select { background:var(--bg); color:var(--txt);
              border:1px solid var(--line); border-radius:6px; padding:7px 10px; font-size:13px; }
  input[type=search] { min-width:200px; }
  .count { color:var(--muted); font-size:12px; margin-left:auto; }
  .wrap { flex:1; overflow:auto; padding:0 12px; }
  table { border-collapse:collapse; width:100%; min-width:1180px; }
  th, td { padding:6px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); }
  th:hover { color:var(--txt); }
  th.sorted-asc::after  { content:" \25B2"; color:var(--accent); }
  th.sorted-desc::after { content:" \25BC"; color:var(--accent); }
  tbody tr:hover { background:#241f17; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; }
  .name { font-weight:600; color:var(--txt); }
  .script { color:var(--muted); font-size:11px; }
  .src { font-size:11px; color:var(--blue); }
  .src.Vanilla { color:var(--muted); }
  .tag { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; background:#2a3340; color:var(--blue); }
  .tag.Sports,.tag.Luxury { background:#3a2a40; color:#b98fd0; }
  .tag.Van,.tag.Pickup { background:#2a3a22; color:var(--green); }
  .tag.Trailer { background:#332a22; color:var(--accent); }
  .bar { display:inline-block; height:8px; background:var(--accent); border-radius:2px; vertical-align:middle; opacity:.7; }
  .namecell { display:flex; align-items:center; gap:9px; }
  .thumb { width:50px; height:38px; object-fit:contain; border-radius:3px; background:#0e0c09;
           border:1px solid var(--line); flex:none; }
  .thumb.ph { opacity:.25; }
  #hov { position:fixed; display:none; z-index:60; pointer-events:none;
         border:1px solid var(--accent); border-radius:6px; background:#0e0c09;
         box-shadow:0 6px 24px rgba(0,0,0,.6); padding:3px; }
  #hov img { display:block; width:360px; height:240px; object-fit:contain; border-radius:4px; background:#0e0c09; }
  #hov .cap { color:var(--accent); font-size:11px; text-align:center; padding:3px 2px 1px; }
  .approx { color:var(--muted); }
  .intf { color:var(--blue); font-size:10px; vertical-align:super; cursor:help; }
  .no { color:#5a5346; }
  footer { padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style>
</head>
<body>
<header>
  __NAV__
  <h1>Project Zomboid — Vehicle Stats <span class="sub">(base game + Workshop mods)</span></h1>
  <div class="sub">Parsed from <code>scripts/.../vehicles/*.txt</code> (vanilla + <code>workshop/content/108600</code>), <code>template!</code> inheritance &amp; part composition resolved. Trunk = full-condition capacity. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by name / script / mod…" autocomplete="off">
  <select id="cat"><option value="">All types</option></select>
  <select id="src"><option value="">All sources</option></select>
  <label class="script"><input type="checkbox" id="vanillaOnly"> vanilla only</label>
  <label class="script"><input type="checkbox" id="hideTrailer"> hide trailers</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="tbl"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<div id="hov"><img alt=""><div class="cap"></div></div>
<footer>
  <b>Trunk</b> = trunk capacity at full condition; <span class="intf">i</span> = vehicle has no cargo trunk, value is its largest interior slot (e.g. glovebox);
  <span class="approx">grey</span> = derived from the trunk part's item type (exact tier/condition varies in-game). In-game capacity scales down with trunk condition
  (e.g. a 130 van trunk shows ~97 at ~75% condition). <b>Roof rack</b> blank unless the vehicle/mod adds one. <b>Loudness</b> lower = stealthier · <b>Repair</b> = Mechanics level · <b>Protection</b> = crash damage protection.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
function trunkCell(v,d){
  if(d.trunk==null) return '<span class="no">–</span>';
  let s = d.trunkApprox ? `<span class="approx">${d.trunk}</span>` : `${d.trunk}`;
  if(d.trunkKind==='glovebox') s += '<span class="intf" title="No cargo trunk — largest interior storage slot">i</span>';
  return s;
}
const COLS = [
  {k:'name', t:'Name', fmt:(v,d)=>`<div class="namecell">${d.img?`<img class="thumb" loading="lazy" decoding="async" src="${d.thumb||d.img}" alt="">`:'<div class="thumb ph"></div>'}<div><span class="name">${wl(v)}</span><br><span class="script">${esc(d.script)}</span></div></div>`},
  {k:'source', t:'Source', fmt:v=>`<span class="src ${v==='Vanilla'?'Vanilla':''}">${esc(v)}</span>`},
  {k:'category', t:'Type', fmt:v=>`<span class="tag ${esc(v).replace(' ','')}">${esc(v)}</span>`},
  {k:'maxSpeed', t:'Max speed', num:true, fmt:(v,d)=>{if(v==null)return '<span class="no">–</span>';const w=Math.round(45*v/maxSpeed);return `${v} <span class="bar" style="width:${w}px"></span>`;}},
  {k:'engineForce', t:'Engine force', num:true},
  {k:'engineQuality', t:'Eng. qual', num:true},
  {k:'engineLoudness', t:'Loud', num:true},
  {k:'trunk', t:'Trunk', num:true, fmt:trunkCell},
  {k:'roofRack', t:'Roof rack', num:true, fmt:v=>v==null?'<span class="no">–</span>':v},
  {k:'mass', t:'Mass', num:true},
  {k:'seats', t:'Seats', num:true},
  {k:'engineRepairLevel', t:'Repair', num:true},
  {k:'protection', t:'Prot.', num:true},
];
function fill(sel, vals, label){ vals.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);}); }
fill(document.getElementById('cat'), [...new Set(DATA.map(d=>d.category))].sort());
fill(document.getElementById('src'), [...new Set(DATA.map(d=>d.source))].sort((a,b)=>a==='Vanilla'?-1:b==='Vanilla'?1:a.localeCompare(b)));
const maxSpeed=Math.max(...DATA.map(d=>d.maxSpeed||0));
// hover image preview (anchored near the row's name)
const hov=document.getElementById('hov'), hovImg=hov.querySelector('img'), hovCap=hov.querySelector('.cap');
const tbody=document.querySelector('tbody');
let curImg=null;
function showHov(tr, x, y){
  const img=tr.dataset.img; if(!img){ hideHov(); return; }
  if(img!==curImg){ curImg=img; hovImg.src=img; hovCap.textContent=tr.dataset.name||''; }
  hov.style.display='block';
  const w=372, h=275;
  let lx=x+18, ly=y+12;
  if(lx+w>innerWidth) lx=x-w-18;
  if(ly+h>innerHeight) ly=innerHeight-h-8;
  if(ly<8) ly=8;
  hov.style.left=lx+'px'; hov.style.top=ly+'px';
}
function hideHov(){ hov.style.display='none'; curImg=null; }
tbody.addEventListener('mousemove', e=>{
  const tr=e.target.closest('tr'); if(tr) showHov(tr, e.clientX, e.clientY); else hideHov();
});
tbody.addEventListener('mouseleave', hideHov);
__TABLE_JS__
buildTable({
  data:DATA, cols:COLS, sortKey:'maxSpeed', sortDir:-1, countNoun:'vehicles',
  rowExtra:(d,tr,tb)=>{ if(d.img){ tr.dataset.img=d.img; tr.dataset.name=d.name; } },
  filters:[
    {id:'q', test:(d,v)=>!v||(d.name+' '+d.script+' '+d.source).toLowerCase().includes(v.toLowerCase())},
    {id:'cat', test:(d,v)=>!v||d.category===v},
    {id:'src', test:(d,v)=>!v||d.source===v},
    {id:'vanillaOnly', test:(d,v)=>!v||d.source==='Vanilla'},
    {id:'hideTrailer', test:(d,v)=>!v||d.category!=='Trailer'},
  ],
});
</script>
<script>/* cache vehicle images cache-first so they download at most once (saves bandwidth) */
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){});});}</script>
</body>
</html>'''

html = html.replace('__DATA__', data_js).replace('__NAV__', pzbuild.nav('cars.html')).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__WLJS__', pzbuild.WL_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK)
out = pzenv.REPO + '/cars.html'
open(out, 'w', encoding='utf-8').write(html)
print(f"Wrote {out} ({len(html)} bytes, {len(cars)} vehicles, {sum(1 for c in cars if c['img'])} with images)")
