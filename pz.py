#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 sp00kz. Dual-licensed; see LICENSE and COMMERCIAL.md.
"""Cross-platform entry point for the PZ build tooling."""
import os, sys, json, shutil, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pzenv

PY = sys.executable
DATASETS = ["seeds", "vehicles", "animals", "guns", "melee", "tools", "recipes", "food", "forage", "xp", "fishing"]
BUILDERS = ["build_html", "build_cars_html", "build_livestock_html", "build_guns_html",
            "build_melee_html", "build_tools_html", "build_crafting", "build_food_html",
            "build_forage_html", "build_xp_html", "build_fishing_html", "build_thumbs", "build_sw",
            "build_map_html"]

def _run(args):
    r = subprocess.run(args)
    if r.returncode: sys.exit(r.returncode)

def parse():
    os.makedirs(pzenv.WORK, exist_ok=True)
    prev = os.path.join(pzenv.WORK, "prev"); os.makedirs(prev, exist_ok=True)
    for f in glob.glob(os.path.join(pzenv.WORK, "*.json")):
        shutil.copy2(f, prev)
    for k in DATASETS:
        print(f"  parse {k}")
        r = subprocess.run([PY, os.path.join(HERE, "parse", f"parse_{k}.py")],
                           capture_output=True, text=True)
        if r.returncode or not r.stdout:
            sys.stderr.write(r.stderr); sys.exit(f"parse_{k} failed")
        if r.stderr:  # summary + warnings
            sys.stderr.write("".join(f"    {ln}\n" for ln in r.stderr.splitlines()))
        with open(os.path.join(pzenv.WORK, f"{k}.json"), "w", encoding="utf-8") as fh:
            fh.write(r.stdout)
    _run([PY, os.path.join(HERE, "validate_schema.py")])

def links(extra):
    for s in ["links/extract_universe.py", "links/validate.py", "links/resolve_misses.py",
              "links/resolve_variants.py", "build/build_linkmap.py"]:
        _run([PY, os.path.join(HERE, s)] + (extra if "resolve_" in s else []))

def build():
    os.makedirs(pzenv.REPO, exist_ok=True)
    os.makedirs(pzenv.WORK, exist_ok=True)
    # Seed empty maps when the network-step outputs are absent.
    for fn, note in (("linkmap.json", "wiki links will use default URLs (run `links` or `update` for curated links)"),
                     ("images_map.json", None), ("vanilla_images_map.json", None)):
        p = os.path.join(pzenv.WORK, fn)
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("{}")
            if note:
                print(f"  note: {fn} not found — {note}")
    for b in BUILDERS:
        _run([PY, os.path.join(HERE, "build", f"{b}.py")])
    _run([PY, os.path.join(HERE, "build_index.py")])
    _run([PY, os.path.join(HERE, "build_sitemap.py")])
    print("site written to", pzenv.REPO)

def node_bin():
    for nb in glob.glob(os.path.join(HERE, ".node", "*", "bin", "node*")):
        return nb
    return shutil.which("node")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    extra = sys.argv[2:]
    if cmd == "parse": parse()
    elif cmd == "links": links(extra)
    elif cmd == "build": build()
    elif cmd == "rebuild": parse(); build()
    elif cmd == "update":
        _run([PY, os.path.join(HERE, "version_check.py")]); parse()
        _run([PY, os.path.join(HERE, "fetch_images.py")]); links(extra); build()
        _run([PY, os.path.join(HERE, "diff_data.py")])
        print("\nReview, then record + commit:\n  python pz.py version --record")
    elif cmd == "images": _run([PY, os.path.join(HERE, "fetch_images.py")] + extra)
    elif cmd == "version": _run([PY, os.path.join(HERE, "version_check.py")] + extra)
    elif cmd == "diff": _run([PY, os.path.join(HERE, "diff_data.py")] + extra)
    elif cmd == "validate": _run([PY, os.path.join(HERE, "validate_schema.py")])
    elif cmd == "verify":
        nb = node_bin()
        if not nb: sys.exit("node not found (install Node.js or use the bundled .node/)")
        _run([nb, os.path.join(HERE, "verify_dom.js")] + extra)
    else:
        print("usage: python pz.py {update|rebuild|parse|links|build|images|version|diff|validate|verify A B}")

if __name__ == "__main__":
    main()
