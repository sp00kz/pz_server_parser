# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 sp00kz. Dual-licensed; see LICENSE and COMMERCIAL.md.
"""Discover installed Workshop mods' media roots and translations.

A Workshop mod ships one or more media layouts:
  <mod>/media/...            legacy (B41) layout
  <mod>/common/media/...     B42 shared content
  <mod>/<version>/media/...  B42 version-specific content (e.g. 42.13/)
The game loads common/ plus the best matching version folder and ignores the
legacy media/ when a versioned layout exists; we mirror that.
"""
import os, re, glob
import pzenv

_VER_RE = re.compile(r'42(\.\d+)*$')


def mod_media_roots():
    """[(mod_folder_name, media_dir)] for every installed Workshop mod."""
    out = []
    ws = pzenv.WORKSHOP
    if not ws or not os.path.isdir(ws):
        return out
    for moddir in sorted(glob.glob(os.path.join(ws, '*', 'mods', '*'))):
        if not os.path.isdir(moddir):
            continue
        name = os.path.basename(moddir)
        roots = []
        common = os.path.join(moddir, 'common', 'media')
        if os.path.isdir(common):
            roots.append(common)
        vers = [os.path.basename(d) for d in glob.glob(os.path.join(moddir, '*'))
                if _VER_RE.fullmatch(os.path.basename(d)) and os.path.isdir(os.path.join(d, 'media'))]
        if vers:
            best = max(vers, key=lambda v: [int(x) for x in v.split('.')])
            roots.append(os.path.join(moddir, best, 'media'))
        elif not roots:
            legacy = os.path.join(moddir, 'media')
            if os.path.isdir(legacy):
                roots.append(legacy)
        out.extend((name, r) for r in roots)
    return out


def mod_files(relglob):
    """[(mod_name, path)] matching relglob under every mod media root."""
    out = []
    for name, root in mod_media_roots():
        for fp in sorted(glob.glob(os.path.join(root, relglob), recursive=True)):
            if os.path.isfile(fp):
                out.append((name, fp))
    return out


def load_mod_item_names(names):
    """Merge mod item display names into `names` (bare item id -> display name).

    Mods use the classic translation format (ItemName_Base.Foo = "...") or the
    generated JSON format ("Base.Foo": "..."); existing entries are kept.
    """
    for _mod, fp in mod_files('lua/shared/Translate/EN/*'):
        try:
            txt = open(fp, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for m in re.finditer(r'ItemName_[A-Za-z0-9_]+\.([A-Za-z0-9_]+)\s*=\s*"([^"]+)"', txt):
            names.setdefault(m.group(1), m.group(2))
        for m in re.finditer(r'"[A-Za-z0-9_]+\.([A-Za-z0-9_]+)"\s*:\s*"([^"]+)"', txt):
            names.setdefault(m.group(1), m.group(2))
    return names
