#!/usr/bin/env python3
"""Detect the installed Project Zomboid version and compare it to work/version.json (exit 10 if changed)."""
import os, sys, re, json, time, struct, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pzenv

# ---- Java .class constant-pool reader ----
def _cp(d):
    i, n = 10, struct.unpack('>H', d[8:10])[0]
    cp, j = {}, 1
    while j < n:
        tag = d[i]; i += 1
        if tag == 1:
            ln = struct.unpack('>H', d[i:i+2])[0]; i += 2
            cp[j] = ('utf', d[i:i+ln].decode('utf8', 'replace')); i += ln
        elif tag in (3, 4): cp[j] = ('int', struct.unpack('>i', d[i:i+4])[0]); i += 4
        elif tag in (5, 6): cp[j] = ('long', 0); i += 8; j += 1
        elif tag == 7: cp[j] = ('class', struct.unpack('>H', d[i:i+2])[0]); i += 2
        elif tag == 8: cp[j] = ('str', struct.unpack('>H', d[i:i+2])[0]); i += 2
        elif tag in (9, 10, 11): cp[j] = ('ref', struct.unpack('>HH', d[i:i+4])); i += 4
        elif tag == 12: cp[j] = ('nt', struct.unpack('>HH', d[i:i+4])); i += 4
        elif tag == 15: i += 3
        elif tag == 16: i += 2
        elif tag in (17, 18): i += 4
        elif tag in (19, 20): i += 2
        else: raise ValueError(f"cp tag {tag}")
        j += 1
    return cp

def _gameversion_major_minor(classbytes):
    """Recover (major, minor) from the GameVersion(...) constructor call sites."""
    d = classbytes; cp = _cp(d)
    def cname(idx):
        c = cp.get(idx); return cp.get(c[1], ('', ''))[1] if c and c[0] == 'class' else ''
    gv = set()
    for k, v in cp.items():
        if v[0] == 'ref':
            ci, nti = v[1]; nt = cp.get(nti)
            if nt and nt[0] == 'nt' and 'GameVersion' in cname(ci) and cp.get(nt[1][0], ('', ''))[1] == '<init>':
                gv.add(k)
    cands = []
    for p in range(len(d) - 2):
        if d[p] == 0xB7 and struct.unpack('>H', d[p+1:p+3])[0] in gv:  # invokespecial
            w = d[max(0, p-14):p]; ints = []; q = 0
            while q < len(w):
                op = w[q]
                if op == 0x10 and q+1 < len(w): ints.append(w[q+1] - 256 if w[q+1] > 127 else w[q+1]); q += 2
                elif op == 0x11 and q+2 < len(w): ints.append(struct.unpack('>h', w[q+1:q+3])[0]); q += 3
                elif 0x03 <= op <= 0x08: ints.append(op - 0x03); q += 1
                else: q += 1
            if len(ints) >= 2: cands.append((ints[-2], ints[-1]))
    # highest (major, minor) among the constructor calls
    cands = [c for c in cands if 30 <= c[0] <= 99]
    return max(cands) if cands else None

def _gitversion(classbytes):
    runs = [r.decode('utf8', 'replace') for r in re.findall(rb'[\x20-\x7e]{3,}', classbytes)]
    commit = next((re.search(r'[0-9a-f]{40}', s).group() for s in runs if re.search(r'[0-9a-f]{40}', s)), None)
    date = next((re.search(r'\d{4}-\d{2}-\d{2}', s).group() for s in runs if re.search(r'\d{4}-\d{2}-\d{2}', s)), None)
    branch = None
    for s in runs:
        if commit and commit in s and '/' in s:           # e.g. "steam/release <hash>"
            branch = s.split(commit)[0].strip().lstrip('0123456789').strip() or None
            break
    return commit, date, branch

def detect():
    jar = pzenv.JAR
    if not (jar and os.path.exists(jar)):
        return None
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    ver = {'version': None, 'major': None, 'minor': None,
           'commit': None, 'builddate': None, 'branch': None,
           'steam_buildid': None, 'betakey': None, 'jar': jar}
    if 'zombie/core/Core.class' in names:
        mm = _gameversion_major_minor(z.read('zombie/core/Core.class'))
        if mm:
            ver['major'], ver['minor'] = mm
            ver['version'] = f"{mm[0]}.{mm[1]}"
    if 'zombie/GitVersion.class' in names:
        ver['commit'], ver['builddate'], ver['branch'] = _gitversion(z.read('zombie/GitVersion.class'))
    acf = (pzenv.STEAMAPPS + os.sep + 'appmanifest_108600.acf') if pzenv.STEAMAPPS else ''
    if acf and os.path.exists(acf):
        a = open(acf, encoding='utf-8', errors='replace').read()
        m = re.search(r'"buildid"\s*"([^"]+)"', a); ver['steam_buildid'] = m.group(1) if m else None
        m = re.search(r'"BetaKey"\s*"([^"]+)"', a); ver['betakey'] = m.group(1) if m else 'public'
    return ver if (ver['version'] or ver['commit']) else None

def _human(v):
    return (f"Build {v.get('version') or '?'} "
            f"({v.get('branch') or 'release'}, {v.get('builddate') or '?'}, "
            f"commit {(v.get('commit') or '')[:8]}, Steam {v.get('steam_buildid')}, beta: {v.get('betakey')})")

def main():
    cur = detect()
    if not cur:
        print(f"Could not read version from install (jar: {pzenv.JAR or 'not found'}).", file=sys.stderr)
        return 2
    print("installed:", _human(cur))
    rec_path = os.path.join(pzenv.WORK, 'version.json')
    rec = json.load(open(rec_path, encoding="utf-8")) if os.path.exists(rec_path) else None
    if '--record' in sys.argv:
        cur['recorded_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        os.makedirs(pzenv.WORK, exist_ok=True)
        json.dump(cur, open(rec_path, 'w', encoding="utf-8"), indent=1)
        print("recorded to", rec_path); return 0
    if rec is None:
        print("recorded:  (none) -> CHANGED (first run)"); return 10
    print("recorded: ", _human(rec))
    same = (rec.get('commit') == cur['commit'] and rec.get('version') == cur['version']
            and rec.get('steam_buildid') == cur['steam_buildid'])
    print("UNCHANGED" if same else "CHANGED")
    return 0 if same else 10

if __name__ == "__main__":
    sys.exit(main())
