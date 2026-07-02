#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Build linkmap.json, mapping each key to an override URL or null."""
import json, urllib.parse, sys
TMP=pzenv.WORK
WIKI='https://pzwiki.net/wiki/'
WS='https://steamcommunity.com/sharedfiles/filedetails/?id='

uni=json.load(open(f'{TMP}/universe.json'))['keys']
res=json.load(open(f'{TMP}/resolved.json'))
wsmap=json.load(open(f'{TMP}/workshop_map.json'))

def wiki_url(title):
    return WIKI+urllib.parse.quote(title.replace(' ','_'), safe="-_.!~*'()")

linkmap={}
stats={'redirect':0,'workshop':0,'nolink_missing':0,'nolink_modnoid':0,'default_ok':0,'unvalidated':0}
for k,info in uni.items():
    vsrc=info['vsource']
    if vsrc:  # mod-sourced -> workshop
        wsid=wsmap.get(vsrc)
        if wsid:
            linkmap[k]=WS+wsid; stats['workshop']+=1
        else:
            linkmap[k]=None; stats['nolink_modnoid']+=1
        continue
    r=res.get(k)
    if r is None:
        stats['unvalidated']+=1   # not yet checked (run `links`); leave the default URL
    elif r['status']=='ok':
        canon=r['canonical']
        if canon!=k:
            linkmap[k]=wiki_url(canon); stats['redirect']+=1
        else:
            stats['default_ok']+=1   # omit; default link correct
    else:
        linkmap[k]=None; stats['nolink_missing']+=1

json.dump(linkmap, open(f'{TMP}/linkmap.json','w'), separators=(',',':'), sort_keys=True)
print(f"linkmap entries (overrides)={len(linkmap)}  (default-ok omitted={stats['default_ok']})", file=sys.stderr)
print(stats, file=sys.stderr)
# a few examples
ex=[(k,v) for k,v in linkmap.items() if v and 'pzwiki' in v][:5]
print("redirect examples:", ex, file=sys.stderr)
