#!/usr/bin/env python3
"""Check two pages are equivalent after a key rename (exit 0 equal, 1 differs)."""
import sys, re, json

dec = json.JSONDecoder()

def extract(html, name):
    m = re.search(rf'const {name}\s*=\s*', html)
    if not m: return None
    start = m.end()
    val, end = dec.raw_decode(html, start)
    return (start, end, val)

def rename_keys(obj, kmap):
    if isinstance(obj, list):
        return [rename_keys(x, kmap) for x in obj]
    if isinstance(obj, dict):
        return {kmap.get(k, k): rename_keys(v, kmap) for k, v in obj.items()}
    return obj

def main():
    a = sys.argv
    old_f, new_f = a[1], a[2]
    data_map = {}; tokens = []
    i = 3
    while i < len(a):
        if a[i] == '--data':
            k, v = a[i+1].split('=', 1); data_map[k] = v; i += 2
        elif a[i] == '--token':
            k, v = a[i+1].split('=', 1); tokens.append((k, v)); i += 2
        else: i += 1
    old = open(old_f, encoding="utf-8").read(); new = open(new_f, encoding="utf-8").read()

    ok = True
    # 1. data arrays
    for blob in ('DATA', 'RECIPES'):
        eo = extract(old, blob); en = extract(new, blob)
        if eo is None and en is None: continue
        if (eo is None) != (en is None):
            print(f"FAIL: {blob} present in only one file"); ok = False; continue
        renamed = rename_keys(eo[2], data_map)
        if renamed == en[2]:
            print(f"ok: {blob} values identical after rename ({len(en[2]) if isinstance(en[2],list) else '?'} records)")
        else:
            print(f"FAIL: {blob} differs beyond rename"); ok = False

    # 2. shell (arrays stripped from both files)
    def strip(html):
        out = html;
        for blob in ('RECIPES', 'DATA'):   # RECIPES first
            e = extract(out, blob)
            if e: out = out[:e[0]] + 'BLOB' + out[e[1]:]
        return out
    old_shell = strip(old); new_shell = strip(new)
    for frm, to in tokens:
        old_shell = old_shell.replace(frm, to)
    if old_shell == new_shell:
        print("ok: shell identical after token rewrites")
    else:
        ok = False
        # show first difference
        import difflib
        diff = list(difflib.unified_diff(old_shell.splitlines(), new_shell.splitlines(), lineterm='', n=1))
        print("FAIL: shell differs beyond tokens:")
        for ln in diff[:40]: print("   " + ln)

    print("\n" + ("RENDERED-EQUIVALENT ✓" if ok else "NOT EQUIVALENT ✗"))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
