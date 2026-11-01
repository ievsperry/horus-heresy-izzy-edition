#!/usr/bin/env python3
"""Add the Liber Imperatus Imperialis Militia expansion to the official Imperialis Militia catalogue.

usage: python3 homebrew/add_imperialis_militia.py

The doc (homebrew/source/imperialis-militia.md, from the Claude Doc "Imperialis Militia Horus Heresy 2.0 - Homebrew
Conversion") is read by build_catalogue.py's Builder; its units move into 2022 - Imperialis Militia.cat as text,
named as the official catalogue names its units ("IM - ...") and linked to the official entries wherever the
catalogue, its libraries or the game system already have them (see expansion_tools.py). On top of the units this
writes:

- the new Provenances of War in the game system's Provenance pick, the slots they open (Ratling Squads as Troops and
  so on), what they bar, and the doc's additions to the official Provenances;
- the doc's extra options on official units (Command Cadre, Medicae Detachment, Ogryn Brute Squad, Fire Support,
  Grenadier and Reconnaissance Squads, Arvus Transport, Cavalry Squad, Sentinel Squadron, Beastmasters' War Beasts,
  Heavy Ordnance, Malcador and Rapier Batteries).

It refuses to run on a catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, add_cost, add_rule, child, el, norm  # noqa: E402
from expansion_tools import E, Text, any_entry, deep, link_el, mid, model_entry  # noqa: E402

CAT = "2022 - Imperialis Militia.cat"
DOC = "homebrew/source/imperialis-militia.md"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]
et.configure(CAT, LIBS, DOC, "Imperialis Militia", "imperialis militia expansion")
C = et.NS["cat"]

# What the Builder cannot place, and this script does instead
ALLOWED = [r"Manticore", r"rule 'Militia Cavalry Mount'", r"rule 'Household Retinue'"]

SUB_TYPES = {"Light": ("bff2-ae16-74a8-8712", "Light Sub-type"), "Automata": ("d8ab-8e21-e193-63ba", "Automata Unit Type"),
             "Hover": ("3a7a-8bb7-b0d3-e2e7", "Hover Sub-type"), "Reinforced": ("9b0d-738c-10e4-4ec1", "Reinforced Sub-type")}
TRANSPORTS = {"IM - Aurox Transport", "IM - Chimera Transport", "IM - Land Raider Proteus Carrier", "IM - Rhino Advancer",
              "IM - Rhino Transport", "IM - Termite Assault Drill"}  # Dedicated Transports only

TRAITOR, LOYALIST = "f9c0-0c5a-3e24-58c7", "d0b6-712f-0b12-a308"
PROVENANCES_GROUP = "7e02-b66b-55aa-1102"  # the game system's Provenances of War pick
PROV = {"Legacy of the Great Crusade": "b669-a356-d5d1-53b8", "Cyber-Augmetics": "ec5e-00ea-dd9c-3313",
        "Survivors of the Dark Age": "08f1-5fe7-1d3a-7b35", "Armoury of Old Night": "4bcd-7022-cefc-04da",
        "Kinfolk Helots": "2bd7-54d3-b0a9-1e44", "Abhuman Muster": "d15d-c66d-d47f-8aee",
        "Debased Rabble": "8d80-c401-0303-d0f9", "Tainted Flesh": "d5e5-b44b-5db6-ab16",
        "Ogryn Conscripts": "07d0-18a3-ce4d-c1b4"}
NEW_PROVENANCES = ["Acolytes of the Saviour Emperor", "Knight World", "Mark of the Aeldari", "Mining Colony",
                   "Ratling Enclave", "Trailblazers", "Voidborne Raiders"]
for n in NEW_PROVENANCES:
    PROV[n] = mid("provenance", n)
# the official transports the doc gives again, as Liber Imperatus has them
OFFICIAL_TRANSPORTS = {"Militia Land Raider Proteus Carrier": "IM - Land Raider Proteus Carrier",
                       "Militia Rhino Transport": "IM - Rhino Transport",
                       "Militia Termite Assault Drill": "IM - Termite Assault Drill"}


def short(name):
    """'Imperialis Militia Astropath' is 'IM - Astropath' and 'Mutated Spawn' 'IM - Mutated Spawn', as the official
    catalogue names its units."""
    return "IM - " + re.sub(r"^Imperialis Militia ", "", name)


def doc_text():
    """The doc, with the wording the Builder reads: 'Laspistol or Autopistol' (and 'Lasgun or Autorifle') is read as
    the las weapon, and auto_weapons() gives the auto one back beside it; the Militia Cavalry Mount is an official special rule, not wargear, and the Militia Jet Pack
    is defined as the official one is (the official catalogue has it only inside its units)."""
    text = open(DOC, encoding="utf-8").read()
    text = text.replace("Laspistol or Autopistol", "Laspistol").replace("Lasgun or Autorifle", "Lasgun")
    out, section = [], None
    for line in text.split("\n"):
        if line in ("Wargear", "Unit Type", "Special Rules", "Unit Composition"):
            section = line
        m = re.match(r"- Militia Cavalry Mount( \(.*\))?$", line)
        if m and section == "Wargear":
            out.append(("rule", line))
            continue
        out.append(("line", line))
    lines, pending = [], []
    for kind, line in out:
        if kind == "rule":
            pending.append(line)
            continue
        lines.append(line)
        if line == "Special Rules" and pending:
            lines += ["", *pending]
            pending = []
    text = "\n".join(lines)
    text = great_war_beasts(text)
    jet = next(p for p in ET.parse(CAT).getroot().iter(C + "profile") if p.get("name") == "Militia Jet Pack")
    desc = jet.find(f"{C}characteristics/{C}characteristic").text.strip()
    text = text.replace("\n### Auxiliary Crew Bay\n", f"\n### Militia Jet Pack\n\n{desc}\n\n### Auxiliary Crew Bay\n", 1)
    # Models bought as options carry the kit their exchanges name
    text = per_model_kit(text, "Imperialis Militia Ascendant Rogue Psyker", "Militia Warden",
                         "Close Combat Weapon, Laspistol")
    text = per_model_kit(text, "Imperialis Militia Demagogue Cadre", "Mounted Demagogue",
                         "Close Combat Weapon, Flak Armour, Laspistol")
    # "Any model may exchange its Auxiliary Vehicle Bay Special Rule for: Bunker Drop"
    text = text.replace("| Any model may exchange its Auxiliary Vehicle Bay Special Rule for: |  |",
                        "| Any model may take (in place of Auxiliary Vehicle Bay): |  |")
    # "Force Weapon": the Force weapons of the Armoury
    text = text.replace("| – Force Weapon | +10 points |", "\n".join(
        f"| – {w} | +10 points |" for w in ("Force Axe", "Force Maul", "Force Staff", "Force Sword")))
    # "Any model with a Lasgun, Autorifle or Bolter may take: Bayonet": every model has one of them
    text = text.replace("| Any model with a Lasgun, Autorifle or Bolter may take: |  |", "| Any model may take: |  |")
    return text


def cond(parent, kind, value, child_id, scope="force", field="selections"):
    el(el(parent, "conditions") if parent.find("conditions") is None else parent.find("conditions"), "condition",
       type=kind, value=value, field=field, scope=scope, childId=child_id, shared=True, includeChildSelections=True,
       includeChildForces=False, percentValue=False)


def hidden_unless(e, child_id, scope="force"):
    """Shown only while the Detachment has this (a Provenance, the Traitor Allegiance)."""
    e.set("hidden", "true")
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
    cond(mod, "atLeast", 1, child_id, scope)


def hidden_if(e, child_id, scope="force"):
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
    cond(mod, "atLeast", 1, child_id, scope)


# ---- Dedicated Transports


def transports(b, entries, official):
    """'Unless an entry says otherwise, a Command Cadre, Grenadier Squad, Reconnaissance Squad, Beastmasters unit, or
    Rogue Psyker unit with at least one Militia Warden, of no more than ten models, may select these transports. A
    Fire Support Squad may select one if it has no more than three models (four for the Chimera).' Each transport
    entry's own line overrides that. The Survivors of the Dark Age transports need that Provenance.
    Returns {unit id: [entryLink]} for the official units, and adds groups to the new units directly."""
    t = {n: b.units[n] for n in ("Imperialis Militia Aurox Transport", "Imperialis Militia Chimera Transport",
                                 "Imperialis Militia Land Raider Proteus Carrier", "Imperialis Militia Rhino Advancer",
                                 "Imperialis Militia Rhino Transport", "Imperialis Militia Termite Assault Drill")}
    survivors = {"Imperialis Militia Land Raider Proteus Carrier", "Imperialis Militia Rhino Advancer",
                 "Imperialis Militia Rhino Transport", "Imperialis Militia Termite Assault Drill"}
    default = ["IM - Command Cadre", "IM - Grenadier Squad", "IM - Reconnaissance Squad", "IM - Beastmasters",
               "IM - Rogue Psyker", "Imperialis Militia Ascendant Rogue Psyker"]
    rules = {}  # transport: [(unit, most models)]
    for tn in t:
        if tn.endswith("Land Raider Proteus Carrier"):
            rules[tn] = [(u, 10) for u in ("IM - Command Cadre", "IM - Grenadier Squad", "IM - Rogue Psyker",
                                           "Imperialis Militia Ascendant Rogue Psyker")]
        elif tn.endswith("Rhino Advancer"):
            rules[tn] = [(u, 20) for u in default + ["Enginseer Auxilia Detachment"]] + [("IM - Fire Support Squad", 6)]
        else:
            rules[tn] = [(u, 10) for u in default] + [("IM - Fire Support Squad", 4 if tn.endswith("Chimera Transport") else 3)]
    # the Enginseer Auxilia Detachment's own line: an Aurox for ten models, a Chimera for twelve
    rules["Imperialis Militia Aurox Transport"].append(("Enginseer Auxilia Detachment", 10))
    rules["Imperialis Militia Chimera Transport"].append(("Enginseer Auxilia Detachment", 12))
    wardens = {"IM - Rogue Psyker": model_id_of(official["IM - Rogue Psyker"], "Militia Wardens"),
               "Imperialis Militia Ascendant Rogue Psyker": model_entry(entries[b.units["Imperialis Militia Ascendant Rogue Psyker"]],
                                                                        "Militia Warden").get("id")}
    per_unit = {}
    for tn, eligible in rules.items():
        for un, most in eligible:
            per_unit.setdefault(un, []).append((tn, most))
    official_links = {}
    for un, offers in per_unit.items():
        if un in official:
            uid = official[un].get("id")
        else:
            uid = entries[b.units[un]].get("id")
        links = []
        for tn, most in offers:
            l = link_el(short(tn), t[tn], mid(uid, "dt"), mx=1)
            if most:
                et.models_over(l, uid, most)
            if tn in survivors:
                hidden_if_not(l, PROV["Survivors of the Dark Age"])
            if un in wardens:  # "with at least one Militia Warden"
                mod = el(child(l, "modifiers"), "modifier", type="set", field="hidden", value="true")
                cond(mod, "lessThan", 1, wardens[un], scope=uid)
            links.append(l)
        if un in official:
            official_links[uid] = links
        else:
            u = entries[b.units[un]]
            g = el(child(u, "selectionEntryGroups"), "selectionEntryGroup", name="Dedicated Transport", hidden=False,
                   id=mid(uid, "dt group"))
            add_constraint(g, "max", 1, mid(uid, "dt group max"))
            child(g, "entryLinks").extend(links)
    return official_links


def hidden_if_not(e, child_id):
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
    cond(mod, "lessThan", 1, child_id)


def model_id_of(unit, name):
    return next(m.get("id") for m in unit.iter(C + "selectionEntry") if m.get("name") == name)


# ---- Provenances of War


def provenance_text(lines):
    out = []
    for l in lines:
        l = l.strip()
        if l.startswith("- "):
            out.append("• " + bc.strip_md(l[2:]))
    return "\n".join(out)


INCOMPATIBLE = {"Acolytes of the Saviour Emperor": ["Mark of the Aeldari"],
                "Knight World": ["Abhuman Muster", "Kinfolk Helots", "Ogryn Conscripts", "Ratling Enclave"],
                "Mark of the Aeldari": ["Acolytes of the Saviour Emperor", "Debased Rabble", "Tainted Flesh"],
                "Ratling Enclave": ["Kinfolk Helots", "Knight World", "Ogryn Conscripts"],
                "Trailblazers": ["Debased Rabble", "Voidborne Raiders"]}


def provenances(b, gst):
    """The new Provenances in the game system's pick, with what they may not be combined with (both ways), and the
    doc's additions to the official ones."""
    sec = next(s for s in b.sections if s["title"] == "Provenances of War")
    pairs = set()
    for a, bs in INCOMPATIBLE.items():
        for x in bs:
            pairs.add(tuple(sorted((a, x))))
    new = []
    for i, name in enumerate(NEW_PROVENANCES):
        sub = next(x for x in sec["subs"] if x["title"] == f"Provenance of War: {name}")
        eid = PROV[name]
        e = E("selectionEntry", id=eid, name=f"{17 + i} {name}", hidden=False, collective=False, import_=True,
              type="upgrade")
        fmax = mid(eid, "force max")
        others = sorted({x for p in pairs if name in p for x in p if x != name})
        if others:
            mod = el(el(e, "modifiers"), "modifier", type="set", field=fmax, value=0)
            cg = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
            for o in others:
                el(cg, "condition", type="greaterThan", value=0, field="selections", scope="force", childId=PROV[o],
                   shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        if name == "Acolytes of the Saviour Emperor":  # "Only an army with the Loyalist Allegiance"
            mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
            cond(mod, "equalTo", 0, LOYALIST)
        add_constraint(e, "max", 1, fmax, scope="force", children=True)
        add_constraint(e, "max", 1, mid(eid, "max"))
        add_rule(e, name, provenance_text(sub["lines"]), eid)
        add_cost(e, 0)
        new.append(e)
    gst.add(PROVENANCES_GROUP, "selectionEntries", new)
    # the official Provenances may not be taken beside a new one they clash with
    root = ET.parse(et.GST).getroot()
    G = et.NS["gst"]
    for official, clashes in [(o, sorted({x for p in pairs if o in p for x in p if x != o and x in NEW_PROVENANCES}))
                              for o in ("Abhuman Muster", "Kinfolk Helots", "Ogryn Conscripts", "Debased Rabble",
                                        "Tainted Flesh")]:
        if not clashes:
            continue
        e = next(x for x in root.iter(G + "selectionEntry") if x.get("id") == PROV[official])
        fmax = next(c.get("id") for c in e.findall(f"{G}constraints/{G}constraint") if c.get("scope") == "force")
        mod = E("modifier", type="set", field=fmax, value=0)
        cg = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
        for o in clashes:
            el(cg, "condition", type="greaterThan", value=0, field="selections", scope="force", childId=PROV[o],
               shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        gst.add(PROV[official], "modifiers", [mod])
    # "These are added to the official Provenances of War"
    table = next(x for x in sec["subs"] if x["title"] == "Modifications to Existing Provenances of War")
    added = {r[0]: r[1] for h, rows in bc.section_tables({"lines": table["lines"], "subs": []}) for r in rows}
    for name, text in added.items():
        e = next(x for x in root.iter(G + "selectionEntry") if x.get("id") == PROV[name])
        rule = e.find(f"{G}rules/{G}rule")
        start, end, _, _ = gst.block(rule.get("id"))
        body = gst.s[start:end]
        j = body.index("</description>")
        body = body[:j] + f"{gst.nl}{gst.nl}Liber Imperatus addition{gst.nl}• " + text.replace("&", "&amp;").replace(
            '"', "&quot;") + body[j:]
        gst.s = gst.s[:start] + body + gst.s[end:]


# ---- naming what an option gives


class Items:
    """Option items by name, as entries: the official ones where they exist, the Builder's otherwise (which then
    travel with the expansion)."""

    MOUNTS = r"^(?:Turret|Centreline|Hull \(Front\)|Pintle|Sponson|Co-axial) Mounted "

    def __init__(self, b):
        self.b = b
        self.extra = set()

    def __call__(self, name):
        b = self.b
        n = re.sub(self.MOUNTS, "", name)
        official = any_entry(n, required=False)
        if official:
            return official
        if " and " in n and "(with" not in n:
            return self.keep(b.wrapper_entry(n, None, 1, None))
        return self.keep(b.option_target(n, mid("item", n))[0])

    def keep(self, eid):
        self.extra.add(eid)
        return eid


def named(root, name, tag="selectionEntry", within=None):
    return next(x for x in (within if within is not None else root).iter(C + tag) if x.get("name") == name)


def copy_official(e, key):
    """An official element as a new one: out of the catalogue namespace, with fresh ids (and the modifiers that
    name its constraints following them)."""
    c = deep(e)
    ids = {}
    for x in c.iter():
        x.tag = x.tag.split("}")[-1]
        for a in ("publicationId", "page"):
            x.attrib.pop(a, None)
        if x.get("id"):
            ids[x.get("id")] = mid(key, x.get("id"))
            x.set("id", ids[x.get("id")])
    for x in c.iter():
        if x.get("field") in ids:
            x.set("field", ids[x.get("field")])
    return c


def take_group(name, key, offers, items, most=None, each=None):
    g = E("selectionEntryGroup", id=mid(key, name), name=name, hidden=False, collective=False, import_=True)
    if most:
        add_constraint(g, "max", most, mid(key, name, "max"))
    for n, p in offers:
        child(g, "entryLinks").append(link_el(n, items(n), mid(key, name), mx=each or 1, pts=p))
    return g


def unit_wide(name, text, parts, items):
    """A whole-unit upgrade ('All Militia Gunners may exchange their Flak Armour for Carapace Armour'), kept as one
    entry with its rule and the wargear it gives."""
    eid = mid("unit wide", name)
    e = E("selectionEntry", id=eid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
    add_rule(e, name, text, eid)
    for p in parts:
        child(e, "entryLinks").append(link_el(p, items(p), eid, mn=1, mx=1))
    add_cost(e, 0)
    return e


WAR_BEASTS = [  # name, M WS BS S T W I A Ld Sv, cost, rules
    ("Acteniceride", "8 4 - 3 4 1 4 2 5 5+", 12, ["Crusader", "Fleet (1)"]),
    ("Arachnid", "7 4 - 4 3 1 4 2 5 5+", 10, ["Fleet (1)", "Poisoned (3+)"]),
    ("Crustacean", "7 4 - 5 4 1 3 2 5 4+", 15, ["Murderous Strike (6+)"]),
    ("Wurm", "7 4 - 3 4 1 4 2 5 5+", 10, ["Fleet (1)", "Pathfinder", "Sudden Strike (1)"]),
]


def war_beasts(root, ops):
    """'An official Imperialis Militia Beastmasters unit may include one War Beast for each Militia Handler': the four
    Liber Imperatus kinds beside the official ones, each made from the official Mastiff."""
    bm = named(root, "IM - Beastmasters")
    group = named(root, "2) War Beasts", "selectionEntryGroup", bm)
    mastiff = named(root, "Mastiff", within=group)
    gst_rules = bc.load_gst_rules()
    new = []
    for name, stats, cost, rules in WAR_BEASTS:
        c = copy_official(mastiff, mid("war beast", name))
        c.set("name", name)
        for p in c.iter("profile"):
            if p.get("name") == "Mastiff":
                p.set("name", name)
            if p.get("typeName") == "Unit":
                chars = [x for x in p.iter("characteristic") if x.get("name") not in ("Unit Type",)]
                for x, v in zip(chars, stats.split()):
                    x.text = v
        for cont in list(c):
            if cont.tag in ("infoLinks", "rules"):
                c.remove(cont)
        for x in c.iter("cost"):
            x.set("value", str(cost))
            break
        links = child(c, "infoLinks")
        for r in rules:
            key = re.sub(r"\s*\(.*\)$", "", r).lower()
            rid, rname = gst_rules[key]
            il = el(links, "infoLink", name=rname, id=mid(c.get("id"), "rule", r), hidden=False, targetId=rid, type="rule")
            if rname != r:
                el(el(il, "modifiers"), "modifier", type="set", field="name", value=r)
        new.append(c)
    ops.add(group.get("id"), "selectionEntries", new)


def existing_units(items, shared, ops, missiles):
    root = ET.parse(CAT).getroot()

    # Command Cadre: "For every five models beyond the unit's starting size, one Militia Bodyguard may be upgraded to
    # a Militia Lieutenant": one more Lieutenant for every five models past the first five
    cc = named(root, "IM - Command Cadre")
    lt = named(root, "1) Militia Lieutenant", within=cc)
    lmax = next(c for c in lt.findall(f"{C}constraints/{C}constraint") if c.get("type") == "max")
    inc = E("modifier", type="increment", field=lmax.get("id"), value=1)
    el(el(inc, "repeats"), "repeat", field="selections", scope=cc.get("id"), value=5, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="model", repeats=1, roundUp=False)
    dec = E("modifier", type="decrement", field=lmax.get("id"), value=1)
    ops.add(lt.get("id"), "modifiers", [inc, dec])

    # Medicae: "Any Militia Medicae may exchange its Flak Armour for: Carapace Armour (+5)"
    md = named(root, "IM - Medicae Detachment")
    for m in [x for x in md.iter(C + "selectionEntry") if x.get("type") == "model"]:
        ops.add(m.get("id"), "selectionEntryGroups",
                [take_group("May exchange Flak Armour for", m.get("id"), [("Carapace Armour", 5)], items, most=1)])

    # Ogryn Brute Squad: the Liber Imperatus weapons beside the official ones
    ob = named(root, "IM - Ogryn Brute Squad")
    brute_extra = [("Heavy Power Weapon", 35), ("Lascutter", 10), ("Power Weapon", 20), ("Augmetic Fist", 10),
                   ("Storm-Welder", 10)]
    g = named(root, "2) Additional Brute Weapons (Not Boss)", "selectionEntryGroup", ob)
    ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=10, pts=p) for n, p in brute_extra])
    boss = named(root, "Ogryn Boss", within=ob)
    g = named(root, "2.1) Additional Boss Weapons", "selectionEntryGroup", boss)
    ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=p) for n, p in brute_extra])
    g = named(root, "1) Ogryn Boss may take one of the following:", "selectionEntryGroup", boss)
    ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=p) for n, p in (
        ("Arc Welder", 15), ("Heavy Rock Cutter", 20), ("Heavy Rock Drill", 20), ("Heavy Rock Saw", 20),
        ("Mining Laser", 15), ("Seismic Cannon", 10))])

    # Fire Support Squad, Heavy Ordnance and Rapier Batteries: Carapace Armour for the whole unit (+20)
    carapace = unit_wide("Carapace Armour (entire unit)", "Every model in the unit exchanges its Flak Armour for "
                         "Carapace Armour.", ["Carapace Armour"], items)
    shared.append(carapace)
    for un in ("IM - Fire Support Squad", "IM - Heavy Ordnance Battery", "IM - Rapier Battery"):
        u = named(root, un)
        ops.add(u.get("id"), "entryLinks", [link_el(carapace.get("name"), carapace.get("id"), u.get("id"), mx=1, pts=20)])

    # Grenadier Squad: Hot-Shot Lasgun, Hot-Shot Volley Gun, the Sergeant's Hot-Shot Laspistol
    gs = named(root, "IM - Grenadier Squad")
    for g in [x for x in gs.iter(C + "selectionEntryGroup") if x.get("name") == "1.3) Weapon (Exchange Lasgun/Autorifle)"]:
        ops.add(g.get("id"), "entryLinks", [link_el("Hot-Shot Lasgun", items("Hot-Shot Lasgun"), g.get("id"), mx=1, pts=5)])
    g = next(x for x in gs.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("1.4) For every ten models"))
    # a Plasma Gun costs +10 here, and the Volley Gun replaces one for free
    ops.add(g.get("id"), "entryLinks", [link_el("Hot-Shot Volley Gun", items("Hot-Shot Volley Gun"), g.get("id"), mx=1,
                                                pts=10)])
    sgt = named(root, "1) Grenadier Sergeant", within=gs)
    g = named(root, "1.1) Weapons (Laspistol/Autopistol)", "selectionEntryGroup", sgt)
    ops.add(g.get("id"), "entryLinks", [link_el("Hot-Shot Laspistol", items("Hot-Shot Laspistol"), g.get("id"), mx=1,
                                                pts=5)])

    # Reconnaissance Squad: Shroud Bombs (+20)
    rs = named(root, "IM - Reconnaissance Squad")
    ops.add(rs.get("id"), "entryLinks", [link_el("Shroud Bombs", items("Shroud Bombs"), rs.get("id"), mx=1, pts=20)])

    # Arvus Transport: its hull weapon, and one ranged weapon Twin-linked
    arvus = named(root, "IM - Arvus Transport")
    stubber = named(root, "Hull (Front) Mounted Heavy Stubber", "entryLink", arvus)
    ops.remove(stubber.get("id"))
    hull = E("selectionEntryGroup", id=mid(arvus.get("id"), "hull"), name="Hull (Front) Mounted weapon", hidden=False,
             collective=False, import_=True, defaultSelectionEntryId=mid(arvus.get("id"), "hull", "Hull (Front) Mounted Heavy Stubber"))
    add_constraint(hull, "min", 1, mid(arvus.get("id"), "hull min"))
    add_constraint(hull, "max", 1, mid(arvus.get("id"), "hull max"))
    hl = el(hull, "entryLinks")
    hl.append(link_el("Hull (Front) Mounted Heavy Stubber", stubber.get("targetId"), mid(arvus.get("id"), "hull"), mx=1))
    for n, p in (("Hull (Front) Mounted Autocannon", 10), ("Hull (Front) Mounted Lascannon", 15),
                 ("Hull (Front) Mounted Multi-Laser", 10)):
        hl.append(link_el(n, items(n), mid(arvus.get("id"), "hull"), mx=1, pts=p))
    twin = unit_wide("Twin-Linked (one ranged weapon)", "One of the Arvus Transport's ranged weapons gains Twin-linked.",
                     [], items)
    shared.append(twin)
    ops.add(arvus.get("id"), "selectionEntryGroups", [hull])
    ops.add(arvus.get("id"), "entryLinks", [link_el(twin.get("name"), twin.get("id"), arvus.get("id"), mx=1, pts=10)])

    # Cavalry Squad: "All models ... may take: Militia Lance and Lascarbine (+6 points each)"
    cav = named(root, "IM - Cavalry Squad")
    g = next(x for x in cav.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("3) Squad Weapon"))
    ops.add(g.get("id"), "entryLinks", [link_el("Militia Lance and Lascarbine", items("Militia Lance and Lascarbine"),
                                                g.get("id"), mx=1, pts=6, per_model_of=cav.get("id"))])

    # Sentinel Squadron: more weapons in place of the Multi-Laser; any of three extras
    sen = named(root, "IM - Sentinel Squadron")
    g = next(x for x in sen.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("Sentinal Weapons"))
    ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=5, pts=p) for n, p in (
        ("Heavy Bolter", 0), ("Multiple Rocket Pod", 5), ("Plasma Cannon", 10), ("Sentinel Powerlifter", 5))])
    sm = named(root, "Sentinel", within=sen)
    extras = take_group("May take any of", sm.get("id"), [("Heavy Chainsword", 5), ("Hunter-Killer Missile", 5),
                                                          ("Searchlights", 5)], items)
    add_rule(extras, "Heavy Chainsword", "A Sentinel with a Sentinel Powerlifter may not take a Heavy Chainsword.",
             extras.get("id"))
    ops.add(sm.get("id"), "selectionEntryGroups", [extras])

    # Heavy Ordnance Battery: an Earthshaker Gun Carriage may change its cannon
    hob = named(root, "IM - Heavy Ordnance Battery")
    carriage = named(root, "Earthshaker Gun Carriage", within=hob)
    g = named(root, "Earthshaker cannon", within=carriage)
    manticore = E("selectionEntry", id=mid("manticore storm eagles"), name="Manticore Missile Launcher (with Four Storm "
                  "Eagle Missiles)", hidden=False, collective=False, import_=True, type="upgrade")
    child(manticore, "entryLinks").append(link_el("Storm Eagle Missile", missiles["Storm Eagle Missile"],
                                                  manticore.get("id"), mn=4, mx=4))
    add_rule(manticore, "Manticore Missile Launcher", "A Manticore Missile Launcher carries four missiles and may fire "
             "only one of them in each Shooting Attack.", manticore.get("id"))
    add_cost(manticore, 0)
    shared.append(manticore)
    ops.add(g.get("id"), "entryLinks", [
        link_el("Anvilus Autocannon Battery and Helical Targeting Array",
                items("Anvilus Autocannon Battery and Helical Targeting Array"), g.get("id"), mx=1, pts=0),
        link_el(manticore.get("name"), manticore.get("id"), g.get("id"), mx=1, pts=35)])

    # Malcador: "The unit may include: Up to 2 additional Malcador Heavy Tanks (+160 points each)", each a copy of
    # the tank with its own weapon choices
    mal = named(root, "IM - Malcador Heavy Tank")
    tank = copy_official(mal, mid("malcador", "additional"))
    tank.set("name", "Additional Malcador Heavy Tank")
    tank.set("type", "model")
    for x in list(tank):
        if x.tag in ("categoryLinks", "costs", "constraints"):
            tank.remove(x)
    add_constraint(tank, "max", 2, mid(tank.get("id"), "max"))
    add_cost(tank, 160)
    ops.add(mal.get("id"), "selectionEntries", [tank])

    war_beasts(root, ops)


