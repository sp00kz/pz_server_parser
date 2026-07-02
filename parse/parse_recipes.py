#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, glob, os

BASE = pzenv.MEDIA
SC   = f"{BASE}/scripts/generated"
TR   = f"{BASE}/lua/shared/Translate/EN"

# ---- name maps ----
def load_map(path, key_re):
    m = {}
    try: t = open(path, encoding='utf-8', errors='replace').read()
    except OSError: return m
    for mm in re.finditer(key_re, t):
        m.setdefault(mm.group(1), mm.group(2))
    return m
itemnames = load_map(f"{TR}/ItemName.json", r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"')
recipenames = load_map(f"{TR}/Recipes.json", r'"([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"')
pzmods.load_mod_item_names(itemnames)
for _mod, _fp in pzmods.mod_files('lua/shared/Translate/EN/*'):
    for _k, _v in load_map(_fp, r'Recipe_([A-Za-z0-9_]+)\s*=\s*"([^"]+)"').items():
        recipenames.setdefault(_k, _v)

def itemname(it):
    it = it.replace('Base.', '')
    return itemnames.get(it, it.replace('_', ' '))

# ---- gather recipe files ----
# Match case-insensitively on the whole path: the game ships typo'd/lowercased
# paths like entities/pottery/cratRecipes/craftrecipe_kiln.txt.
files = glob.glob(f"{SC}/recipes/*.txt")
files += [f for f in glob.glob(f"{SC}/entities/**/*.txt", recursive=True)
          if 'craftrecipe' in f.lower() or 'cratrecipe' in f.lower()]
files += [f"{SC}/entities/recipes_fuel.txt"]
files = [('Vanilla', f) for f in sorted(set(files))]
# mod scripts: any .txt may hold craftRecipe blocks; non-recipe files yield none
files += pzmods.mod_files('scripts/**/*.txt')

# ---- block parser ----
def parse_recipes(path):
    lines = open(path, encoding='utf-8', errors='replace').readlines()
    recs = []
    i, n = 0, len(lines)
    while i < n:
        m = re.match(r'\s*craftRecipe\s+([A-Za-z0-9_]+)\s*$', lines[i])
        if not m: i += 1; continue
        name = m.group(1)
        i += 1
        depth = 0; body = []
        # collect until matching close of this recipe
        started = False
        while i < n:
            s = lines[i]
            depth += s.count('{') - s.count('}')
            if '{' in s: started = True
            body.append(s)
            i += 1
            if started and depth <= 0: break
        recs.append((name, body))
    return recs

def section(body, sec):
    """Return lines inside a named sub-block."""
    out = []; depth = 0; capturing = False
    for s in body:
        st = s.strip()
        if not capturing and re.match(rf'{sec}\b', st):
            capturing = True; depth = 0
            depth += s.count('{') - s.count('}')
            continue
        if capturing:
            d0 = depth
            depth += s.count('{') - s.count('}')
            if d0 == 0 and s.count('{'): continue
            if depth <= 0: break
            out.append(st)
    return out

def kv(body, key):
    for s in body:
        m = re.match(rf'\s*{key}\s*=\s*(.+?),?\s*$', s)
        if m: return m.group(1).strip()
    return None

def parse_skillmap(val):
    d = {}
    if not val: return d
    for part in val.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            try: d[k.strip()] = int(v)
            except ValueError: pass
    return d

def parse_mappers(body):
    """Parse itemMapper blocks into {name: [distinct OUT items]}."""
    mappers = {}
    cur = None
    depth = 0; inblock = False
    for s in body:
        st = s.strip()
        mm = re.match(r'itemMapper\s+(\w+)', st)
        if mm:
            cur = mm.group(1); mappers[cur] = []; inblock = False; depth = 0
            continue
        if cur is not None:
            depth += s.count('{') - s.count('}')
            m2 = re.match(r'(Base\.[A-Za-z0-9_]+)\s*=', st)
            if m2:
                v = m2.group(1)
                if v not in mappers[cur]: mappers[cur].append(v)
            if '}' in s and depth <= 0: cur = None
    return mappers

ITEM_RE   = re.compile(r'item\s+(\d[\d.]*|variable\[\d+:\d+\])\s+(.*)')
FLUID_RE  = re.compile(r'-fluid\s+([\d.]+)\s+(?:categories)?\[([^\]]+)\]')
ENERGY_RE = re.compile(r'energy\s+([\d.]+)\s+([A-Za-z0-9_]+)')

def fluidname(x):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', x.strip())

def parse_count(cnt):
    """'3' -> 3; 'variable[1:20]' -> '1–20'."""
    m = re.match(r'variable\[(\d+):(\d+)\]', cnt)
    if m: return f"{m.group(1)}–{m.group(2)}"
    return int(float(cnt)) if re.match(r'^[\d.]+$', cnt) else cnt

def canon(tok):
    """Normalize an item token to its bare item id."""
    tok = tok.strip()
    tok = tok.rsplit(':', 1)[-1]          # drop leading count prefix
    tok = tok.replace('Base.', '')
    return tok.strip()

def parse_items(seclines, mappers):
    consumed, tools, outs = [], [], []
    for st in seclines:
        m = ITEM_RE.match(st)
        if not m:
            mf = FLUID_RE.match(st)
            if mf:
                amt = float(mf.group(1))
                lb = '/'.join(fluidname(x) for x in mf.group(2).split(';')) + ' (fluid)'
                consumed.append({'count': int(amt) if amt == int(amt) else amt,
                                 'label': lb, 'items': [], 'tool': False})
            continue
        cnt = parse_count(m.group(1)); rest = m.group(2)
        keep = 'mode:keep' in rest
        # label + normalized item id list
        lb = None; items = []
        br = re.search(r'\[([^\]]+)\]', rest)
        tg = re.search(r'tags\[([^\]]+)\]', rest)
        mp = re.search(r'mapper:(\w+)', rest)
        if mp:
            items = [canon(x) for x in mappers.get(mp.group(1), [])]
            lb = '/'.join(sorted({itemname(x) for x in items})) or mp.group(1)
        elif tg:
            tags = [t.split(':')[-1] for t in tg.group(1).split(';')]
            lb = '/'.join(sorted(set(tags)))   # tags, no item ids
        elif br:
            items = [canon(x) for x in br.group(1).split(';')]
            lb = '/'.join(sorted({itemname(x) for x in items}))
        else:
            lb = '?'
        entry = {'count': cnt, 'label': lb, 'items': sorted(set(items)), 'tool': keep}
        (tools if keep else consumed).append(entry)
    return consumed, tools

CATEGORY_SKILL = {'Carpentry':'Woodwork','Metalworking':'MetalWelding','Blacksmithing':'Blacksmith'}

out = []
for src, fp in files:
    for name, body in parse_recipes(fp):
        cat = kv(body, 'category')
        xp = parse_skillmap(kv(body, 'xpAward'))
        req = parse_skillmap(kv(body, 'SkillRequired'))
        time = kv(body, 'time')
        try: time = int(time) if time else None
        except ValueError: time = None
        mappers = parse_mappers(body)
        cons, tools = parse_items(section(body, 'inputs'), mappers)
        # outputs
        outs = []
        for st in section(body, 'outputs'):
            m = ITEM_RE.match(st)
            if not m:
                me = ENERGY_RE.match(st)
                if me:
                    outs.append({'count': int(float(me.group(1))),
                                 'label': f"Energy ({me.group(2)})", 'items': []})
                continue
            cnt = m.group(1); rest = m.group(2).strip().rstrip(',')
            mp = re.search(r'mapper:(\w+)', rest)
            if mp:
                items = [canon(x) for x in mappers.get(mp.group(1), [])]
                lb = '/'.join(sorted({itemname(x) for x in items})) or mp.group(1)
            else:
                b = re.match(r'(Base\.[A-Za-z0-9_]+|[A-Za-z0-9_.]+)', rest)
                items = [canon(b.group(1))] if b else []
                lb = itemname(b.group(1)) if b else rest
            outs.append({'count': parse_count(cnt),
                         'label': lb, 'items': sorted(set(items))})
        # skill set = union of xp + req skills
        skills = sorted(set(xp) | set(req))
        if not skills and cat in CATEGORY_SKILL: skills = [CATEGORY_SKILL[cat]]
        out.append({
            'id': name,
            'name': recipenames.get(name, name.replace('_',' ')),
            'source': src,
            'category': cat,
            'skills': skills,
            'xp': xp,
            'req': req,
            'time': time,
            'consumed': cons,
            'tools': tools,
            'outputs': outs,
            'learn': kv(body,'NeedToBeLearn')=='true',
        })

# de-dupe by id
seen={}; uniq=[]
for r in out:
    if r['id'] in seen: continue
    seen[r['id']]=1; uniq.append(r)
print(f"{len(uniq)} recipes; skills: {sorted({s for r in uniq for s in r['skills']})}", file=sys.stderr)
no_out = [r['id'] for r in uniq if not r['outputs']]
no_in = [r['id'] for r in uniq if not r['consumed'] and not r['tools']]
if no_out: print(f"warning: {len(no_out)} recipes with no outputs, e.g. {no_out[:5]}", file=sys.stderr)
if no_in: print(f"warning: {len(no_in)} recipes with no inputs, e.g. {no_in[:5]}", file=sys.stderr)
json.dump(uniq, sys.stdout)
