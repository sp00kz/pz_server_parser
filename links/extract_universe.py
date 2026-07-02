#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Extract every linked item name and the mod-source -> Workshop ID map; writes work/universe.json and work/workshop_map.json."""
import json, re, os
WORK=pzenv.WORK
WS=pzenv.WORKSHOP
def L(f): return json.load(open(f'{WORK}/{f}'))

# mod folder name -> workshop id
wsmap={}
if os.path.isdir(WS):
    for idd in os.listdir(WS):
        md=f"{WS}/{idd}/mods"
        if os.path.isdir(md):
            for mod in os.listdir(md):
                wsmap.setdefault(mod, idd)
json.dump(wsmap, open(f'{WORK}/workshop_map.json','w'), indent=0)

def key(v):
    if v is None: return None
    return re.sub(r'\s*\([^)]*\)\s*$','',str(v)).strip()

universe={}
def add(name, page, source=None):
    k=key(name)
    if not k: return
    e=universe.setdefault(k, {'pages':set(),'sources':set()})
    e['pages'].add(page)
    e['sources'].add(source or 'Vanilla')

def src(d):
    s=d.get('source','Vanilla')
    return None if s=='Vanilla' else s

for d in L('seeds.json'): add(d['name'],'seeds', src(d))
for d in L('vehicles.json'): add(d['name'],'vehicles', src(d))
for s in L('animals.json'):
    add(s['name'],'livestock', src(s))
    for b in s.get('breeds',[]): add(b['name'],'livestock', src(s))
for d in L('guns.json'): add(d['name'],'guns', src(d))
for d in L('melee.json'): add(d['name'],'melee', src(d))
for d in L('tools.json'): add(d['name'],'tools', src(d))
for d in L('forage.json'): add(d['name'],'foraging', src(d))
for d in L('food.json')['items']: add(d['name'],'food', src(d))
for d in L('fishing.json'): add(d['name'],'fishing', src(d))

def add_label(lab, page, source=None):
    if lab is None: return
    for part in str(lab).split('/'):
        part=part.strip()
        if part: add(part, page, source)
for r in L('recipes.json'):
    rs=src(r)
    for o in r.get('outputs',[]): add_label(o.get('label'),'crafting', rs)
    for c in r.get('consumed',[]): add_label(c.get('label'),'crafting', rs)
    for t in r.get('tools',[]): add_label(t.get('label'),'crafting', rs)

# a key seen from any vanilla context links to the wiki; mod-only keys link to their mod
def vsource(v):
    if 'Vanilla' in v['sources']: return None
    return sorted(v['sources'])[0]

out={'keys':{k:{'pages':sorted(v['pages']),'vsource':vsource(v)} for k,v in universe.items()}}
json.dump(out, open(f'{WORK}/universe.json','w'), indent=0)
modded=sum(1 for v in universe.values() if vsource(v))
print(f"universe: {len(universe)} keys ({modded} mod-sourced); workshop mods: {len(wsmap)}")
