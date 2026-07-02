#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Validate universe keys against pzwiki in API batches, writing resolved.json incrementally."""
import json, urllib.parse, time, sys, os
TMP=pzenv.WORK
API="https://pzwiki.net/w/api.php"

uni=json.load(open(f'{TMP}/universe.json'))['keys']
# keys to validate: everything except modded-vehicle-only keys
to_check=[k for k,v in uni.items() if not v['vsource']]

resolved={}
rp=f'{TMP}/resolved.json'
if os.path.exists(rp):
    try: resolved=json.load(open(rp))
    except Exception: resolved={}

remaining=[k for k in to_check if k not in resolved]
print(f"to_check={len(to_check)} already={len(resolved)} remaining={len(remaining)}", file=sys.stderr)

def call(titles):
    q=urllib.parse.urlencode({'action':'query','format':'json','redirects':'1',
                              'titles':'|'.join(titles)})
    for attempt in range(4):
        body=pzenv.http_get(f"{API}?{q}",40)
        try:
            return json.loads(body)
        except Exception:
            time.sleep(2+attempt*3)
    raise RuntimeError("API parse failed for batch: "+titles[0])

B=50
for i in range(0,len(remaining),B):
    batch=remaining[i:i+B]
    data=call(batch)
    q=data.get('query',{})
    norm={d['from']:d['to'] for d in q.get('normalized',[])}
    redir={d['from']:d['to'] for d in q.get('redirects',[])}
    pages={p['title']:p for p in q.get('pages',{}).values()}
    def resolve_title(t):
        seen=set()
        while t in norm and t not in seen: seen.add(t); t=norm[t]
        seen=set()
        while t in redir and t not in seen: seen.add(t); t=redir[t]
        return t
    for k in batch:
        ft=resolve_title(k)
        pg=pages.get(ft)
        if pg is not None and 'missing' not in pg:
            resolved[k]={'status':'ok','canonical':pg['title']}
        else:
            resolved[k]={'status':'missing','canonical':None}
    json.dump(resolved,open(rp,'w'),indent=0)
    open(f'{TMP}/heartbeat.txt','w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    done=len(resolved)
    print(f"batch {i//B+1}: {done}/{len(to_check)} resolved", file=sys.stderr)
    time.sleep(0.4)

ok=sum(1 for v in resolved.values() if v['status']=='ok')
miss=sum(1 for v in resolved.values() if v['status']=='missing')
redir_ct=sum(1 for k,v in resolved.items() if v['status']=='ok' and v['canonical']!=k)
print(f"DONE ok={ok} missing={miss} (of which redirected/renamed canonical={redir_ct})", file=sys.stderr)
