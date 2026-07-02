#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
import json, re
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild

recipes = pzschema.records('recipes')
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
wl_fn = pzbuild.WL_FN
OUT = pzenv.REPO

# archetype skill -> (display, emoji)
ARCH = [
    ('Woodwork','Carpentry','🪚'),
    ('MetalWelding','Welding','🔧'),
    ('Blacksmith','Blacksmithing','⚒️'),
    ('Tailoring','Tailoring','🧵'),
    ('Carving','Carving','🔪'),
    ('Cooking','Cooking','🍳'),
    ('Electricity','Electrical','⚡'),
    ('Glassmaking','Glassmaking','🫙'),
    ('Pottery','Pottery','🏺'),
    ('FlintKnapping','Knapping','🪨'),
    ('Masonry','Masonry','🧱'),
    ('Maintenance','Maintenance','🛠️'),
    ('Butchering','Butchering','🔪'),
    ('Fishing','Fishing','🎣'),
]
SKILL_DISP = {s:(d,e) for s,d,e in ARCH}
ARCH_SKILLS = [s for s,_,_ in ARCH]

# main site nav
MAIN = [('index.html','🌱 Seeds'),('cars.html','🚗 Vehicles'),('livestock.html','🐄 Livestock'),
        ('guns.html','🔫 Guns'),('melee.html','🗡️ Melee'),('tools.html','🧰 Tools'),('crafting.html','🛠️ Crafting'),('food.html','🍎 Food'),('foraging.html','🌲 Foraging')]
def mainnav(active):
    return pzbuild.nav(active)

CSS = '''
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
  table { border-collapse:collapse; width:100%; min-width:980px; }
  th,td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top; }
  th { position:sticky; top:0; z-index:2; background:var(--hdr); cursor:pointer; user-select:none;
       font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); box-shadow:inset 0 -1px 0 var(--line); white-space:nowrap; }
  th:hover{color:var(--txt);}
  th.sorted-asc::after{content:" \\25B2";color:var(--accent);} th.sorted-desc::after{content:" \\25BC";color:var(--accent);}
  tbody tr:hover{background:#241f17;}
  td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}
  .rname{font-weight:600;}
  .xp{color:var(--green);font-weight:600;white-space:nowrap;}
  .xp2{color:var(--accent);}
  .req{color:var(--muted);}
  .mat{color:var(--txt);} .tool{color:var(--muted);font-size:12px;}
  .loop{color:var(--accent);font-weight:600;}
  .no{color:#5a5346;}
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
  code{color:var(--accent);}
  footer{padding:12px 20px;color:var(--muted);font-size:11px;border-top:1px solid var(--line);flex:none;}
  /* index cards */
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:12px;padding:16px 20px;}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;}
  .card h3{margin:0 0 6px;font-size:16px;color:var(--accent);}
  .card .meta{color:var(--muted);font-size:12px;margin-bottom:8px;}
  .card a.open{color:var(--blue);text-decoration:none;font-size:12px;}
  .lvlrow{display:flex;align-items:center;gap:6px;margin:8px 0;font-size:13px;}
  .recs{margin-top:8px;border-top:1px solid var(--line);padding-top:8px;font-size:12px;}
  .rec{padding:4px 0;border-bottom:1px solid #241f17;}
  .rec b{color:var(--txt);} .rec .e{color:var(--green);}
  .badge{display:inline-block;padding:1px 6px;border-radius:8px;font-size:10px;background:#332a22;color:var(--accent);margin-left:4px;}
'''

def fmt_mats(mats):
    if not mats: return '<span class="no">–</span>'
    return ', '.join(f'{m["count"]}× {m["label"]}' for m in mats)
def fmt_tools(ts):
    if not ts: return '<span class="no">–</span>'
    return ', '.join(t['label'] for t in ts)

# sub-pages
def subpage(skill):
    disp, emoji = SKILL_DISP[skill]
    rs = [r for r in recipes if skill in r.get('xp',{}) or skill in r.get('req',{})]
    data = pzenv.embed_json(rs)
    nav = mainnav('crafting.html')
    html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid crafting and building recipes for every skill: XP, materials, tools, craft time and no-waste crafting cycles. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, crafting, recipes, blacksmithing, carpentry, tailoring, XP, skills">
