#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, collections

BASE = pzenv.MEDIA
WEAP = f"{BASE}/scripts/generated/items/weapon.txt"
NORM = f"{BASE}/scripts/generated/items/normal.txt"
NAMES = f"{BASE}/lua/shared/Translate/EN/ItemName.json"

names = {}
for m in re.finditer(r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"',
                     open(NAMES, encoding='utf-8', errors='replace').read()):
    names.setdefault(m.group(1), m.group(2))
pzmods.load_mod_item_names(names)
MOD_FILES = pzmods.mod_files('scripts/**/*.txt')

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

# tag -> tool function
TOOLFN = {
    'choptree':'Chop trees', 'cutplant':'Cut plants', 'digplow':'Till soil', 'diggrave':'Dig graves',
    'takedirt':'Dig dirt', 'removestump':'Remove stumps', 'hammer':'Hammer (build)', 'sledgehammer':'Demolish',
    'removebarricade':'Remove barricades', 'crowbar':'Pry', 'screwdriver':'Screwdriver', 'saw':'Saw wood',
    'metalsaw':'Saw metal', 'smallsaw':'Saw (small)', 'butcheranimal':'Butcher', 'sharpknife':'Fine cutting',
    'dullknife':'Cutting', 'clearashes':'Clear ashes', 'takedung':'Collect dung', 'mixingutensil':'Cooking utensil',
    'fishingspear':'Fishing spear', 'write':'Writing', 'whetstone':'Sharpen blades', 'file':'File/sharpen',
    'fleshingtool':'Hide fleshing', 'sewingneedle':'Sewing', 'awl':'Leatherworking', 'drillwood':'Drill wood',
    'drillmetal':'Drill metal', 'drillwoodpoor':'Drill wood', 'knappingtool':'Knapping', 'tongs':'Forge tongs',
    'crudetongs':'Forge tongs', 'scissors':'Cutting (shears)', 'razor':'Shaving', 'smallpunch':'Punch & chisel',
    'masonstrowel':'Masonry', 'spade':'Dig', 'shovel':'Dig', 'generator':'Power generator',
    'sharpenable':None,  # property, not a function
}

def functions(kv):
    tags = [t.split(':')[-1].strip() for t in (kv.get('Tags', '') or '').split(';') if t.strip()]
    fns = []
    for t in tags:
        lbl = TOOLFN.get(t)
        if lbl and lbl not in fns:
            fns.append(lbl)
    return fns

def durab(kv):
    lower = num(kv, 'ConditionLowerChanceOneIn')
    if lower is None: return None, None, None
    cmax = num(kv, 'ConditionMax')
    return (cmax if cmax else 1) * lower, cmax, lower

out = []

# durable tools/equipment from normal.txt (mod files: any non-weapon item)
seen_norm = set()
for src, path in [('Vanilla', NORM)] + MOD_FILES:
  for kv in parse_items(path):
    if src != 'Vanilla' and kv.get('Type') == 'Weapon':
        continue   # weapons handled below
    if kv.get('BodyLocation') or kv.get('ClothingItem'):
        continue   # clothing (B42 mods declare it via ItemType, not Type)
    d, cmax, lower = durab(kv)
    if lower is None:
        continue
    iid = kv['__id__']
    if iid in seen_norm:
        continue   # first definition wins (vanilla parsed first)
    seen_norm.add(iid)
    fns = functions(kv)
    out.append({
        'item': iid, 'name': names.get(iid) or kv.get('DisplayName') or iid,
        'source': src,
        'fn': fns or [kv.get('DisplayCategory', 'Tool')],
        'category': kv.get('DisplayCategory', 'Tool'),
        'durab': d, 'condMax': cmax, 'condLower': lower,
        'weight': num(kv, 'Weight'), 'weapon': False,
    })

# melee weapons that also function as tools
seen_weap = set()
for src, path in [('Vanilla', WEAP)] + MOD_FILES:
  for kv in parse_items(path):
    if src != 'Vanilla' and kv.get('Type') != 'Weapon':
        continue
    if kv.get('Ranged') == 'true' or kv.get('SubCategory') == 'Firearm':
        continue
    fns = functions(kv)
    if not fns:
        continue   # no tool function
    d, cmax, lower = durab(kv)
    iid = kv['__id__']
    if iid in seen_weap:
        continue
    seen_weap.add(iid)
    out.append({
        'item': iid, 'name': names.get(iid) or kv.get('DisplayName') or iid,
        'source': src,
        'fn': fns, 'category': 'Tool-Weapon',
        'durab': d, 'condMax': cmax, 'condLower': lower,
        'weight': num(kv, 'Weight'), 'weapon': True,
    })

# merge identical same-named variants; differentiate when they differ
def sig(x): return (tuple(x['fn']), x['category'], x['durab'], x['condMax'], x['condLower'], x['weight'], x['weapon'])
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
        subs.setdefault(sig(m), []).append(m)
    # a variant group containing a vanilla item links to the wiki, not a mod
    rows = [dict(grp[0], _q=qualifier(grp),
                 source='Vanilla' if any(m['source'] == 'Vanilla' for m in grp) else grp[0]['source'])
            for grp in subs.values()]
    if len(rows) > 1:
        for r in rows:
            r['name'] = f"{name} ({r['_q']})" if r['_q'] else name
        cnt = collections.Counter(r['name'] for r in rows)
        for r in rows:
            if cnt[r['name']] > 1:
                r['name'] = f"{r['name']} (~{r['durab']} durab)"
    for r in rows:
        r.pop('_q', None); r.pop('item', None); merged.append(r)

merged.sort(key=lambda x: -(x['durab'] or 0))
print(f"{len(merged)} tools ({sum(1 for x in merged if x['weapon'])} also weapons)", file=sys.stderr)
json.dump(merged, sys.stdout, separators=(',', ':'))