def hidden_unless_any(e, ids):
    e.set("hidden", "true")
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
    cg = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
    for i in ids:
        el(cg, "condition", type="atLeast", value=1, field="selections", scope="force", childId=i, shared=True,
           includeChildSelections=True, includeChildForces=False, percentValue=False)
    return e


def provenance_options(items, shared, ops):
    """The options the new Provenances (and the doc's additions to Debased Rabble and Tainted Flesh) give official
    units, each shown only while the Detachment has that Provenance."""
    root = ET.parse(CAT).getroot()
    aeldari, ratling, trail, void = (PROV[n] for n in ("Mark of the Aeldari", "Ratling Enclave", "Trailblazers",
                                                         "Voidborne Raiders"))

    def whole(name, text, parts):
        e = unit_wide(name, text, parts, items)
        shared.append(e)
        return e

    lasblasters = whole("Lasblasters (entire unit)", "Every model in the unit exchanges its Lasgun for a Lasblaster.",
                        ["Lasblaster"])
    catapults = whole("Shuriken Catapults (entire unit)", "Every model in the unit exchanges its Lasgun for a Shuriken "
                      "Catapult.", ["Shuriken Catapult"])
    shuriken_pistols = whole("Shuriken Pistols (entire unit)", "Every model in the unit exchanges its Laspistol for a "
                             "Shuriken Pistol.", ["Shuriken Pistol"])
    boarding = whole("Boarding Shields (entire unit)", "Every Infantry model in the unit takes a Boarding Shield.",
                     ["Boarding Shield"])
    combat = whole("Combat Shields (entire unit)", "Every model in the unit takes a Combat Shield.", ["Combat Shield"])

    def unit_links(uid, offers):
        ops.add(uid, "entryLinks", [hidden_unless_any(link_el(e.get("name"), e.get("id"), mid(uid, "prov"), mx=1, pts=p),
                                                      [prov]) for e, p, prov in offers])

    # Mark of the Aeldari, Voidborne Raiders: Infantry Squads, Grenadier Squads and Command Cadres
    squad = named(root, "Infantry Squad", within=named(root, "IM - Infantry Squad"))
    unit_links(squad.get("id"), [(lasblasters, 0, aeldari), (combat, 20, void)])
    for un in ("IM - Grenadier Squad", "IM - Command Cadre"):
        u = named(root, un)
        unit_links(u.get("id"), [(lasblasters, 0, aeldari), (catapults, 20, aeldari), (shuriken_pistols, 10, aeldari),
                                 (boarding, 25, void)])
        # Trailblazers: "Any number of models ... may exchange their Lasgun for a Longlas or Sniper Rifle (+10 each)"
        for g in [x for x in u.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("1.3) Weapon (Exchange Lasgun")]:
            ops.add(g.get("id"), "entryLinks", [hidden_unless_any(link_el(n, items(n), mid(g.get("id"), "trail"), mx=1,
                                                                          pts=10), [trail])
                                                for n in ("Longlas", "Sniper Rifle")])

    # the Force Commander
    fc = named(root, "1) Force Commander", within=named(root, "IM - Force Commander"))
    pistol = named(root, "1.1) Weapon (Exchange Laspistol/Autopistol)", "selectionEntryGroup", fc)
    ccw = named(root, "1.2) Weapon (Exchange Close Combat Weapon)", "selectionEntryGroup", fc)
    ops.add(pistol.get("id"), "entryLinks", [
        hidden_unless_any(link_el("Shuriken Pistol", items("Shuriken Pistol"), mid(fc.get("id"), "aeldari"), mx=1), [aeldari]),
        hidden_unless_any(link_el("Fusion Pistol", items("Fusion Pistol"), mid(fc.get("id"), "aeldari"), mx=1, pts=10),
                          [aeldari])])
    # Debased Rabble, Tainted Flesh: "exchange a Power Weapon for a Tainted Axe, Tainted Blade or Tainted Maul (+5)",
    # here as the swaps a Power Weapon is bought by (+10), plus 5
    for g in (pistol, ccw):
        ops.add(g.get("id"), "entryLinks", [
            hidden_unless_any(link_el(n, items(n), mid(g.get("id"), "tainted"), mx=1, pts=15),
                              [PROV["Debased Rabble"], PROV["Tainted Flesh"]])
            for n in ("Tainted Axe", "Tainted Blade", "Tainted Maul")])
    extras = take_group("Provenance wargear", fc.get("id"), [], items)
    for n, p, prov in (("Longlas", 10, ratling), ("Sniper Rifle", 10, ratling), ("Boarding Shield", 0, void)):
        child(extras, "entryLinks").append(hidden_unless_any(link_el(n, items(n), mid(fc.get("id"), "prov wargear"), mx=1,
                                                                     pts=p), [prov]))
    add_rule(extras, "Provenance wargear", "Ratling Enclave: a Force Commander may take a Longlas or a Sniper Rifle. "
             "Voidborne Raiders: a Force Commander not upgraded to a Mounted Force Commander may take a Boarding "
             "Shield for free.", extras.get("id"))
    ops.add(fc.get("id"), "selectionEntryGroups", [extras])


