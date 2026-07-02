#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys

BASE = pzenv.MEDIA
WEAP = f"{BASE}/scripts/generated/items/weapon.txt"
NAMES = f"{BASE}/lua/shared/Translate/EN/ItemName.json"

names = {}
for m in re.finditer(r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"',
                     open(NAMES, encoding='utf-8', errors='replace').read()):
    names.setdefault(m.group(1), m.group(2))
pzmods.load_mod_item_names(names)

def parse_items(path):
    lines = open(path, encoding='utf-8', errors='replace').readlines()
    i, n, out = 0, len(lines), []
    while i < n:
        m = re.match(r'\s*item\s+([A-Za-z0-9_]+)\s*$', lines[i])
        if m:
            name = m.group(1); kv = {}; depth = 0; started = False
            while i < n:
                s = lines[i].strip(); depth += s.count('{') - s.count('}')
                if '{' in s: started = True
                if '=' in s and started:
                    k, v = s.split('=', 1); kv[k.strip()] = v.strip().rstrip(',').strip()
                if started and depth <= 0: break
                i += 1
            kv['__id__'] = name; out.append(kv)
        i += 1
    return out

def num(kv, key):
    v = kv.get(key)
    if v is None: return None
    try: return float(v) if '.' in v else int(v)
    except ValueError: return None

CAT = {'axe':'Axe', 'blunt':'Long Blunt', 'smallblunt':'Short Blunt',
       'longblade':'Long Blade', 'smallblade':'Short Blade', 'spear':'Spear',
       'improvised':'Improvised', 'unarmed':'Unarmed'}
def category(kv):
    cats = [c.split(':')[-1] for c in (kv.get('Categories', '') or '').split(';') if c.strip()]
    friendly = [CAT.get(c, c.title()) for c in cats]
    # prefer a real skill category over 'Improvised' when both present
    real = [f for f in friendly if f != 'Improvised']
    return (real[0] if real else (friendly[0] if friendly else 'Improvised'))

def r1(v):
    return None if v is None else round(v, 2)

out = []
seen_ids = set()
for src, path in [('Vanilla', WEAP)] + pzmods.mod_files('scripts/**/*.txt'):
  for kv in parse_items(path):
    if kv.get('Ranged') == 'true' or kv.get('SubCategory') == 'Firearm':
        continue
    mn, mx = num(kv, 'MinDamage'), num(kv, 'MaxDamage')
    if mn is None and mx is None:
        continue
    iid = kv['__id__']
    if iid in seen_ids:              # first definition wins (vanilla parsed first)
        continue
    seen_ids.add(iid)
    swing = num(kv, 'Swingtime')
    cmax = num(kv, 'ConditionMax'); clower = num(kv, 'ConditionLowerChanceOneIn')
    durab = (cmax * clower) if (cmax is not None and clower is not None) else None
    avg = (mn + mx) / 2 if (mn is not None and mx is not None) else None
    dps = (avg / swing) if (avg is not None and swing) else None
    out.append({
        'item': iid,
        'name': names.get(iid) or kv.get('DisplayName') or iid,
        'source': src,
        'category': category(kv),
        'sub': kv.get('SubCategory'),
        'minDmg': r1(mn), 'maxDmg': r1(mx), 'avg': r1(avg),
        'dps': r1(dps),
        'range': num(kv, 'MaxRange'), 'minRange': num(kv, 'MinRange'),
        'swing': swing, 'minSwing': num(kv, 'MinimumSwingtime'),
        'hits': num(kv, 'MaxHitcount'),
        'crit': num(kv, 'CriticalChance'), 'critMult': num(kv, 'CritDmgMultiplier'),
        'knock': num(kv, 'KnockdownMod'),
        'condMax': cmax, 'condLower': clower, 'durab': durab,
        'door': num(kv, 'DoorDamage'), 'tree': num(kv, 'TreeDamage'),
        'twoH': kv.get('TwoHandWeapon') == 'true' or kv.get('RequiresEquippedBothHands') == 'true',
        'length': num(kv, 'WeaponLength'),
        'weight': num(kv, 'Weight'),
    })

import collections
# merge statistically identical same-named variants; differentiate when stats differ
def statsig(x):
    return (x['category'], x['minDmg'], x['maxDmg'], x['range'], x['swing'], x['minSwing'], x['hits'],
            x['crit'], x['critMult'], x['knock'], x['durab'], x['condMax'], x['condLower'],
            x['door'], x['tree'], x['twoH'], x['weight'])

def qualifier(grp):
    ids = ' '.join(m['item'] for m in grp).lower()
    if 'forged' in ids: return 'forged'
    if 'old' in ids: return 'old'
    return ''

byname = collections.OrderedDict()
for x in out:
    byname.setdefault(x['name'], []).append(x)

merged = []
for name, members in byname.items():
    subs = collections.OrderedDict()
    for m in members:
        subs.setdefault(statsig(m), []).append(m)
    # a variant group containing a vanilla item links to the wiki, not a mod
    rows = [dict(grp[0], _q=qualifier(grp),
                 source='Vanilla' if any(m['source'] == 'Vanilla' for m in grp) else grp[0]['source'])
            for grp in subs.values()]
    if len(rows) > 1:
        for r, grp in zip(rows, subs.values()):
            r['name'] = f"{name} ({r['_q']})" if r['_q'] else name
        # disambiguate remaining name collisions by durability
        cnt = collections.Counter(r['name'] for r in rows)
        for r in rows:
            if cnt[r['name']] > 1:
                r['name'] = f"{r['name']} (~{r['durab']} durab)"
    for r in rows:
        r.pop('_q', None); merged.append(r)

merged.sort(key=lambda x: (x['category'], -(x['avg'] or 0)))
print(f"{len(out)} raw -> {len(merged)} melee weapons; cats: {sorted({x['category'] for x in merged})}", file=sys.stderr)
json.dump(merged, sys.stdout, separators=(',', ':'))
