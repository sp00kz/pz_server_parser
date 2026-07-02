#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys

BASE = pzenv.MEDIA
FOOD = f"{BASE}/scripts/generated/items/food.txt"
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

# generic-named foraged species -> real identity
OVERRIDE = {
    'BerryBlack':'Blackberry', 'BerryBlue':'Blueberry', 'BeautyBerry':'Beautyberry',
    'WinterBerry':'Winterberry', 'HollyBerry':'Holly Berry', 'BerryPoisonIvy':'Poison Ivy Berries',
    'BerryGeneric1':'Wild Berries', 'BerryGeneric2':'Wild Berries', 'BerryGeneric3':'Wild Berries',
    'BerryGeneric4':'Wild Berries', 'BerryGeneric5':'Wild Berries',
}
def dispname(iid, kv=None):
    return OVERRIDE.get(iid) or names.get(iid) or (kv or {}).get('DisplayName') or iid

def neg(kv, key):
    """Return the stat negated (positive = need restored)."""
    v = num(kv, key)
    return None if v is None else -v

CONTAINER = {
    'Saucepan':'saucepan', 'SaucepanCopper':'copper saucepan',
    'Pot':'pot', 'PotForged':'forged pot', 'PotCopper':'copper pot',
    'Pan':'pan', 'PanForged':'forged pan', 'PanCopper':'copper pan', 'Pan, Frying':'frying pan',
    'GriddlePan':'griddle pan', 'RoastingPan':'roasting pan', 'BakingTray':'baking tray',
    'Bowl':'bowl', 'ClayBowl':'clay bowl', 'BowlBamboo':'bamboo bowl',
    'Mug':'mug', 'Cup':'cup', 'Glass':'glass', 'Bottle':'bottle', 'Jar':'jar',
}
def vessel(kv):
    return CONTAINER.get(kv.get('ReplaceOnUse', '').replace('Base.', ''))

def is_serving(v):
    return bool(v) and any(w in v for w in ('bowl', 'mug', 'cup', 'glass'))

def notes(kv):
    """Return state notes for an item."""
    iid = kv['__id__']; ns = []
    tags = kv.get('Tags', '') or ''
    if iid.startswith('Water') and ('Pot' in iid or 'Saucepan' in iid or 'Pan' in iid):
        ns.append('water')   # 'cooking in water' marker
    if 'driedfood' in tags:
        ns.append('dried & uncooked — cook before eating (eaten dry it dehydrates you)')
    elif kv.get('Packaged') == 'true' and kv.get('IsCookable') != 'true' and not kv.get('EatType'):
        ns.append('uncooked, full package')
    if kv.get('Spice') == 'true':
        ns.append('used as a seasoning')
    if kv.get('DangerousUncooked') == 'true':
        ns.append('dangerous if eaten raw')
    if kv.get('CannedFood') == 'true':
        ns.append('canned')
    if iid.endswith('Whole'):
        ns.append('whole item (slice it for portions)')
    elif iid.endswith('Recipe'):
        ns.append('assembled dish, ready to cook')
    return ns

def evolved(kv):
    """Parse EvolvedRecipe into {recipe: hunger-contribution}."""
    out = {}
    for part in (kv.get('EvolvedRecipe', '') or '').split(';'):
        m = re.match(r'\s*(.+?):(\d+)', part)
        if m:
            out[m.group(1).strip()] = int(m.group(2))
    return out

out = []
seen_ids = set()
for src, path in [('Vanilla', FOOD)] + pzmods.mod_files('scripts/**/*.txt'):
  for kv in parse_items(path):
    cal = num(kv, 'Calories'); hung = num(kv, 'HungerChange')
    if cal is None and hung is None:   # skip non-nutritive entries
        continue
    iid = kv['__id__']
    if iid in seen_ids:                # first definition wins (vanilla parsed first)
        continue
    seen_ids.add(iid)
    out.append({
        'id': iid,
        'name': dispname(iid, kv),
        'source': src,
        'category': kv.get('FoodType') or kv.get('DisplayCategory') or '—',
        'hunger': neg(kv, 'HungerChange'),      # positive = hunger restored
        'thirst': neg(kv, 'ThirstChange'),      # positive = thirst restored
        'cal': cal,
        'carb': num(kv, 'Carbohydrates'),
        'fat': num(kv, 'Lipids'),
        'prot': num(kv, 'Proteins'),
        'unhappy': num(kv, 'UnhappyChange'),    # negative = reduces unhappiness
        'stress': num(kv, 'StressChange'),      # negative = reduces stress
        'fresh': num(kv, 'DaysFresh'),
        'rot': num(kv, 'DaysTotallyRotten'),
        'cook': kv.get('IsCookable') == 'true',
        'raw': kv.get('DangerousUncooked') == 'true',
        'weight': num(kv, 'Weight'),
        'ev': evolved(kv),
        '_vessel': vessel(kv),
        '_notes': notes(kv),
    })

import collections
# merge same food + identical nutrition, differing only by cookware
def sig(x):
    # signature: food + nutrition; spoilage may differ, perishability may not
    return (x['name'], x['hunger'], x['thirst'], x['cal'], x['carb'], x['fat'],
            x['prot'], x['unhappy'], x['stress'], x['cook'], x['raw'], x['rot'] is not None)

groups = collections.OrderedDict()
for x in out:
    groups.setdefault(sig(x), []).append(x)

def build_desc(members):
    vessels = []
    for m in members:
        if m['_vessel'] and m['_vessel'] not in vessels:
            vessels.append(m['_vessel'])
    nlist = []
    for m in members:
        for n in m['_notes']:
            if n not in nlist: nlist.append(n)
    water = 'water' in nlist
    nlist = [n for n in nlist if n != 'water']
    parts = []
    if vessels:
        verb = 'uncooked, cooking in water in' if water else ('served in' if is_serving(vessels[0]) else 'cooked in')
        parts.append(f'{verb} a {vessels[0]}' if len(vessels) == 1 else f'{verb}: ' + ', '.join(vessels))
    elif water:
        parts.append('uncooked, cooking in water')
    parts += nlist
    return ', '.join(parts)

def rng(members, key):
    vals = [m[key] for m in members if m[key] is not None]
    if not vals: return None, None
    lo, hi = min(vals), max(vals)
    return lo, (hi if hi != lo else None)

merged = []
for members in groups.values():
    base = {k: v for k, v in members[0].items() if not k.startswith('_')}
    if any(m['source'] == 'Vanilla' for m in members):
        base['source'] = 'Vanilla'   # wiki link over mod link for mixed groups
    ev = {}
    for m in members:
        ev.update(m['ev'])
    base['ev'] = ev
    base['fresh'], base['freshMax'] = rng(members, 'fresh')
    base['rot'], base['rotMax'] = rng(members, 'rot')
    base['weight'] = min([m['weight'] for m in members if m['weight'] is not None], default=base.get('weight'))
    base['desc'] = build_desc(members)
    base['variants'] = len(members)
    merged.append(base)

merged.sort(key=lambda x: (x['category'], x['name']))
rc = collections.Counter()
for x in merged:
    for r in x['ev']: rc[r] += 1
recipes = sorted([r for r, n in rc.items() if n >= 5], key=lambda r: -rc[r])
print(f"{len(out)} raw -> {len(merged)} merged food items; {len(recipes)} recipes", file=sys.stderr)
json.dump({'items': merged, 'recipes': recipes}, sys.stdout, separators=(',', ':'))
