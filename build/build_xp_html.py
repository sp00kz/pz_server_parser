#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import pzschema, pzbuild, pzenv
linkmap_js = pzenv.embed_json(json.load(open(pzenv.WORK + '/linkmap.json')))
rows = pzschema.records('xp')
data_js = pzenv.embed_json(rows)
NAV = pzbuild.nav('actions.html')
META = ("Project Zomboid skill XP from in-world actions: how much XP butchering, "
        "fishing, foraging, vehicle work, first aid and animal care give. "
        "Game version 42.19.0 (unstable branch, 2026-06-01).")

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project Zomboid — Action XP (Build 42.19.0)</title>
<meta name="description" content="__META__">
<meta name="keywords" content="Project Zomboid, Build 42, B42, XP, skills, butchering, fishing, foraging, animal care, mechanics">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Action XP">
<meta property="og:description" content="__META__">
<meta name="pz:gameversion" content="42.19.0">
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
  input[type=search]{min-width:200px;}
  .count{color:var(--muted);font-size:12px;margin-left:auto;}
  .wrap { flex:1; overflow:auto; padding:0 12px 30px; }
  table { border-collapse:collapse; width:100%; min-width:760px; }
  th,td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap; vertical-align:top; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); }
  th:hover{color:var(--txt);}
  th.sorted-asc::after{content:" \25B2";color:var(--accent);} th.sorted-desc::after{content:" \25BC";color:var(--accent);}
  tbody tr:hover{background:#241f17;}
  td.num{text-align:right;font-variant-numeric:tabular-nums;}
  .name{font-weight:600;}
  .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;background:#2a3a22;color:var(--green);}
  .tag.area{background:#2a3340;color:var(--blue);}
  .src{color:#6f6450;font-size:11px;}
  .no{color:#7d7460;font-size:12px;}
  footer{padding:12px 20px;color:var(--muted);font-size:11px;border-top:1px solid var(--line);flex:none;}
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Action XP</h1>
  <div class="sub">Build 42.19.0 · XP granted by in-world actions, parsed from the game files. Click a column to sort.</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by action / skill…" autocomplete="off">
  <select id="skill"><option value="">All skills</option></select>
  <select id="area"><option value="">All areas</option></select>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="t"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  XP shown is per action. <b>varies</b> = computed in-game (e.g. by amount, size, or condition); <b>engine-granted</b> = set in the engine, not the data files.
  This lists in-world actions — crafting XP is on the <a class="wk" href="crafting.html">Crafting</a> page, and combat XP scales per hit.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
__TABLE_JS__
function fill(sel,vals){vals.forEach(v=>{if(v==null||v==='')return;const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});}
fill(document.getElementById('skill'), [...new Set(DATA.map(d=>d.skill))].sort());
fill(document.getElementById('area'), [...new Set(DATA.map(d=>d.category))].sort());
const COLS=[
  {k:'action', t:'Action', fmt:v=>`<span class="name">${esc(v)}</span>`},
  {k:'skill', t:'Skill', fmt:v=>`<span class="tag">${esc(v)}</span>`},
  {k:'xp', t:'XP', num:true, fmt:(v,d)=> v==null ? `<span class="no">${esc(d.note||'varies')}</span>` : v},
  {k:'category', t:'Area', fmt:v=>`<span class="tag area">${esc(v)}</span>`},
  {k:'source', t:'Source', fmt:v=>`<span class="src">${esc(v)}</span>`},
];
buildTable({
  data:DATA, cols:COLS, sortKey:'skill', sortDir:1, countNoun:'actions',
  tiebreak:(a,b)=>a.action.localeCompare(b.action),
  filters:[
    {id:'q', test:(d,v)=>!v||(d.action+' '+d.skill+' '+d.note+' '+d.category).toLowerCase().includes(v.toLowerCase())},
    {id:'skill', test:(d,v)=>!v||d.skill===v},
    {id:'area', test:(d,v)=>!v||d.category===v},
  ],
});
</script></body></html>'''

html = (html.replace('__NAV__', NAV).replace('__DATA__', data_js)
        .replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS)
        .replace('__LINKMAP__', linkmap_js).replace('__META__', META).replace('__TOOLLINK__', pzbuild.TOOL_LINK))
out = pzenv.REPO + '/actions.html'
open(out, 'w', encoding='utf-8').write(html)
print(f"Wrote {out} ({len(html)} bytes, {len(rows)} actions)")
