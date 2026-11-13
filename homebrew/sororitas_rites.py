"""Adepta Sororitas: the seven Rites of War, called by build_catalogue.py for that faction.

The md's Rites name units as the book does ("Paragon Warsuit Squads", "Sisters Repentia Squads"), which the
builder's Rite reading only partly matches, so their effects are made here from explicit unit lists. The builder's
own reading of them (slots, bans, rules and limits) is cleared first; its Warlord limits (who may lead each
Rite, from the Prerequisites) are kept.

What the app can check is built: the slots a Rite opens, the Line sub-type, the rules it grants, the units it
bars (hidden, and an error if taken), the Troops that may fill its Compulsory Troops slots, and the slots it
closes. Everything else (Faith points, re-rolls, embarking, reserves, once-per-battle abilities, "no more Battle
Sisters Squads than penitent units", Fortifications and Allied Detachments) is the Rite's text.
"""
import re

from build_catalogue import SLOTS, add_constraint, child, el, make_id

COMPULSORY = next(c for c in SLOTS["Troops"] if c[1] == "Compulsory Troops:")[0]
TROOPS = SLOTS["Troops"][0][0]

PENITENTS = ["Repentia Squad", "Arco-flagellants", "Penitent Engines", "Mortifiers"]

# Rite: [(unit, slot, may fill a Compulsory Troops slot)]; a Troops unit that may fill one gains the Line sub-type
SLOT_RITES = {
    "Armoured Convent": [("Paragon Warsuits", "Troops", True)],
    "Penitent Host": [("Repentia Squad", "Troops", True), ("Arco-flagellants", "Troops", True),
                      ("Penitent Engines", "Elites", False), ("Mortifiers", "Elites", False)],
    "Wings of the Saint": [("Seraphim Squad", "Troops", True), ("Zephyrim Squad", "Troops", True)],
    "The Cleansing Pyre": [("Dominion Squad", "Troops", True)],
    "Bastion of the Martyred Heart": [("Celestian Sacresants", "Troops", True)],
    # its Compulsory Troops may be Dominion Squads, so they may be taken as Troops (without the Line sub-type)
    "Shadows of the Sanctum": [("Dominion Squad", "Troops", True)],
}
LINE = {"Shadows of the Sanctum": ["Sisters Novitiate"]}  # Troops already: Line when it fills the compulsory slot
NO_LINE = {"Shadows of the Sanctum": ["Dominion Squad"]}
COMPULSORY_ONLY = {
    "Crusade of Faith": ["Battle Sisters Squad"],
    "Wings of the Saint": ["Seraphim Squad", "Zephyrim Squad"],
    "The Cleansing Pyre": ["Dominion Squad", "Battle Sisters Squad"],
    "Bastion of the Martyred Heart": ["Battle Sisters Squad", "Celestian Sacresants"],
    "Shadows of the Sanctum": ["Sisters Novitiate", "Dominion Squad"],
}


# Sororitas profiles carry no Jump sub-type: these units have jump packs (Junith's pulpit and Celestine's wings
# count as one). A Canoness's jump pack is an option, so she is not one of them.
JUMP = ["Seraphim Squad", "Zephyrim Squad", "Junith Eruita", "Saint Celestine"]


def jump(d):
    return d["name"] in JUMP


def infantry(d, heavy=True):
    """Every model Infantry; heavy=False also leaves out Heavy and Mechanised ones (Paragons, Penitent Engines)."""
    return all(re.search(r"\bInfantry\b", t) and (heavy or not re.search(r"\b(Heavy|Mechanised)\b", t))
               for t in d["types"])


def bans(b, name):
    ds = b.datasheets
    if name == "Crusade of Faith":
        return PENITENTS + ["Ministorum Priest"]
    if name == "Wings of the Saint":  # Heavy Support other than Exorcists
        return [d["name"] for d in ds if d["slot"] == "Heavy Support" and d["name"] != "Exorcist"]
    if name == "The Cleansing Pyre":
        return ["Zephyrim Squad", "Seraphim Squad", "Penitent Engines", "Mortifiers", "Arco-flagellants"] + \
               [d["name"] for d in ds if jump(d)]
    if name == "Bastion of the Martyred Heart":  # no Fast Attack choices
        return [d["name"] for d in ds if d["slot"] == "Fast Attack"]
    if name == "Shadows of the Sanctum":  # no Heavy Support choices, no Paragon Warsuits
        return [d["name"] for d in ds if d["slot"] == "Heavy Support"] + ["Paragon Warsuits"]
    return []


