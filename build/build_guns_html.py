#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
linkmap_js = pzenv.embed_json(__import__('json').load(open(pzenv.WORK + '/linkmap.json')))
import json, re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import pzschema, pzbuild
guns = pzschema.records('guns')   # load via the schema layer

# weapon attachments / upgrades
BASE = pzenv.MEDIA
PARTF = f"{BASE}/scripts/generated/items/weaponpart.txt"
NAMESF = f"{BASE}/lua/shared/Translate/EN/ItemName.json"
pnames = {}
for m in re.finditer(r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"', open(NAMESF, encoding='utf-8', errors='replace').read()):
    pnames.setdefault(m.group(1), m.group(2))

def parse_blocks(path):
    lines = open(path, encoding='utf-8', errors='replace').readlines()
    i, out = 0, []
    while i < len(lines):
        m = re.match(r'\s*item\s+(\S+)\s*$', lines[i])
        if m:
            name = m.group(1); kv = {}; depth = 0; started = False
            while i < len(lines):
                s = lines[i].strip(); depth += s.count('{') - s.count('}')
                if '{' in s: started = True
                if '=' in s and started:
                    k, v = s.split('=', 1); kv[k.strip()] = v.strip().rstrip(',').strip()
                if started and depth <= 0: break
                i += 1
            kv['id'] = name; out.append(kv)
        i += 1
    return out

def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None
def fmtn(v):
    f = fnum(v)
    if f is None: return str(v)
    return str(int(f)) if f == int(f) else str(f)

SLOT = {'Scope':'Sight / Optic', 'Canon':'Barrel / Rail', 'Sling':'Sling', 'RecoilPad':'Stock'}

def effects(kv):
    e = []  # g: 1 good, -1 bad, 0 neutral
    # suppression is lua-side; the reduction is only stated in the item Tooltip
    m = re.search(r'soundradius\s*:\s*(-\d+%?)', kv.get('Tooltip', '') or '', re.I)
    if m:
        e.append({'t': f"{m.group(1)} sound radius", 'g': 1})
    if 'MaxSightRange' in kv:
        e.append({'t': f"Sight range {fmtn(kv.get('MinSightRange','?'))}–{fmtn(kv['MaxSightRange'])} tiles", 'g': 1})
    at = fnum(kv.get('AimingTimeModifier'))
    if at:
        e.append({'t': ('Faster aim' if at < 0 else 'Slower aim') + f" ({'+' if at>0 else ''}{fmtn(kv['AimingTimeModifier'])})", 'g': 1 if at < 0 else -1})
    if fnum(kv.get('HitChanceModifier')):
        e.append({'t': f"+{fmtn(kv['HitChanceModifier'])} hit chance", 'g': 1})
    rd = fnum(kv.get('RecoilDelayModifier'))
    if rd:
        e.append({'t': f"{fmtn(kv['RecoilDelayModifier'])} recoil delay", 'g': 1 if rd < 0 else -1})
    rt = fnum(kv.get('ReloadTimeModifier'))
    if rt:
        e.append({'t': f"{fmtn(kv['ReloadTimeModifier'])} reload time", 'g': 1 if rt < 0 else -1})
    ps = fnum(kv.get('ProjectileSpreadModifier'))
    if ps:
        e.append({'t': f"Tighter pellet spread ({fmtn(kv['ProjectileSpreadModifier'])})", 'g': 1 if ps < 0 else -1})
    if fnum(kv.get('MaxRangeModifier')):
        e.append({'t': f"+{fmtn(kv['MaxRangeModifier'])} range", 'g': 1})
    if 'LightDistance' in kv or 'TorchCone' in kv:
        e.append({'t': 'Adds flashlight beam', 'g': 1})
    wt = fnum(kv.get('WeightModifier'))
    if wt:
        e.append({'t': f"+{fmtn(kv['WeightModifier'])} weight", 'g': 0})
    return e

parts, pslot, psrc = [], {}, {}
def add_part(kv, src):
    mount = [x.strip().replace('Base.', '') for x in (kv.get('MountOn', '') or '').split(';') if x.strip()]
    rec = {'id': kv['id'], 'name': pnames.get(kv['id']) or kv.get('DisplayName') or kv['id'],
           'slot': SLOT.get(kv.get('PartType',''), kv.get('PartType','Other')),
           'mount': mount, 'effects': effects(kv)}
    at = pslot.get(kv['id'])
    if at is None:
        pslot[kv['id']] = len(parts); psrc[kv['id']] = src; parts.append(rec)
    elif src != 'Vanilla' and psrc[kv['id']] == 'Vanilla':
        parts[at] = rec; psrc[kv['id']] = src   # mod redefinition wins (game load order)

for kv in parse_blocks(PARTF):
    add_part(kv, 'Vanilla')
import pzmods
for src, path in pzmods.mod_files('scripts/**/*.txt'):
    for kv in parse_blocks(path):
        if kv.get('MountOn') and kv.get('PartType'):   # weapon parts only
            add_part(kv, src)

for g in guns:
    ups = [{'name': p['name'], 'slot': p['slot'], 'effects': p['effects']} for p in parts if g['item'] in p['mount']]
    ups.sort(key=lambda u: (u['slot'], u['name']))
    g['upgrades'] = ups
    g['_up'] = len(ups)

NAV = pzbuild.nav('guns.html')

html = r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Project Zomboid firearms reference: damage, range, attachments and upgrades (scopes, suppressors) and durability. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="keywords" content="Project Zomboid, Build 42, B42, 42.19.0, PZ, Project Zomboid reference, guns, firearms, weapons, attachments, scopes, suppressors, durability">
<meta name="robots" content="index, follow">
__AUTHOR__
<meta property="og:type" content="website">
<meta property="og:title" content="Project Zomboid Build 42.19.0 — Firearms">
<meta property="og:description" content="Project Zomboid firearms reference: damage, range, attachments and upgrades (scopes, suppressors) and durability. Game version 42.19.0 (unstable branch, 2026-06-01); data parsed directly from the Project Zomboid game files.">
<meta name="pz:gameversion" content="42.19.0">
<meta name="pz:branch" content="unstable">
<meta name="pz:builddate" content="2026-06-01">
<title>Project Zomboid — Firearms (Build 42.19.0)</title>
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
  table { border-collapse:collapse; width:100%; min-width:1000px; }
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
  .tag.Shotgun { background:#3a2a22; color:var(--accent); }
  .tag.Rifle,.tag.AssaultRifle { background:#2a3a22; color:var(--green); }
  .tag.Revolver,.tag.Pistol { background:#3a2a40; color:#b98fd0; }
  .bar { display:inline-block; height:8px; background:var(--accent); border-radius:2px; vertical-align:middle; opacity:.75; }
  .no { color:#5a5346; }
  .uptag { color:var(--accent); font-weight:600; }
  .upslots { color:var(--muted); font-size:11px; }
  tr.hasup { cursor:pointer; }
  tr.hasup.open { background:#2a2418; }
  tr.hasup.open .uptag { color:var(--green); }
  .uprow td { white-space:normal; background:#181410; border-bottom:2px solid var(--line); }
  .updetail { display:flex; flex-wrap:wrap; gap:8px 22px; padding:8px 6px 10px; }
  .slot { min-width:200px; }
  .slotname { color:var(--accent); font-size:11px; text-transform:uppercase; letter-spacing:.4px; margin-bottom:4px; border-bottom:1px solid var(--line); padding-bottom:2px; }
  .upitem { font-size:12px; padding:3px 0; }
  .upitem b { color:var(--txt); }
  .eff { display:inline-block; font-size:11px; padding:0 6px; border-radius:6px; margin:1px 2px; }
  .eff.good { background:#21331f; color:var(--green); }
  .eff.bad { background:#3a2622; color:#d08a7a; }
  .eff.neu { background:#2a2620; color:var(--muted); }
  footer { padding:12px 20px; color:var(--muted); font-size:11px; border-top:1px solid var(--line); flex:none; }
  code { color:var(--accent); }
  .wk{color:inherit;text-decoration:none;border-bottom:1px dotted #6b5f48;}
  .wk:hover{color:var(--accent);border-bottom-color:var(--accent);}
</style></head><body>
<header>__NAV__
  <h1>Project Zomboid — Firearms</h1>
  <div class="sub">Build 42.19.0 · parsed from <code>scripts/generated/items/weapon.txt</code>. Click a column to sort.</div>
<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">Game data: <b style="color:var(--accent)">Project Zomboid Build 42.19.0</b> · unstable branch · built 2026-06-01</div>
</header>
<div class="controls">
  <input type="search" id="q" placeholder="Filter by name or ammo…" autocomplete="off">
  <select id="cls"><option value="">All classes</option></select>
  <select id="ammo"><option value="">All ammo</option></select>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><table id="tbl"><thead><tr id="hrow"></tr></thead><tbody></tbody></table></div>
<footer>
  <b>Damage</b> min–max per shot · <b>Range</b> max effective tiles · <b>Hit%</b> base hit chance · <b>Crit%</b> critical chance ·
  <b>Recoil</b> delay between shots (lower = faster follow-up) · <b>Aim</b> time to steady · <b>Noise</b> sound radius (higher = attracts more zombies) ·
  <b>Durab</b> ≈ shots before it breaks (ConditionMax × condition-loss rarity) ·
  <b>Upgrades</b> = attachments that fit this gun (scopes, red dots, lasers, choke tubes, recoil pads, slings) — <b>click a row to see each attachment and its effect</b>.
  Stats are base values before aiming skill, attachments, and condition.__SUPNOTE__
__TOOLLINK__</footer>
<script>
const DATA = __DATA__;
__WLJS__
const COLS = [
  {k:'name', t:'Firearm', fmt:(v,d)=>`<span class="name">${wl(v)}</span>`},
  {k:'category', t:'Class', fmt:v=>`<span class="tag ${esc(v).replace(' ','')}">${esc(v)}</span>`},
  {k:'ammo', t:'Ammo'},
  {k:'maxDmg', t:'Damage', num:true, fmt:(v,d)=>{let h=`${d.minDmg}\u2013${d.maxDmg}`;if(v!=null){const w=Math.round(40*v/maxDmg);h+=` <span class="bar" style="width:${w}px"></span>`;}return h;}},
  {k:'maxRange', t:'Range', num:true},
  {k:'mag', t:'Mag', num:true},
  {k:'hitChance', t:'Hit %', num:true},
  {k:'critChance', t:'Crit %', num:true},
  {k:'recoil', t:'Recoil', num:true},
  {k:'aimTime', t:'Aim', num:true},
  {k:'reload', t:'Reload', num:true},
  {k:'projectiles', t:'Pellets', num:true},
  {k:'noise', t:'Noise', num:true},
  {k:'durab', t:'Durab', num:true, fmt:(v)=>v==null?'<span class="no">\u2013</span>':v},
  {k:'weight', t:'Wt', num:true},
  {k:'_up', t:'Upgrades', num:true, fmt:(v,d)=>{
    if(!d.upgrades||!d.upgrades.length)return '<span class="no">\u2013</span>';
    const slots=[...new Set(d.upgrades.map(u=>u.slot))];
    return `<span class="uptag">\u25b8 ${d.upgrades.length}</span> <span class="upslots">${slots.map(esc).join(' \u00b7 ')}</span>`;}},
];
function fill(sel,vals){vals.forEach(v=>{if(v==null)return;const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);});}
fill(document.getElementById('cls'), [...new Set(DATA.map(d=>d.category))].sort());
fill(document.getElementById('ammo'), [...new Set(DATA.map(d=>d.ammo))].filter(Boolean).sort());
const maxDmg=Math.max(...DATA.map(d=>d.maxDmg||0));
function upDetail(d){
  const bySlot={};d.upgrades.forEach(u=>{(bySlot[u.slot]=bySlot[u.slot]||[]).push(u);});
  let h='<div class="updetail">';
  for(const slot of Object.keys(bySlot)){
    h+=`<div class="slot"><div class="slotname">${esc(slot)}</div>`;
    for(const u of bySlot[slot]){
      const eff=u.effects.map(e=>`<span class="eff ${e.g>0?'good':e.g<0?'bad':'neu'}">${esc(e.t)}</span>`).join(' ');
      h+=`<div class="upitem"><b>${esc(u.name)}</b> ${eff||''}</div>`;
    }
    h+='</div>';
  }
  return h+'</div>';
}
__TABLE_JS__
buildTable({
  data:DATA, cols:COLS, sortKey:'maxDmg', sortDir:-1, countNoun:'firearms',
  rowExtra:(d,tr,tb)=>{
    if(d.upgrades&&d.upgrades.length){tr.classList.add('hasup');
      const dr=document.createElement('tr');dr.className='uprow';dr.style.display='none';
      const td=document.createElement('td');td.colSpan=COLS.length;td.innerHTML=upDetail(d);
      dr.appendChild(td);tb.appendChild(dr);
      tr.onclick=()=>{const open=dr.style.display==='none';dr.style.display=open?'':'none';tr.classList.toggle('open',open);};
    }},
  filters:[
    {id:'q', test:(d,v)=>!v||((d.name+' '+(d.ammo||'')).toLowerCase().includes(v.toLowerCase()))},
    {id:'cls', test:(d,v)=>!v||d.category===v},
    {id:'ammo', test:(d,v)=>!v||d.ammo===v},
  ],
});
</script></body></html>'''
data_js = pzenv.embed_json(guns)
# suppressors exist only via mods; note their absence when none are installed
supnote = '' if any('uppressor' in p['name'] for p in parts) else ' Vanilla B42 has no suppressors.'
html = html.replace('__NAV__', NAV).replace('__DATA__', data_js).replace('__WLJS__', pzbuild.WL_JS).replace('__TABLE_JS__', pzbuild.TABLE_JS).replace('__LINKMAP__', linkmap_js).replace('__AUTHOR__', pzbuild.AUTHOR_META).replace('__TOOLLINK__', pzbuild.TOOL_LINK).replace('__SUPNOTE__', supnote)
open(pzenv.REPO + '/guns.html','w',encoding='utf-8').write(html)
nup = sum(1 for g in guns if g['upgrades'])
print(f"Wrote guns.html ({len(html)} bytes, {len(guns)} firearms, {nup} with upgrades, {len(parts)} parts)")
