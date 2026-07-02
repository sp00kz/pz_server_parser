# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 sp00kz. Dual-licensed; see LICENSE and COMMERCIAL.md.
"""Resolve machine-specific paths and PZ_* settings."""
import os, glob, json, urllib.request

TOOLS = os.path.dirname(os.path.abspath(__file__))

# Local KEY=VALUE config; environment variables take precedence.
_local = os.environ.get("PZ_ENV_FILE") or os.path.join(TOOLS, "pz.env.local")
if os.path.isfile(_local):
    with open(_local, encoding="utf-8") as _fh:
        for _line in _fh:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

WORK  = os.environ.get("PZ_WORK") or os.path.join(TOOLS, "work")
REPO  = os.environ.get("PZ_REPO") or os.path.join(os.path.dirname(TOOLS), "pz_server")

def _find_dir(patterns):
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            if os.path.isdir(p):
                return p
    return ""

# Project Zomboid install media dir (Steam).
_CANDS = [
    "/mnt/*/program files (x86)/steam/steamapps/common/ProjectZomboid/media",
    "/mnt/*/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media",
    "/mnt/*/SteamLibrary/steamapps/common/ProjectZomboid/media",
    os.path.expanduser("~/.steam/steam/steamapps/common/ProjectZomboid/media"),
    os.path.expanduser("~/.local/share/Steam/steamapps/common/ProjectZomboid/media"),
    # macOS
    os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/ProjectZomboid/media"),
]
if os.name == "nt":  # Windows
    _CANDS = [
        r"C:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media",
        "?:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media",
        "?:/SteamLibrary/steamapps/common/ProjectZomboid/media",
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\ProjectZomboid\media"),
    ] + _CANDS
MEDIA = os.environ.get("PZ_MEDIA") or _find_dir(_CANDS)

def _split_steamapps(p):
    norm = p.replace("\\", "/")
    if "/steamapps/" in norm:
        return p[:norm.index("/steamapps/")] + os.sep + "steamapps"
    return ""
STEAMAPPS = os.environ.get("PZ_STEAMAPPS") or _split_steamapps(MEDIA)
WORKSHOP = os.environ.get("PZ_WORKSHOP") or (os.path.join(STEAMAPPS, "workshop", "content", "108600") if STEAMAPPS else "")
GAME = os.environ.get("PZ_GAME") or (os.path.dirname(MEDIA) if MEDIA else "")
JAR = os.path.join(GAME, "projectzomboid.jar") if GAME else ""

# Game user dir(s), per-OS.
if os.environ.get("PZ_USERDIR"):
    USERDIRS = [os.environ["PZ_USERDIR"]]
else:
    USERDIRS = sorted(glob.glob("/mnt/*/Users/*/Zomboid"))
    home_z = os.path.join(os.path.expanduser("~"), "Zomboid")
    if os.path.isdir(home_z): USERDIRS.append(home_z)

UA = os.environ.get("PZ_UA") or ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Site identity. AUTHOR empty omits the author meta tag; SITE_URL is used by build_sitemap.py.
AUTHOR = os.environ.get("PZ_AUTHOR", "")
SITE_URL = os.environ.get("PZ_SITE_URL", "").rstrip("/")

# Generator repository URL shown in page footers; "" hides the link.
TOOL_URL = os.environ.get("PZ_TOOL_URL", "https://github.com/sp00kz/pz_server_parser").rstrip("/")


# --- HTTP + HTML-embed helpers ----
def http_get(url, timeout=40):
    """GET `url`; return the body as text ('' on failure)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except Exception:
        return ""


def http_download(url, dst, timeout=60):
    """Download `url` to `dst`; return True if a non-empty file resulted."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if not data:
            return False
        with open(dst, "wb") as fh:
            fh.write(data)
        return os.path.getsize(dst) > 0
    except Exception:
        return False


def embed_json(obj):
    """Compact json.dumps escaped for safe embedding in an HTML <script> block."""
    return (json.dumps(obj, separators=(",", ":"))
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


if __name__ == "__main__":
    for k in ("TOOLS", "WORK", "REPO", "GAME", "MEDIA", "STEAMAPPS", "WORKSHOP", "JAR"):
        print(f"{k:10} {globals()[k]}")
    print("USERDIRS  ", USERDIRS)
    print(f"AUTHOR     {AUTHOR!r}")
    print(f"SITE_URL   {SITE_URL!r}")
    print(f"TOOL_URL   {TOOL_URL!r}")
