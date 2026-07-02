#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '.')))
import pzenv
"""Report items added, removed, or changed between work/*.json and work/prev/*.json.

Usage: python3 diff_data.py [dataset ...]   (default: all known datasets)"""
import json, os, sys
WORK=pzenv.WORK
PREV=f'{WORK}/prev'

# dataset file -> (list extractor, identity key)
DATASETS={
 'seeds.json':     (lambda d: d,            ('name',)),
 'vehicles.json':  (lambda d: d,            ('script','name')),
 'animals.json':   (lambda d: d,            ('name',)),
 'guns.json':      (lambda d: d,            ('name',)),
 'melee.json':     (lambda d: d,            ('name',)),
 'tools.json':     (lambda d: d,            ('name',)),
 'recipes.json':   (lambda d: d,            ('id','name')),
 'food.json':      (lambda d: d['items'],   ('id','name')),
 'forage.json':    (lambda d: d,            ('name','cat')),
}

def load(path, extract):
    if not os.path.exists(path): return None
    try: return extract(json.load(open(path)))
    except Exception as e: return None

def idof(item, keys):
    return ' | '.join(str(item.get(k,'')) for k in keys)

def diff_one(fn):
    extract, keys = DATASETS[fn]
    new=load(f'{WORK}/{fn}', extract)
    old=load(f'{PREV}/{fn}', extract)
    if new is None:
        return f"{fn}: (no current data)"
    if old is None:
        return f"{fn}: {len(new)} items (no previous snapshot to diff)"
    nmap={idof(i,keys):i for i in new}
    omap={idof(i,keys):i for i in old}
    added=[k for k in nmap if k not in omap]
    removed=[k for k in omap if k not in nmap]
    changed=[]
    for k in nmap:
        if k in omap and nmap[k]!=omap[k]:
            flds=sorted({f for f in set(nmap[k])|set(omap[k]) if nmap[k].get(f)!=omap[k].get(f)})
            changed.append((k,flds))
    lines=[f"{fn}: {len(new)} items  (+{len(added)} -{len(removed)} ~{len(changed)})"]
    for k in added[:15]:   lines.append(f"    + {k}")
    if len(added)>15: lines.append(f"    + ... {len(added)-15} more")
    for k in removed[:15]: lines.append(f"    - {k}")
    if len(removed)>15: lines.append(f"    - ... {len(removed)-15} more")
    for k,flds in changed[:20]: lines.append(f"    ~ {k}  [{', '.join(flds)}]")
    if len(changed)>20: lines.append(f"    ~ ... {len(changed)-20} more")
    return '\n'.join(lines)

def main():
    want=sys.argv[1:] or list(DATASETS)
    any_change=False
    for fn in want:
        if fn not in DATASETS:
            print(f"(unknown dataset {fn})"); continue
        out=diff_one(fn); print(out)
        if '+0 -0 ~0' not in out and 'no previous' not in out and 'no current' not in out:
            any_change=True
    print('\n'+("CHANGES DETECTED" if any_change else "no data changes vs previous snapshot"))

if __name__=='__main__':
    main()
