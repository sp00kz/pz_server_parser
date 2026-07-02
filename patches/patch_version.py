#!/usr/bin/env python3
"""Add the PZ game version to every page as a header line, SEO meta tags, and the title."""
import re
TMP='<TOOLS>/work'
VER='42.19.0'; BRANCH='unstable'; BDATE='2026-06-01'
VFULL=f'Build {VER}'

DESC_SUFFIX=(f" Game version {VER} ({BRANCH} branch, {BDATE}); data parsed directly "
             "from the Project Zomboid game files.")
COMMON_KW=f"Project Zomboid, Build 42, B42, {VER}, PZ, Project Zomboid reference"

# per-builder SEO copy
PAGES={
 'build_html.py':      ("Seeds & Crops", "Project Zomboid seed and crop reference: growth time, water needs, sow/best/risk months and yields for every crop.", "seeds, crops, farming, growth time, yield, sow months"),
 'build_cars_html.py': ("Vehicles", "Project Zomboid vehicle stats: top speed, engine power and quality, mass, seats, trunk capacity and crash protection for the base game plus Workshop mods.", "vehicles, cars, vehicle stats, trunk capacity, engine, Workshop mods"),
 'build_livestock_html.py':("Livestock", "Project Zomboid livestock reference: products, maturation, gestation, trailer size, temperament and breed gene tendencies.", "livestock, animals, cow, pig, sheep, chicken, breeds, farming"),
 'build_guns_html.py': ("Firearms", "Project Zomboid firearms reference: damage, range, attachments and upgrades (scopes, suppressors) and durability.", "guns, firearms, weapons, attachments, scopes, suppressors, durability"),
 'build_melee_html.py':("Melee Weapons", "Project Zomboid melee weapons: damage, DPS, reach, swing speed, crit, knockdown and durability.", "melee weapons, damage, dps, reach, durability"),
 'build_tools_html.py':("Tools", "Project Zomboid tools: what each does, durability (uses before breaking) and weight, including weapons that double as tools.", "tools, durability, axe, hammer, saw, crafting tools"),
 'build_crafting.py':  ("Crafting", "Project Zomboid crafting and building recipes for every skill: XP, materials, tools, craft time and no-waste crafting cycles.", "crafting, recipes, blacksmithing, carpentry, tailoring, XP, skills"),
 'build_food_html.py': ("Food & Nutrition", "Project Zomboid food and nutrition: hunger and thirst restored, calories, carbs, fat, protein, mood effects and spoilage for every food.", "food, nutrition, calories, hunger, thirst, cooking, spoilage"),
 'build_forage_html.py':("Foraging", "Project Zomboid foraging: natural forageables (berries, mushrooms, herbs, fruit, vegetables) with zones, seasons, level needed, amount, XP and poison flags.", "foraging, berries, mushrooms, herbs, poison, wild plants"),
}

def meta_block(label, desc, kw):
    full=f"{desc}{DESC_SUFFIX}"
    og=f"Project Zomboid {VFULL} — {label}"
    return ("\n"
        f'<meta name="description" content="{full}">\n'
        f'<meta name="keywords" content="{COMMON_KW}, {kw}">\n'
        '<meta name="robots" content="index, follow">\n'
        '<meta name="author" content="">\n'
        '<meta property="og:type" content="website">\n'
        f'<meta property="og:title" content="{og}">\n'
        f'<meta property="og:description" content="{full}">\n'
        f'<meta name="pz:gameversion" content="{VER}">\n'
        f'<meta name="pz:branch" content="{BRANCH}">\n'
        f'<meta name="pz:builddate" content="{BDATE}">')

VER_DIV=(f'<div class="gamever" style="margin-top:6px;font-size:11px;color:var(--muted)">'
         f'Game data: <b style="color:var(--accent)">Project Zomboid {VFULL}</b>'
         f' · {BRANCH} branch · built {BDATE}</div>\n')

for f,(label,desc,kw) in PAGES.items():
    p=f'{TMP}/{f}'; src=open(p).read()
    if 'pz:gameversion' in src:
        print(f"skip (already versioned): {f}"); continue
    mb=meta_block(label,desc,kw)
    # SEO meta after the viewport tag
    src2=re.sub(r'(<meta name="viewport"[^>]*>)', lambda m: m.group(1)+mb, src)
    assert src2!=src, f"viewport anchor not found in {f}"; src=src2
    # version line before each </header>
    assert '</header>' in src, f"</header> not found in {f}"
    src=src.replace('</header>', VER_DIV+'</header>')
    # version in the title
    src=src.replace('(B42 + mods)', f'(Build {VER} + mods)').replace('(B42)', f'(Build {VER})')
    src=src.replace('<title>PZ Crafting — {disp}</title>', f'<title>PZ Crafting — {{disp}} — Build {VER}</title>')
    # replace visible "Build 42 ·" with the exact version
    src=src.replace('Build 42 ·', f'Build {VER} ·')
    open(p,'w').write(src)
    print(f"versioned: {f}")
print("DONE")
