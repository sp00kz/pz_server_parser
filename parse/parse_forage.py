#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, glob, os

BASE = pzenv.MEDIA
CATDIR = f"{BASE}/lua/shared/Foraging/Categories"
NAMES = f"{BASE}/lua/shared/Translate/EN/ItemName.json"

names = {}
for m in re.finditer(r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"',
                     open(NAMES, encoding='utf-8', errors='replace').read()):
    names.setdefault(m.group(1), m.group(2))
pzmods.load_mod_item_names(names)

# ---------- Lua table-literal parser ----------
def strip_comments(s):
    out = []; i = 0; n = len(s); q = None
    while i < n:
        c = s[i]
        if q:
            out.append(c)
            if c == '\\' and i + 1 < n: out.append(s[i+1]); i += 2; continue
            if c == q: q = None
            i += 1; continue
        if c in '"\'': q = c; out.append(c); i += 1; continue
        if c == '-' and i + 1 < n and s[i+1] == '-':
            while i < n and s[i] != '\n': i += 1
            continue
        out.append(c); i += 1
    return ''.join(out)

def skip_ws(s, i):
    while i < len(s) and s[i] in ' \t\r\n,;': i += 1
    return i

def parse_string(s, i):
    q = s[i]; i += 1; buf = []
    while i < len(s) and s[i] != q:
        if s[i] == '\\': buf.append(s[i+1]); i += 2; continue
        buf.append(s[i]); i += 1
    return ''.join(buf), i + 1

def parse_expr(s, i):
    # read a non-table value up to a top-level , ; or }
    depth = 0; start = i
    while i < len(s):
        c = s[i]
        if c in '([{': depth += 1
        elif c in ')]}':
            if depth == 0: break
            depth -= 1
        elif c in ',;' and depth == 0: break
        i += 1
    return s[start:i].strip(), i

def parse_value(s, i):
    i = skip_ws(s, i)
    c = s[i]
    if c == '{': return parse_table(s, i)
    if c in '"\'': return parse_string(s, i)
    m = re.match(r'-?\d+\.?\d*', s[i:])
    if m and (c == '-' or c.isdigit()):
        tok = m.group(); return (float(tok) if '.' in tok else int(tok)), i + len(tok)
    if s.startswith('true', i): return True, i + 4
    if s.startswith('false', i): return False, i + 5
    return parse_expr(s, i)

def parse_table(s, i):
    assert s[i] == '{'; i += 1; d = {}; pos = 0
    while True:
        i = skip_ws(s, i)
        if i >= len(s): break
        if s[i] == '}': return d, i + 1
        key = None
        if s[i] == '[':
            j = i + 1; j = skip_ws(j and s, j) if False else j
            kv, j = parse_value(s, i + 1)
            j = skip_ws(s, j)
            if s[j] == ']': j += 1
            j = skip_ws(s, j)
            if j < len(s) and s[j] == '=':
                key = kv; i = j + 1
        else:
            m = re.match(r'([A-Za-z_]\w*)\s*=(?!=)', s[i:])
            if m:
                key = m.group(1); i += m.end()
        val, i = parse_value(s, i)
        if key is None:
            pos += 1; d[pos] = val
        else:
            d[key] = val
    return d, i

def parse_top_table(s, varhint):
    m = re.search(rf'local\s+{varhint}\s*=\s*', s)
    if not m:
        m = re.search(r'local\s+\w+\s*=\s*(?=\{)', s)
    if not m: return None
    i = s.index('{', m.end() - 1)
    t, _ = parse_table(s, i)
    return t

def parse_def_block(s):
    """Parse the table literal passed as addForageDef's 2nd arg."""
    m = re.search(r'addForageDef\s*\(', s)
    if not m: return {}
    i = m.end()
    # skip first arg up to top-level comma
    depth = 0; q = None
    while i < len(s):
        c = s[i]
        if q:
            if c == q: q = None
        elif c in '"\'': q = c
        elif c in '([{': depth += 1
        elif c in ')]}': depth -= 1
        elif c == ',' and depth == 0: i += 1; break
        i += 1
    i = skip_ws(s, i)
    if i < len(s) and s[i] == '{':
        t, _ = parse_table(s, i); return t
    return {}

# ---------- zone generalization ----------
ZONEMAP = {
    'Forest':'Forest', 'DeepForest':'Forest', 'PHForest':'Forest', 'PRForest':'Forest',
    'OrganicForest':'Forest', 'BirchForest':'Forest', 'PHMixForest':'Forest',
    'BirchMixForest':'Forest', 'FarmMixForest':'Forest', 'FarmForest':'Forest',
    'FarmLand':'Farmland', 'Farm':'Farmland',
    'Vegitation':'Vegetation',
    'TownZone':'Town', 'TrailerPark':'Trailer Park',
    'Nav':'Roadside', 'ForagingNav':'Roadside',
}
ZONE_ORDER = ['Forest', 'Vegetation', 'Farmland', 'Roadside', 'Town', 'Trailer Park']
def generalize(zonekeys):
    g = []
    for z in zonekeys:
        gz = ZONEMAP.get(z, z)
        if gz not in g: g.append(gz)
    return sorted(g, key=lambda x: ZONE_ORDER.index(x) if x in ZONE_ORDER else 99)

