"""T'au Empire: the four Rites of War and the fixed-Sept characters, called by build_catalogue.py for that faction.

The md's Rites name units as the book does ("Pathfinder Teams", "Kroot Hound Packs", "Crisis Battlesuit Teams")
and their Warlords in a form the builder's Rite reading does not take ("a T'au Commander (in Enforcer, Coldstar,
or Crisis Battlesuit armour) or a Cadre Fireblade"), so the builder's reading of them is cleared and they are
made here from explicit unit lists: who may be the Warlord, the slots a Rite opens, the Line sub-type, the rules
it grants, a bigger unit, the units it bars (hidden, and an error if taken), the Troops that may fill its
Compulsory Troops slots and one more drone for Strike and Breacher Teams. Faith in the Greater Good's numbers
(more Infantry than Battlesuits), Reserves, Run, Deep Strike and once-per-battle effects are the Rite's text.

Commander Farsight may only be in a Farsight Enclaves Detachment, and Commander Shadowsun and Aun'Va only in a
T'au Sept one: shown, but an error in a Detachment of another Sept.
"""
import re

from build_catalogue import SLOTS, WARLORD_ENTRY, add_constraint, child, el, make_id

COMPULSORY = next(c for c in SLOTS["Troops"] if c[1] == "Compulsory Troops:")[0]

ETHEREALS = ["Ethereal", "Aun'Va", "Aun'Shi"]
FIXED_SEPT = {"Commander Farsight": "Farsight Enclaves", "Commander Shadowsun": "T'au Sept", "Aun'Va": "T'au Sept",
              "Farsight Blade-Sworn Team": "Farsight Enclaves"}
BLADE_SWORN_DRONES = {"Gun Drone": 10, "Marker Drone": 15, "Shield Drone": 15}
BOTH_WEAPONS = ("Paired vibro-blades", "Grav-resonance maul", "Gravitic impact hammer")  # replace pistol and blade
# "may only include ... if every model in the Detachment has the Sept (X) special rule": no Auxiliaries beside it
SEPT_ONLY_DETACHMENT = ["Farsight Blade-Sworn Team"]


def commanders(b):
    """The T'au Commanders: the Commander, the named Commanders and the Shas'o."""
    return [d["name"] for d in b.datasheets if d["name"] == "Commander" or d["name"].startswith(("Commander ", "Shas'o "))]


def battlesuit(d):
    return any(re.match(r"(?:[^:]*: )?Battlesuit", t) for t in d["types"])


def vehicle(d):
    return any(re.match(r"(?:[^:]*: )?Vehicle", t) for t in d["types"])


def kroot(d):
    return "Kroot" in d["rules"]  # the Kroot special rule


def suited_commanders(b):
    """The Commanders in an Enforcer, Coldstar or Crisis Battlesuit (Kauyon, Mont'ka): their wargear says so (the
    Commander's XV8 Crisis suit, which it may upgrade to an XV85 Enforcer or XV86 Coldstar)."""
    return [n for n in commanders(b)
            if re.search(r"\b(Crisis|Coldstar|Enforcer)\b", " ".join(map(str, next(d for d in b.datasheets if d["name"] == n)["wargear"])))]


WARLORDS = {
    "Hunter Cadre": lambda b: ETHEREALS + ["Cadre Fireblade"],
    "Kauyon": lambda b: suited_commanders(b) + ["Cadre Fireblade"],
    "Kroot Kindred": lambda b: ["Kroot Shaper", "Kroot Master Shaper"],
    "Mont'ka": lambda b: suited_commanders(b),
}
# Rite: [(unit, slot, may fill a Compulsory Troops slot)]; such a Troops unit gains the Line sub-type
SLOT_RITES = {
    "Kauyon": [("Pathfinders", "Troops", True)],
    "Kroot Kindred": [("Kroot Hounds", "Troops", True), ("Krootox Riders", "Troops", True)],
    "Mont'ka": [("Crisis Battlesuits", "Troops", True)],
}
LINE = {"Kroot Kindred": ["Kroot Carnivores"]}  # Troops already, Line when filling the compulsory slot
COMPULSORY_ONLY = {
    "Kauyon": ["Strike Team", "Pathfinders"],
    "Kroot Kindred": ["Kroot Carnivores", "Kroot Hounds", "Krootox Riders"],
    "Mont'ka": ["Crisis Battlesuits", "Breacher Team"],
}
SIZES = {"Kroot Kindred": [("Kroot Carnivores", 30)]}
MORE_DRONES = {"Hunter Cadre": ["Strike Team", "Breacher Team"]}  # one Marker Drone above the drone limit
T_AU_SKIMMERS = ["Piranhas", "Piranha TX-42", "Tetra Scout Speeders"]


