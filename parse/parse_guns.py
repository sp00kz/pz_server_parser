#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv, pzmods
import re, json, sys, os

BASE = pzenv.MEDIA
WEAP = f"{BASE}/scripts/generated/items/weapon.txt"
NAMES = f"{BASE}/lua/shared/Translate/EN/ItemName.json"

names = {}
txt = open(NAMES, encoding='utf-8', errors='replace').read()
for m in re.finditer(r'"Base\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"', txt):
    names[m.group(1)] = m.group(2)
pzmods.load_mod_item_names(names)

# parse item blocks
def parse_items(path):
    items = []
    lines = open(path, encoding='utf-8', errors='replace').readlines()
    i, n = 0, len(lines)
    while i < n:
        m = re.match(r'\s*item\s+([A-Za-z0-9_]+)\s*$', lines[i])
        if m:
            name = m.group(1); kv = {}; depth = 0; started = False
            while i < n:
                s = lines[i].strip()
                depth += s.count('{') - s.count('}')
                if '{' in s: started = True
                if '=' in s and started:
                    k, v = s.split('=', 1)
                    kv[k.strip()] = v.strip().rstrip(',').strip()
                if started and depth <= 0:
                    break
                i += 1
            kv['__name__'] = name
            items.append(kv)
        i += 1
    return items

def num(kv, key):
    v = kv.get(key)
    if v is None: return None
    try: return float(v) if '.' in v else int(v)
    except ValueError: return None

CAL = {'bullets_9mm':'9mm','bullets_556':'5.56mm','bullets_308':'.308','bullets_3030':'.30-30',
       'bullets_357':'.357 Mag','bullets_44':'.44 Mag','bullets_45':'.45 ACP','bullets_38':'.38 Spc',
       'shotgunshells':'12ga','shells':'12ga'}
def caliber(kv):
    a = (kv.get('AmmoType','') or '').split(':')[-1]
    if a in CAL: return CAL[a]
    if 'cap' in a.lower(): return 'caps (toy)'
    return a.replace('bullets_','').replace('_',' ') or None

def gun_class(name, kv):
    s = name.lower()
    rt = (kv.get('WeaponReloadType') or '').lower()
    if 'shotgun' in s or 'shotgun' in rt: return 'Shotgun'
    if 'revolver' in s: return 'Revolver'
    if 'pistol' in s or rt=='handgun': return 'Pistol'
    if 'assault' in s: return 'Assault Rifle'
    if 'rifle' in s or 'carbine' in s: return 'Rifle'
    return 'Firearm'

out = []
seen_ids = set()
for src, path in [('Vanilla', WEAP)] + pzmods.mod_files('scripts/**/*.txt'):
  for kv in parse_items(path):
    if kv.get('Ranged') != 'true':   # firearms only
        continue
    name = kv['__name__']
    if name in seen_ids:             # first definition wins (vanilla parsed first)
        continue
    seen_ids.add(name)
    out.append({
        'item': name,
        'name': names.get(name) or kv.get('DisplayName') or name,
        'source': src,
        'category': gun_class(name, kv),
        'ammo': caliber(kv),
        'mag': num(kv,'MaxAmmo') or num(kv,'ClipSize'),
        'minDmg': num(kv,'MinDamage'),
        'maxDmg': num(kv,'MaxDamage'),
        'maxRange': num(kv,'MaxRange'),
        'sightRange': num(kv,'MaxSightRange'),
        'hitChance': num(kv,'HitChance'),
        'critChance': num(kv,'CriticalChance'),
        'critMult': num(kv,'CritDmgMultiplier'),
        'recoil': num(kv,'RecoilDelay'),
        'aimTime': num(kv,'Aimingtime'),
        'reload': num(kv,'Reloadtime'),
        'projectiles': num(kv,'Projectilecount'),
        'noise': num(kv,'SoundRadius'),
        'jamChance': num(kv,'JamGunChance'),
        'weight': num(kv,'Weight'),
        'durab': ((num(kv,'ConditionMax') or 1) * num(kv,'ConditionLowerChanceOneIn'))
                 if num(kv,'ConditionLowerChanceOneIn') else None,
        'condMax': num(kv,'ConditionMax'),
        'condLower': num(kv,'ConditionLowerChanceOneIn'),
    })

out.sort(key=lambda x:(x['category'], x['name']))
print(f"{len(out)} firearms", file=sys.stderr)
json.dump(out, sys.stdout, indent=0)
