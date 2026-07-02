#!/usr/bin/env python3
"""Generate sitemap.xml listing the root and every page. Set the site URL via PZ_SITE_URL."""
import os, sys, glob, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pzenv, pzbuild

SITE = pzenv.SITE_URL
if not SITE:
    sys.exit("PZ_SITE_URL is not set — export it (e.g. https://USERNAME.github.io/REPO) "
             "or add it to pz.env.local; see README.")
REPO = pzenv.REPO
lastmod = datetime.date.today().isoformat()

main = [h for h, _ in pzbuild.NAV_TABS if os.path.exists(os.path.join(REPO, h))]
craft = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, "craft_*.html")))

def entry(fn):
    loc = SITE + "/" if fn == "index.html" else f"{SITE}/{fn}"
    pri = "1.0" if fn == "index.html" else ("0.5" if fn.startswith("craft_") else "0.8")
    return (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n    <priority>{pri}</priority>\n  </url>")

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "\n".join(entry(f) for f in main + craft) + "\n</urlset>\n")

out = os.path.join(REPO, "sitemap.xml")
open(out, "w", encoding="utf-8").write(xml)
print(f"Wrote {out} ({len(main)+len(craft)} URLs, lastmod {lastmod})")
