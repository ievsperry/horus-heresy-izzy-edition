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

from build_catalogue import PTS, SLOTS, WARLORD_ENTRY, add_constraint, child, el, make_id, norm

COMPULSORY = next(c for c in SLOTS["Troops"] if c[1] == "Compulsory Troops:")[0]

ETHEREALS = ["Ethereal", "Aun'Va", "Aun'Shi"]
FIXED_SEPT = {"Commander Farsight": "Farsight Enclaves", "Commander Shadowsun": "T'au Sept", "Aun'Va": "T'au Sept",
              "Farsight Blade-Sworn Team": "Farsight Enclaves", "Blade-Sworn Cadre Master": "Farsight Enclaves",
              "Blade-Sworn Honour Guard Team": "Farsight Enclaves"}
BLADE_SWORN_DRONES = {"Gun Drone": 10, "Marker Drone": 15, "Shield Drone": 15}
BOTH_WEAPONS = ("Paired vibro-blades", "Grav-resonance maul", "Gravitic impact hammer")  # replace pistol and blade
# "may only include ... if every model in the Detachment has the Sept (X) special rule": no Auxiliaries beside it
SEPT_ONLY_DETACHMENT = ["Farsight Blade-Sworn Team", "Blade-Sworn Cadre Master", "Blade-Sworn Honour Guard Team"]
BLADE_SWORN = ["Farsight Blade-Sworn Team", "Blade-Sworn Cadre Master", "Blade-Sworn Honour Guard Team"]  # two-weapon swaps
# units whose drones cost 10/15/15 points
OWN_DRONE_COSTS = BLADE_SWORN + ["Crisis Bodyguard Team", "Fireblade Honour Guard Team", "Ethereal Honour Guard",
                                 "Royal Guard Team"]