def bans(b, name):
    ds = b.datasheets
    slot = lambda s: [d["name"] for d in ds if d["slot"] == s]
    if name == "Hunter Cadre":
        return slot("Lords of War") + slot("Fortifications")
    if name == "Kroot Kindred":  # no battlesuits but Stealth Battlesuits, no T'au vehicles, Lords of War or Fortifications
        return [d["name"] for d in ds if battlesuit(d) and d["name"] != "Stealth Battlesuits"] + \
               [d["name"] for d in ds if vehicle(d)] + T_AU_SKIMMERS + slot("Lords of War") + slot("Fortifications")
    if name == "Mont'ka":  # Heavy Support only Broadsides; no Kroot or Vespid; no Fortifications
        return [n for n in slot("Heavy Support") if n != "Broadside Battlesuits"] + \
               [d["name"] for d in ds if kroot(d) or d["name"].startswith("Vespid")] + slot("Fortifications")
    return []


def grants(b, name):
    """Rite: {rule: [units]}."""
    if name == "Kauyon":
        return {"Infiltrate": ["Strike Team", "Pathfinders"], "Move Through Cover": ["Strike Team", "Pathfinders"]}
    if name == "Kroot Kindred":
        k = [d["name"] for d in b.datasheets if kroot(d)]
        return {"Infiltrate": k, "Scout": k}  # Move Through Cover and +1 Attack on the charge are in Kroot
    if name == "Mont'ka":
        return {"Deep Strike": ["Crisis Battlesuits"] + commanders(b)}
    return {}


