#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, glob, os

BASE = pzenv.MEDIA

STAT_KEYS = {'mass','engineForce','maxSpeed','engineLoudness','engineQuality','brakingForce',
             'seats','engineRepairLevel','playerDamageProtection','frontEndHealth','rearEndHealth'}
# trunk/glovebox item capacities
ITEMCAP = {'SmallTrunk':40,'NormalTrunk':55,'BigTrunk':70,'TrailerTrunk':100,'GloveBox':5}

def num(v):
    """Parse a script number, tolerating a Java float suffix."""
    if v is None: return None
    v = v.strip().rstrip('fF')
    try:
        return float(v) if '.' in v else int(v)
    except ValueError:
        return None

# ---------- generic brace/stack parser ----------
def parse_file(path, source):
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    root = {'kind':'root','name':None,'kv':{},'comp':[],'children':[],'source':source}
    stack = [root]
    pending = None
    for raw in lines:
        s = raw.split('//')[0].strip()
        if not s:
            continue
        # strip trailing comma
        if s == '{':
            kind, name = (pending or ('anon', None))
            node = {'kind':kind,'name':name,'kv':{},'comp':[],'children':[],'source':source}
            stack[-1]['children'].append(node)
            stack.append(node)
            pending = None
            continue
        if s == '}':
            if len(stack) > 1: stack.pop()
            pending = None
            continue
        if '=' in s:
            k, v = s.split('=', 1)
            k = k.strip(); v = v.strip().rstrip(',').strip()
            cur = stack[-1]
            if k == 'template':       # composition include
                cur['comp'].append(v)
            elif k == 'template!':
                cur['kv']['__parent__'] = v
            else:
                cur['kv'][k] = v
            continue
        # header token line
        toks = s.split()
        if toks[0] == 'template' and len(toks) >= 2 and toks[1] == 'vehicle':
            pending = ('vehicle_t', toks[2] if len(toks) > 2 else None)
        elif toks[0] == 'vehicle':
            pending = ('vehicle', toks[1] if len(toks) > 1 else None)
        elif toks[0] == 'part':
            pending = ('part', toks[1] if len(toks) > 1 else None)
        else:
            pending = (toks[0], toks[1] if len(toks) > 1 else None)
    return root

def collect_blocks(node, out):
    if node['kind'] in ('vehicle','vehicle_t'):
        out.append(node)
    for c in node['children']:
        collect_blocks(c, out)