JET_PACK_TEAMS = ["Farsight Blade-Sworn Team", "Blade-Sworn Honour Guard Team", "Royal Guard Team"]  # no Devilfish with Repulsor Jet-Packs
# Retinue Squads: the squad and who may take it (no Force Organisation slot; one in the leader's own entry)
RETINUES = {
    "Crisis Bodyguard Team": lambda b: [d["name"] for d in b.datasheets if "Cadre Commander" in d["rules"] and battlesuit(d)],
    "Crisis Bodyguards": lambda b: [d["name"] for d in b.datasheets if "Cadre Commander" in d["rules"] and battlesuit(d)],
    "Fireblade Honour Guard Team": lambda b: ETHEREALS + ["Cadre Fireblade"],
    "Ethereal Honour Guard": lambda b: ETHEREALS,
    "Blade-Sworn Honour Guard Team": lambda b: ["Blade-Sworn Cadre Master", "Commander Farsight"],
}
ALSO_OWN_SLOT = ["Crisis Bodyguards"]  # a Retinue Squad that may also be taken as its own Elites choice
# Sept wargear: unit -> {option: the Septs that may take it}; None is experimental wargear (any Sept). An option is
# hidden, and an error if taken, outside its Septs.
SEPT_WARGEAR = {'Blade-Sworn Cadre Master': {'Talisman of Arthas Moloch': ['Farsight Enclaves']},
 'Breacher Team': {'Grav-resonance maul': ["Kyu'shan"],
                   'Sashimono holo-banner': ["Kyu'shan"],
                   'Urban breacher shield': ["Sa'cea"],
                   'Vibro-blade': ["Kyu'shan"],
                   'Vibro-lance': ["Kyu'shan"]},
 'Broadside Battlesuits': {'Experimental nova-shield': ["Bork'an"],
                           'Harmonic aegis projector': ["Kyu'shan"],
                           "Multi-spectrum sensor suite (Sa'cea)": ["Sa'cea"],
                           'Null-signature array': ["Dal'yth"],
                           'Overcharged plasma accelerator': ["Bork'an"],
                           'Stabilized fire-control uplink': ["Sa'cea"]},
 'Cadre Fireblade': {'Chrono-harmonic scrambler field': None,
                     "Command-link drone (T'au Sept)": ["T'au Sept"],
                     'Dynamic mirror-field': ["Dal'yth"],
                     'Experimental sub-munition rail-carbine': None,
                     'Grav-resonance maul': ["Kyu'shan"],
                     'Gravitic impact hammer': ['Farsight Enclaves'],
                     'Harmonic aegis projector': ["Kyu'shan"],
                     'High-capacity pulse drum': ["Vior'la"],
                     'Paired vibro-blades': ['Farsight Enclaves'],
                     "Puretide engram neurochip (T'au Sept)": ["T'au Sept"],
                     'Repulsor jet-pack': ['Farsight Enclaves', "Kyu'shan"],
                     'Seeker-suite targeter': ["Bork'an"],
                     'Tactical telemetry relay-array': None,
                     'Talisman of Arthas Moloch': ['Farsight Enclaves'],
                     'Urban breacher shield': ["Sa'cea"],
                     'Vibro-axe': ['Farsight Enclaves'],
                     'Vibro-blade': ["Kyu'shan", 'Farsight Enclaves'],
                     'Vibro-lance': ["Kyu'shan"],
                     'Vibro-maul': ['Farsight Enclaves']},
 'Commander': {'Chrono-harmonic scrambler field': None,
               "Command-link drone (T'au Sept)": ["T'au Sept"],
               'Dynamic mirror-field': ["Dal'yth"],
               'Experimental nova-shield': ["Bork'an"],
               'Experimental sub-munition rail-carbine': None,
               'Fusion blades': ['Farsight Enclaves'],
               'Grav-resonance maul': ["Kyu'shan"],
               'Harmonic aegis projector': ["Kyu'shan"],
               "Multi-spectrum sensor suite (Sa'cea)": ["Sa'cea"],
               'Onager gauntlet': ['Farsight Enclaves'],
               'Oni battlesuit cleaver': ["Kyu'shan"],
               'Overcharged plasma accelerator': ["Bork'an"],
               "Puretide engram neurochip (T'au Sept)": ["T'au Sept"],
               'Quantum-phase blink projector': None,
               'Seeker-suite targeter': ["Bork'an"],
               'Stabilized fire-control uplink': ["Sa'cea"],
               'Stealth-drone controller': ["Dal'yth"],
               'Sub-orbital thruster pack': ["Vior'la"],
               'Tactical telemetry relay-array': None,
               'Talisman of Arthas Moloch': ['Farsight Enclaves'],
               'Thermoneutronic projector': ["Vior'la"],
               'Vector-lock retro-thrusters': ["T'au Sept"],
               'Vibro-blade': ["Kyu'shan"],
               'Vibro-lance': ["Kyu'shan"]},
 'Crisis Battlesuits': {'Dynamic mirror-field': ["Dal'yth"],
                        'Experimental nova-shield': ["Bork'an"],
                        'Experimental sub-munition rail-carbine': None,
                        'Harmonic aegis projector': ["Kyu'shan"],
                        "Multi-spectrum sensor suite (Sa'cea)": ["Sa'cea"],
                        'Onager gauntlet': ['Farsight Enclaves'],
                        'Oni battlesuit cleaver': ["Kyu'shan"],
                        'Overcharged plasma accelerator': ["Bork'an"],
                        'Seeker-suite targeter': ["Bork'an"],
                        'Stabilized fire-control uplink': ["Sa'cea"],
                        'Sub-orbital thruster pack': ["Vior'la"],
                        'Thermoneutronic projector': ["Vior'la"],
                        'Vector-lock retro-thrusters': ["T'au Sept"]},
 'Crisis Bodyguard Team': {'Experimental nova-shield': ["Bork'an"],
                           'Experimental sub-munition rail-carbine': None,
                           'Fusion blades': ['Farsight Enclaves'],
                           'Onager gauntlet': ['Farsight Enclaves'],
                           'Oni battlesuit cleaver': ["Kyu'shan"],
                           'Stabilized fire-control uplink': ["Sa'cea"],
                           'Sub-orbital thruster pack': ["Vior'la"],
                           'Thermoneutronic projector': ["Vior'la"],
                           'Vector-lock retro-thrusters': ["T'au Sept"]},
 'Crisis Bodyguards': {'Experimental nova-shield': ["Bork'an"],
                       'Experimental sub-munition rail-carbine': None,
                       'Fusion blades': ['Farsight Enclaves'],
                       'Onager gauntlet': ['Farsight Enclaves'],
                       'Oni battlesuit cleaver': ["Kyu'shan"],
                       'Stabilized fire-control uplink': ["Sa'cea"],
                       'Sub-orbital thruster pack': ["Vior'la"],
                       'Thermoneutronic projector': ["Vior'la"],
                       'Vector-lock retro-thrusters': ["T'au Sept"]},
 'Devilfish': {'Null-signature array': ["Dal'yth"]},
 'Ethereal': {'Chrono-harmonic scrambler field': None,
              "Command-link drone (T'au Sept)": ["T'au Sept"],
              'Dynamic mirror-field': ["Dal'yth"],
              'Harmonic aegis projector': ["Kyu'shan"],
              "Puretide engram neurochip (T'au Sept)": ["T'au Sept"],
              'Repulsor jet-pack': ["Kyu'shan"],
              'Tactical telemetry relay-array': None},
 'Ethereal Honour Guard': {'Grav-resonance maul': ["Kyu'shan"],
                           'Vibro-blade': ["Kyu'shan"],
                           'Vibro-lance': ["Kyu'shan"]},
 'Fireblade Honour Guard Team': {'Grav-resonance maul': ["Kyu'shan"],
                                 'Repulsor jet-pack': ["Kyu'shan"],
                                 'Sashimono holo-banner': ["Kyu'shan"],
                                 'Urban breacher shield': ["Sa'cea"],
                                 'Vibro-blade': ["Kyu'shan"],
                                 'Vibro-lance': ["Kyu'shan"]},
 'Ghostkeel': {'Dynamic mirror-field': ["Dal'yth"],
               'Experimental nova-shield': ["Bork'an"],
               'Stealth-drone controller': ["Dal'yth"],
               'Vector-lock retro-thrusters': ["T'au Sept"]},
 'Hammerhead Gunship': {'Null-signature array': ["Dal'yth"],
                        'Overcharged plasma accelerator': ["Bork'an"],
                        'Stabilized fire-control uplink': ["Sa'cea"]},
 'Pathfinders': {'Grav-resonance maul': ["Kyu'shan"],
                 'High-capacity pulse drum': ["Vior'la"],
                 "Multi-spectrum sensor suite (Sa'cea)": ["Sa'cea"],
                 'Seeker-suite targeter': ["Bork'an"],
                 'Stealth-drone controller': ["Dal'yth"],
                 'Vibro-blade': ["Kyu'shan"],
                 'Vibro-lance': ["Kyu'shan"]},
 'Piranhas': {'Null-signature array': ["Dal'yth"]},
 'Riptide': {'Overcharged plasma accelerator': ["Bork'an"], 'Stabilized fire-control uplink': ["Sa'cea"]},
 'Sky Ray Gunship': {'Null-signature array': ["Dal'yth"], 'Stabilized fire-control uplink': ["Sa'cea"]},
 'Stealth Battlesuits': {'Dynamic mirror-field': ["Dal'yth"],
                         'Seeker-suite targeter': ["Bork'an"],
                         'Stealth-drone controller': ["Dal'yth"],
                         'Thermoneutronic projector': ["Vior'la"],
                         'Vector-lock retro-thrusters': ["T'au Sept"]},
 'Strike Team': {'Grav-resonance maul': ["Kyu'shan"],
                 'High-capacity pulse drum': ["Vior'la"],
                 'Sashimono holo-banner': ["Kyu'shan"],
                 'Urban breacher shield': ["Sa'cea"],
                 'Vibro-blade': ["Kyu'shan"],
                 'Vibro-lance': ["Kyu'shan"]}}
