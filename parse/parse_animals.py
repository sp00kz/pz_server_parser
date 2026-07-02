#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, glob, os

BASE = pzenv.MEDIA
DEF  = f"{BASE}/lua/shared/Definitions/animal"
TR   = f"{BASE}/lua/shared/Translate/EN"

FARM = ['cow','pig','sheep','chicken','turkey','rabbit']
FILES = {'cow':'Cow','pig':'Pig','sheep':'Sheep','chicken':'Chicken','turkey':'Turkey','rabbit':'Rabbit'}

# translated names
names = {}
for fp in glob.glob(f"{TR}/*.json"):
    t = open(fp, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'"IGUI_(?:AnimalType_Global|Breed)_([a-z0-9]+)"\s*:\s*"([^"]+)"', t):
        names.setdefault(m.group(1), m.group(2))
for _mod, fp in pzmods.mod_files('lua/shared/Translate/EN/*'):
    t = open(fp, encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'IGUI_(?:AnimalType_Global|Breed)_([A-Za-z0-9]+)\s*=\s*"([^"]+)"', t):
        names.setdefault(m.group(1).lower(), m.group(2))

def lines_nc(path):
    out = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        s = ln.strip()
        if s and not s.startswith('--'):
            out.append(s)
    return out

def ev(expr):
    expr = expr.strip().rstrip(';').strip()
    if not re.fullmatch(r'[\d\s\*\+\(\)\.]+', expr): return None
    try: return int(eval(expr, {"__builtins__": {}}, {}))
    except Exception: return None

def species_facts(species, lines):
    text = '\n'.join(lines)
    # matures: min ageToGrow
    ages = [ev(m) for m in re.findall(r'ageToGrow\s*=\s*([^;\n]+)', text)]
    ages = [a for a in ages if a and a >= 25]
    matures = min(ages) if ages else None
    # gestation: max pregnantPeriod
    preg = [ev(m) for m in re.findall(r'pregnantPeriod\s*=\s*([^;\n]+)', text)]
    preg = [p for p in preg if p and p >= 10]
    gest = max(preg) if preg else None
    def maxnum(key):
        vs = [ev(m) for m in re.findall(rf'{key}\s*=\s*([0-9\*\+\(\)\. ]+)', text)]
        vs = [v for v in vs if v is not None]
        return max(vs) if vs else None
    trailer = maxnum('trailerBaseSize')
    enc = maxnum('baseEncumbrance')
    flees = 'alwaysFleeHumans = true' in text
    # products
    birds = species in ('chicken','turkey')
    prods = ['Meat']
    if 'milkType' in text: prods.append('Milk')
    if re.search(r'wool|maxWool', text): prods.append('Wool')
    if birds: prods += ['Eggs','Feathers']
    else: prods.append('Leather')
    prods.append('Manure')
    return dict(matures=matures, gestation=gest, trailer=trailer, encumbrance=enc,
                temperament=('Skittish' if flees else 'Docile'), products=prods)

GENES = ['meatRatio','maxMilk','maxWeight','maxWool','woolInc']
def breeds_for(species, lines):
    text = '\n'.join(lines)
    bres = []
    bkeys = sorted(set(re.findall(r'breeds\["%s"\]\.breeds\["(\w+)"\]' % species, text)))
    for bk in bkeys:
        genes = {}
        for g in GENES:
            mn = re.search(rf'breeds\["{species}"\]\.breeds\["{bk}"\]\.forcedGenes\["{g}"\]\.minValue\s*=\s*([0-9.]+)', text)
            mx = re.search(rf'breeds\["{species}"\]\.breeds\["{bk}"\]\.forcedGenes\["{g}"\]\.maxValue\s*=\s*([0-9.]+)', text)
            if mn and mx:
                genes[g] = [float(mn.group(1)), float(mx.group(1))]
        bres.append({'key':bk, 'name':names.get(bk, bk.title()), 'genes':genes})
    # breeds differ if gene sets are not all identical
    gsets = [json.dumps(b['genes'], sort_keys=True) for b in bres]
    differ = len(set(gsets)) > 1
    return bres, differ

out = []
seen_sp = set()
def emit(sp, lines, source):
    if sp in seen_sp:
        return
    seen_sp.add(sp)
    f = species_facts(sp, lines)
    breeds, differ = breeds_for(sp, lines)
    if source != 'Vanilla' and (f['matures'] is None or f['trailer'] is None or f['encumbrance'] is None):
        print(f"skipping incomplete mod species {sp} ({source})", file=sys.stderr)
        return
    out.append({
        'key': sp,
        'name': names.get(sp, sp.title()),
        'source': source,
        **f,
        'breeds': breeds,
        'breedsDiffer': differ,
    })

for sp in FARM:
    emit(sp, lines_nc(f"{DEF}/{FILES[sp]}Definitions.lua"), 'Vanilla')

# mod-added species: discover species keys from each mod definition file
for mod, fp in pzmods.mod_files('lua/shared/Definitions/animal/*.lua'):
    lines = lines_nc(fp)
    text = '\n'.join(lines)
    for sp in sorted(set(re.findall(r'breeds\["(\w+)"\]\.breeds', text))):
        emit(sp, lines, mod)

print(f"{len(out)} farm species", file=sys.stderr)
json.dump(out, sys.stdout, indent=0)