# ---------- item capacity map ----------
ITEMMAP = {}
item_re = re.compile(r'^\s*item\s+([A-Za-z0-9_]+)\s*$')
mod_re = re.compile(r'^\s*module\s+([A-Za-z0-9_]+)')
maxcap_re = re.compile(r'^\s*MaxCapacity\s*=\s*([0-9]+)')
def index_items(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except OSError:
        return
    module = 'Base'; cur = None
    for ln in lines:
        mm = mod_re.match(ln)
        if mm: module = mm.group(1); continue
        im = item_re.match(ln)
        if im: cur = im.group(1); continue
        cm = maxcap_re.match(ln)
        if cm and cur:
            cap = int(cm.group(1))
            ITEMMAP[f'{module}.{cur}'] = cap
            ITEMMAP.setdefault(cur, cap)
            cur = None

# ---------- gather files ----------
files = []  # (path, source)
for fp in glob.glob(os.path.join(BASE, 'scripts/generated/vehicles/*.txt')):
    files.append((fp, 'Vanilla'))
for fp in glob.glob(os.path.join(BASE, 'scripts/vehicles/*.txt')):
    files.append((fp, 'Vanilla'))
for mod, fp in pzmods.mod_files('scripts/vehicles/*.txt'):
    files.append((fp, mod))

# index item capacities
for fp in glob.glob(os.path.join(BASE, 'scripts/generated/items/*.txt')):
    index_items(fp)
for _mod, fp in pzmods.mod_files('scripts/**/*.txt'):
    index_items(fp)

all_blocks = []
for fp, src in files:
    try:
        root = parse_file(fp, src)
        collect_blocks(root, all_blocks)
    except Exception as e:
        print(f"parse error {fp}: {e}", file=sys.stderr)

templates = {}
vehicles = []
for b in all_blocks:
    if not b['name']:
        continue
    if b['kind'] == 'vehicle_t':
        templates[b['name']] = b
    else:
        vehicles.append(b)

# ---------- resolution ----------
def part_flat(node):
    """Flatten a part node."""
    f = {'name':node['name'],'category':node['kv'].get('category'),
         'itemType':node['kv'].get('itemType'),'capacity':None,'container':False,'seat':None}
    for c in node['children']:
        if c['kind'] == 'container':
            f['container'] = True
            if 'capacity' in c['kv']:
                cv = num(c['kv']['capacity'])
                if cv is not None: f['capacity'] = int(cv)
            if 'seat' in c['kv']:
                f['seat'] = c['kv']['seat']
    return f

def merge_flat(a, b):
    if a is None: return dict(b)
    r = dict(a)
    for k in ('category','itemType','capacity','seat'):
        if b.get(k) is not None: r[k] = b[k]
    r['container'] = a.get('container') or b.get('container')
    return r

def get_parts(node):
    return {c['name']: part_flat(c) for c in node['children']
            if c['kind'] == 'part' and c['name']}

def _merge_into(res, parts):
    for name, fp in parts.items():
        res[name] = merge_flat(res.get(name), fp)

def resolve_parts(node, seen=None):
    seen = seen or set()
    key = id(node)
    if key in seen: return {}
    seen.add(key)
    res = {}
    parent = node['kv'].get('__parent__')
    if parent and parent in templates:
        _merge_into(res, resolve_parts(templates[parent], seen))
    for comp in node['comp']:
        if '/part/' in comp:
            parts = comp.split('/')
            tmpl, part = parts[0], parts[-1]
            if tmpl in templates:
                pr = resolve_parts(templates[tmpl], seen)
                if part in pr: _merge_into(res, {part: pr[part]})
        elif comp in templates:
            _merge_into(res, resolve_parts(templates[comp], seen))
    _merge_into(res, get_parts(node))
    return res

def resolve_stats(node, seen=None):
    seen = seen or set()
    key = id(node)
    if key in seen: return {}
    seen.add(key)
    merged = {}
    parent = node['kv'].get('__parent__')
    if parent and parent in templates:
        merged.update(resolve_stats(templates[parent], seen))
    for k, v in node['kv'].items():
        if k in STAT_KEYS:
            n = num(v)
            if n is not None: merged[k] = n
    return merged

def part_capacity(fp):
    """Return (capacity, derived) for a part."""
    if fp.get('capacity') is not None:
        return fp['capacity'], False
    it = fp.get('itemType') or ''
    if it in ITEMMAP:                       # exact item
        return ITEMMAP[it], True
    short = it.split('.')[-1]
    if short in ITEMMAP:
        return ITEMMAP[short], True
    for key, cap in ITEMCAP.items():        # vanilla generic tiers
        if key in it:
            return cap, True
    return None, False

# containers that are not player storage
NONSTORAGE_CAT = {'gastank','engine','nodisplay'}
NONSTORAGE_TOK = ('gastank','gas','fuel','battery','muffler','radio','heater','engine',
                  'tire','brake','suspension','window','windshield','headlight','lightbar')
def is_storage(name, cat, fp):
    if cat in NONSTORAGE_CAT: return False
    low = name.lower()
    if any(t in low for t in NONSTORAGE_TOK): return False
    if fp.get('seat'): return False        # seat occupancy, not cargo
    return fp.get('container')

def classify(parts):
    trunk_cap=None; trunk_derived=False; roof=None; interior=None; interior_name=None
    for name, fp in parts.items():
        cat = (fp.get('category') or '').lower()
        it = (fp.get('itemType') or '')
        low = name.lower()
        cap, derived = part_capacity(fp)
        is_roof = 'roof' in low or 'roof' in it.lower()
        is_trunk = (('trunk' in low or 'truckbed' in low or 'cargo' in low or 'trunk' in it.lower())
                    and 'door' not in low)
        if not cap: continue
        if is_roof:
            roof = max(roof or 0, cap)
        elif not is_storage(name, cat, fp):
            continue
        elif is_trunk:
            if trunk_cap is None or cap > trunk_cap:
                trunk_cap, trunk_derived = cap, derived
        else:
            if interior is None or cap > interior:
                interior, interior_name = cap, name
    return trunk_cap, trunk_derived, roof, interior, interior_name

# ---------- names ----------
names = {}
def load_names(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            txt = f.read()
    except OSError:
        return
    for m in re.finditer(r'IGUI_VehicleName([A-Za-z0-9_]+)"?\s*[:=]\s*"([^"]+)"', txt):
        k, v = m.group(1), m.group(2)
        if any(x in k for x in ('Smashed','Burnt')) or 'Wreck' in v: continue
        names.setdefault(k, v)

load_names(os.path.join(BASE, 'lua/shared/Translate/EN/IG_UI.json'))
for _mod, fp in pzmods.mod_files('lua/shared/Translate/EN/*'):
    load_names(fp)

def category(n):
    s = n.lower()
    if 'trailer' in s: return 'Trailer'
    if 'stepvan' in s: return 'Step Van'
    if 'van' in s: return 'Van'
    if 'pickup' in s or 'truck' in s: return 'Pickup'
    if 'suv' in s: return 'SUV'
    if 'offroad' in s: return 'Offroad'
    if 'race' in s or 'sport' in s: return 'Sports'
    if 'luxury' in s: return 'Luxury'
    if 'taxi' in s: return 'Taxi'
    return 'Car'

EXCLUDE = ('Smashed','Burnt','Wreck','Creature','LadyDelighter','Dismantle','_test')
seen_keys = set()
out = []
for vb in vehicles:
    vname = vb['name']
    if any(x in vname for x in EXCLUDE): continue
    key = (vb['source'], vname)
    if key in seen_keys: continue
    seen_keys.add(key)
    st = resolve_stats(vb)
    parts = resolve_parts(vb)
    is_trailer = 'trailer' in vname.lower()
    if 'maxSpeed' not in st and not is_trailer:
        continue
    if is_trailer:
        for k in ('maxSpeed','engineForce','engineQuality','engineLoudness','brakingForce','engineRepairLevel','seats'):
            st.pop(k, None)
    trunk, trunk_derived, roof, interior, interior_name = classify(parts)
    storage = trunk if trunk is not None else interior
    storage_kind = 'trunk' if trunk is not None else ('glovebox' if interior is not None else None)
    out.append({
        'script': vname,
        'name': names.get(vname, vname),
        'source': vb['source'],
        'category': category(vname),
        'maxSpeed': st.get('maxSpeed'),
        'engineForce': st.get('engineForce'),
        'engineQuality': st.get('engineQuality'),
        'engineLoudness': st.get('engineLoudness'),
        'mass': st.get('mass'),
        'seats': st.get('seats'),
        'engineRepairLevel': st.get('engineRepairLevel'),
        'protection': st.get('playerDamageProtection'),
        'trunk': storage,
        'trunkKind': storage_kind,
        'trunkApprox': trunk_derived,
        'roofRack': roof,
    })

out.sort(key=lambda x: (x['source'] != 'Vanilla', x['category'], -(x['maxSpeed'] or 0), x['name']))
nmods = len({x['source'] for x in out if x['source']!='Vanilla'})
print(f"{len(templates)} templates, {len(vehicles)} vehicle blocks -> {len(out)} vehicles ({nmods} mods)", file=sys.stderr)
json.dump(out, sys.stdout, indent=0)
