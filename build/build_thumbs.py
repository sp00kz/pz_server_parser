#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Write <=150px PNG thumbnails of the vehicle images to images/thumbs/."""
import os, glob
from PIL import Image
IMGDIR=pzenv.REPO + '/images'
THUMBDIR=f'{IMGDIR}/thumbs'
os.makedirs(THUMBDIR, exist_ok=True)
MAX=(150,150)   # thumbnail box (px)

srcs=[p for p in glob.glob(f'{IMGDIR}/*.png')]
tot_src=tot_thumb=n=0
for src in srcs:
    name=os.path.basename(src)
    dst=f'{THUMBDIR}/{name}'
    im=Image.open(src)
    im=im.convert('RGBA') if im.mode in ('P','LA') else im
    im.thumbnail(MAX, Image.LANCZOS)
    im.save(dst, 'PNG', optimize=True)
    tot_src+=os.path.getsize(src); tot_thumb+=os.path.getsize(dst); n+=1
print(f"{n} thumbs written to {THUMBDIR}")
if tot_src:
    print(f"full: {tot_src/1e6:.1f} MB  ->  thumbs: {tot_thumb/1e6:.2f} MB  ({tot_thumb/tot_src*100:.1f}%)")
