# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 sp00kz. Dual-licensed; see LICENSE and COMMERCIAL.md.
"""Shared front-end building blocks for the page builders."""
import pzenv
import html as _html

# Author meta tag; omitted unless PZ_AUTHOR is set.
AUTHOR_META = f'<meta name="author" content="{_html.escape(pzenv.AUTHOR, quote=True)}">' if pzenv.AUTHOR else ''

# Footer link to the generator repository; hidden when pzenv.TOOL_URL is "".
TOOL_LINK = (
    f'<div style="margin-top:6px"><a href="{pzenv.TOOL_URL}" target="_blank" rel="noopener" '
    f'style="color:var(--muted);text-decoration:none;border-bottom:1px dotted">'
    f'Generated with the PZ Reference Generator — build your own</a></div>'
) if pzenv.TOOL_URL else ''

# wl() links a display name to pzwiki, applying LINKMAP overrides and splitting 'a/b' labels.
# LINKMAP is consulted before the '/' split: names like "Challenger T/A" are single map keys.
WL_FN = '''function esc(s){return s==null?s:String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function wl(v){if(v==null||v==='')return '';const s=String(v);let key=s.trim();if(key.endsWith(')')){const pi=key.lastIndexOf('(');if(pi>0)key=key.slice(0,pi).trim();}let url;if(Object.prototype.hasOwnProperty.call(LINKMAP,key))url=LINKMAP[key];else if(s.includes('/'))return s.split('/').map(p=>wl(p.trim())).join(' / ');else url=WIKI+encodeURIComponent(key.replace(/ /g,'_'));if(!url)return esc(v);return `<a class="wk" target="_blank" rel="noopener" href="${url}">${esc(v)}</a>`;}'''
WL_JS = '''const WIKI='https://pzwiki.net/wiki/';
const LINKMAP=__LINKMAP__;
''' + WL_FN



# Shared table engine for the JS-table pages; a builder calls buildTable(CFG).
TABLE_JS = r'''function buildTable(CFG){
  const DATA=CFG.data, FILT=CFG.filters||[];
  const dyn=typeof CFG.cols==='function';
  const getCols=()=>dyn?CFG.cols():CFG.cols;
  let sortKey=CFG.sortKey, sortDir=CFG.sortDir;
  const gv=(d,c)=>c&&c.get?c.get(d):d[c.k];
  const hrow=document.getElementById('hrow');
  function header(cols){hrow.innerHTML='';cols.forEach(c=>{const th=document.createElement('th');th.textContent=c.t;th.dataset.k=c.k;
    if(c.num)th.style.textAlign='right';
    th.onclick=()=>{if(sortKey===c.k){sortDir*=-1;}else{sortKey=c.k;sortDir=CFG.pickDir?CFG.pickDir(c):(c.num?-1:1);}render();};
    hrow.appendChild(th);});}
  if(!dyn)header(CFG.cols);
  function render(){
    const cols=getCols();
    if(dyn)header(cols);
    const vals={};
    FILT.forEach(fl=>{const e=document.getElementById(fl.id);vals[fl.id]=e?(e.type==='checkbox'?e.checked:e.value):null;});
    let rows=DATA.filter(d=>FILT.every(fl=>fl.test(d,vals[fl.id])));
    const col=cols.find(c=>c.k===sortKey);
    rows.sort((a,b)=>{let va=col&&col.get?col.get(a):a[sortKey],vb=col&&col.get?col.get(b):b[sortKey];
      if(Array.isArray(va))va=va.join(', ');if(Array.isArray(vb))vb=vb.join(', ');
      if(va==null)va=-Infinity;if(vb==null)vb=-Infinity;
      if(typeof va==='boolean'){va=va?1:0;vb=vb?1:0;}
      if(typeof va==='string')return String(va).localeCompare(String(vb))*sortDir||(CFG.tiebreak?CFG.tiebreak(a,b):0);
      return (va-vb)*sortDir;});
    document.querySelectorAll('th').forEach(th=>{th.className=th.dataset.k===sortKey?(sortDir>0?'sorted-asc':'sorted-desc'):'';});
    const ctx=CFG.ctx?CFG.ctx(rows):undefined;
    const tb=document.querySelector('tbody');tb.innerHTML='';
    for(const d of rows){const tr=document.createElement('tr');
      for(const c of cols){const td=document.createElement('td');if(c.num)td.className='num';if(c.cls)td.className=(td.className+' '+c.cls).trim();
        let raw=gv(d,c);td.innerHTML=c.fmt?c.fmt(raw,d,ctx):(raw==null?'<span class="no">–</span>':esc(raw));tr.appendChild(td);}
      tb.appendChild(tr);
      if(CFG.rowExtra)CFG.rowExtra(d,tr,tb);}
    if(CFG.onRender)CFG.onRender(rows,ctx,cols);
    const cnt=document.getElementById('count');if(cnt)cnt.textContent=CFG.count?CFG.count(rows,ctx):rows.length+' / '+DATA.length+' '+CFG.countNoun;
  }
  FILT.forEach(fl=>{if(fl.manual)return;const e=document.getElementById(fl.id);if(e)e.addEventListener(e.type==='checkbox'?'change':'input',render);});
  if(CFG.onInit)CFG.onInit();
  render();
  return {render, setSort:(k,d)=>{sortKey=k;sortDir=d;}};
}'''


# Site nav definition; nav(active) returns the <nav> markup with the current page marked active.
NAV_TABS = [
    ('map.html', '🗺️ Map'),
    ('index.html', '🏠 Home'), ('seeds.html', '🌱 Seeds'), ('cars.html', '🚗 Vehicles'), ('livestock.html', '🐄 Livestock'),
    ('guns.html', '🔫 Guns'), ('melee.html', '🗡️ Melee'), ('tools.html', '🧰 Tools'),
    ('crafting.html', '🛠️ Crafting'), ('food.html', '🍎 Food'), ('foraging.html', '🌲 Foraging'),
    ('fishing.html', '🎣 Fishing'), ('actions.html', '⭐ Action XP'),
]
def nav(active=''):
    return '<nav>' + ''.join(
        f'<a href="{h}"{" class=\"active\"" if h == active else ""}>{l}</a>'
        for h, l in NAV_TABS) + '</nav>'
