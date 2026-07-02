#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
import pzschema, pzbuild

payload = {'items': pzschema.records('food'), 'recipes': pzschema.load_raw('food')['recipes']}
food = payload['items']

NAV = pzbuild.nav('food.html')

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid food and nutrition: hunger and thirst restored, calories, carbs, fat, protein, mood effects and spoilage for every food. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, food, nutrition, calories, hunger, thirst, cooking, spoilage">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Food & Nutrition">
<meta property="og:description" content="Project Zomboid food and nutrition: hunger and thirst restored, calories, carbs, fat, protein, mood effects and spoilage for every food. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Food &amp; Nutrition (Build 42.19.0)</title>
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
  .fdesc { color:var(--muted); font-size:11px; font-style:italic; margin-top:1px; white-space:normal; max-width:280px; }
  .cap { padding:10px 20px; background:#1b2418; border-bottom:1px solid var(--line); color:var(--txt); font-size:13px; flex:none; }
  .cap b { color:var(--accent); }
  .tag { display:inline-block; padding:1px 7px; border-radius:10px; font-size:11px; background:#2a3340; color:var(--blue); }
  .bar { display:inline-block; height:8px; background:var(--accent); border-radius:2px; vertical-align:middle; opacity:.7; margin-left:4px; }
  .good { color:var(--green); } .bad { color:var(--red); }
  .ic { font-size:13px; }
  .no { color:#5a5346; }
  footer { padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Food &amp; Nutrition</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>scripts/generated/items/food.txt</code>. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by food name…" autocomplete="off">
  <select id="type"><option value="">All types</option></select>
  <select id="recipe"><option value="">— Recipe ingredient breakdown —</option></select>
  <label class="sub"><input type="checkbox" id="cook"> cookable only</label>
  <span class="count" id="count"></span>
</div>
<div id="cap" class="cap" style="display:none"></div>
<div class="wrap"><table id="tbl"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  <b>Hunger / Thirst</b> = how much of that need eating restores (higher = more filling) ·
  <b>Cal</b> calories · <b>Carbs / Fat / Protein</b> in grams ·
  <b>Mood</b> = unhappiness change when eaten (<span class="good">green reduces</span>, <span class="bad">red raises</span>) ·
  <b>Fresh</b> days until it starts spoiling · <b>Rots</b> days until fully rotten (blank = non-perishable) ·
  🍳 cookable · ⚠ dangerous raw. Values are for a fresh, full item before traits/spoilage.
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
const RECIPES = __RECIPES__;
const RLABEL={'Stir fry':'Stir Fry','ConeIcecream':'Ice Cream Cone','PieSweet':'Sweet Pie','HotDrink':'Hot Drink','FruitSalad':'Fruit Salad','AddBaitToChum':'Chum (fishing bait)'};
const REMO={Pizza:'🍕',Soup:'🥣',Stew:'🍲',Salad:'🥗',Burger:'🍔',Sandwich:'🥪',Taco:'🌮',Burrito:'🌯',Pasta:'🍝',Rice:'🍚',Omelette:'🍳',Pie:'🥧',Cake:'🍰',Toast:'🍞',Bread:'🍞',Pancakes:'🥞',Hotdog:'🌭',Muffin:'🧁',Oatmeal:'🥣',HotDrink:'☕','ConeIcecream':'🍦',PieSweet:'🥧',FruitSalad:'🥗',AddBaitToChum:'🎣'};
const rlabel=r=>RLABEL[r]||r;
const f = v => v==null ? '<span class="no">–</span>' : (Number.isInteger(v) ? v : Math.round(v*10)/10);
const fr = (v,hi) => v==null ? '<span class="no">–</span>' : (hi!=null&&hi!==v ? `${v}–${hi}` : v);
const moodCell = v => v==null ? '<span class="no">–</span>' : `<span class="${v<0?'good':v>0?'bad':''}">${v<0?'':'+'}${v}</span>`;
const calFmt=(v,d,ctx)=>{let h=f(v);if(v!=null){const w=Math.round(40*v/ctx.mx);h+=`<span class="bar" style="width:${w}px"></span>`;}return h;};
const COLS = [
  {k:'name', t:'Food', fmt:(v,d)=>`<span class="name">${wl(v)}</span>${d.desc?`<div class="fdesc">${esc(d.desc)}</div>`:''}`},
  {k:'category', t:'Type', fmt:v=>`<span class="tag">${esc(v)}</span>`},
  {k:'hunger', t:'Hunger', num:true, fmt:f},
  {k:'cal', t:'Cal', num:true, fmt:calFmt},
  {k:'carb', t:'Carbs', num:true, fmt:f},
  {k:'fat', t:'Fat', num:true, fmt:f},
  {k:'prot', t:'Protein', num:true, fmt:f},
  {k:'thirst', t:'Thirst', num:true, fmt:f},
  {k:'unhappy', t:'Mood', num:true, fmt:moodCell},
  {k:'fresh', t:'Fresh', num:true, fmt:(v,d)=>fr(v,d.freshMax)},
  {k:'rot', t:'Rots', num:true, fmt:(v,d)=>fr(v,d.rotMax)},
  {k:'weight', t:'Wt', num:true, fmt:f},
  {k:'cook', t:'Cook', fmt:(v,d)=>`${v?'<span class="ic" title="cookable">\ud83c\udf73</span>':''}${d.raw?' <span class="ic bad" title="dangerous uncooked">\u26a0</span>':''}`||'<span class="no">\u2013</span>'},
];
const NUTR=new Set(['hunger','cal','carb','fat','prot','thirst']);
function perAdd(d,k,cur){
  const ev=d.ev[cur]; if(ev==null)return null;
  if(k==='hunger')return ev;
  const base=d.hunger; const pct=(base&&base>0)?ev/base:1;
  const v=d[k]; return v==null?null:Math.round(v*pct*100)/100;
}
const pa=k=>d=>perAdd(d,k,curRecipe());
const RCOLS=[
  COLS[0],
  {k:'category', t:'Type', fmt:v=>`<span class="tag">${esc(v)}</span>`},
  {k:'hunger', t:'+ Hunger', num:true, get:pa('hunger'), fmt:f},
  {k:'cal', t:'+ Cal', num:true, get:pa('cal'), fmt:calFmt},
  {k:'carb', t:'+ Carbs', num:true, get:pa('carb'), fmt:f},
  {k:'fat', t:'+ Fat', num:true, get:pa('fat'), fmt:f},
  {k:'prot', t:'+ Protein', num:true, get:pa('prot'), fmt:f},
  {k:'thirst', t:'+ Thirst', num:true, get:pa('thirst'), fmt:f},
];
function fill(sel,vals){vals.forEach(v=>{if(v==null)return;const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});}
fill(document.getElementById('type'), [...new Set(DATA.map(d=>d.category))].sort());
const rsel=document.getElementById('recipe');
RECIPES.forEach(r=>{const o=document.createElement('option');o.value=r;o.textContent=(REMO[r]?REMO[r]+' ':'')+rlabel(r);rsel.appendChild(o);});
function curRecipe(){return rsel.value;}
__TABLE_JS__
const T=buildTable({
  data:DATA, sortKey:'cal', sortDir:-1,
  cols:()=>curRecipe()?RCOLS:COLS,
  ctx:rows=>{const cur=curRecipe();return {mx:Math.max(1,...rows.map(d=>(cur?perAdd(d,'cal',cur):d.cal)||0))};},
  count:(rows)=>{const cur=curRecipe();return cur?(rows.length+' ingredients'):(rows.length+' / '+DATA.length+' foods');},
  onRender:(rows)=>{
    const cur=curRecipe();const cap=document.getElementById('cap');
    if(cur&&rows.length){
      const top=rows.reduce((m,r)=>(perAdd(r,'cal',cur)||0)>(perAdd(m,'cal',cur)||0)?r:m,rows[0]);
      cap.style.display='';
      cap.innerHTML=`${REMO[cur]||'\ud83c\udf7d\ufe0f'} <b>${esc(rlabel(cur))}</b> \u2014 values show what <b>one</b> of each ingredient adds to the dish. Hunger is set by the recipe; calories &amp; macros scale to that hunger (a fraction of the whole item). Most calories per add: <b>${esc(top.name)}</b> (+${f(perAdd(top,'cal',cur))} cal for +${esc(top.ev[cur])} hunger).`;
    }else{cap.style.display='none';}
  },
  filters:[
    {id:'q', test:(d,v)=>!v||d.name.toLowerCase().includes(v.toLowerCase())},
    {id:'type', test:(d,v)=>!v||d.category===v},
    {id:'cook', test:(d,v)=>!v||d.cook},
    {id:'recipe', manual:true, test:(d,v)=>!v||d.ev[v]!=null},
  ],
});
rsel.addEventListener('change',()=>{if(curRecipe()){T.setSort('cal',-1);}T.render();});
</script></body></html>'''
data_js = pzenv.embed_json(food)
recipes_js = pzenv.embed_json(payload['recipes'])
html = html.replace('__NAV__', NAV).replace('__DATA__', data_js).replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__RECIPES__', recipes_js).replace('__TOOLLINK__', pzbuild.TOOL_LINK)
open(pzenv.REPO + '/food.html', 'w', encoding='utf-8').write(html)
print(f"Wrote food.html ({len(html)} bytes, {len(food)} foods, {len(payload['recipes'])} recipes)")