<meta name="robots" content="index, follow">
{pzbuild.AUTHOR_META}
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Crafting">
<meta property="og:description" content="Project Zomboid crafting and building recipes for every skill: XP, materials, tools, craft time and no-waste crafting cycles. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>PZ Crafting — {disp} — Build 42.19.0</title><style>{CSS}</style></head><body>
<header>{nav}
<div class="sub"><a href="crafting.html" style="color:var(--blue);text-decoration:none">&larr; All archetypes</a></div>
<h1>{emoji} {disp} <span class="sub">— {len(rs)} recipes</span></h1>
<div class="sub">XP, materials (cost), tools, and craft time. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter recipe / item…" autocomplete="off">
  <label class="sub"><input type="checkbox" id="learn"> hide learn-only (need recipe book)</label>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="t"><thead><tr id="hr"></tr></thead><tbody></tbody></table></div>
<footer>XP shown for <b>{disp}</b> (recipes may also grant other skills). <b>Materials</b> are consumed (cost); <b>Tools</b> are kept. <b>Time</b> = action duration (game ticks). <b>Req</b> = level needed.{pzbuild.TOOL_LINK}</footer>
<script>
const SKILL="{skill}"; const DATA={data};
const WIKI='https://pzwiki.net/wiki/';
const LINKMAP={linkmap_js};
{wl_fn}
const COLS=[
 {{k:'name',t:'Recipe',fmt:(v,d)=>`<span class="rname">${{esc(v)}}</span>`}},
 {{k:'_out',t:'Makes',fmt:(v,d)=>d.outputs.map(o=>`${{o.count}}× ${{wl(o.label)}}`).join(', ')||'–'}},
 {{k:'_xp',t:'XP',num:true,fmt:(v,d)=>{{let m=Object.entries(d.xp).map(([s,x])=>`<span class="${{s===SKILL?'xp':'xp2'}}">${{esc(s)}} +${{esc(x)}}</span>`);return m.join('<br>')||'<span class=no>–</span>';}}}},
 {{k:'_req',t:'Req',num:true,fmt:(v,d)=>Object.entries(d.req).map(([s,l])=>`<span class=req>${{esc(s)}} ${{esc(l)}}</span>`).join('<br>')||'<span class=no>–</span>'}},
 {{k:'_mats',t:'Materials (cost)',fmt:(v,d)=>d.consumed.map(m=>`${{m.count}}× ${{wl(m.label)}}`).join(', ')||'<span class=no>–</span>'}},
 {{k:'_tools',t:'Tools',fmt:(v,d)=>`<span class=tool>${{d.tools.map(m=>wl(m.label)).join(', ')||'–'}}</span>`}},
 {{k:'time',t:'Time',num:true}},
];
function xpv(d){{return d.xp[SKILL]||0;}}
function reqv(d){{return d.req[SKILL]||0;}}
function matc(d){{return d.consumed.reduce((a,m)=>a+(typeof m.count==='number'?m.count:1),0);}}
let sortKey='_xp',sortDir=-1;
const hr=document.getElementById('hr');
COLS.forEach(c=>{{const th=document.createElement('th');th.textContent=c.t;th.dataset.k=c.k;if(c.num)th.style.textAlign='right';
 th.onclick=()=>{{if(sortKey===c.k)sortDir*=-1;else{{sortKey=c.k;sortDir=(c.num?-1:1);}}render();}};hr.appendChild(th);}});