# "Limit 1 per Detachment"
ONE_PER_DETACHMENT = ["Puretide engram neurochip (T'au Sept)", "Onager gauntlet", "Talisman of Arthas Moloch",
                      "Quantum-phase blink projector", "Experimental sub-munition rail-carbine",
                      "Chrono-harmonic scrambler field", "Tactical telemetry relay-array"]
# 0-1 per Detachment, any number when every model in it has one of these Septs
LIMITED_UNLESS_SEPT = {"Royal Guard Team": ["Kyu'shan", "Farsight Enclaves"]}
ONE_PER_UNIT = {"Crisis Bodyguard Team": ["Onager gauntlet"]}


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
    Commander's XV8 Crisis suit, which it may upgrade to an XV85 Enforcer or XV86 Coldstar; Farsight's XV-86
    Supernova counts as a Coldstar)."""
    return [n for n in commanders(b)
            if re.search(r"\b(Crisis|Coldstar|Enforcer|XV-?86)\b", " ".join(map(str, next(d for d in b.datasheets if d["name"] == n)["wargear"])))]


WARLORDS = {
    "Hunter Cadre": lambda b: ETHEREALS + ["Cadre Fireblade", "Blade-Sworn Cadre Master"],
    "Kauyon": lambda b: suited_commanders(b) + ["Cadre Fireblade", "Blade-Sworn Cadre Master"],
    "Kroot Kindred": lambda b: ["Kroot Shaper", "Kroot Master Shaper"],
    "Mont'ka": lambda b: suited_commanders(b),
    "Host of the Jade Throne": lambda b: [n for n in commanders(b) + ["Cadre Fireblade"]
                                          if "Cadre Commander" in next(d for d in b.datasheets if d["name"] == n)["rules"]],
}
SEPT_RITES = {"Host of the Jade Throne": "Kyu'shan"}  # the Rite's Detachment must be of this Sept
MAX_SLOTS = {"Host of the Jade Throne": {"Heavy Support": 1}}  # at most this many choices of a slot
# Rite: [(unit, slot, may fill a Compulsory Troops slot)]; such a Troops unit gains the Line sub-type
SLOT_RITES = {
    "Kauyon": [("Pathfinders", "Troops", True)],
    "Kroot Kindred": [("Kroot Hounds", "Troops", True), ("Krootox Riders", "Troops", True)],
    "Mont'ka": [("Crisis Battlesuits", "Troops", True)],
    "Host of the Jade Throne": [("Crisis Battlesuits", "Troops", False)],
}
LINE = {"Kroot Kindred": ["Kroot Carnivores"]}  # Troops already, Line when filling the compulsory slot
COMPULSORY_ONLY = {
    "Kauyon": ["Strike Team", "Pathfinders"],
    "Kroot Kindred": ["Kroot Carnivores", "Kroot Hounds", "Krootox Riders"],
    "Mont'ka": ["Crisis Battlesuits", "Breacher Team"],
    "Host of the Jade Throne": ["Strike Team", "Breacher Team"],
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
    if name == "Host of the Jade Throne":  # no Kroot or Vespid; no Fortifications
        return [d["name"] for d in ds if kroot(d) or d["name"].startswith("Vespid")] + slot("Fortifications")
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
    if name == "Host of the Jade Throne":
        return {"Heart of the Cadre": ["Crisis Battlesuits"]}
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
        if name in SEPT_RITES:  # hidden, and an error, unless the Detachment is of the Rite's Sept
            sid = make_id("fleet", b.faction, SEPT_RITES[name])
            entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{rid}']")
            cid = add_constraint(entry, "max", 1, make_id(rid, "tau sept"))
            for field, value in (("hidden", "true"), (cid, 0)):
                m = el(child(entry, "modifiers"), "modifier", type="set", field=field, value=value)
                el(el(m, "conditions"), "condition", type="lessThan", value=1, field="selections", scope="force",
                   childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
        for slot, most in MAX_SLOTS.get(name, {}).items():
            entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{rid}']")
            cid = add_constraint(entry, "max", 1, make_id(rid, "tau max", slot))
            m = el(child(entry, "modifiers"), "modifier", type="set", field=cid, value=0)
            el(el(m, "conditions"), "condition", type="greaterThan", value=most, field="selections", scope="force",
               childId=SLOTS[slot][0][0], shared=True, includeChildSelections=True, includeChildForces=False)
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

    # the Blade-Sworn: their own drone costs, and the swaps that replace both pistol and vibro-blade
    for n in OWN_DRONE_COSTS:
        for g in (unit(n).iter("selectionEntryGroup") if n in b.units else []):
            if g.get("name") == "Drones":
                for e in g.findall("selectionEntries/selectionEntry"):
                    cost = BLADE_SWORN_DRONES.get(e.get("name"))
                    for c in e.findall("costs/cost"):
                        if cost is not None:
                            c.set("value", str(cost))
    for n in BLADE_SWORN:
        bs = unit(n) if n in b.units else None
        if bs is None:
            continue
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
    # a Blade-Sworn unit with Repulsor Jet-Packs may not take a Devilfish
    for n in JET_PACK_TEAMS:
        team = unit(n) if n in b.units else None
        if team is None:
            continue
        pack = next((l for l in team.iter("entryLink") if l.get("name", "").lower().startswith("repulsor jet-pack")), None)
        dt = next((g for g in team.iter("selectionEntryGroup") if g.get("name") == "Dedicated Transport"), None)
        if pack is not None and dt is not None:
            for c in dt.findall("constraints/constraint"):
                if c.get("type") == "max":
                    m = el(child(dt, "modifiers"), "modifier", type="set", field=c.get("id"), value=0)
                    el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections",
                       scope=b.units[n], childId=pack.get("id"), shared=True,
                       includeChildSelections=True, includeChildForces=False)
    # options of one Sept, and options one per unit
    for n, opts in SEPT_WARGEAR.items():
        if n not in b.units:
            b.problems.append(f"Sept wargear: no unit '{n}'")
            continue
        wanted = {norm(k): v for k, v in opts.items()}
        found = set()
        for e in unit(n).iter():
            if e.tag not in ("selectionEntry", "entryLink") or norm(e.get("name", "")) not in wanted:
                continue
            septs = wanted[norm(e.get("name"))]
            found.add(norm(e.get("name")))
            if septs is None:
                continue
            ids = [make_id("fleet", b.faction, s_) for s_ in septs]
            cid = add_constraint(e, "max", 0, make_id(e.get("id"), "sept wargear"), scope="force", children=True)
            for field, value, kind in ((cid, -1, "or"), ("hidden", "true", "and")):
                m = el(child(e, "modifiers"), "modifier", type="set", field=field, value=value)
                conds = el(el(el(m, "conditionGroups"), "conditionGroup", type=kind), "conditions")
                for sid in ids:
                    el(conds, "condition", type="atLeast" if kind == "or" else "lessThan", value=1, field="selections",
                       scope="force", childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
        for k in set(wanted) - found:
            b.problems.append(f"Sept wargear: '{k}' not found in {n}")
    for name in ONE_PER_DETACHMENT:  # one model in the Detachment
        for e in b.shared_entries:
            if norm(e.get("name", "")) == norm(name):
                add_constraint(e, "max", 1, make_id(e.get("id"), "one per detachment"), scope="force", children=True)
    for n, names in ONE_PER_UNIT.items():
        for e in (unit(n).iter() if n in b.units else []):
            if e.tag in ("selectionEntry", "entryLink") and e.get("name") in names:
                add_constraint(e, "max", 1, make_id(e.get("id"), "one per unit"), scope=b.units[n], children=True)
    # Retinue Squads: no Force Organisation slot; a "Retinue" choice (one squad) in each leader's own entry
    retinue_ids = {b.units[n] for n in RETINUES if n in b.units}
    for n in RETINUES:  # a Retinue Squad's characters are bodyguards, not Warlords
        for me in (unit(n).findall("selectionEntries/selectionEntry") if n in b.units else []):
            for l in me.findall("entryLinks/entryLink"):
                if l.get("name") in ("Warlord", "Warlord Traits"):
                    me.find("entryLinks").remove(l)
    also_slot = {b.units[n] for n in ALSO_OWN_SLOT if n in b.units}
    for l in list(links):  # no slot of their own, but for those that may also be taken on their own
        if l.get("targetId") in retinue_ids - also_slot:
            links.remove(l)
    leaders = {}
    for n, who in RETINUES.items():
        if n not in b.units:
            continue
        for lead in who(b):
            if lead in b.units:
                leaders.setdefault(lead, []).append(n)
    for lead, squads in leaders.items():
        lu = unit(lead)
        gid = make_id(lu.get("id"), "retinue")
        g = el(child(lu, "selectionEntryGroups"), "selectionEntryGroup", name="Retinue", hidden=False, id=gid)
        add_constraint(g, "max", 1, gid + "max")
        for n in squads:
            el(child(g, "entryLinks"), "entryLink", import_=True, name=n, hidden=False, id=make_id(gid, n),
               type="selectionEntry", targetId=b.units[n])
    # every link that takes a unit: its root choice, or the Retinue choice in a leader
    all_links = list(links) + [l for l in b.shared_entries.iter("entryLink") if l.get("targetId") in retinue_ids]

    # a unit whose Detachment must be all of one Sept: an error beside any Auxiliaries (they have no Sept)
    aux = sorted({b.units[d["name"]] for d in b.datasheets if any(r.startswith("Auxiliaries") for r in d["rules"])})
    for n in SEPT_ONLY_DETACHMENT:
        for l in all_links:
            if n in b.units and l.get("targetId") == b.units[n] and aux:
                cid = add_constraint(l, "max", 1000, make_id(l.get("id"), "no auxiliaries"), scope="force", children=True)
                m = el(child(l, "modifiers"), "modifier", type="set", field=cid, value=0)
                conds = el(el(el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
                for a in aux:
                    el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=a,
                       shared=True, includeChildSelections=True, includeChildForces=False)

    # Cadre Commander is Master of the Legion: one model with it for every full 1,000 points in the army, as the
    # Legiones Astartes catalogue's Master of the Legion entry does (a 0-point upgrade every such model must take,
    # at most one per 1,000 points of the roster)
    cc_units = [d["name"] for d in b.datasheets if "Cadre Commander" in d["rules"]]
    if cc_units:
        eid = make_id("cadre commander", b.faction, "limit")
        e = el(b.shared_entries, "selectionEntry", type="upgrade", import_=True, name="Cadre Commander", hidden=False,
               id=eid, publicationId=b.pub_id)
        cmax = make_id(eid, "per 1000")
        m = el(el(e, "modifiers"), "modifier", type="increment", field=cmax, value=1)
        el(el(m, "repeats"), "repeat", field=PTS, scope="roster", value=1000, percentValue=False, shared=True,
           includeChildSelections=False, includeChildForces=False, childId="any", repeats=1, roundUp=False)
        el(el(e, "constraints"), "constraint", type="max", value=0, field="selections", scope="roster", shared=True,
           id=cmax, percentValue=False, includeChildSelections=True, includeChildForces=False)
        rule = next((r for tree in (b.shared_rules, b.root) for r in tree.iter("rule")
                     if r.get("name") == "Cadre Commander"), None)
        if rule is not None:
            el(el(e, "infoLinks"), "infoLink", name="Cadre Commander", id=make_id(eid, "rule"), hidden=False,
               targetId=rule.get("id"), type="rule")
        el(el(e, "costs"), "cost", name="Pts", typeId=PTS, value=0)
        for n in cc_units:
            for me in unit(n).findall("selectionEntries/selectionEntry"):
                if me.get("type") != "model":
                    continue
                lid = make_id(me.get("id"), "cadre commander")
                link = el(child(me, "entryLinks"), "entryLink", import_=True, name="Cadre Commander", hidden=False,
                          id=lid, type="selectionEntry", targetId=eid)
                add_constraint(link, "min", 1, lid + "min")
                add_constraint(link, "max", 1, lid + "max")

    # 0-1 per Detachment, unless every model in it has one of the Septs (no Auxiliaries beside them)
    for n, septs in LIMITED_UNLESS_SEPT.items():
        for l in all_links:
            if n not in b.units or l.get("targetId") != b.units[n]:
                continue
            cid = add_constraint(l, "max", 1, make_id(l.get("id"), "limited"), scope="force", children=True)
            m = el(child(l, "modifiers"), "modifier", type="set", field=cid, value=-1)
            g = el(el(m, "conditionGroups"), "conditionGroup", type="and")
            for a_ in aux:
                el(child(g, "conditions"), "condition", type="lessThan", value=1, field="selections", scope="force",
                   childId=a_, shared=True, includeChildSelections=True, includeChildForces=False)
            og = el(child(g, "conditionGroups"), "conditionGroup", type="or")
            for sept in septs:
                el(child(og, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
                   childId=make_id("fleet", b.faction, sept), shared=True, includeChildSelections=True,
                   includeChildForces=False)

    # every Drone has Saviour Protocols
    for e in b.shared_entries.iter("selectionEntry"):
        if e.get("type") == "model" and re.search(r"\bDrones?$", e.get("name", "")) and \
                not any(norm(i.get("name", "")) == norm("Saviour Protocols") for i in e.findall("infoLinks/infoLink")):
            if not b.link_rule(e, "Saviour Protocols", e.get("id") + "saviour"):
                b.problems.append("no Saviour Protocols rule")
                break

    # characters of one Sept: an error in a Detachment of another
    for n, sept in FIXED_SEPT.items():
        sid = make_id("fleet", b.faction, sept)
        if n not in b.units or not any(e.get("id") == sid for e in b.root.iter("selectionEntry")):
            b.problems.append(f"fixed Sept: no '{n}' or no Sept '{sept}'")
            continue
        for l in all_links:
            if l.get("targetId") != b.units[n]:
                continue
            cid = add_constraint(l, "max", 0, make_id(l.get("id"), "sept only"), scope="force", children=True)
            m = el(child(l, "modifiers"), "modifier", type="set", field=cid, value=-1)
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
               childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