MON = ['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def months_str(ms):
    ms = sorted(set(int(x) for x in ms if isinstance(x, (int, float))))
    if not ms: return None
    if len(ms) == 12: return 'All year'
    # contiguous (incl. wrap-around)?
    full = set(ms)
    for start in ms:
        seq = []; c = start
        while c in full and len(seq) < 12:
            seq.append(c); c = c % 12 + 1
        if len(seq) == len(ms):
            return f'{MON[seq[0]]}–{MON[seq[-1]]}'
    return ', '.join(MON[m] for m in ms)

def to_list(t):
    if isinstance(t, dict):
        return [t[k] for k in sorted(t) if isinstance(k, int)]
    return t if isinstance(t, list) else []

# foraged items sharing a generic in-game name -> their real identity
OVERRIDE = {
    'BerryBlack':'Blackberry', 'BerryBlue':'Blueberry', 'BeautyBerry':'Beautyberry',
    'WinterBerry':'Winterberry', 'HollyBerry':'Holly Berry', 'BerryPoisonIvy':'Poison Ivy Berries',
    'BerryGeneric1':'Wild Berries', 'BerryGeneric2':'Wild Berries', 'BerryGeneric3':'Wild Berries',
    'BerryGeneric4':'Wild Berries', 'BerryGeneric5':'Wild Berries',
    'MushroomGeneric1':'Wild Mushrooms', 'MushroomGeneric2':'Wild Mushrooms', 'MushroomGeneric3':'Wild Mushrooms',
    'MushroomGeneric4':'Wild Mushrooms', 'MushroomGeneric5':'Wild Mushrooms', 'MushroomGeneric6':'Wild Mushrooms',
    'MushroomGeneric7':'Wild Mushrooms',
}
def itemname(full):
    iid = str(full).replace('Base.', '').strip()
    if iid in OVERRIDE: return OVERRIDE[iid]
    return names.get(iid, iid.replace('_', ' '))

# scavenge/town clutter; excluded
EXCLUDE = {'Junk', 'JunkWeapons', 'Clothing', 'Trash', 'Ammunition', 'Artifacts'}
CATNAME = {'MedicinalPlants':'Medicinal Plants', 'WildHerbs':'Wild Herbs', 'WildPlants':'Wild Plants',
           'ForestRarities':'Forest Rarities', 'DeadAnimals':'Dead Animals', 'FishBait':'Fish Bait',
           'Crops':'Wild Crops'}

# ---------- build ----------
out = []
SOURCES = [('Vanilla', p) for p in sorted(glob.glob(f'{CATDIR}/*.lua'))]
SOURCES += pzmods.mod_files('lua/shared/Foraging/**/*.lua')
for source, path in SOURCES:
    catfile = os.path.splitext(os.path.basename(path))[0]
    s = strip_comments(open(path, encoding='utf-8', errors='replace').read())
    top = parse_top_table(s, r'\w+')
    if not top: continue
    defblock = parse_def_block(s)

    def emit(itemfull, fields, grpitems_fallback=None):
        zones = fields.get('zones') or defblock.get('zones') or {}
        zonekeys = [k for k in zones.keys() if isinstance(k, str)] if isinstance(zones, dict) else []
        months = to_list(fields.get('months') or defblock.get('months') or [])
        bonus = to_list(fields.get('bonusMonths') or defblock.get('bonusMonths') or [])
        cats = to_list(fields.get('categories') or defblock.get('categories') or [])
        cat = next((c for c in cats if isinstance(c, str)), catfile)
        if cat in EXCLUDE: return
        cat = CATNAME.get(cat, cat)
        xp = fields.get('xp', defblock.get('xp'))
        skill = fields.get('skill', defblock.get('skill', 0))
        pc = fields.get('poisonChance', defblock.get('poisonChance', 0))
        out.append({
            'name': itemname(itemfull),
            'category': cat,
            'source': source,
            'zones': generalize(zonekeys),
            'season': months_str(months),
            'best': months_str(bonus) if bonus else None,
            'xp': xp if isinstance(xp, (int, float)) else None,
            'skill': int(skill) if isinstance(skill, (int, float)) else 0,
            'min': fields.get('minCount', defblock.get('minCount', 1)),
            'max': fields.get('maxCount', defblock.get('maxCount', 1)),
            'poison': bool(isinstance(pc, (int, float)) and pc > 0),
        })

    for key, entry in top.items():
        if not isinstance(entry, dict): continue
        if 'type' in entry:                 # direct item def
            emit(entry['type'], entry)
        elif 'items' in entry:              # grouped spawn table
            grp_items = entry['items']
            if isinstance(grp_items, dict):
                for _, full in grp_items.items():
                    emit(full, entry)

# de-dupe identical entries
seen = {}
uniq = []
for r in out:
    k = (r['name'], r['category'], tuple(r['zones']), r['season'], r['skill'])
    if k in seen: continue
    seen[k] = 1; uniq.append(r)

uniq.sort(key=lambda x: (x['category'], x['name']))
cats = sorted({r['category'] for r in uniq})
print(f"{len(uniq)} forageable items; categories: {cats}", file=sys.stderr)
json.dump(uniq, sys.stdout, separators=(',', ':'))
