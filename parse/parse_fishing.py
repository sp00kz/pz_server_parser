#!/usr/bin/env python3
"""Parse per-fish fishing data from lua/shared/Fishing/."""
import os, sys, re, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import pzenv, pzmods

FDIR = pzenv.MEDIA + '/lua/shared/Fishing'
PROPS = FDIR + '/fishing_properties.lua'
UTILS = FDIR + '/FishingUtils.lua'
# vanilla properties + any mod fishing lua (non-fish files yield no FishConfig blocks)
FILES = [('Vanilla', PROPS)] + pzmods.mod_files('lua/shared/Fishing/*.lua')

BAIT_CATS = ['Insect', 'Minnows', 'Leeches', 'Worms', 'Flesh', 'Plant']
ART_LURES = {'Base.JigLure': 'jig', 'Base.MinnowLure': 'minnowLure'}

def humanize(s):
    s = re.sub(r'^Base\.', '', s)
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    s = re.sub(r'(?<=[A-Za-z])(?=[0-9])', ' ', s)
    return s.strip()

def family(name):
    n = name.lower()
    for key, lab in (('bass','Bass'),('catfish','Catfish'),('crappie','Crappie'),
                     ('sunfish','Sunfish'),('bluegill','Sunfish'),('perch','Perch'),
                     ('gar','Gar'),('drum','Drum'),('walleye','Perch'),('sauger','Perch'),
                     ('muskellunge','Pike'),('paddlefish','Other'),('baitfish','Bait')):
        if key in n:
            return lab
    return 'Other'

def skill_limits():
    out = {}
    for m in re.finditer(r'skillSizeLimit\[(\d+)\]\s*=\s*([\d.]+)', open(UTILS, encoding='utf-8', errors='replace').read()):
        out[int(m.group(1))] = float(m.group(2))
    return out

def min_skill(max_weight, limits):
    for lvl in sorted(limits):
        if max_weight <= limits[lvl]:
            return lvl
    return max(limits) if limits else None

def net_items(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    items = set()
    for block in ('fishNet', 'fishNetWithBait'):
        for m in re.finditer(rf'Fishing\.{block}\s*,\s*"([\w.]+)"', txt):
            items.add(m.group(1))
    return items

def parse_props(path, source, limits, nets, rows, seen_items):
    fish = {}          # var name -> record
    var_item = {}      # var name -> item id
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.search(r'local (\w+)\s*=\s*Fishing\.FishConfig:new\("([\w.]+)"\)', line)
        if m:
            var, item = m.group(1), m.group(2)
            var_item[var] = item
            fish[var] = {'item': item, 'name': humanize(item), 'minLen': 10,
                         'maxLen': None, 'maxWeight': None, 'trophyLen': None,
                         'trophyWeight': None, 'weightFactor': None,
                         'predator': False, 'river': False, 'lake': False,
                         'baits': {b: 0.0 for b in BAIT_CATS}, 'jig': 0.0, 'minnowLure': 0.0,
                         'favorite': None, 'favoriteCoeff': None}
            continue
        m = re.search(r'(\w+):setLocation\((\w+),\s*(\w+)\)', line)
        if m and m.group(1) in fish:
            fish[m.group(1)]['river'] = (m.group(2) == 'true')
            fish[m.group(1)]['lake'] = (m.group(3) == 'true')
            continue
        for fn, key in (('setMaxLength', 'maxLen'), ('setTrophyLength', 'trophyLen'),
                        ('setMaxWeight', 'maxWeight'), ('setTrophyWeight', 'trophyWeight'),
                        ('setWeightFactor', 'weightFactor')):
            m = re.search(rf'(\w+):{fn}\(([\d.]+)\)', line)
            if m and m.group(1) in fish:
                v = float(m.group(2))
                fish[m.group(1)][key] = int(v) if v == int(v) and key != 'maxWeight' and key != 'trophyWeight' else v
                break
        m = re.search(r'(\w+):setPredator\((\w+)\)', line)
        if m and m.group(1) in fish:
            fish[m.group(1)]['predator'] = (m.group(2) == 'true'); continue
        m = re.search(r'(\w+)\.minLength\s*=\s*(\d+)', line)
        if m and m.group(1) in fish:
            fish[m.group(1)]['minLen'] = int(m.group(2)); continue
        m = re.search(r'(\w+):addLures\(Fishing\.lure\.(\w+),\s*([\d.]+)\)', line)
        if m and m.group(1) in fish and m.group(2) in BAIT_CATS:
            fish[m.group(1)]['baits'][m.group(2)] = float(m.group(3)); continue
        m = re.search(r'(\w+)\.lure\["([\w.]+)"\]\s*=\s*([\d.]+)', line)
        if m and m.group(1) in fish:
            rec, item, coeff = fish[m.group(1)], m.group(2), float(m.group(3))
            if item in ART_LURES:
                rec[ART_LURES[item]] = coeff
            else:
                # per-item override = the favorite bait
                if rec['favoriteCoeff'] is None or coeff > rec['favoriteCoeff']:
                    rec['favorite'] = humanize(item); rec['favoriteCoeff'] = coeff
            continue

    for var, rec in fish.items():
        if rec['item'] in seen_items:   # first definition wins (vanilla parsed first)
            continue
        seen_items.add(rec['item'])
        rec['source'] = source
        rec['minSkill'] = min_skill(rec.get('maxWeight') or 0, limits)
        rec['net'] = rec['item'] in nets
        rec['category'] = family(rec['name'])
        rows.append(rec)

def parse():
    limits = skill_limits()
    nets = set()
    for _src, path in FILES:
        nets |= net_items(path)
    rows, seen_items = [], set()
    for src, path in FILES:
        parse_props(path, src, limits, nets, rows, seen_items)
    rows.sort(key=lambda r: (r['category'], -(r.get('maxWeight') or 0)))
    return rows

rows = parse()
print(f"{len(rows)} fish parsed", file=sys.stderr)
json.dump(rows, sys.stdout, separators=(',', ':'))