def great_war_beasts(text):
    """The Ogryn Beastmasters' '#### Great War Beasts' block as part of the datasheet: the beasts' profiles in its
    table, and their kit, Unit Type and special rules as lines of their own."""
    i = text.index("### Imperialis Militia Ogryn Beastmasters ")
    j = text.index("#### Great War Beasts", i)
    k = text.index("\n### ", j)
    unit, block = text[i:j], text[j:k]
    beasts = [l for l in block.split("\n") if l.startswith("| ") and not l.startswith(("| Model", "| ---"))]
    names = [l.split("|")[1].strip() for l in beasts]
    rules = block.split("Special Rules", 1)[1].strip().split("\n")
    # profiles: after the Ogryn Handler's row
    rows = unit.split("\n")
    h = next(n for n, l in enumerate(rows) if l.startswith("| Ogryn Handler |"))
    rows[h + 1:h + 1] = beasts
    unit = "\n".join(rows)
    unit = unit.replace("- Flak Armour (Ogryn Handler only)\n- Frag Grenades (Ogryn Handler only)",
                        "- Ogryn Handler: Close Combat Weapon, Flak Armour, Frag Grenades\n" +
                        "\n".join(f"- {n}: Close Combat Weapon" for n in names))
    unit = unit.replace("- Close Combat Weapon\n- Ogryn Handler:", "- Ogryn Handler:")
    unit = unit.replace("- Ogryn Handler: Infantry (Militia, Monstrous, Skirmish)",
                        "- Ogryn Handler: Infantry (Militia, Monstrous, Skirmish)\n" +
                        "\n".join(f"- {n}: Infantry (Monstrous, Skirmish)" for n in names))
    beast_rules = []
    for r in rules:
        m = re.match(r"- (.+?)(?: \((.+?) only\))?$", r.strip())
        if not m:
            continue
        if m.group(2):
            beast_rules.append(r.strip())
        elif "(all except" in r:
            ex = re.search(r"\(all except (.+)\)", r).group(1).replace(" and ", ", ").split(", ")
            rule = r.strip()[2:r.strip().index(" (all except")]
            beast_rules.append(f"- {rule} ({', '.join(n for n in names if n not in ex)} only)")
        else:
            beast_rules.append(f"- {m.group(1)} ({', '.join(names)} only)")
    sr = unit.index("Special Rules")
    end = unit.index("\n\n| Option", sr)
    unit = unit[:end] + "\n" + "\n".join(beast_rules) + unit[end:]
    return text[:i] + unit + text[k:]


