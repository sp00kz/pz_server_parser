#!/usr/bin/env python3
"""Patch wl() in all builders to consult LINKMAP."""
import json, re, sys
TMP='<TOOLS>/work'
LMPATH=f'{TMP}/linkmap.json'

# JS builders: replace the old wl block with the __LINKMAP__ block
OLD_JS = ("const WIKI='https://pzwiki.net/wiki/';\n"
"function wl(v){if(v==null||v==='')return '';const b=String(v).replace(/\\s*\\([^)]*\\)\\s*$/,'').trim();"
"return `<a class=\"wk\" target=\"_blank\" rel=\"noopener\" href=\"${WIKI}${encodeURIComponent(b.replace(/ /g,'_'))}\">${v}</a>`;}")

NEW_JS = ("const WIKI='https://pzwiki.net/wiki/';\n"
"const LINKMAP=__LINKMAP__;\n"
"function wl(v){if(v==null||v==='')return '';const s=String(v);"
"if(s.includes('/'))return s.split('/').map(p=>wl(p.trim())).join(' / ');"
"let key=s.trim();if(key.endsWith(')')){const pi=key.lastIndexOf('(');if(pi>0)key=key.slice(0,pi).trim();}"
"let url=Object.prototype.hasOwnProperty.call(LINKMAP,key)?LINKMAP[key]:WIKI+encodeURIComponent(key.replace(/ /g,'_'));"
"if(!url)return v;"
"return `<a class=\"wk\" target=\"_blank\" rel=\"noopener\" href=\"${url}\">${v}</a>`;}")

JS_BUILDERS=['build_html.py','build_cars_html.py','build_guns_html.py','build_melee_html.py',
             'build_tools_html.py','build_food_html.py','build_forage_html.py']

LM_DEF_LINE = ("linkmap_js = __import__('json').dumps(__import__('json').load("
               "open('<TOOLS>/work/linkmap.json')), separators=(',',':'))\n")

for f in JS_BUILDERS:
    p=f'{TMP}/{f}'; src=open(p).read()
    if 'const LINKMAP=' in src:
        print(f"skip (already patched): {f}"); continue
    assert OLD_JS in src, f"OLD_JS not found in {f}"
    src=src.replace(OLD_JS, NEW_JS)
    # define linkmap_js after the shebang
    src=src.replace('#!/usr/bin/env python3\n', '#!/usr/bin/env python3\n'+LM_DEF_LINE, 1)
    # inject the replace into the final assembly
    assert "replace('__DATA__', data_js)" in src, f"__DATA__ assembly not found in {f}"
    src=src.replace("replace('__DATA__', data_js)", "replace('__DATA__', data_js).replace('__LINKMAP__', linkmap_js)")
    open(p,'w').write(src)
    print(f"patched JS builder: {f}")

# crafting: two identical f-string wl copies
cf=f'{TMP}/build_crafting.py'; src=open(cf).read()
if 'const LINKMAP=' in src:
    print("skip (already patched): build_crafting.py")
else:
    OLD_CR=('function wl(v){{if(v==null||v==='+"'')"+'return v;const s=String(v);if(s.includes(\'/\'))return s;'
            'return `<a class="wk" target="_blank" rel="noopener" '
            'href="https://pzwiki.net/wiki/${{encodeURIComponent(s.replace(/ /g,\'_\'))}}">${{s}}</a>`;}}')
    NEW_CR=("const WIKI='https://pzwiki.net/wiki/';\n"
            "const LINKMAP={linkmap_js};\n"
            "function wl(v){{if(v==null||v==='')return v;const s=String(v);"
            "if(s.includes('/'))return s.split('/').map(p=>wl(p.trim())).join(' / ');"
            "let key=s.trim();if(key.endsWith(')')){{const pi=key.lastIndexOf('(');if(pi>0)key=key.slice(0,pi).trim();}}"
            "let url=Object.prototype.hasOwnProperty.call(LINKMAP,key)?LINKMAP[key]:WIKI+encodeURIComponent(key.replace(/ /g,'_'));"
            "if(!url)return v;"
            'return `<a class="wk" target="_blank" rel="noopener" href="${{url}}">${{v}}</a>`;}}')
    cnt=src.count(OLD_CR)
    assert cnt==2, f"expected 2 crafting wl copies, found {cnt}"
    src=src.replace(OLD_CR, NEW_CR)
    # define linkmap_js after the recipes load
    m=re.search(r"recipes = json\.load\(open\([^\n]*\)\)\n", src)
    assert m, "recipes load line not found in build_crafting.py"
    src=src[:m.end()]+LM_DEF_LINE+src[m.end():]
    open(cf,'w').write(src)
    print("patched build_crafting.py (2 wl copies)")

# livestock: python wl
lf=f'{TMP}/build_livestock_html.py'; src=open(lf).read()
if '_LINKMAP' in src:
    print("skip (already patched): build_livestock_html.py")
else:
    OLD_LV=("""def wl(v):
    if not v: return v
    b = _re.sub(r'\\s*\\([^)]*\\)\\s*$', '', str(v)).strip()
    href = 'https://pzwiki.net/wiki/' + _up.quote(b.replace(' ', '_'))
    return f'<a class="wk" target="_blank" rel="noopener" href="{href}">{v}</a>'""")
    NEW_LV=("""_LINKMAP = json.load(open('<TOOLS>/work/linkmap.json'))
def wl(v):
    if not v: return v
    s = str(v)
    if '/' in s: return ' / '.join(wl(p.strip()) for p in s.split('/'))
    key = s.strip()
    if key.endswith(')'):
        pi = key.rfind('(')
        if pi > 0: key = key[:pi].strip()
    if key in _LINKMAP:
        url = _LINKMAP[key]
    else:
        url = 'https://pzwiki.net/wiki/' + _up.quote(key.replace(' ', '_'))
    if not url: return v
    return f'<a class="wk" target="_blank" rel="noopener" href="{url}">{v}</a>'""")
    assert OLD_LV in src, "OLD_LV not found in build_livestock_html.py"
    src=src.replace(OLD_LV, NEW_LV)
    open(lf,'w').write(src)
    print("patched build_livestock_html.py")

print("PATCH COMPLETE")
