"""Shared data layer for the PZ reference build tooling: dataset loading, uniform role access, wiki-link keys, and validation."""
import json, os
from .schema import DATASETS, Dataset, Field

WORK = os.path.join(os.path.dirname(__file__), "..", "work")
WORK = os.path.abspath(WORK)


def _path(name):
    return os.path.join(WORK, DATASETS[name].file)


def load_raw(name):
    """Full parsed JSON (dict or list) exactly as on disk."""
    return json.load(open(_path(name), encoding="utf-8"))


def records(name, validate=True):
    """The list of records for a dataset (unwraps food's 'items' container)."""
    ds = DATASETS[name]
    data = load_raw(name)
    recs = data[ds.container] if ds.container else data
    if validate:
        errs = _validate_records(name, recs)
        if errs:
            raise SchemaError(f"{name}: {len(errs)} schema violation(s):\n  " + "\n  ".join(errs[:20]))
    return recs


# uniform role access
def _role_key(name, role):
    return DATASETS[name].by_role(role)

def get_id(rec, name):       k=_role_key(name,'id');       return rec.get(k) if k else rec.get('name')
def get_name(rec, name):     k=_role_key(name,'name');     return rec.get(k)
def get_category(rec, name): k=_role_key(name,'category'); return rec.get(k) if k else None
def get_source(rec, name):   k=_role_key(name,'source');   return rec.get(k) if k else None


# shared wiki-link key
def wiki_key(value):
    """Display name -> wiki lookup key: drop a trailing '(qualifier)'."""
    if value is None:
        return None
    s = str(value).strip()
    if s.endswith(")"):
        i = s.rfind("(")
        if i > 0:
            s = s[:i].strip()
    return s


# validation
class SchemaError(Exception):
    pass

def _type_ok(v, f):
    if v is None:
        return f.nullable
    return isinstance(v, f.types)

def _validate_records(name, recs):
    ds = DATASETS[name]
    errs = []
    known = {f.key for f in ds.fields}
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            errs.append(f"[{i}] not an object"); continue
        for f in ds.fields:
            if f.key not in r:
                errs.append(f"[{i}] missing field '{f.key}'")
            elif not _type_ok(r[f.key], f):
                errs.append(f"[{i}] field '{f.key}'={r[f.key]!r} not {getattr(f.types,'__name__',f.types)}"
                            + ("" if not f.nullable else " (nullable)"))
        for k in r:
            if k not in known:
                errs.append(f"[{i}] unknown field '{k}' (not in schema)")
    return errs

def validate(name):
    """Return list of violation strings for one dataset (empty = ok)."""
    ds = DATASETS[name]
    data = load_raw(name)
    recs = data[ds.container] if ds.container else data
    return _validate_records(name, recs)

def validate_all():
    """Validate every dataset; return {name: [errors]} for those with problems."""
    out = {}
    for name in DATASETS:
        try:
            e = validate(name)
        except FileNotFoundError:
            e = ["<file missing>"]
        if e:
            out[name] = e
    return out
