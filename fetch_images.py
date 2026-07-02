#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '.')))
import pzenv
"""Fetch a vehicle image for any vehicle that lacks one, then regenerate thumbnails.

  modded vehicles  -> copy the mod's local Workshop preview.png
  vanilla vehicles -> download <Script>_Model.png from PZwiki
  python3 fetch_images.py [--test|--refetch]
"""
import json, os, re, sys, subprocess, tempfile, urllib.parse
TMP = pzenv.WORK
REPO = pzenv.REPO
IMG = f"{REPO}/images"
WS = pzenv.WORKSHOP
API = "https://pzwiki.net/w/api.php"

def load(f): return json.load(open(f"{TMP}/{f}"))
def sanit(s): return re.sub(r'[^A-Za-z0-9]', '_', s)

def wiki_file_url(title):
    q = urllib.parse.urlencode({'action':'query','titles':f'File:{title}','prop':'imageinfo','iiprop':'url','format':'json'})
    try:
        body = pzenv.http_get(f"{API}?{q}", 30)
        p = list(json.loads(body)['query']['pages'].values())[0]
        return None if 'missing' in p else p.get('imageinfo',[{}])[0].get('url')
    except Exception:
        return None

def download(url, dst):
    return pzenv.http_download(url, dst, 60)

def valid_png(path):
    try:
        from PIL import Image
        Image.open(path).verify(); return True
    except Exception:
        return False

def mod_preview(source, wsmap):
    wsid = wsmap.get(source)
    if not wsid: return None
    p = f"{WS}/{wsid}/mods/{source}/preview.png"
    return p if os.path.exists(p) else None

def self_test():
    print("self-test: PZwiki vanilla download + mod-preview lookup (no changes)")
    ok = True
    tmp_png = os.path.join(tempfile.gettempdir(), "_fi_vanilla.png")
    url = wiki_file_url("CarNormal_Model.png")
    if url and download(url, tmp_png) and valid_png(tmp_png):
        from PIL import Image; print(f"  vanilla  OK  {Image.open(tmp_png).size}  {url}")
    else:
        ok = False; print("  vanilla  FAIL")
    wsmap = load("workshop_map.json")
    src = next((s for s in wsmap if os.path.exists(f"{WS}/{wsmap[s]}/mods/{s}/preview.png")), None)
    if src and valid_png(f"{WS}/{wsmap[src]}/mods/{src}/preview.png"):
        print(f"  mod      OK  preview for '{src}'")
    else:
        ok = False; print("  mod      FAIL")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1

def main():
    if "--test" in sys.argv:
        return self_test()
    refetch = "--refetch" in sys.argv
    cars = load("vehicles.json")
    imgmap = load("images_map.json")
    vmap = load("vanilla_images_map.json")
    wsmap = load("workshop_map.json")
    os.makedirs(IMG, exist_ok=True)

    def has_image(c):
        return bool(imgmap.get(c['source']) or vmap.get(c['script']))

    todo = [c for c in cars if refetch or not has_image(c)]
    mod_sources, van_scripts = {}, {}
    for c in todo:
        if c['source'] != 'Vanilla': mod_sources.setdefault(c['source'], c)
        else: van_scripts.setdefault(c['script'], c)
    print(f"vehicles missing an image: {len(todo)}  (mods: {len(mod_sources)}, vanilla: {len(van_scripts)})")

    got = fail = 0
    for src, c in mod_sources.items():
        rel = f"images/{sanit(src)}.png"; dst = f"{REPO}/{rel}"
        pv = mod_preview(src, wsmap)
        if pv:
            import shutil; shutil.copyfile(pv, dst)
            if valid_png(dst): imgmap[src] = rel; got += 1; print(f"  mod  {src} -> {rel}")
            else: fail += 1; print(f"  mod  {src} FAIL (bad preview)")
        else:
            fail += 1; print(f"  mod  {src} FAIL (no local Workshop preview)")
    for scr, c in van_scripts.items():
        rel = f"images/m_{sanit(scr)}.png"; dst = f"{REPO}/{rel}"
        url = wiki_file_url(f"{scr}_Model.png")
        if url and download(url, dst) and valid_png(dst):
            vmap[scr] = rel; got += 1; print(f"  van  {scr} -> {rel}")
        else:
            fail += 1; print(f"  van  {scr} ({c['name']}) FAIL (no PZwiki render)")

    if got:
        json.dump(imgmap, open(f"{TMP}/images_map.json", "w"), indent=0)
        json.dump(vmap, open(f"{TMP}/vanilla_images_map.json", "w"), indent=0)
        print("regenerating thumbnails...")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "build", "build_thumbs.py")], check=False)
    print(f"DONE fetched={got} failed={fail}. " + ("Rebuild: ./build_site.sh" if got else "nothing to do."))
    return 0

if __name__ == "__main__":
    sys.exit(main())