def per_model_kit(text, unit, model, kit):
    """A wargear line of the model's own, at the end of the unit's Wargear list."""
    i = text.index(f"### {unit} ")
    j = text.index("\nUnit Type", i)
    return text[:j].rstrip("\n") + f"\n- {model}: {kit}\n" + text[j:]


def build():
    text = doc_text()
    first = next(l for l in text.splitlines() if l.startswith("# "))[2:].strip()
    b = bc.Builder(first, "Imperialis Militia", text)
    root = b.build()
    bad = [p for p in b.problems if not any(re.search(a, p) for a in ALLOWED)]
    if bad:
        sys.exit("the doc does not build cleanly:\n  " + "\n  ".join(bad))
    return b, root


def split_profiles(b, root, weapon, key):
    """The doc's armoury gives a Manticore's missiles as profiles of one weapon: each becomes an entry of its own, by
    its profile's name after the dash."""
    w = root.find(f"sharedSelectionEntries/selectionEntry[@id='{b.weapons[norm(weapon)]}']")
    out = {}
    for p in w.findall("profiles/profile"):
        name = p.get("name").split(" – ")[-1].split(" - ")[-1]
        e = el(root.find("sharedSelectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name,
               hidden=False, id=mid(key, name))
        child(e, "profiles").append(deep(p))
        for il in w.findall("infoLinks/infoLink"):
            if il.get("name").split(" (")[0] in p.find("characteristics").findall("characteristic")[3].text:
                child(e, "infoLinks").append(deep(il))
        for x in e.iter():
            if x.get("id") and x is not e:
                x.set("id", mid(e.get("id"), x.get("id")))
        add_cost(e, 0)
        out[name] = e.get("id")
    return out


def beasts_per_handler(unit, handler, beasts, per, key):
    """'Up to three Great War Beasts per Ogryn Handler' (or one War Beast per Militia Handler), in any mix: the beast
    models in one group whose limit grows with the handlers."""
    holder = unit.find("selectionEntries")
    gid = mid(unit.get("id"), key)
    g = el(child(unit, "selectionEntryGroups"), "selectionEntryGroup", name=key, hidden=False, id=gid)
    cmax = add_constraint(g, "max", 0, mid(gid, "max"))
    mod = el(el(g, "modifiers"), "modifier", type="increment", field=cmax, value=per)
    el(el(mod, "repeats"), "repeat", field="selections", scope=unit.get("id"), value=1, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId=handler, repeats=1, roundUp=False)
    inner = el(g, "selectionEntries")
    for m in [x for x in list(holder) if x.get("name") in beasts]:
        holder.remove(m)
        for c in list(m.findall("constraints/constraint")):
            if c.get("type") == "max":
                m.find("constraints").remove(c)
        for mods in m.findall("modifiers"):
            m.remove(mods)
        inner.append(m)
    return g


def special_cases(b, root, entries):
    unit = lambda n: entries[b.units[n]]

    # Ogryn Beastmasters: up to three Great War Beasts per Ogryn Handler
    bu = unit("Imperialis Militia Ogryn Beastmasters")
    handler = model_entry(bu, "Ogryn Handler").get("id")
    names = [m.get("name") for m in bu.find("selectionEntries") if m.get("name") != "Ogryn Handler"]
    beasts_per_handler(bu, handler, names, 3, "Great War Beasts")

    # Manticore: four missiles, any of them swapped for another kind
    mu = unit("Imperialis Militia Manticore Missile Tank Battery")
    missiles = split_profiles(b, root, "Manticore", "manticore")
    me = model_entry(mu, "Militia Manticore Missile Tank")
    for l in list(me.iter("entryLink")):
        target = entries.get(l.get("targetId"))
        if target is not None and target.get("name", "").startswith("Turret Mounted Manticore Missile Launcher"):
            for p in me.iter():
                if l in list(p):
                    p.remove(l)
    g = el(child(me, "selectionEntryGroups"), "selectionEntryGroup", name="Manticore Missiles", hidden=False,
           id=mid(me.get("id"), "missiles"), defaultSelectionEntryId=mid(me.get("id"), "missiles", "Manticore Missile"))
    add_constraint(g, "min", 4, mid(me.get("id"), "missiles min"))
    add_constraint(g, "max", 4, mid(me.get("id"), "missiles max"))
    for name, eid in missiles.items():
        l = el(child(g, "entryLinks"), "entryLink", import_=True, name=name, hidden=False,
               id=mid(me.get("id"), "missiles", name), type="selectionEntry", targetId=eid)
        add_constraint(l, "max", 4, mid(l.get("id"), "max"))
    add_rule(me, "Manticore Missile Launcher", "A Manticore Missile Launcher carries four missiles and may fire only "
             "one of them in each Shooting Attack.", me.get("id"))
    tidy(b, root, entries)
    auto_weapons(b, entries)
    return missiles


AUTO = {"Laspistol": "Autopistol", "Lasgun": "Autorifle"}


def auto_weapons(b, entries):
    """'Laspistol or Autopistol', 'Lasgun or Autorifle': two different weapons. Wherever a unit the doc gives that
    choice has the las weapon, it gets the auto one beside it: in every pick that offers the las weapon, at the same
    cost, and as a pick of the two where a model simply carries it."""
    doc = open(DOC, encoding="utf-8").read()
    for ds in b.datasheets:
        i = doc.index(f"### {ds['name']} ")
        j = doc.find("\n### ", i + 4)
        text = doc[i:j if j > 0 else None]
        pairs = {las: auto for las, auto in AUTO.items() if f"{las} or {auto}" in text}
        if not pairs:
            continue
        u = entries[b.units[ds["name"]]]
        for g in list(u.iter("selectionEntryGroup")):
            links = g.find("entryLinks")
            if links is None:
                continue
            for las, auto in pairs.items():
                l = next((x for x in links if x.get("name") == las), None)
                if l is None or any(x.get("name") == auto for x in links):
                    continue
                c = deep(l)
                c.set("name", auto)
                c.set("targetId", any_entry(auto))
                for x in c.iter():
                    if x.get("id"):
                        x.set("id", mid(x.get("id"), auto))
                for x in c.iter():
                    if x.get("field") and x.get("field") != "hidden" and not x.get("field").startswith("d2ee"):
                        x.set("field", mid(x.get("field"), auto))
                links.insert(list(links).index(l) + 1, c)
        for m in [x for x in u.iter("selectionEntry") if x.get("type") == "model"]:
            links = m.find("entryLinks")
            if links is None:
                continue
            for las, auto in pairs.items():
                l = next((x for x in links if x.get("name") == las), None)
                if l is None:
                    continue
                links.remove(l)
                key = mid(m.get("id"), las, auto)
                g = el(child(m, "selectionEntryGroups"), "selectionEntryGroup", name=f"{las} or {auto}", hidden=False,
                       id=key, defaultSelectionEntryId=mid(key, las))
                add_constraint(g, "min", 1, mid(key, "min"))
                add_constraint(g, "max", 1, mid(key, "max"))
                gl = el(g, "entryLinks")
                gl.append(link_el(las, l.get("targetId"), key, mx=1))
                gl.append(link_el(auto, any_entry(auto), key, mx=1))


def one_more_per_five(unit, model_id):
    """'For every five models beyond the unit's starting size, one ... may be upgraded to a ...': one more of this
    model for every five models past the first five."""
    m = next(x for x in unit.iter("selectionEntry") if x.get("id") == model_id)
    cmax = next(c for c in m.findall("constraints/constraint") if c.get("type") == "max")
    mods = child(m, "modifiers")
    mod = el(mods, "modifier", type="increment", field=cmax.get("id"), value=1)
    el(el(mod, "repeats"), "repeat", field="selections", scope=unit.get("id"), value=5, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="model", repeats=1, roundUp=False)
    el(mods, "modifier", type="decrement", field=cmax.get("id"), value=1)


def tidy(b, root, entries):
    """What the Builder leaves empty: options that give a special rule, weapons given in pairs, a weapon with its
    co-axial gun; the Mounted Command Cadre's extra Lieutenants."""
    shared = root.find("sharedSelectionEntries")
    gst_rules = bc.load_gst_rules()
    for e in list(shared):
        name = e.get("name")
        if e.find("profiles") is not None or e.find("entryLinks") is not None or e.find("infoLinks") is not None:
            continue
        key = norm(name)
        if key in ("bunker drop", "pathfinder", "twin-linked"):
            rid, rname = gst_rules[key]
            el(child(e, "infoLinks"), "infoLink", name=rname, id=mid(e.get("id"), "rule"), hidden=False, targetId=rid,
               type="rule")
            continue
        m = re.match(r"One Hull \(Left\) and One Hull \(Right\) Mounted (.+)$", name)
        if m:
            child(e, "entryLinks").append(link_el(m.group(1), weapon_id(b, m.group(1)), e.get("id"), mn=2, mx=2))
            continue
        m = re.match(r"Turret Mounted (.+?) with Co-axial (.+)$", name)
        if m:
            for w in m.groups():
                child(e, "entryLinks").append(link_el(w, weapon_id(b, w), e.get("id"), mn=1, mx=1))
    # the Mounted Command Cadre: Lieutenants as the Command Cadre has them, not a unit upgrade
    u = entries[b.units["Imperialis Militia Mounted Command Cadre"]]
    for g in u.iter("selectionEntryGroup"):
        for l in list(g.findall("entryLinks/entryLink")):
            if l.get("name") == "Mounted Militia Lieutenant":
                g.find("entryLinks").remove(l)
    one_more_per_five(u, model_entry(u, "Mounted Militia Lieutenant").get("id"))
    for gs in u.iter("selectionEntryGroups"):
        for g in list(gs):
            if not list(g.iter("entryLink")) and not list(g.iter("selectionEntry")):
                gs.remove(g)


def weapon_id(b, name):
    """A weapon the doc's Armoury or the game system has."""
    wid = b.find_weapon(name)[0]
    return wid or any_entry(name)


def add_top(cat, container, elements):
    """Text.add_top, but at the catalogue's own container: the official file has a closing tag of a nested
    entryLinks at the top level's indent, which add_top would take for the catalogue's."""
    i = cat.s.index(f"{cat.nl}  <{container}>") + len(cat.nl)
    j = cat.s.index(f"{cat.nl}  </{container}>", i) + len(cat.nl)
    cat.s = cat.s[:j] + "".join(et.xml(e, 2).replace("\n", cat.nl) + cat.nl for e in elements) + cat.s[j:]


class Ops:
    """Edits to the official file, made once the expansion's ids are final."""

    def __init__(self):
        self.ops = []

    def add(self, eid, container, elements):
        self.ops.append(("add", eid, container, elements))

    def remove(self, eid):
        self.ops.append(("remove", eid))

    def run(self, cat):
        for op in self.ops:
            if op[0] == "add":
                for e in op[3]:
                    for x in e.iter():
                        for a in ("targetId", "childId"):
                            if x.get(a):
                                x.set(a, et.cfg.remap.get(x.get(a), x.get(a)))
                cat.add(op[1], op[2], op[3])
            else:
                cat.remove(op[1])


def official_transport_choices(ops, official, official_links):
    """The official units' Dedicated Transport picks: the Liber Imperatus transports in place of the official
    entries they replace, in the pick the unit has or a new one."""
    for uid, links in official_links.items():
        unit = next(u for u in official.values() if u.get("id") == uid)
        g = next((x for x in unit.iter(C + "selectionEntryGroup") if "Dedicated Transport" in x.get("name", "")), None)
        if g is None:
            ng = E("selectionEntryGroup", id=mid(uid, "dt group"), name="Dedicated Transport", hidden=False,
                   collective=False, import_=True)
            add_constraint(ng, "max", 1, mid(uid, "dt group max"))
            el(ng, "entryLinks").extend(links)
            ops.add(uid, "selectionEntryGroups", [ng])
            continue
        for l in g.iter(C + "entryLink"):
            if l.get("name") in OFFICIAL_TRANSPORTS:
                ops.remove(l.get("id"))
        ops.add(g.get("id"), "entryLinks", links)


def main():
    cat = Text(CAT)
    if 'name="IM - Astropath"' in cat.s:
        sys.exit(f"{CAT} already has the Imperialis Militia expansion")
    gst = Text(et.GST)
    idx = et.official_index()
    official = et.official_units()
    b, root = build()
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    missiles = special_cases(b, root, entries)
    official_links = transports(b, entries, official)
    items = Items(b)
    shared = []
    ops = Ops()
    existing_units(items, shared, ops, missiles)
    provenance_options(items, shared, ops)
    for ds in b.datasheets:
        et.rename(root, entries[b.units[ds["name"]]], short(ds["name"]))
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx, extra_ids=items.extra)
    roots = []
    for ds in b.datasheets:
        u = entries[b.units[ds["name"]]]
        et.drop_unit_category(u)
        et.add_types(u, SUB_TYPES)
        if u.get("name") in TRANSPORTS:
            continue
        r = et.root_link(u, ds)
        rules = " ".join(ds["rules"])
        m = re.search(r"Provenance \((.+?)\)", rules)
        if m:  # "Provenance (Kinfolk Helots)"
            hidden_unless(r, PROV[m.group(1)])
        elif re.search(r"(^| )Traitor( |$)", rules) or "Traitor" in ds["rules"]:
            hidden_unless(r, TRAITOR)
        if u.get("name") == "IM - Mutated Spawn":  # "0-1 per Detachment (see Tainted Flesh)"
            c = add_constraint(r, "max", 1, mid(u.get("id"), "detachment"), scope="force", children=True)
            mod = el(child(r, "modifiers"), "modifier", type="set", field=c, value=-1)
            cond(mod, "atLeast", 1, PROV["Tainted Flesh"])
        roots.append(r)
    # the slots the Provenances open
    for uname, slot, prov in (("IM - Ratling Squad", "Troops", "Ratling Enclave"),
                              ("IM - Ogryn Beastmasters", "Fast Attack", "Ogryn Conscripts")):
        u = next(x for x in units if x.get("name") == uname)
        r = et.root_link(u, None, slot=slot, key="provenance " + prov)
        hidden_unless(r, PROV[prov])
        roots.append(r)

    official_transport_choices(ops, official, official_links)
    # "Imperialis Militia Discipline Master Cadres may not be taken" (Acolytes of the Saviour Emperor)
    official_root = ET.parse(CAT).getroot()
    for l in official_root.find(C + "entryLinks"):
        if l.get("name") == "IM - Discipline Master Cadre":
            mod = E("modifier", type="set", field="hidden", value="true")
            cond(mod, "atLeast", 1, PROV["Acolytes of the Saviour Emperor"])
            ops.add(l.get("id"), "modifiers", [mod])
    ops.run(cat)
    # the official transports the doc's replace, now unused
    official_shared = official_root.find(C + "sharedSelectionEntries")
    for name in OFFICIAL_TRANSPORTS:
        e = next(x for x in official_shared if x.get("name") == name)
        if cat.s.count(e.get("id")) == 1:
            cat.remove(e.get("id"))

    provenances(b, gst)
    add_top(cat, "entryLinks", roots)
    for e in shared:
        for x in e.iter():
            for a in ("targetId", "childId"):
                if x.get(a):
                    x.set(a, et.cfg.remap.get(x.get(a), x.get(a)))
    add_top(cat, "sharedSelectionEntries", units + keep_entries + shared)
    if keep_groups:
        add_top(cat, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        add_top(cat, "sharedRules", keep_rules)
    cat.bump("catalogue")
    cat.save()
    gst.save()
    print(f"{CAT}: {len(units)} units, {len(keep_entries)} entries, {len(keep_groups)} groups, "
          f"{len(keep_rules)} rules added; {len(NEW_PROVENANCES)} Provenances of War in {et.GST}")


if __name__ == "__main__":
    main()
