#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys

BASE = pzenv.MEDIA + "/lua/server/Farming"
FILES = {
    "Vegetable": f"{BASE}/farming_vegetableconf_vegetables.lua",
    "Herb": f"{BASE}/farming_vegetableconf_herbs.lua",
}

prop_start = re.compile(r'farming_vegetableconf\.props(?:\.([A-Za-z0-9_]+)|\["([^"]+)"\])\s*=\s*\{')

def parse_value(v):
    v = v.strip().rstrip(',').strip()
    if v.startswith('{'):
        inner = v.strip('{}').strip()
        # list of quoted strings?
        strs = re.findall(r'"([^"]+)"', inner)
        if strs:
            return strs
        nums = re.findall(r'-?\d+', inner)
        return [int(n) for n in nums]
    if v.startswith('"'):
        return v.strip('"')
    if v in ('true', 'false'):
        return v == 'true'
    try:
        if '.' in v:
            return float(v)
        return int(v)
    except ValueError:
        return v

def parse_file(path, category, source='Vanilla'):
    seeds = []
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    i = 0
    n = len(lines)
    while i < n:
        m = prop_start.search(lines[i])
        # ignore matches on commented lines
        if m and not lines[i].lstrip().startswith('--'):
            name = m.group(1) or m.group(2)
            block = {}
            i += 1
            while i < n and lines[i].strip() != '}':
                ln = lines[i]
                stripped = ln.lstrip()
                if not stripped.startswith('--'):
                    kv = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$', ln)
                    if kv:
                        key = kv.group(1)
                        val = parse_value(kv.group(2))
                        block[key] = val  # last assignment wins
                i += 1
            block['_name'] = name
            block['_category'] = category
            block['_source'] = source
            seeds.append(block)
        i += 1
    return seeds

all_seeds = []
for cat, path in FILES.items():
    all_seeds += parse_file(path, cat)
# mod crops: any farming lua defining farming_vegetableconf.props blocks
for mod, path in pzmods.mod_files('lua/server/Farming/*.lua'):
    cat = 'Herb' if 'herb' in path.lower() else 'Vegetable'
    all_seeds += parse_file(path, cat, mod)
seen_names = set()
all_seeds = [s for s in all_seeds
             if not (s['_name'] in seen_names or seen_names.add(s['_name']))]

MONTHS = ['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def months(lst):
    if not lst: return []
    return [MONTHS[x] for x in lst if isinstance(x, int) and 1 <= x <= 12]

out = []
for s in all_seeds:
    ttg = s.get('timeToGrow')
    hl = s.get('harvestLevel')
    growth_days = round(hl * ttg / 24, 1) if (ttg and hl) else None
    rot = s.get('rotTime', ttg/2 if ttg else None)
    rot_days = round(rot / 24, 1) if rot else None
    seed_item = None
    if isinstance(s.get('seedTypes'), list) and s['seedTypes']:
        seed_item = s['seedTypes'][0].replace('Base.', '')
    elif s.get('seedName'):
        seed_item = s['seedName'].replace('Base.', '')
    produce = (s.get('vegetableName') or '').replace('Base.', '')
    out.append({
        'name': s['_name'],
        'category': s['_category'],
        'source': s['_source'],
        'seed': seed_item,
        'produce': produce,
        'yieldMin': s.get('minVeg'),
        'yieldMax': s.get('maxVeg'),
        'timeToGrow': ttg,
        'stages': hl,
        'growthDays': growth_days,
        'rotDays': rot_days,
        'waterLvl': s.get('waterLvl'),
        'waterNeeded': s.get('waterNeeded'),
        'sow': months(s.get('sowMonth')),
        'best': months(s.get('bestMonth')),
        'risk': months(s.get('riskMonth')),
        'bad': months(s.get('badMonth')),
        'coldHardy': bool(s.get('coldHardy')),
        'scythe': bool(s.get('scytheHarvest')),
        'harvestPos': s.get('harvestPosition'),
    })

out.sort(key=lambda x: x['name'])
print(f"Parsed {len(out)} seeds", file=sys.stderr)
json.dump(out, sys.stdout, indent=0)