def grants(b, name):
    """Rite: {rule: [units]}."""
    ds = b.datasheets
    if name == "Armoured Convent":
        return {"Scout": ["Immolator"]}
    if name == "Penitent Host":
        return {"Rage (1)": PENITENTS}
    if name == "Wings of the Saint":
        jumpers = [d["name"] for d in ds if jump(d)]
        return {"Deep Strike": jumpers, "Hit & Run": jumpers}
    if name == "Bastion of the Martyred Heart":
        foot = [d["name"] for d in ds if infantry(d)]
        return {"Stubborn": foot, "Heart of the Legion": foot}
    if name == "Shadows of the Sanctum":
        flank = [d["name"] for d in ds if infantry(d, heavy=False) or d["slot"] == "Dedicated Transports"]
        return {"Infiltrate": ["Sisters Novitiate", "Dominion Squad"],
                "Move Through Cover": ["Sisters Novitiate", "Dominion Squad"], "Outflank": flank}
    return {}


def clear_builder_rites(b, rites):
    """Take out the builder's partial reading of these Rites, keeping who may be the Warlord."""
    ids = {r["id"] for r in rites.values()}
    parent = {c: p for p in b.root.iter() for c in p}
    for e in [b.root] + [b.shared_entries]:
        parent.update({c: p for p in e.iter() for c in p})

    def warlord_link(x):
        while x is not None:
            if x.tag == "entryLink" and x.get("name") == "Warlord":
                return True
            x = parent.get(x)
        return False

    links = b.root.find("entryLinks")
    for l in list(links):  # the Rites' own slot links
        if l.get("hidden") == "true" and any(c.get("childId") in ids for c in l.iter("condition")):
            links.remove(l)
    for tree in (b.root, b.shared_entries):
        for il in list(tree.iter("infoLink")):  # rules a Rite grants
            if il.get("hidden") == "true" and any(c.get("childId") in ids for c in il.iter("condition")):
                parent[il].remove(il)
        for m in list(tree.iter("modifier")):
            if any(c.get("childId") in ids for c in m.iter("condition")) and not warlord_link(m):
                if m in parent:
                    parent[m].remove(m)
    for r in rites.values():  # the Rite's limits
        entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{r['id']}']")
        for tag in ("constraints", "modifiers"):
            g = entry.find(tag)
            if g is not None:
                entry.remove(g)


def apply(b):
    rites = {r["name"]: r for r in b.rite_specs}
    clear_builder_rites(b, rites)
    links = b.root.find("entryLinks")
    ds_by = {d["name"]: d for d in b.datasheets}
    unit = lambda n: b.shared_entries.find(f"selectionEntry[@id='{b.units[n]}']")

    def has_cat(link, cat):
        return any(c.get("targetId") == cat for c in link.findall("categoryLinks/categoryLink"))

    def error(rite, key, ids):
        entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{rite['id']}']")
        cid = add_constraint(entry, "max", 1, make_id(rite["id"], "sororitas limit", key))
        mod = el(child(entry, "modifiers"), "modifier", type="set", field=cid, value=0)
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
        for t in ids:
            el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=t,
               shared=True, includeChildSelections=True, includeChildForces=False)

    for name, rite in rites.items():
        rid = rite["id"]
        for n, slot, comp in SLOT_RITES.get(name, []):
            if ds_by[n]["slot"] == slot:
                continue
            before = len(links)
            b.rite_slot(links, rite, ds_by[n], b.units[n], slot, comp)
            if len(links) > before and slot != "Troops":  # a second slot link for the same Rite and unit
                e = links[before]
                e.set("id", make_id(e.get("id"), slot))
                for c in e.iter("categoryLink"):
                    c.set("id", make_id(c.get("id"), slot))
            if slot == "Troops" and comp and n not in NO_LINE.get(name, []):
                b.rite_line(unit(n), rid)
        for n in LINE.get(name, []):
            b.rite_line(unit(n), rid)
        for rname, units in grants(b, name).items():
            for n in units:
                b.rite_rule(unit(n), b.units[n], rid, rname)
        barred = sorted(set(bans(b, name)))
        for l in links:
            if l.get("name") in barred:
                b.rite_condition(el(child(l, "modifiers"), "modifier", type="set", field="hidden", value="true"), rid)
        if barred:
            error(rite, "bans", sorted({b.units[n] for n in barred}))
        allowed = COMPULSORY_ONLY.get(name)
        if allowed:
            for l in links:
                if l.get("name") not in allowed and has_cat(l, COMPULSORY):
                    b.rite_condition(el(child(l, "modifiers"), "modifier", type="remove", field="category",
                                        value=COMPULSORY), rid)