function keyval(d,k){{if(k==='_xp')return xpv(d);if(k==='_req')return reqv(d);if(k==='_mats')return matc(d);if(k==='_out')return d.outputs.length;if(k==='_tools')return d.tools.length;return d[k];}}
function render(){{
 const q=document.getElementById('q').value.toLowerCase();const hl=document.getElementById('learn').checked;
 let rows=DATA.filter(d=>{{if(hl&&d.learn)return false;
   if(q){{const hay=(d.name+' '+d.outputs.map(o=>o.label).join(' ')+' '+d.consumed.map(m=>m.label).join(' ')).toLowerCase();if(!hay.includes(q))return false;}}return true;}});
 rows.sort((a,b)=>{{let va=keyval(a,sortKey),vb=keyval(b,sortKey);if(va==null)va=-Infinity;if(vb==null)vb=-Infinity;
   if(typeof va==='string')return va.localeCompare(vb)*sortDir;return (va-vb)*sortDir;}});
 document.querySelectorAll('th').forEach(th=>{{th.className=th.dataset.k===sortKey?(sortDir>0?'sorted-asc':'sorted-desc'):'';}});
 const tb=document.querySelector('tbody');tb.innerHTML='';
 for(const d of rows){{const tr=document.createElement('tr');for(const c of COLS){{const td=document.createElement('td');if(c.num)td.className='num';
   let raw=keyval(d,c.k);td.innerHTML=c.fmt?c.fmt(raw,d):(raw==null?'<span class=no>–</span>':raw);tr.appendChild(td);}}tb.appendChild(tr);}}
 document.getElementById('count').textContent=rows.length+' / '+DATA.length+' recipes';
}}
['q','learn'].forEach(id=>{{const e=document.getElementById(id);e.addEventListener(e.type==='checkbox'?'change':'input',render);}});
render();
</script></body></html>'''
    open(f'{OUT}/craft_{skill}.html','w',encoding='utf-8').write(html)
    return len(rs)

# non-recipe skills, leveled by actions
NONCRAFT = [('Mechanics','🔩','repairing & installing vehicle parts'),
            ('Agriculture','🌾','planting, tending & harvesting crops'),
            ('Animal Care','🐾','feeding, breeding & caring for animals')]

# index
def index():
    # embed fields needed for recommendations
    slim=[{'id':r['id'],'name':r['name'],
           'xp':{k:v for k,v in r['xp'].items()},'req':r['req'],'time':r['time'],
           'c':[{'n':m['count'],'l':m['label'],'i':m.get('items',[])} for m in r['consumed']],
           't':[t['label'] for t in r['tools']],
           'o':[{'n':o['count'],'l':o['label'],'i':o.get('items',[])} for o in r['outputs']],'learn':r['learn']}
          for r in recipes if any(s in ARCH_SKILLS for s in r['xp'])]
    data=pzenv.embed_json(slim)
    # full recipe set for the lookup search
    alldata=pzenv.embed_json([{'id':r['id'],'name':r['name'],'cat':r['category'],'skills':r['skills'],
           'xp':r['xp'],'req':r['req'],'time':r['time'],
           'c':[{'n':m['count'],'l':m['label']} for m in r['consumed']],
           't':[t['label'] for t in r['tools']],
           'o':[{'n':o['count'],'l':o['label']} for o in r['outputs']],'learn':r['learn']}
          for r in recipes])
    arch=pzenv.embed_json([{'skill':s,'disp':d,'emoji':e,'n':sum(1 for r in recipes if s in r['xp'])} for s,d,e in ARCH])
    noncraft=pzenv.embed_json([{'skill':s,'emoji':e,'how':h} for s,e,h in NONCRAFT])
    nav=mainnav('crafting.html')
    EXTRA_CSS='''
  .profile{padding:12px 20px;background:var(--panel);border-bottom:1px solid var(--line);flex:none;}
  .profile .ph{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
  .profile .ph b{color:var(--accent);} .profile .ph .hint{color:var(--muted);font-size:12px;}
  .profile button{background:var(--bg);color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer;font-size:12px;}
  .profile button:hover{color:var(--txt);border-color:var(--accent);}
  .skgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px 14px;}
  .skitem{display:flex;align-items:center;gap:6px;font-size:13px;}
  .skitem label{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .skitem select{padding:2px 4px;width:48px;}
  .skitem .open{color:var(--blue);text-decoration:none;font-size:11px;}
  section.blk{margin:18px 0;}
  section.blk h2{font-size:15px;color:var(--accent);margin:0 0 4px;border-bottom:1px solid var(--line);padding-bottom:4px;}
  section.blk .lead{color:var(--muted);font-size:12px;margin-bottom:10px;}
  .cyc{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin-bottom:8px;}
  .cyc.free{border-color:var(--green);}
  .cyc .step{margin:2px 0;}
  .cyc .step .num{color:var(--muted);}
  .cyc .arrow{color:var(--accent);}
  .cyc .skills{margin-top:5px;font-size:12px;}
  .cyc .tag{display:inline-block;padding:1px 7px;border-radius:8px;font-size:11px;margin-right:4px;}
  .cyc .tag.xp{background:#21331f;color:var(--green);}
  .cyc .tag.free{background:#1f3a24;color:#8fe06a;border:1px solid #3f7a3f;}
  .cyc .tag.cost{background:#332a22;color:var(--accent);}
  .cyc .tag.loss{background:#3a2622;color:#d08a7a;}
  .cyc .tag.unk{background:#26221c;color:var(--muted);}
  .cyc .bk{font-size:11px;}
  .grp{font-size:12px;color:var(--accent);margin:16px 0 7px;text-transform:uppercase;letter-spacing:.5px;font-weight:600;}
  .grp:first-child{margin-top:0;}
  .profile button{margin-left:6px;}
  .skitem input.ck{accent-color:var(--accent);cursor:pointer;flex:none;}
  .cyc.locked{opacity:.55;border-style:dashed;}
  .cyc .lock{color:var(--red);font-size:11px;}
  .bycols{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;}
  .skcard{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;}
  .skcard h3{margin:0 0 2px;font-size:15px;color:var(--accent);}
  .skcard .meta{color:var(--muted);font-size:11px;margin-bottom:7px;}
  .skcard .open{color:var(--blue);text-decoration:none;}
  .rec{padding:4px 0;border-bottom:1px solid #241f17;font-size:12px;}
  .rec:last-child{border-bottom:none;}
  .rec b{color:var(--txt);} .rec .e{color:var(--green);font-weight:600;}
  .rec .cost{color:var(--muted);}
  .noncraft{display:flex;gap:10px;flex-wrap:wrap;}
  .nc{background:var(--panel);border:1px dashed var(--line);border-radius:8px;padding:10px 12px;font-size:12px;color:var(--muted);}
  .nc b{color:var(--txt);}
'''
    html=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid crafting and building recipes for every skill: XP, materials, tools, craft time and no-waste crafting cycles. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, crafting, recipes, blacksmithing, carpentry, tailoring, XP, skills">
<meta name="robots" content="index, follow">
{pzbuild.AUTHOR_META}
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Crafting">
<meta property="og:description" content="Project Zomboid crafting and building recipes for every skill: XP, materials, tools, craft time and no-waste crafting cycles. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>PZ Crafting — Archetypes</title><style>{CSS}{EXTRA_CSS}</style></head><body>
<header>{nav}
<h1>🛠️ Crafting &amp; Building</h1>
<div class="sub">Set your level for each skill below — it&apos;s saved in your browser. The page then shows the best <b>no-waste cycles</b> and most XP-efficient recipes you can do right now. Open any skill for its full recipe list.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="profile">
  <div class="ph"><b>Your skill levels</b> <span class="hint">set your level &amp; tick which skills to show · saved automatically</span>
    <span style="margin-left:auto"></span>
    <button id="skall">Show all</button><button id="sknone">Hide all</button>
    <button id="reset">Reset levels</button></div>
  <div class="skgrid" id="skgrid"></div>
</div>
<div class="controls">
  <input type="search" id="q" placeholder="🔍 Look up any recipe — name, item made, material, skill…" autocomplete="off">
  <label class="sub"><input type="checkbox" id="qlearn"> hide magazine-only</label>
  <span class="count" id="qc"></span>
</div>
<div class="wrap">
  <section class="blk" id="searchSec" style="display:none">
    <h2>Search results</h2>
    <div class="lead" id="qlead"></div>
    <table id="qt"><thead><tr id="qhr"></tr></thead><tbody></tbody></table>
  </section>
  <div id="normal">
  <section class="blk">
    <h2>♻ Crafting cycles you can run now</h2>
    <div class="lead"><b>♻ Zero-loss cycle</b> = the crafted item comes back in full every lap, so you only ever spend fuel/tools (e.g. charcoal). <b>Cross-skill</b> cycles grind two skills at once; <b>same-skill</b> ones just re-forge an item back and forth for XP in one skill. <span class="bk">📖</span> = the recipe must be learned from a magazine first.</div>
    <div id="cycles"></div>
  </section>
  <section class="blk">
    <h2>Most XP-efficient recipes by skill</h2>
    <div class="lead">Top recipes you can craft at your current level, ranked by XP per unit of material (then per time).</div>
    <div class="bycols" id="bySkill"></div>
  </section>
  <section class="blk">
    <h2>Action-leveled skills</h2>
    <div class="lead">These have no crafting recipes — you level them by doing, not building.</div>
    <div class="noncraft" id="noncraft"></div>
  </section>
  </div>
</div>
<footer><b>Efficiency</b> = XP per unit of material consumed (then per time). <b>♻ cycle</b> = two recipes whose outputs feed each other (e.g. cut a bar into halves, forge halves back into a bar) — repeatable while gaining XP in both skills. <b>Cost</b> shown is what&apos;s consumed beyond the looped items (fuel, charcoal, etc.).{pzbuild.TOOL_LINK}</footer>
<script>
const DATA={data}; const ARCH={arch}; const NONCRAFT={noncraft}; const ALLDATA={alldata};
const WIKI='https://pzwiki.net/wiki/';
const LINKMAP={linkmap_js};
{wl_fn}
const ARCHSET=new Set(ARCH.map(a=>a.skill));
const DISP={{}}; ARCH.forEach(a=>DISP[a.skill]=a.disp);
const LS='pz_skills';
let levels={{}}; try{{levels=JSON.parse(localStorage.getItem(LS))||{{}};}}catch(e){{}}
function save(){{try{{localStorage.setItem(LS,JSON.stringify(levels));}}catch(e){{}}}}
function lvl(s){{return +levels[s]||0;}}
// which skills' recipes/cycles to display (default all on)
let show={{}}; try{{show=JSON.parse(localStorage.getItem('pz_show'))||{{}};}}catch(e){{}}
function shown(s){{return show[s]!==false;}}
function saveShow(){{try{{localStorage.setItem('pz_show',JSON.stringify(show));}}catch(e){{}}}}
function matc(r){{return r.c.reduce((a,m)=>a+(typeof m.n==='number'?m.n:1),0);}}
// req met for crafting skills we track (ignore non-tracked req skills like Strength)
function reqMet(r){{return Object.entries(r.req).every(([s,l])=> !ARCHSET.has(s) || lvl(s)>=l);}}
function reqMissing(r){{return Object.entries(r.req).filter(([s,l])=>ARCHSET.has(s)&&lvl(s)<l).map(([s,l])=>(DISP[s]||s)+' '+l);}}

// ---- loop detection: match on shared item ids, not exact compound labels ----
const byConsItem={{}};
for(const r of DATA){{ for(const c of r.c){{ for(const id of (c.i||[])){{(byConsItem[id]=byConsItem[id]||new Set()).add(r);}} }} }}
const share=(a,b)=>a&&b&&a.some(x=>b.includes(x));
const num=v=>typeof v==='number'?v:null;
// items that are fuel/abrasives, not "product waste" — present in a cost list doesn't break zero-loss
const FUEL=new Set(['charcoal','welding torch','welding rods','welding mask','water']);
function buildLoops(){{
  const res=[];const seen=new Set();
  for(const r1 of DATA){{
    for(const o1 of r1.o){{
      if(!o1.i||!o1.i.length)continue;
      const cands=new Set();
      for(const id of o1.i){{(byConsItem[id]||[]).forEach(r=>cands.add(r));}}
      for(const r2 of cands){{
        if(r2===r1||!Object.keys(r2.xp).length)continue;
        for(const o2 of r2.o){{
          if(!o2.i||!o2.i.length)continue;
          const c1=r1.c.find(c=>share(c.i,o2.i)); if(!c1)continue;   // r1 consumes what r2 makes
          const c2=r2.c.find(c=>share(c.i,o1.i)); if(!c2)continue;   // r2 consumes what r1 makes
          const key=[r1.id,r2.id].sort().join('|');if(seen.has(key))continue;seen.add(key);
          // does the cycled item survive a full lap?  gain = units returned per unit spent
          let gain=null;
          const a=num(o1.n),b=num(c1.n),c=num(o2.n),d=num(c2.n);
          if(a!=null&&b&&c!=null&&d) gain=(a/b)*(c/d);
          // gain>1 = not a real reversible cycle (both recipes just degrade) -> drop
          if(gain!=null && gain>1.001) continue;
          // cost = everything consumed EXCEPT the looped items (c1 in r1, c2 in r2)
          const cost={{}};
          r1.c.filter(c=>c!==c1).forEach(c=>cost[c.l]=(cost[c.l]||0)+(typeof c.n==='number'?c.n:1));
          r2.c.filter(c=>c!==c2).forEach(c=>cost[c.l]=(cost[c.l]||0)+(typeof c.n==='number'?c.n:1));
          const costList=Object.entries(cost).map(([l,n])=>({{l,n}}));
          const realCost=costList.filter(x=>!FUEL.has(x.l.toLowerCase())); // ingredients lost beyond fuel
          const conserves = gain!=null && gain>=0.999;        // product comes back
          const zeroLoss = conserves && realCost.length===0;   // only fuel/tools spent
          const lossPct = (gain!=null && gain<0.999) ? Math.round((1-gain)*100) : 0;
          const xps={{}};
          for(const [s,x] of Object.entries(r1.xp))xps[s]=(xps[s]||0)+x;
          for(const [s,x] of Object.entries(r2.xp))xps[s]=(xps[s]||0)+x;
          res.push({{r1,r2,o1:o1.l,o2:o2.l,cost:costList,realCost,zeroLoss,conserves,lossPct,gain,xps,
            xpsum:Object.values(xps).reduce((a,b)=>a+b,0),
            multi:Object.keys(xps).length>1}});
        }}
      }}
    }}
  }}
  // best first: zero-loss, then product-conserving, then multi-skill, then XP/cycle
  return res.sort((a,b)=> (b.zeroLoss-a.zeroLoss) || (b.conserves-a.conserves) || (b.multi-a.multi) || (b.xpsum-a.xpsum));
}}
const LOOPS=buildLoops();

// ---- render ----
function recsFor(skill){{
  const L=lvl(skill);
  let rs=DATA.filter(r=>r.xp[skill] && (r.req[skill]||0)<=L && reqMet(r) && !r.learn);
  rs.forEach(r=>{{r._e=r.xp[skill]/Math.max(matc(r),1); r._t=r.xp[skill]/Math.max(r.time||100,1)*100;}});
  rs.sort((a,b)=>b._e-a._e || b._t-a._t || b.xp[skill]-a.xp[skill]);
  return rs;
}}
const fmtCost=arr=>arr.map(x=>esc(x.n)+'× '+esc(x.l)).join(', ');
const bk=r=>r.learn?' <span class="bk" title="needs the recipe magazine">📖</span>':'';
function cycChip(L){{
  const skills=Object.entries(L.xps).map(([s,x])=>`<span class="tag xp">${{esc(DISP[s]||s)}} +${{esc(x)}}</span>`).join('');
  let status;
  if(L.zeroLoss)        status='<span class="tag free">♻ Zero-loss cycle</span>';
  else if(L.conserves)  status='<span class="tag cost">product kept · spends ingredients</span>';
  else if(L.gain!=null) status=`<span class="tag loss">lossy · ~${{L.lossPct}}% lost / cycle</span>`;
  else                  status='<span class="tag unk">ratio unknown</span>';
  const costStr=L.cost.length?`<span class="tag cost">cost: ${{fmtCost(L.cost)}}</span>`:'';
  return {{free:L.zeroLoss,html:`
    <div class="step"><span class="num">1.</span> <b>${{esc(L.r1.name)}}</b>${{bk(L.r1)}} <span class="arrow">→</span> ${{esc(L.o1)}}</div>
    <div class="step"><span class="num">2.</span> <b>${{esc(L.r2.name)}}</b>${{bk(L.r2)}} <span class="arrow">→</span> ${{esc(L.o2)}} <span class="num">(back to start)</span></div>
    <div class="skills">${{skills}} ${{status}} ${{costStr}} <span class="tag" style="color:var(--muted)">${{L.xpsum}} XP/cycle</span></div>`}};
}}
function renderCycles(){{
  const box=document.getElementById('cycles');
  const vis=L=>Object.keys(L.xps).some(shown);
  const open=LOOPS.filter(L=>vis(L)&&reqMet(L.r1)&&reqMet(L.r2));
  const locked=LOOPS.filter(L=>vis(L)&&!(reqMet(L.r1)&&reqMet(L.r2)));
  const cross=open.filter(L=>L.multi), same=open.filter(L=>!L.multi);
  let h='';
  if(!open.length) h+='<div class="no">No cycles available yet — raise some skill levels above (try Blacksmithing + Welding).</div>';
  if(cross.length){{
    h+='<div class="grp">Cross-skill cycles — XP in two skills per lap (the good stuff)</div>';
    for(const L of cross){{const c=cycChip(L);h+=`<div class="cyc${{c.free?' free':''}}">${{c.html}}</div>`;}}
  }}
  if(same.length){{
    h+='<div class="grp">Same-skill grind cycles — repeat for XP in one skill</div>';
    for(const L of same.slice(0,30)){{const c=cycChip(L);h+=`<div class="cyc${{c.free?' free':''}}">${{c.html}}</div>`;}}
  }}
  if(locked.length){{
    h+='<details style="margin-top:10px"><summary style="cursor:pointer;color:var(--muted)">'+locked.length+' more cycles need higher levels</summary>';
    for(const L of locked.slice(0,30)){{
      const miss=[...new Set([...reqMissing(L.r1),...reqMissing(L.r2)])];
      const c=cycChip(L);
      h+=`<div class="cyc locked">${{c.html}}<div class="lock">🔒 needs ${{esc(miss.join(', '))}}</div></div>`;
    }}
    h+='</details>';
  }}
  box.innerHTML=h;
}}
function renderBySkill(){{
  const box=document.getElementById('bySkill');let h='';
  const vis=ARCH.filter(a=>shown(a.skill));
  if(!vis.length){{box.innerHTML='<div class="no">No skills selected — tick some boxes in the panel above.</div>';return;}}
  for(const a of vis){{
    const recs=recsFor(a.skill).slice(0,5);
    h+=`<div class="skcard"><h3>${{a.emoji}} ${{a.disp}} <span class="meta">lvl ${{lvl(a.skill)}}</span></h3>
      <div class="meta">${{a.n}} XP recipes · <a class="open" href="craft_${{a.skill}}.html">full list →</a></div>`;
    if(!recs.length)h+='<div class="no">no craftable recipes at this level</div>';
    for(const r of recs){{
      h+=`<div class="rec"><b>${{esc(r.name)}}</b> <span class="e">+${{r.xp[a.skill]}}</span> · <span class="cost">${{matc(r)}} mat · ${{r.c.map(c=>c.n+'× '+esc(c.l)).join(', ')||'free'}}</span></div>`;
    }}
    h+='</div>';
  }}
  box.innerHTML=h;
}}
function render(){{renderCycles();renderBySkill();}}

// ---- profile panel ----
const grid=document.getElementById('skgrid');
for(const a of ARCH){{
  const opts=Array.from({{length:11}},(_,i)=>`<option value="${{i}}"${{lvl(a.skill)===i?' selected':''}}>${{i}}</option>`).join('');
  const div=document.createElement('div');div.className='skitem';
  div.innerHTML=`<input type="checkbox" class="ck" data-skill="${{a.skill}}"${{shown(a.skill)?' checked':''}} title="show ${{a.disp}} recipes &amp; cycles">
    <label title="${{a.disp}}">${{a.emoji}} ${{a.disp}}</label>
    <select data-skill="${{a.skill}}">${{opts}}</select>`;
  grid.appendChild(div);
}}
grid.querySelectorAll('select[data-skill]').forEach(sel=>{{
  sel.onchange=()=>{{levels[sel.dataset.skill]=+sel.value;save();render();}};
}});
grid.querySelectorAll('input.ck').forEach(ck=>{{
  ck.onchange=()=>{{show[ck.dataset.skill]=ck.checked;saveShow();render();}};
}});
document.getElementById('reset').onclick=()=>{{levels={{}};save();grid.querySelectorAll('select').forEach(s=>s.value='0');render();}};
document.getElementById('skall').onclick=()=>{{show={{}};saveShow();grid.querySelectorAll('input.ck').forEach(c=>c.checked=true);render();}};
document.getElementById('sknone').onclick=()=>{{ARCH.forEach(a=>show[a.skill]=false);saveShow();grid.querySelectorAll('input.ck').forEach(c=>c.checked=false);render();}};
// non-craft note
document.getElementById('noncraft').innerHTML=NONCRAFT.map(n=>`<div class="nc"><b>${{n.emoji}} ${{n.skill}}</b> — ${{n.how}}</div>`).join('');

// ---- global recipe lookup (searches every recipe, incl. no-XP utility ones) ----
const EMO={{}}; ARCH.forEach(a=>EMO[a.skill]=a.emoji);
const skillLabel=s=>(EMO[s]?EMO[s]+' ':'')+(DISP[s]||s);
const QHEAD=['Recipe','Skill · XP','Req','Makes','Materials','Tools','Time'];
const qhr=document.getElementById('qhr');
QHEAD.forEach((t,i)=>{{const th=document.createElement('th');th.textContent=t;if(i===6)th.style.textAlign='right';qhr.appendChild(th);}});
const dash='<span class=no>–</span>';
const xpStr=r=>{{const e=Object.entries(r.xp);return e.length?e.map(([s,x])=>`<span class="xp">${{esc(skillLabel(s))}} +${{esc(x)}}</span>`).join('<br>'):dash;}};
const reqStr=r=>{{const e=Object.entries(r.req);return e.length?e.map(([s,l])=>`<span class=req>${{esc(DISP[s]||s)}} ${{esc(l)}}</span>`).join('<br>'):dash;}};
const matStr=r=>r.c.length?r.c.map(m=>m.n+'× '+wl(m.l)).join(', '):dash;
const outStr=r=>r.o.length?r.o.map(o=>o.n+'× '+wl(o.l)).join(', '):dash;
const toolStr=r=>r.t.length?`<span class=tool>${{r.t.map(wl).join(', ')}}</span>`:dash;
function runSearch(){{
  const q=document.getElementById('q').value.trim().toLowerCase();
  const hl=document.getElementById('qlearn').checked;
  const sec=document.getElementById('searchSec'), norm=document.getElementById('normal');
  if(!q){{sec.style.display='none';norm.style.display='';document.getElementById('qc').textContent='';return;}}
  const terms=q.split(' ').filter(Boolean);
  let rows=ALLDATA.filter(r=>{{
    if(hl&&r.learn)return false;
    const hay=(r.name+' '+r.o.map(o=>o.l).join(' ')+' '+r.c.map(c=>c.l).join(' ')+' '+r.t.join(' ')+' '+r.skills.join(' ')+' '+(r.cat||'')).toLowerCase();
    return terms.every(t=>hay.includes(t));
  }});
  rows.sort((a,b)=>(Object.values(b.xp).reduce((x,y)=>x+y,0))-(Object.values(a.xp).reduce((x,y)=>x+y,0)) || a.name.localeCompare(b.name));
  const tb=document.querySelector('#qt tbody');tb.innerHTML='';
  for(const r of rows.slice(0,300)){{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td class="rname">${{esc(r.name)}}${{bk(r)}}</td><td>${{xpStr(r)}}</td><td>${{reqStr(r)}}</td><td>${{outStr(r)}}</td><td>${{matStr(r)}}</td><td>${{toolStr(r)}}</td><td class="num">${{r.time==null?'–':r.time}}</td>`;
    tb.appendChild(tr);
  }}
  document.getElementById('qc').textContent=rows.length+' match'+(rows.length===1?'':'es');
  document.getElementById('qlead').innerHTML=rows.length>300?('showing first 300 of '+rows.length+' — refine your search'):'';
  sec.style.display='';norm.style.display='none';
}}
['q','qlearn'].forEach(id=>{{const e=document.getElementById(id);e.addEventListener(e.type==='checkbox'?'change':'input',runSearch);}});

render();
</script></body></html>'''
    open(f'{OUT}/crafting.html','w',encoding='utf-8').write(html)

counts={s:subpage(s) for s,_,_ in ARCH}
index()
print("wrote crafting.html +", len(ARCH), "sub-pages; recipe counts:", counts)