def clear_builder_rites(b, rites):
    """Take out the builder's reading of these Rites: slot links, rules, bans, limits and Warlord bars."""
    ids = {r["id"] for r in rites.values()}
    links = b.root.find("entryLinks")
    for l in list(links):
        if l.get("hidden") == "true" and any(c.get("childId") in ids for c in l.iter("condition")):
            links.remove(l)
    for tree in (b.root, b.shared_entries):
        parent = {c: p for p in tree.iter() for c in p}
        for il in list(tree.iter("infoLink")):
            if il.get("hidden") == "true" and any(c.get("childId") in ids for c in il.iter("condition")):
                parent[il].remove(il)
        for m in list(tree.iter("modifier")):
            if any(c.get("childId") in ids for c in m.iter("condition")) and m in parent:
                parent[m].remove(m)
    for r in rites.values():
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
    owner = {}
    for u in b.shared_entries:
        for l in u.iter("entryLink"):
            if l.get("targetId") == WARLORD_ENTRY:
                owner[l] = u.get("name")

    def error(rite, key, ids):
        entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{rite['id']}']")
        cid = add_constraint(entry, "max", 1, make_id(rite["id"], "tau limit", key))
        mod = el(child(entry, "modifiers"), "modifier", type="set", field=cid, value=0)
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
        for t in ids:
            el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=t,
               shared=True, includeChildSelections=True, includeChildForces=False)

    for name, rite in rites.items():
        rid = rite["id"]
        allowed = set(WARLORDS.get(name, lambda b: [])(b))
        if allowed:  # only these may be the Warlord while the Rite is chosen
            for wl, uname in owner.items():
                if uname in allowed:
                    continue
                cmax = next((c for c in wl.findall("constraints/constraint") if c.get("type") == "max"), None)
                if cmax is not None:
                    b.rite_condition(el(child(wl, "modifiers"), "modifier", type="set", field=cmax.get("id"), value=0), rid)
        for n, slot, comp in SLOT_RITES.get(name, []):
            if ds_by[n]["slot"] != slot:
                b.rite_slot(links, rite, ds_by[n], b.units[n], slot, comp)
            if slot == "Troops" and comp:
                b.rite_line(unit(n), rid)
        for n in LINE.get(name, []):
            b.rite_line(unit(n), rid)
        for n, size in SIZES.get(name, []):
            b.rite_size(unit(n), rid, size)
        for rname, units in grants(b, name).items():
            for n in units:
                b.rite_rule(unit(n), b.units[n], rid, rname)
        for n in MORE_DRONES.get(name, []):
            for g in unit(n).iter("selectionEntryGroup"):
                if g.get("name") == "Drones":
                    cmax = next((c for c in g.findall("constraints/constraint") if c.get("type") == "max"), None)
                    if cmax is not None:
                        b.rite_condition(el(child(g, "modifiers"), "modifier", type="increment", field=cmax.get("id"),
                                            value=1), rid)
        barred = sorted(set(bans(b, name)) & set(b.units))
        for l in links:
            if l.get("name") in barred:
                b.rite_condition(el(child(l, "modifiers"), "modifier", type="set", field="hidden", value="true"), rid)
        if barred:
            error(rite, "bans", sorted({b.units[n] for n in barred}))
        only = COMPULSORY_ONLY.get(name)
        if only:
            for l in links:
                if l.get("name") not in only and any(c.get("targetId") == COMPULSORY for c in l.findall("categoryLinks/categoryLink")):
                    b.rite_condition(el(child(l, "modifiers"), "modifier", type="remove", field="category",
                                        value=COMPULSORY), rid)

    # the Kroot Evolutionary Adaptations: one of the three per unit
    adaptations = ("Skeletal Wings / Swift Striders", "Thickened Hide", "Muscular Hypertrophy")
    for d in b.datasheets:
        u = unit(d["name"])
        parent = {c: p for p in u.iter() for c in p}
        found = [l for l in u.iter("entryLink") if l.get("name") in adaptations]
        if not found:
            continue
        holder = parent[parent[found[0]]]  # the group (or entry) the option rows went into
        gid = make_id(b.units[d["name"]], "evolutionary adaptation")
        g = el(child(holder, "selectionEntryGroups"), "selectionEntryGroup", name="Evolutionary Adaptation",
               hidden=False, id=gid)
        add_constraint(g, "max", 1, gid + "max")
        links_el = el(g, "entryLinks")
        for l in found:
            parent[l].remove(l)
            links_el.append(l)

    # Farsight Blade-Sworn Team: its own drone costs, and the swaps that replace both pistol and vibro-blade
    bs = unit("Farsight Blade-Sworn Team") if "Farsight Blade-Sworn Team" in b.units else None
    if bs is not None:
        for g in bs.findall("selectionEntryGroups/selectionEntryGroup"):
            if g.get("name") == "Drones":
                for e in g.findall("selectionEntries/selectionEntry"):
                    cost = BLADE_SWORN_DRONES.get(e.get("name"))
                    for c in e.findall("costs/cost"):
                        if cost is not None:
                            c.set("value", str(cost))
        for me in bs.findall("selectionEntries/selectionEntry"):
            both = [e.get("id") for e in me.iter("selectionEntry") if e.get("name") in BOTH_WEAPONS]
            blade = next((g for g in me.iter("selectionEntryGroup") if g.get("name") == "Exchange vibro-blade"), None)
            if blade is None or not both:
                continue
            for c in blade.findall("constraints/constraint"):  # the vibro-blade (or its swap) goes with the pistol
                m = el(child(blade, "modifiers"), "modifier", type="set", field=c.get("id"), value=0)
                conds = el(el(el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
                for eid in both:
                    el(conds, "condition", type="atLeast", value=1, field="selections", scope=me.get("id"), childId=eid,
                       shared=True, includeChildSelections=True, includeChildForces=False)

    # a unit whose Detachment must be all of one Sept: an error beside any Auxiliaries (they have no Sept)
    aux = sorted({b.units[d["name"]] for d in b.datasheets if any(r.startswith("Auxiliaries") for r in d["rules"])})
    for n in SEPT_ONLY_DETACHMENT:
        for l in links:
            if n in b.units and l.get("targetId") == b.units[n] and aux:
                cid = add_constraint(l, "max", 1000, make_id(l.get("id"), "no auxiliaries"), scope="force", children=True)
                m = el(child(l, "modifiers"), "modifier", type="set", field=cid, value=0)
                conds = el(el(el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
                for a in aux:
                    el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=a,
                       shared=True, includeChildSelections=True, includeChildForces=False)

    # characters of one Sept: an error in a Detachment of another
    for n, sept in FIXED_SEPT.items():
        sid = make_id("fleet", b.faction, sept)
        if n not in b.units or not any(e.get("id") == sid for e in b.root.iter("selectionEntry")):
            b.problems.append(f"fixed Sept: no '{n}' or no Sept '{sept}'")
            continue
        for l in links:
            if l.get("targetId") != b.units[n]:
                continue
            cid = add_constraint(l, "max", 0, make_id(l.get("id"), "sept only"), scope="force", children=True)
            m = el(child(l, "modifiers"), "modifier", type="set", field=cid, value=-1)
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
               childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
