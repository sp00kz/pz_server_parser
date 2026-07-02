#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Resolve status=missing keys via pzwiki search, accepting a hit only when its normalized title equals the key's normalized form."""
import json, urllib.parse, time, re, sys
TMP=pzenv.WORK
API="https://pzwiki.net/w/api.php"

res=json.load(open(f'{TMP}/resolved.json'))

def norm(s):
    s=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',str(s))   # split camelCase
    s=re.sub(r'[^a-z0-9]','',s.lower())            # drop non-alnum
    s=re.sub(r's$','',s)                           # strip trailing s
    return s

def is_junk(k):
    if k in ('*','',None): return True
    if k.endswith(':') or k.rstrip().endswith('\\'): return True
    if re.search(r'\b(I{1,3}|IV|V|VI{0,3}|IX|X)\s*:\s*\\?$', k): return True
    if len(k)<=1: return True
    return False

RECHECK='--recheck' in sys.argv   # force re-searching every non-junk miss
# missing, not previously searched, not junk
cand=[k for k,v in res.items() if v['status']=='missing' and (RECHECK or not v.get('searched')) and not is_junk(k)]
# mark junk as searched
for k,v in res.items():
    if v['status']=='missing' and is_junk(k):
        v['searched']='junk'
print(f"missing->candidates to search: {len(cand)}", file=sys.stderr)

def search(term):
    q=urllib.parse.urlencode({'action':'query','list':'search','srsearch':term,
                              'srlimit':'5','format':'json'})
    for attempt in range(4):
        body=pzenv.http_get(f"{API}?{q}",40)
        try:
            return json.loads(body).get('query',{}).get('search',[])
        except Exception:
            time.sleep(2+attempt*3)
    # Abort rather than return []: an outage must not be persisted as searched='nomatch'.
    raise RuntimeError("wiki search failed (network?) for: "+term)

accepted=0
for i,k in enumerate(cand):
    hits=search(k)
    nk=norm(k)
    match=None
    for h in hits:
        if norm(h['title'])==nk:
            match=h['title']; break
    if match:
        res[k]={'status':'ok','canonical':match,'via':'search'}
        accepted+=1
    else:
        res[k]['searched']='nomatch'
    if i%20==0:
        json.dump(res,open(f'{TMP}/resolved.json','w'),indent=0)
        open(f'{TMP}/heartbeat.txt','w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        print(f"  {i+1}/{len(cand)} searched, {accepted} accepted", file=sys.stderr)
    time.sleep(0.3)

json.dump(res,open(f'{TMP}/resolved.json','w'),indent=0)
open(f'{TMP}/heartbeat.txt','w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
ok=sum(1 for v in res.values() if v['status']=='ok')
miss=sum(1 for v in res.values() if v['status']=='missing')
print(f"DONE search-accepted={accepted}; totals ok={ok} missing={miss}", file=sys.stderr)
