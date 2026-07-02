#!/usr/bin/env python3
"""Parse skill-XP-granting actions from game Lua and engine animal actions."""
import os, sys, re, json, glob, struct, zipfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
import pzenv, pzmods

LUA = pzenv.MEDIA + '/lua'

SKILL = {
    'Husbandry': 'Animal Care', 'PlantScavenging': 'Foraging', 'Woodwork': 'Carpentry',
    'MetalWelding': 'Welding', 'Doctor': 'First Aid', 'Farming': 'Agriculture',
}
def skill(p): return SKILL.get(p, p)

LABEL = {
    'ButcheringUtil': 'Butcher animal', 'FishingNet': 'Fishing net', 'ISCheckFishingNetAction': 'Check fishing net',
    'ISPickupFishAction': 'Catch fish', 'ISGiveWaterToAnimal': 'Give water to animal',
    'ISHutchGrabEgg': 'Collect egg from hutch', 'ISInstallVehiclePart': 'Install vehicle part',
    'ISUninstallVehiclePart': 'Remove vehicle part', 'ISTakeEngineParts': 'Salvage engine part',
    'ISRepairEngine': 'Repair engine', 'ISRepairLightbar': 'Repair lightbar',
    'ISRemoveBurntVehicle': 'Scrap burnt vehicle', 'ISPickAxeGroundCoverItem': 'Dig up ground cover',
    'ISRemoveHeadFromAnimal': 'Remove head from carcass', 'ISRemoveLeatherFromAnimal': 'Remove leather from carcass',
    'STrapGlobalObject': 'Check trap', 'SFarmingSystem': 'Harvest / tend crop', 'forageSystem': 'Forage',
    'ISBuildUtil': 'Build', 'ISFixGenerator': 'Repair generator', 'ISApplyBandage': 'Apply bandage',
    'ISCleanBurn': 'Clean burn', 'ISRemoveBullet': 'Remove bullet', 'ISRemoveGlass': 'Remove glass shards',
    'ISSplint': 'Apply splint', 'ISStitch': 'Stitch wound', 'ISRemovePatch': 'Remove clothing patch',
    'ISRepairClothing': 'Repair clothing', 'buildUtil': 'Build',
}
EXCLUDE = {'XpUpdate'}  # not a discrete action
XP_FUNCS = ('addXpNoMultiplier', 'addXp', 'AddXP')

def humanize(cls):
    s = re.sub(r'^(IS|S|C)(?=[A-Z])', '', cls)
    s = re.sub(r'Action$|Util$|System$', '', s)
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s).strip()
    return s or cls

def category(path):
    p = path.replace('\\', '/').lower()
    if '/vehicles/' in p: return 'Vehicle'
    if 'fish' in p: return 'Fishing'
    if 'animal' in p or 'butcher' in p or 'hutch' in p: return 'Animal'
    if 'farm' in p: return 'Farming'
    if 'forag' in p: return 'Foraging'
    if 'trap' in p: return 'Trapping'
    return 'Other'

def split_args(inner):
    out, depth, cur = [], 0, ''
    for ch in inner:
        if ch in '([{': depth += 1; cur += ch
        elif ch in ')]}': depth -= 1; cur += ch
        elif ch == ',' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

def balanced(txt, open_idx):
    depth, i = 0, open_idx
    while i < len(txt):
        if txt[i] == '(': depth += 1
        elif txt[i] == ')':
            depth -= 1
            if depth == 0: return txt[open_idx+1:i]
        i += 1
    return None

def parse_lua():
    rows = []
    sources = [(None, f) for f in glob.glob(f'{LUA}/**/*.lua', recursive=True)]
    sources += pzmods.mod_files('lua/**/*.lua')
    for mod, f in sources:
        cls = os.path.basename(f)[:-4]
        if cls in EXCLUDE: continue
        txt = open(f, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'\b(addXpNoMultiplier|addXp|AddXP)\s*\(', txt):
            inner = balanced(txt, m.end()-1)
            if inner is None: continue
            args = split_args(inner)
            pi = next((k for k, a in enumerate(args) if re.match(r'Perks\.[A-Za-z]+$', a.strip())), None)
            if pi is None or pi+1 >= len(args): continue
            perk = args[pi].strip().split('.')[1]
            amt = args[pi+1].strip()
            num = int(amt) if amt.isdigit() else (float(amt) if re.match(r'^\d+\.\d+$', amt) else None)
            rows.append({
                'action': LABEL.get(cls, humanize(cls)), 'skill': skill(perk),
                'xp': num, 'varies': num is None, 'note': '' if num is not None else f'varies — {amt}',
                'category': category(f),
                'source': (f'{mod}: {os.path.basename(f)}' if mod
                           else os.path.relpath(f, LUA).replace('\\', '/')),
            })
    return rows

# engine-granted Husbandry animal actions; amounts computed at runtime
JAR_ACTIONS = [
    ('Milk animal', 'engine-granted — scales in-game'),
    ('Shear animal', 'engine-granted — scales in-game'),
    ('Feed animal from hand', 'engine-granted'),
    ('Pet animal', 'engine-granted'),
    ('Lure animal', 'engine-granted'),
]
def parse_jar():
    return [{'action': a, 'skill': 'Animal Care', 'xp': None, 'varies': True,
             'note': note, 'category': 'Animal', 'source': 'engine (IsoAnimal)'} for a, note in JAR_ACTIONS]

def butcher_range():
    f = pzenv.MEDIA + '/lua/shared/Definitions/animal/AnimalPartsDefinitions.lua'
    try:
        vals = [int(x) for x in re.findall(r'xpPerItem\s*=\s*(\d+)', open(f, encoding='utf-8', errors='replace').read())]
        return (min(vals), max(vals)) if vals else None
    except Exception:
        return None

rows = parse_lua() + parse_jar()
# replace xpPerItem note with the per-animal range
_br = butcher_range()
if _br:
    for r in rows:
        if 'animalDef.xpPerItem' in r['note']:
            r['note'] = f'{_br[0]}–{_br[1]} per part (by animal)'
# de-dupe identical rows
seen, uniq = set(), []
for r in rows:
    k = (r['action'], r['skill'], r['xp'], r['note'])
    if k in seen: continue
    seen.add(k); uniq.append(r)
uniq.sort(key=lambda r: (r['skill'], r['action']))
print(f"{len(uniq)} XP actions across {len({r['skill'] for r in uniq})} skills", file=sys.stderr)
json.dump(uniq, sys.stdout, separators=(',', ':'))
