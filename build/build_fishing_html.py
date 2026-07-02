#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import pzschema, pzbuild, pzenv
linkmap_js = pzenv.embed_json(json.load(open(pzenv.WORK + '/linkmap.json')))
rows = pzschema.records('fishing')
data_js = pzenv.embed_json(rows)
NAV = pzbuild.nav('fishing.html')
META = ("Project Zomboid Build 42 fishing reference: every fish with its best bait, "
        "size and weight, trophy size and the fishing level needed to catch it. "
        "Game version 42.19.0 (unstable branch, 2026-06-01).")

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project Zomboid — Fishing (Build 42.19.0)</title>
<meta name="description" content="__META__">
<meta name="keywords" content="Project Zomboid, Build 42, B42, fishing, fish, bait, lure, size, weight, trophy, skill level">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Fishing">
<meta property="og:description" content="__META__">
<meta name="pz:gameversion" content="42.19.0">
__AUTHOR__
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
  table { border-collapse:collapse; width:100%; min-width:920px; }
  th,td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); white-space:nowrap; }
  th:hover{color:var(--txt);}
  th.sorted-asc::after{content:" \25B2";color:var(--accent);} th.sorted-desc::after{content:" \25BC";color:var(--accent);}
  tbody tr:hover{background:#241f17;}
  td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}
  .name{font-weight:600;}
  .fam{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:10px;font-size:10px;background:#2a3340;color:var(--blue);}
  .ic{margin-left:5px;cursor:help;}
  .fav{color:var(--accent);font-weight:600;white-space:nowrap;}
  .baits{display:flex;flex-wrap:wrap;gap:3px;max-width:340px;}
  .bait{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;border:1px solid transparent;}
  .t5{background:#2a3a22;color:#9fd07a;} .t4{background:#28331f;color:var(--green);}
  .t3{background:#33301f;color:var(--accent);} .t2{background:#3a3022;color:#d8a96a;}
  .t1{background:#3a2422;color:#d08a7a;}
  .tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;white-space:nowrap;}
  .pred{background:#3a2422;color:#d08a7a;} .net{background:#2a3340;color:var(--blue);}
  .skill{color:var(--green);font-weight:600;}
  .no{color:#5a5346;}
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
  footer{padding:10px 20px;color:var(--muted);font-size:11px;border-top:1px solid var(--line);flex:none;line-height:1.5;}
  footer b{color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Fishing</h1>
  <div class="sub">Build 42.19.0 · per-fish bait, size and skill, parsed from the game files. Click a column to sort.</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by fish / bait…" autocomplete="off">
  <select id="bait"><option value="">Any bait works</option></select>
  <select id="skill"><option value="">Any fishing level</option></select>
  <label class="sub"><input type="checkbox" id="pred"> predators only</label>
  <label class="sub"><input type="checkbox" id="net"> net/trap only</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="t"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  <b>Best bait</b> ⭐ is each fish's single most effective bait. <b>Bait ratings:</b> Great ≥0.8, Good ≥0.6, Average ≥0.4, Below ≥0.2, Poor &gt;0 (0 = won't bite). <b>Min level</b> = Fishing skill needed before the fish can be hooked. <b>⚠ Predator</b> = only caught while actively reeling (not passive fishing). <b>🪤 Net/trap</b> = obtainable with a fishing net, not a rod.
  <br><b>Time &amp; weather (all fish, not per-species):</b> dawn (4–6h) and dusk (18–20h) give +20% bite; rain +20%; fog or strong wind −20%; ideal air temp 15–30 °C. <b>No seasons</b> — Build 42 fishing has no month/season rules. <b>Where you fish</b> matters: fish density comes from water area, in-game Fishing zones and the world's <i>Fish Abundance</i> sandbox setting; chumming (throwing bait in the water) makes a temporary local hotspot. XP per catch scales with size (≈ 2 × length in cm); trophy fish need level 8+.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
__TABLE_JS__
function fill(sel,vals){vals.forEach(v=>{if(v==null||v==='')return;const o=document.createElement('option');o.value=v[0];o.textContent=v[1];sel.appendChild(o);});}
const BAITS=[['Insect','Insect'],['Minnows','Minnows'],['Leeches','Leeches'],['Worms','Worms'],['Flesh','Flesh'],['Plant','Plant'],['jig','Jig Lure'],['minnowLure','Minnow Lure']];
fill(document.getElementById('bait'), BAITS);
fill(document.getElementById('skill'), Array.from({length:11},(_,i)=>[String(i),'Level '+i+' or under']));
function baitVal(d,k){return (d.baits&&d.baits[k]!=null)?d.baits[k]:(d[k]||0);}
function tier(c){return c>=0.8?'t5':c>=0.6?'t4':c>=0.4?'t3':c>=0.2?'t2':'t1';}
function baitChips(d){
  const items=BAITS.map(([k,lab])=>[lab,baitVal(d,k)]).filter(x=>x[1]>0).sort((a,b)=>b[1]-a[1]);
  if(!items.length) return '<span class="no">–</span>';
  return '<div class="baits">'+items.map(([lab,c])=>`<span class="bait ${tier(c)}" title="${c}">${esc(lab)}</span>`).join('')+'</div>';
}
const COLS=[
  {k:'name', t:'Fish', fmt:(v,d)=>`<span class="name">${wl(v)}</span>`
    +(d.predator?` <span class="ic" title="Predator — only caught while actively reeling">⚠</span>`:'')
    +(d.net?` <span class="ic" title="Also catchable with a net/trap">🪤</span>`:'')
    +`<span class="fam">${esc(d.category)}</span>`},
  {k:'favorite', t:'Best bait', fmt:(v,d)=> v?`<span class="fav">⭐ ${esc(v)}</span>`:'<span class="no">no favorite</span>'},
  {k:'maxLen', t:'Max len', num:true, fmt:v=> v==null?'<span class="no">–</span>':`${v} cm`},
  {k:'maxWeight', t:'Max wt', num:true, fmt:v=> v==null?'<span class="no">–</span>':`${v} kg`},
  {k:'trophyLen', t:'Trophy', get:d=>d.trophyLen||0, fmt:(v,d)=> d.trophyLen?`${d.trophyLen} cm · ${d.trophyWeight} kg`:'<span class="no">–</span>'},
  {k:'minSkill', t:'Min level', num:true, fmt:v=> v==null?'<span class="no">–</span>':`<span class="skill">Lv ${v}</span>`},
  {k:'baits', t:'Bait effectiveness', get:d=>0, fmt:(v,d)=> baitChips(d)},
];
buildTable({
  data:DATA, cols:COLS, sortKey:'minSkill', sortDir:1, countNoun:'fish',
  tiebreak:(a,b)=>a.name.localeCompare(b.name),
  filters:[
    {id:'q', test:(d,v)=>!v||(d.name+' '+(d.favorite||'')+' '+d.category).toLowerCase().includes(v.toLowerCase())},
    {id:'bait', test:(d,v)=>!v||baitVal(d,v)>0},
    {id:'skill', test:(d,v)=>v===''||v==null||(d.minSkill!=null&&d.minSkill<=+v)},
    {id:'pred', test:(d,v)=>!v||d.predator},
    {id:'net', test:(d,v)=>!v||d.net},
  ],
});
</script></body></html>'''

html = (html.replace('__NAV__', NAV).replace('__DATA__', data_js)
        .replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS)
        .replace('__LINKMAP__', linkmap_js).replace('__META__', META)
        .replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK))
out = pzenv.REPO + '/fishing.html'
open(out, 'w', encoding='utf-8').write(html)
print(f"Wrote {out} ({len(html)} bytes, {len(rows)} fish)")
