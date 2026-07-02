#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Resolve still-missing keys by generating morphological variants and checking direct title existence via the API."""
import json, urllib.parse, time, re, sys
TMP=pzenv.WORK
API="https://pzwiki.net/w/api.php"
res=json.load(open(f'{TMP}/resolved.json'))

def singular(w):
    out=set()
    if re.search(r'[^aeiou]ies$',w): out.add(w[:-3]+'y')
    if re.search(r'(ses|xes|zes|ches|shes)$',w): out.add(w[:-2])
    if w.endswith('s') and not w.endswith('ss'): out.add(w[:-1])
    return out

def variants(k):
    v=[]
    def add(x):
        if not x: return
        x=x.strip()
        if x and x!=k and x not in v: v.append(x)
    # spacing fixes at camelCase and letter/digit boundaries
    spaced=re.sub(r'(?<=[a-z])(?=[A-Z])',' ',k)
    spaced=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])',' ',spaced)
    spaced=re.sub(r'\s+',' ',spaced).strip()
    add(spaced)
    # singular of whole key and of last word of spaced form
    for s in singular(k): add(s)
    words=spaced.split(' ')
    if words:
        for s in singular(words[-1]):
            add(' '.join(words[:-1]+[s]))
    # plurals
    for base in (k, spaced):
        add(base+'s'); add(base+'es')
        if base.endswith('y'): add(base[:-1]+'ies')
    # disambiguation suffixes
    for dis in (' (crop)',' (food)',' (animal)'):
        add(spaced+dis)
    # berry/mushroom namespace forms
    add('Berries ('+spaced.lower()+')')
    add('Mushrooms ('+spaced.lower()+')')
    # strip "Wild " prefix
    if spaced.lower().startswith('wild '):
        add(spaced[5:])
    # berry-suffixed names map to the generic Berries page
    low=spaced.lower()
    if low.endswith('berry') or low.endswith('berries'):
        add('Berries')
    # strip "Crafted " prefix to base item
    if low.startswith('crafted '):
        base=spaced[8:]; add(base); add(base+' (crop)')
    # "...plant" seed names -> plant + (crop)
    for suf in ('plant','plants'):
        if low.endswith(suf) and len(spaced)>len(suf):
            base=spaced[:-len(suf)].strip()
            add(base.title()); add(base.title()+' (crop)')
    # title-case
    add(spaced.title())
    return v

RECHECK='--recheck' in sys.argv   # force re-testing every miss
cand=[k for k,info in res.items() if info['status']=='missing' and info.get('searched')!='junk'
      and (RECHECK or not info.get('vtested'))]
# variant universe
keyvars={k:variants(k) for k in cand}
allvars=sorted({vv for vs in keyvars.values() for vv in vs})
print(f"missing non-junk={len(cand)}; distinct variants to test={len(allvars)}", file=sys.stderr)

# batch existence check, following redirects
exist={}   # variant -> canonical title or None
def call(titles):
    q=urllib.parse.urlencode({'action':'query','format':'json','redirects':'1','titles':'|'.join(titles)})
    for a in range(4):
        body=pzenv.http_get(f"{API}?{q}",40)
        try: return json.loads(body)
        except Exception: time.sleep(2+a*3)
    # Abort rather than return {}: an outage must not be persisted as vtested='nomatch'.
    raise RuntimeError("API call failed (network?) for batch: "+titles[0])
B=50
for i in range(0,len(allvars),B):
    batch=allvars[i:i+B]
    d=call(batch).get('query',{})
    norm={x['from']:x['to'] for x in d.get('normalized',[])}
    redir={x['from']:x['to'] for x in d.get('redirects',[])}
    pages={p['title']:p for p in d.get('pages',{}).values()}
    def resolve(t):
        s=set()
        while t in norm and t not in s: s.add(t); t=norm[t]
        s=set()
        while t in redir and t not in s: s.add(t); t=redir[t]
        return t
    for t in batch:
        ft=resolve(t); pg=pages.get(ft)
        exist[t]=ft if (pg is not None and 'missing' not in pg) else None
    open(f'{TMP}/heartbeat.txt','w').write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    print(f"  variant batch {i//B+1}: tested {min(i+B,len(allvars))}/{len(allvars)}", file=sys.stderr)
    time.sleep(0.3)

acc=0
for k in cand:
    hit=False
    for v in keyvars[k]:
        if exist.get(v):
            res[k]={'status':'ok','canonical':exist[v],'via':'variant'}
            acc+=1; hit=True; break
    if not hit:
        res[k]['vtested']='nomatch'
json.dump(res,open(f'{TMP}/resolved.json','w'),indent=0)
ok=sum(1 for v in res.values() if v['status']=='ok')
miss=sum(1 for v in res.values() if v['status']=='missing')
print(f"DONE variant-accepted={acc}; totals ok={ok} missing={miss}", file=sys.stderr)
