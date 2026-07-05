# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 sp00kz. Dual-licensed; see LICENSE and COMMERCIAL.md.
"""Schema for every parsed dataset: each Dataset declares its fields and canonical roles (id/name/category/source) for uniform access."""
from dataclasses import dataclass, field as _f

NUM = (int, float)
STR = str
BOOL = bool
LIST = list
DICT = dict


@dataclass
class Field:
    key: str
    types: object          # a type or tuple of types
    nullable: bool = False  # value may be null; key still required
    role: str = ""         # 'id' | 'name' | 'category' | 'source' | ''
    note: str = ""


@dataclass
class Dataset:
    name: str
    file: str
    fields: list
    container: str = ""    # "" = top-level list; else key holding the list
    wiki: str = "name"     # role feeding the wiki link: 'name' or 'labels'
    extra_lists: tuple = ()  # other top-level keys to carry through

    def by_role(self, role):
        return next((f.key for f in self.fields if f.role == role), None)

    @property
    def id_key(self):       return self.by_role("id")
    @property
    def name_key(self):     return self.by_role("name")
    @property
    def category_key(self): return self.by_role("category")
    @property
    def source_key(self):   return self.by_role("source")


def _flds(*specs):
    """specs: (key, types[, nullable[, role]])"""
    out = []
    for s in specs:
        k, t = s[0], s[1]
        nullable = s[2] if len(s) > 2 else False
        role = s[3] if len(s) > 3 else ""
        out.append(Field(k, t, nullable, role))
    return out


DATASETS = {
 "seeds": Dataset("seeds", "seeds.json", _flds(
    ("name", STR, False, "name"), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("seed", STR, False, "id"), ("produce", STR),
    ("yieldMin", NUM), ("yieldMax", NUM), ("timeToGrow", NUM), ("stages", NUM),
    ("growthDays", NUM), ("rotDays", NUM), ("waterLvl", NUM), ("waterNeeded", NUM),
    ("sow", LIST), ("best", LIST), ("risk", LIST), ("bad", LIST),
    ("coldHardy", BOOL), ("scythe", BOOL), ("harvestPos", STR, True))),

 "vehicles": Dataset("vehicles", "vehicles.json", _flds(
    ("script", STR, False, "id"), ("name", STR, False, "name"),
    ("source", STR, False, "source"), ("category", STR, False, "category"),
    ("maxSpeed", NUM, True), ("engineForce", NUM, True), ("engineQuality", NUM, True),
    ("engineLoudness", NUM, True), ("mass", NUM), ("seats", NUM, True),
    ("engineRepairLevel", NUM, True), ("protection", NUM),
    ("trunk", NUM, True), ("trunkKind", STR, True), ("trunkApprox", BOOL),
    ("roofRack", NUM, True))),

 "animals": Dataset("animals", "animals.json", _flds(
    ("key", STR, False, "id"), ("name", STR, False, "name"),
    ("source", STR, False, "source"),
    ("matures", NUM), ("gestation", NUM, True), ("trailer", NUM), ("encumbrance", NUM),
    ("temperament", STR), ("products", LIST), ("breeds", LIST), ("breedsDiffer", BOOL))),

 "guns": Dataset("guns", "guns.json", _flds(
    ("item", STR, False, "id"), ("name", STR, False, "name"), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("ammo", STR), ("mag", NUM), ("minDmg", NUM), ("maxDmg", NUM), ("maxRange", NUM),
    ("sightRange", NUM, True), ("hitChance", NUM), ("critChance", NUM), ("critMult", NUM),
    ("recoil", NUM), ("aimTime", NUM), ("reload", NUM), ("projectiles", NUM, True),
    ("noise", NUM), ("jamChance", NUM), ("weight", NUM),
    ("durab", NUM, True), ("condMax", NUM, True), ("condLower", NUM, True))),

 "melee": Dataset("melee", "melee.json", _flds(
    ("item", STR, False, "id"), ("name", STR, False, "name"), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("sub", STR, True), ("minDmg", NUM), ("maxDmg", NUM), ("avg", NUM), ("dps", NUM),
    ("range", NUM), ("minRange", NUM, True), ("swing", NUM), ("minSwing", NUM),
    ("hits", NUM), ("crit", NUM, True), ("critMult", NUM, True), ("knock", NUM, True),
    ("condMax", NUM, True), ("condLower", NUM, True), ("durab", NUM, True),
    ("door", NUM, True), ("tree", NUM, True), ("twoH", BOOL), ("length", NUM, True),
    ("weight", NUM))),

 "tools": Dataset("tools", "tools.json", _flds(
    ("name", STR, False, "name"), ("fn", LIST), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("durab", NUM), ("condMax", NUM, True), ("condLower", NUM), ("weight", NUM),
    ("weapon", BOOL))),

 "recipes": Dataset("recipes", "recipes.json", _flds(
    ("id", STR, False, "id"), ("name", STR, False, "name"), ("category", STR, True, "category"),
    ("source", STR, False, "source"),
    ("skills", LIST), ("xp", DICT), ("req", DICT), ("time", NUM, True),
    ("consumed", LIST), ("tools", LIST), ("outputs", LIST), ("learn", BOOL)),
    wiki="labels"),

 "food": Dataset("food", "food.json", _flds(
    ("id", STR, False, "id"), ("name", STR, False, "name"), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("hunger", NUM, True), ("thirst", NUM, True), ("cal", NUM, True),
    ("carb", NUM, True), ("fat", NUM, True), ("prot", NUM, True),
    ("unhappy", NUM, True), ("stress", NUM, True), ("fresh", NUM, True), ("rot", NUM, True),
    ("cook", BOOL), ("raw", BOOL), ("weight", NUM), ("ev", DICT),
    ("freshMax", NUM, True), ("rotMax", NUM, True), ("desc", STR), ("variants", NUM)),
    container="items", extra_lists=("recipes",)),

 "xp": Dataset("xp", "xp.json", _flds(
    ("action", STR, False, "name"), ("skill", STR, False, "category"),
    ("xp", NUM, True), ("varies", BOOL), ("note", STR), ("category", STR), ("source", STR))),

 "forage": Dataset("forage", "forage.json", _flds(
    ("name", STR, False, "name"), ("category", STR, False, "category"),
    ("source", STR, False, "source"), ("zones", LIST),
    ("season", STR, True), ("best", STR, True), ("xp", NUM), ("skill", NUM),
    ("min", NUM), ("max", NUM), ("poison", BOOL))),

 "fishing": Dataset("fishing", "fishing.json", _flds(
    ("name", STR, False, "name"), ("item", STR, False, "id"), ("category", STR, False, "category"),
    ("source", STR, False, "source"),
    ("maxLen", NUM, True), ("maxWeight", NUM, True), ("trophyLen", NUM, True),
    ("trophyWeight", NUM, True), ("minLen", NUM), ("weightFactor", NUM, True),
    ("predator", BOOL), ("river", BOOL), ("lake", BOOL), ("minSkill", NUM, True),
    ("favorite", STR, True), ("favoriteCoeff", NUM, True),
    ("baits", DICT), ("jig", NUM), ("minnowLure", NUM), ("net", BOOL))),
}
