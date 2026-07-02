# Project Zomboid Reference — build tooling

[Demo Site](https://sp00kz.github.io/pz_server/)

Generates a self-contained, static **Project Zomboid Build 42** reference website
by reading the data straight out of an installed copy of the game. Every page is a
single HTML file with its data and styling embedded — no server, no database, no
build step for the *viewer*; you just open the files or host them anywhere static.

This repository is the **generator**, not the site. Run it against your own game
install and it writes the finished pages into a separate output folder of your
choosing.

## What it generates

Sortable, filterable tables for: seeds & crops, vehicles, livestock, firearms,
melee weapons, tools, crafting recipes (one sub-page per skill), food & nutrition,
foraging, and action XP — plus a landing page and a `sitemap.xml`. Item names link
to the [PZ Wiki](https://pzwiki.net); modded vehicles link to their Steam Workshop
page.

## Requirements

| Need | Used for | Required? |
|------|----------|-----------|
| **Project Zomboid** (Build 42), installed | source of all data | yes |
| **Python ≥ 3.8** | the whole pipeline | yes |
| **Pillow** (`pip install Pillow`) | image thumbnails | yes |
| **Node.js** + `npm install` | the optional `verify` render check | optional |

The network steps (`update` / `links` / `images`) use Python's standard library —
no `curl` or other external binary is required. For the fullest result run `update`
once (online) so pages get vehicle images and curated wiki links; afterwards
`rebuild` (parse + build) works fully offline with just Python + Pillow. A
never-online `rebuild` still succeeds, but vehicles have no images and links fall
back to default wiki URLs until you run `update`/`links`. Node is only for `verify`.

## 1. Get the code

```sh
git clone https://github.com/sp00kz/pz_server_parser.git
cd pz_server_parser
```

## 2. Install the prerequisites

<sub>Click your operating system to expand.</sub>

<details>
<summary><b>Linux</b></summary>

```sh
# Debian / Ubuntu (use your distro's package manager otherwise)
sudo apt update
sudo apt install python3 python3-pip

# Pillow — inside a virtualenv (recommended; re-run the activate line in every new shell):
python3 -m venv .venv && . .venv/bin/activate && pip install Pillow
# …or system-wide on PEP 668 distros (Ubuntu 23.04+ / Debian 12+):
pip install --break-system-packages Pillow      # or: sudo apt install python3-pil

# Optional: Node.js for the `verify` render check
sudo apt install nodejs npm
npm install            # installs jsdom into ./node_modules
```
</details>

<details>
<summary><b>Windows (WSL)</b></summary>

Run everything inside your WSL distribution; the steps are identical to Linux.
WSL can read your Windows Steam install through `/mnt/<drive>/…`, which the tool
auto-detects (see step 3).

```sh
sudo apt update
sudo apt install python3 python3-pip
python3 -m venv .venv && . .venv/bin/activate && pip install Pillow

# Optional: Node.js for the `verify` render check
sudo apt install nodejs npm
npm install
```
</details>

<details>
<summary><b>Windows (native)</b></summary>

Install **Python 3** from [python.org](https://www.python.org/downloads/) and tick
**“Add python.exe to PATH”** in the installer. Then, in PowerShell or Command
Prompt:

```bat
py -m pip install Pillow

:: Optional: install Node.js from nodejs.org for the verify render check
npm install
```

Use the cross-platform entry point `py pz.py …` (the `.sh` scripts need a Unix
shell; `pz.py` does not).
</details>

<details>
<summary><b>macOS</b></summary>

```sh
# Using Homebrew (https://brew.sh)
brew install python
pip3 install Pillow

# Optional: Node.js for the `verify` render check
brew install node
npm install
```
</details>

## 3. Configure

Copy the example config and set your two values:

```sh
cp pz.env.local.example pz.env.local
```

```ini
# pz.env.local  (gitignored — nothing here is committed)
PZ_AUTHOR=Your Name                          # written to each page's <meta author>; omit to skip
PZ_SITE_URL=https://USERNAME.github.io/REPO  # absolute, no trailing slash; required for sitemap.xml
PZ_TOOL_URL=https://github.com/USERNAME/REPO # footer "build your own" link to your generator; set "" to hide
```

You can also set these as ordinary environment variables instead of using the file
— real environment variables take precedence.

**Output location.** By default the finished site is written to a sibling folder
named `pz_server` next to this tooling directory (created automatically if it does
not exist). Point it anywhere with `PZ_REPO`:

```sh
export PZ_REPO=/path/to/where/the/site/should/go
```

**Game files.** The tool auto-detects a default Steam install. If detection fails
(custom Steam library, non-standard path), set `PZ_MEDIA` to the game's `media`
folder. Examples per OS — *replace the drive/letter/path with your own*:

<details>
<summary><b>Where the game's <code>media</code> folder usually lives</b></summary>

```sh
# Linux
PZ_MEDIA="$HOME/.steam/steam/steamapps/common/ProjectZomboid/media"
# or
PZ_MEDIA="$HOME/.local/share/Steam/steamapps/common/ProjectZomboid/media"

# WSL (reading the Windows install)
PZ_MEDIA="/mnt/c/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media"

# macOS
PZ_MEDIA="$HOME/Library/Application Support/Steam/steamapps/common/ProjectZomboid/media"
```

```bat
:: Windows (native)
set "PZ_MEDIA=C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media"
```

A second Steam library would replace the `…/Steam/steamapps` prefix with your
library's path, e.g. `D:\SteamLibrary\steamapps\common\ProjectZomboid\media`.
Add these to `pz.env.local` to make them stick.
</details>

Check what got detected at any time:

```sh
python3 pzenv.py
```

## 4. Run

The cross-platform entry point is `pz.py` (works on Linux, WSL, Windows, macOS):

```sh
python3 pz.py rebuild        # offline: parse the game files + build all pages
python3 pz.py update         # full refresh: version + parse + images + links + build + diff (needs network)
```

| Command | Does |
|---------|------|
| `python3 pz.py rebuild`   | parse + build, no network (fastest; use after editing the tooling) |
| `python3 pz.py update`    | the works: version check → parse → fetch images → audit wiki links → build → diff |
| `python3 pz.py parse`     | parse the game files into `work/*.json` |
| `python3 pz.py build`     | build the HTML/sitemap from existing `work/*.json` |
| `python3 pz.py images`    | fetch vehicle images (network) |
| `python3 pz.py links`     | re-audit the PZ-Wiki links (network) |
| `python3 pz.py version`   | print the detected game version/build |
| `python3 pz.py diff`      | show what changed since the previous parse |
| `python3 pz.py validate`  | check parsed data against the schema |
| `python3 pz.py verify A B`| render two pages headless (jsdom) and compare — needs Node |

`python3 pz.py version --record` stamps the current build as the baseline that
later `diff`s compare against. If you installed Pillow into a virtualenv, activate
it (`. .venv/bin/activate`) in each new shell before running these commands.

On Linux / WSL / macOS you can alternatively use the bash front-end `./pz <command>`
(same verbs); it prepends a vendored Node under `.node/` to `PATH` if you have put
one there, otherwise it uses your system Node.

After a run, open the generated pages directly, or serve the output folder with any
static server, e.g.:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory "$PZ_REPO"
```

## How it works

```
game files ──parse/*.py──▶ work/*.json ──build/*.py──▶ <output>/*.html
                  │                           ▲
            schema validation          shared engine (pzbuild.py)
            (pzschema/)                 + wiki link map (links/)
```

- **`pzenv.py`** resolves every machine-specific path and the optional
  `PZ_AUTHOR` / `PZ_SITE_URL` identity. It is the only place that touches the
  environment, and it loads `pz.env.local` if present.
- **`parse/`** reads the game's `scripts/` and `lua/` files into normalised JSON
  in `work/`.
- **`pzschema/`** declares the shape of every dataset and validates it.
- **`build/`** + **`pzbuild.py`** render the JSON into pages through one shared
  table/link engine, so all pages stay consistent.
- **`links/`** audits each item name against the PZ Wiki and produces the link map.

`work/` is regenerated output and is gitignored.

## Notes & limitations

- Built and tested against Project Zomboid **Build 42** (unstable branch). Game
  patches can rename or move fields; run `python3 pz.py diff` after updating to see
  what moved.
- The wiki-link audit talks to pzwiki.net and uses a browser `User-Agent`
  (overridable with `PZ_UA`) to pass its Cloudflare check. It caches results in
  `work/` so re-runs are incremental.
- Modded-vehicle images come from the locally installed Workshop content; vanilla
  images come from the PZ Wiki. Nothing personal or environment-specific is written
  into the generated site beyond the `PZ_AUTHOR` / `PZ_SITE_URL` you configure.

## License

This **generator** is dual-licensed:

- **GNU AGPL-3.0** for everyone — see [`LICENSE`](LICENSE). Free to use, modify and
  share, but copyleft: derivatives and network-served versions must also be AGPL,
  with source.
- **Commercial license** for use without the AGPL's obligations (e.g. in a
  closed-source product) — see [`COMMERCIAL.md`](COMMERCIAL.md). Contact
  sp00kz &lt;ben@thegeeks.us&gt;.

Copyright © 2026 sp00kz.

The license covers the **generator code only**. The data it reads is part of
*Project Zomboid*, © The Indie Stone — this is an unofficial fan tool, not
affiliated with or endorsed by The Indie Stone, and the game's data and assets
remain their property. The generated HTML pages are not covered by this license.
