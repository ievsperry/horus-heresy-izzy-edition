#!/usr/bin/env python3
"""Protodreadnoughts (homebrew/source/protodreadnoughts.md).

The Lucifer-Pattern, Furibundus-Pattern and Unification-Pattern Protodreadnoughts go into the Mech Library, which
the Legiones Astartes, Mechanicum, Imperialis Militia and Questoris Household catalogues all import, and every one of
those catalogues (each Legion, Blackshields and Shattered Legions too) gets a root entry for them. Their options for
one army only are hidden in every other army:

- World Eaters and Iron Warriors: the XII and IV Legion chassis upgrades and weapons (by the Legion's faction entry);
- Mechanicum: the High Techno-Arcana chassis upgrades (by the Order of High Techno-arcana the force has taken; the
  Infernal Warp-Capacitor for a Traitor force with the Reductor Order or a Proscribed Order) and the Mechanicum
  weapon swaps;
- Mechanicum or Questoris Household: the Questoris Household Bondsman-Rig, which moves the squadron to Troops and
  gives it the Line Sub-type.

The Leagues of Votann's Ironkin Ancestor-Rig, Cthonian Siege-Strider and Brokhyr Ballistic Strider are added to that
catalogue each time it is built (apply(), named in build_catalogue.py's FACTION_LIMITS), with their League upgrades
shown only for the League the Detachment has chosen.

Every model's arm is one pick: a close combat arm carries its in-built weapon, which has a pick of its own, so an arm
exchanged for a gun loses its in-built weapon, as on the datasheets.

usage: python3 homebrew/protodreadnoughts.py    (the Imperial units; it refuses to run twice)"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, add_cost, child, el, make_id, norm  # noqa: E402

GST = "2022 - Horus Heresy.gst"
LIBRARY = "2022 - Mech Library.cat"
NS = "{http://www.battlescribe.net/schema/catalogueSchema}"
GNS = "{http://www.battlescribe.net/schema/gameSystemSchema}"

WEAPON = ("1a1a-e592-2849-a5c0", "Weapon", [("Range", "95ba-cda7-b831-6066"), ("Strength", "24d9-b8e1-a355-2458"),
                                            ("AP", "f7a6-e0d8-7973-cd8d"), ("Type", "2f86-c8b4-b3b4-3ff9")])
WARGEAR = ("2a1f-7837-f0ef-be44", "Wargear Item", "Description", "347e-ee4a-764f-6be3")
UNIT_PROFILE = ("4bb2-cb95-e6c8-5a21", "Unit")
ARMIGER = ("41ff-7fc9-d4a0-da2", "Armiger Unit Type")
HEAVY = ("9231-183c-b97b-63f9", "Heavy Sub-type")
LINE = ("6399-5c65-7833-1025", "Line Sub-type")
LEGIONES_ASTARTES = ("ffcb-13b4-9b4c-84da", "Legiones Astartes (X)")

# faction selections (each catalogue's Allegiance entry) and the Orders of High/Proscribed Techno-arcana
WORLD_EATERS, IRON_WARRIORS = "90ee-77dd-1b7f-ddfe", "5f54-457a-fbb9-6730"
MECHANICUM, QUESTORIS = "ddf5-d792-3146-6e9a", "807e-0cf8-7f28-7b6d"
TRAITOR = "f9c0-0c5a-3e24-58c7"
ORDERS = {"Cybernetica": "9bcd-f556-5740-2f9f", "Lacrymaerta": "bd4b-63fa-928c-887d", "Macrotek": "1247-a94b-070d-2a7b",
          "Malagra": "5e62-8d7e-a487-0490", "Myrmidax": "8305-5ac6-f395-e570", "Reductor": "73dc-f5bb-be45-2547"}
PROSCRIBED = ["e033-44c5-e827-20ff", "d929-7702-8f4b-3393", "de6f-55bd-6647-586a"]  # Malefikite, Nekrotek, Malamina
LEAGUES = {"Greater Thurian League": "53a0-2151-818f-1792", "Kronus Hegemony": "c420-ead6-6567-06b5",
           "Trans-Hyperian Alliance": "f1d3-30f8-4eba-00eb", "Urani-Surtr Regulates": "6323-25ed-9221-9ff4",
           "Ymyr Conglomerate": "a97e-906d-8554-dab7"}

# who may see an option: a list of alternatives, each a list of selections the force must all have
SHOW = {None: None, "mech": [[MECHANICUM]], "we": [[WORLD_EATERS]], "iw": [[IRON_WARRIORS]],
        "mech or questoris": [[MECHANICUM], [QUESTORIS]],
        "infernal": [[TRAITOR, ORDERS["Reductor"]]] + [[TRAITOR, p] for p in PROSCRIBED]}
SHOW.update({f"order {k}": [[v]] for k, v in ORDERS.items()})
SHOW.update({f"league {k}": [[v]] for k, v in LEAGUES.items()})


def mid(*key):
    return make_id("protodreadnought", *key)


class Ctx:
    """What a build can link: entries and rules by name, and the new shared entries it makes."""

    def __init__(self, key, entries, rules):
        self.key, self.entries, self.rules, self.new = key, entries, rules, []

    def id(self, name):
        i = self.entries.get(norm(name))
        if i is None:
            sys.exit(f"{self.key}: no entry named {name}")
        return i


def index(files):
    entries, rules = {}, {}
    for f in files:
        root = ET.parse(f).getroot()
        ns = GNS if f.endswith(".gst") else NS
        for e in root.findall(f"{ns}sharedSelectionEntries/{ns}selectionEntry"):
            entries.setdefault(norm(e.get("name")), e.get("id"))
        for r in root.iter(f"{ns}rule"):
            rules.setdefault(norm(r.get("name")), r.get("id"))
    return entries, rules


def show_if(e, who):
    """Hidden unless the force has one of the alternatives' selections (all of them)."""
    alts = SHOW[who]
    if not alts:
        return e
    e.set("hidden", "true")
    for alt in alts:
        mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="and"), "conditions") if len(alt) > 1 \
            else el(mod, "conditions")
        for c in alt:
            el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=c, shared=True,
               includeChildSelections=True, includeChildForces=False, percentValue=False)
    return e


def rule_links(ctx, e, text, key):
    """Info links for the special rules a weapon's Type names ("Brutal (2)" links Brutal (X), shown as Brutal (2))."""
    seen = set()
    for tok in re.split(r",\s*|;\s*", re.sub(r"\.$", "", text)):
        tok = tok.strip().lstrip("†")
        base = re.sub(r"\s*\([^()]*\)$", "", tok)
        if not tok or re.match(r"(Melee|Assault|Heavy|Pistol|Rapid[- ]Fire|Ordnance|Salvo)\b", tok, re.I):
            continue
        for name in (tok, base + " (X)", base):
            rid = ctx.rules.get(norm(name))
            if rid and rid not in seen:
                seen.add(rid)
                link = el(child(e, "infoLinks"), "infoLink", id=mid(*key, "rule", name), name=name, hidden=False,
                          targetId=rid, type="rule")
                if name != tok:
                    el(el(link, "modifiers"), "modifier", type="set", field="name", value=tok)
                break


def weapon(ctx, name, profiles):
    """A new weapon: [(profile name or None, range, strength, AP, type)]."""
    key = (ctx.key, "weapon", name)
    e = ET.Element("selectionEntry", {"id": mid(*key), "name": name, "hidden": "false", "collective": "false",
                                      "import": "true", "type": "upgrade"})
    for pname, *chars in profiles:
        pname = pname or name
        p = el(child(e, "profiles"), "profile", id=mid(*key, pname), name=pname, hidden=False, typeId=WEAPON[0],
               typeName=WEAPON[1])
        cs = el(p, "characteristics")
        for (cname, cid), v in zip(WEAPON[2], chars):
            el(cs, "characteristic", name=cname, typeId=cid).text = v
        rule_links(ctx, e, chars[3], key)
    add_cost(e, 0)
    ctx.new.append(e)
    ctx.entries[norm(name)] = e.get("id")
    return e


def wargear(ctx, name, text, rules=()):
    key = (ctx.key, "wargear", name)
    e = ET.Element("selectionEntry", {"id": mid(*key), "name": name, "hidden": "false", "collective": "false",
                                      "import": "true", "type": "upgrade"})
    p = el(child(e, "profiles"), "profile", id=mid(*key, "profile"), name=name, hidden=False, typeId=WARGEAR[0],
           typeName=WARGEAR[1])
    el(el(p, "characteristics"), "characteristic", name=WARGEAR[2], typeId=WARGEAR[3]).text = text
    for r in rules:
        rid = ctx.rules.get(norm(r))
        if rid:
            el(child(e, "infoLinks"), "infoLink", id=mid(*key, "rule", r), name=r, hidden=False, targetId=rid,
               type="rule")
    add_cost(e, 0)
    ctx.new.append(e)
    ctx.entries[norm(name)] = e.get("id")
    return e


def link(parent, ctx, name, key, cost=None, mn=None, mx=None, who=None):
    l = el(child(parent, "entryLinks"), "entryLink", id=mid(*key, name), name=name, hidden=False, collective=False,
           import_=True, targetId=ctx.id(name), type="selectionEntry")
    if mn is not None:
        add_constraint(l, "min", mn, mid(*key, name, "min"))
    if mx is not None:
        add_constraint(l, "max", mx, mid(*key, name, "max"))
    if cost is not None:
        add_cost(l, cost)
    return show_if(l, who)


def group(parent, name, key, mn, mx):
    g = el(child(parent, "selectionEntryGroups"), "selectionEntryGroup", id=mid(*key), name=name, hidden=False,
           collective=False, import_=True)
    if mn:
        add_constraint(g, "min", mn, mid(*key, "min"))
    if mx:
        add_constraint(g, "max", mx, mid(*key, "max"))
    return g


def option(g, ctx, opt, key):
    """One choice in a pick: (label, cost, weapons, in-built pick or None, who). A label that is one weapon with
    nothing in-built is a plain link to it."""
    label, cost, weapons, inbuilt, who = opt
    if weapons == [label] and not inbuilt:
        return link(g, ctx, label, key, cost=cost, mx=1, who=who)
    e = el(child(g, "selectionEntries"), "selectionEntry", id=mid(*key, label), name=label, hidden=False,
           collective=False, import_=True, type="upgrade")
    add_constraint(e, "max", 1, mid(*key, label, "max"))
    for w in weapons:
        link(e, ctx, w, key + (label,), mn=1, mx=1)
    if inbuilt:
        pick(e, ctx, "In-built weapon", inbuilt, key + (label, "in-built"))
    add_cost(e, cost)
    return show_if(e, who)


def pick(parent, ctx, name, options, key, mn=1, mx=1):
    """A pick (one of the options, the first by default)."""
    g = group(parent, name, key, mn, mx)
    first = None
    for opt in options:
        o = option(g, ctx, opt, key)
        first = o if first is None else first
    if mn:
        g.set("defaultSelectionEntryId", first.get("id"))
    return g


def per_model(e, unit_id, pts):
    """A whole-unit pick priced per model."""
    add_cost(e, 0)
    mod = el(child(e, "modifiers"), "modifier", type="increment", field=bc.PTS, value=pts)
    el(el(mod, "repeats"), "repeat", field="selections", scope=unit_id, value=1, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="model", repeats=1, roundUp=False)


def upgrades(unit, ctx, name, items, key, who=None):
    """A pick of at most one whole-unit upgrade: [(name, pts per model, text, who, rules)]."""
    g = group(unit, name, key, 0, 1)
    show_if(g, who)
    for uname, pts, text, uwho, rules in items:
        if norm(uname) not in ctx.entries:
            wargear(ctx, uname, text, rules)
        l = el(child(g, "entryLinks"), "entryLink", id=mid(*key, uname), name=uname, hidden=False, collective=False,
               import_=True, targetId=ctx.id(uname), type="selectionEntry")
        add_constraint(l, "max", 1, mid(*key, uname, "max"))
        per_model(l, unit.get("id"), pts)
        show_if(l, uwho)
    return g


def unit_entry(ctx, spec):
    """A squadron of one model type, as the official Armiger and Dreadnought units are built."""
    key = (ctx.key, spec["name"])
    u = ET.Element("selectionEntry", {"id": mid(*key, "unit"), "name": spec["name"], "hidden": "false",
                                      "collective": "false", "import": "true", "type": "unit"})
    for r, shown in spec["rules"]:
        rid = ctx.rules.get(norm(r))
        if rid is None:
            sys.exit(f"{ctx.key}: no rule {r}")
        l = el(child(u, "infoLinks"), "infoLink", id=mid(*key, "rule", r), name=r, hidden=False, targetId=rid,
               type="rule")
        if shown:
            el(el(l, "modifiers"), "modifier", type="set", field="name", value=shown)
    cats = child(u, "categoryLinks")
    for cid, cname in [ARMIGER] + ([HEAVY] if "Heavy" in spec["type"] else []):
        el(cats, "categoryLink", id=mid(*key, "cat", cname), name=cname, hidden=False, targetId=cid, primary=False)
    m = el(child(u, "selectionEntries"), "selectionEntry", id=mid(*key, "model"), name=spec["model"], hidden=False,
           collective=False, import_=True, type="model")
    add_constraint(m, "min", 1, mid(*key, "model", "min"))
    add_constraint(m, "max", spec["max"], mid(*key, "model", "max"))
    p = el(child(m, "profiles"), "profile", id=mid(*key, "profile"), name=spec["model"], hidden=False,
           typeId=UNIT_PROFILE[0], typeName=UNIT_PROFILE[1])
    cs = el(p, "characteristics")
    for (cname, cid), v in zip(bc.UNIT_CHARS, [spec["type"]] + spec["stats"]):
        el(cs, "characteristic", name=cname, typeId=cid).text = v
    for w in spec["wargear"]:
        link(m, ctx, w, key + ("model",), mn=1, mx=1)
    for gname, opts in spec["arms"]:
        pick(m, ctx, gname, opts, key + (gname,))
    for gname, opts, most in spec["carapace"]:
        g = group(m, gname, key + (gname,), 0, most)
        for name, cost, who in opts:
            link(g, ctx, name, key + (gname,), cost=cost, mx=1, who=who)
    add_cost(m, spec["model_pts"])
    add_cost(u, spec["unit_pts"])
    for gname, items, who in spec["upgrades"]:
        upgrades(u, ctx, gname, items, key + (gname,), who)
    for name, pts, text, who in spec.get("unit_options", []):
        if norm(name) not in ctx.entries:
            wargear(ctx, name, text)
        l = link(u, ctx, name, key + ("unit option",), mx=1, who=who)
        per_model(l, u.get("id"), pts)
    return u


# ---- the datasheets ---------------------------------------------------------------------------------------------

EXTRA_ARMOUR = ("Grants a 2+ Armour Save and a 6+ Invulnerable Save against all shooting and melee attacks. In "
                "addition, enemy attacks targeting this model do not benefit from To Wound re-rolls granted by the "
                "Armourbane (X) special rule, and the value of any Brutal (X) special rule is reduced by 1 (to a "
                "minimum of 1).")
TARGETING = ("Grants Skyfire and Interceptor to all weapons fired by this model if it remained stationary in its "
             "preceding Movement phase.")
INBUILT_IMPERIAL = [("Heavy Flamer", 5, "Heavy Flamer"), ("Plasma Blaster", 10, "Plasma Blaster"),
                    ("Graviton Gun", 15, "Graviton Gun"), ("Meltagun", 15, "Meltagun")]


def inbuilt(default, items, mech=False):
    opts = [(default, 0, [default], None, None)] + [(n, c, [w], None, None) for n, c, w in items]
    if mech:
        opts += [("Volkite Charger", 5, ["Volkite Charger"], None, "mech"),
                 ("Phased Plasma-Fusil", 10, ["Phased Plasma-Fusil"], None, "mech")]
    return opts


def imperial_weapons(ctx):
    weapon(ctx, "Siege Claw", [(None, "-", "10", "2", "Melee, Brutal (3)")])
    weapon(ctx, "Siege Drill", [(None, "-", "12", "2", "Melee, Armourbane (Melee)")])
    weapon(ctx, "Cyclone Missile System", [("Cyclone Missile System - Frag", '48"', "4", "6", 'Heavy 1, Large Blast (5"), Pinning'),
                                           ("Cyclone Missile System - Krak", '48"', "8", "3", "Heavy 2, Twin-linked")])
    weapon(ctx, "Twin-linked Cyclone Missile Pod", [
        ("Twin-linked Cyclone Missile Pod - Frag", '48"', "4", "6", 'Heavy 1, Large Blast (5"), Pinning, Twin-linked'),
        ("Twin-linked Cyclone Missile Pod - Krak", '48"', "8", "3", "Heavy 2, Twin-linked")])
    weapon(ctx, "Twin-linked Gravis Bolt Cannon", [(None, '48"', "5", "4", "Heavy 6, Twin-linked")])
    weapon(ctx, "Twin-linked Gravis Autocannon", [(None, '48"', "7", "4", "Heavy 3, Rending (6+), Twin-linked")])
    weapon(ctx, "Twin-linked Gravis Lascannon", [(None, '48"', "9", "2", "Heavy 2, Sunder, Twin-linked")])
    if norm("Twin-linked Mauler Bolt Cannon") not in ctx.entries:
        weapon(ctx, "Twin-linked Mauler Bolt Cannon", [(None, '24"', "6", "4", "Heavy 4, Pinning, Twin-linked")])
    weapon(ctx, "Excoriator Chain-Cleaver", [(None, "-", "+2", "2", "Melee, Shred, Brutal (2), Unwieldy; a pair "
                                                                   "grants +1 Attack")])
    weapon(ctx, "Graviton Crusher-Claw", [(None, "-", "+2", "2", "Melee, Concussive (1), Haywire, Unwieldy")])
    weapon(ctx, "Shrapnel Cannon", [(None, '18"', "5", "5", "Heavy 6, Pinning, Shred")])
    weapon(ctx, "Twin-linked Shrapnel Cannon", [(None, '18"', "5", "5", "Heavy 6, Pinning, Shred, Twin-linked")])
    weapon(ctx, "Carapace Phosphex Discharger", [(None, '18"', "5", "2", 'Heavy 1, Blast (3"), Poisoned (3+), '
                                                                         "Crawling Fire, Lingering Death, One Shot")])
    wargear(ctx, "Dreadnought Extra Armour", EXTRA_ARMOUR)
    wargear(ctx, "Protodreadnought Helical Targeting Array", TARGETING, ["Skyfire", "Interceptor"])


def fist(name, cost, default_inbuilt):
    """A close combat arm with its in-built weapon."""
    return (name, cost, [name], inbuilt(default_inbuilt, INBUILT_IMPERIAL, mech=True), None)


def lucifer_arm():
    return [fist("Gravis Power Fist", 0, "Combi-bolter"),
            fist("Gravis Chainfist", 10, "Combi-bolter"),
            ("Gravis Bolt Cannon", 5, ["Gravis Bolt Cannon"], None, None),
            ("Gravis Autocannon", 10, ["Gravis Autocannon"], None, None),
            ("Cyclone Missile System", 15, ["Cyclone Missile System"], None, None),
            ("Gravis Lascannon", 15, ["Gravis Lascannon"], None, None),
            ("Gravis Melta Cannon", 15, ["Gravis Melta Cannon"], None, None),
            ("Heavy Conversion Beamer", 20, ["Heavy Conversion Beamer"], None, None),
            ("Siege Drill with in-built Heavy Flamer", 15, ["Siege Drill", "Heavy Flamer"], None, None),
            # Mechanicum: a Mauler Bolt Cannon for the bolt cannon or autocannon (+5), a Kheres or Darkfire for the
            # lascannon (+15, +20)
            ("Mauler Bolt Cannon", 10, ["Mauler Bolt Cannon"], None, "mech"),
            ("Kheres Assault Cannon", 30, ["Kheres Assault Cannon"], None, "mech"),
            ("Darkfire Cannon", 35, ["Darkfire Cannon"], None, "mech"),
            ("Excoriator Chain-Cleaver", 15, ["Excoriator Chain-Cleaver"], inbuilt("Combi-bolter", INBUILT_IMPERIAL),
             "we"),
            ("Graviton Crusher-Claw", 15, ["Graviton Crusher-Claw"], inbuilt("Combi-bolter", INBUILT_IMPERIAL), "iw"),
            ("Shrapnel Cannon", 5, ["Shrapnel Cannon"], None, "iw")]


def furibundus_arm():
    return [("Siege Claw", 0, ["Siege Claw"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL, mech=True), None),
            ("Siege Drill", 10, ["Siege Drill"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL, mech=True), None),
            ("Twin-linked Gravis Bolt Cannon", 10, ["Twin-linked Gravis Bolt Cannon"], None, None),
            ("Twin-linked Gravis Autocannon", 15, ["Twin-linked Gravis Autocannon"], None, None),
            ("Twin-linked Cyclone Missile Pod", 25, ["Twin-linked Cyclone Missile Pod"], None, None),
            ("Twin-linked Gravis Lascannon", 25, ["Twin-linked Gravis Lascannon"], None, None),
            ("Cyclonic Melta Lance", 25, ["Cyclonic Melta Lance"], None, None),
            ("Grav-Flux Bombard", 25, ["Grav-Flux Bombard"], None, None),
            ("Heavy Conversion Beamer", 20, ["Heavy Conversion Beamer"], None, None),
            ("Twin-linked Mauler Bolt Cannon", 20, ["Twin-linked Mauler Bolt Cannon"], None, "mech"),
            ("Kheres Assault Cannon", 40, ["Kheres Assault Cannon"], None, "mech"),
            ("Darkfire Cannon", 45, ["Darkfire Cannon"], None, "mech"),
            ("Excoriator Chain-Cleaver", 15, ["Excoriator Chain-Cleaver"],
             inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL), "we"),
            ("Graviton Crusher-Claw", 15, ["Graviton Crusher-Claw"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL),
             "iw"),
            ("Twin-linked Shrapnel Cannon", 10, ["Twin-linked Shrapnel Cannon"], None, "iw")]


def unification_arm(base):
    """The gun arms, priced from the arm's own weapon (the primary arm's Gravis Bolt Cannon, 0; the missile arm's
    Cyclone Missile System, 0)."""
    if base == "primary":
        costs = {"Gravis Bolt Cannon": 0, "Gravis Autocannon": 5, "Gravis Plasma Cannon": 10,
                 "Volkite Dual-Culverin": 10, "Cyclone Missile System": 10, "Gravis Lascannon": 15}
        order = ["Gravis Bolt Cannon", "Gravis Autocannon", "Gravis Plasma Cannon", "Volkite Dual-Culverin",
                 "Cyclone Missile System", "Gravis Lascannon"]
    else:
        costs = {"Cyclone Missile System": 0, "Gravis Bolt Cannon": -10, "Gravis Autocannon": -5,
                 "Gravis Plasma Cannon": 0, "Volkite Dual-Culverin": 0, "Gravis Lascannon": 5}
        order = ["Cyclone Missile System", "Gravis Bolt Cannon", "Gravis Autocannon", "Gravis Plasma Cannon",
                 "Volkite Dual-Culverin", "Gravis Lascannon"]
    out = [(n, costs[n], [n], None, None) for n in order]
    bolt, las = costs["Gravis Bolt Cannon"], costs["Gravis Lascannon"]
    return out + [("Mauler Bolt Cannon", bolt + 5, ["Mauler Bolt Cannon"], None, "mech"),
                  ("Kheres Assault Cannon", las + 15, ["Kheres Assault Cannon"], None, "mech"),
                  ("Darkfire Cannon", las + 20, ["Darkfire Cannon"], None, "mech"),
                  ("Shrapnel Cannon", bolt, ["Shrapnel Cannon"], None, "iw")]


TECHNO_ARCANA = [
    ("Cortex-Controller Slave-Node", 15, "Replaces the living pilot with a hard-wired Cybernetica Cortex; the model "
     "gains the Cybernetica unit sub-type, Fearless, and Programmed Behaviour (if not within 12\" of a friendly model "
     "with a Cortex Controller, it must fire at the nearest visible enemy unit and cannot make Reactions). While "
     "within 12\" of a friendly Cortex Controller, it adds +1 to its Ballistic Skill when making Interceptor "
     "Reactions.", "order Cybernetica", ["Fearless"]),
    ("Siege-Breaker Auspex & Shock-Prow", 20, "When resolving shooting or melee attacks against Fortifications, "
     "Buildings, or Vehicles, this model gains Sunder (re-rolling failed Armour Penetration rolls). In addition, it "
     "gains Hammer of Wrath (2) resolved at Strength 8, AP 3.", "order Reductor", ["Sunder", "Hammer of Wrath (X)"]),
    ("Bio-Augmetic Vat-Pilot", 20, "The living pilot is heavily fused into nutrient-stasis manifolds and sub-dermal "
     "flesh-grafts; the model gains Feel No Pain (5+) and It Will Not Die (5+).", "order Lacrymaerta",
     ["Feel No Pain (X)", "It Will Not Die (X)"]),
    ("Anima-Hunting Logic-Engine", 20, "When targeting enemy units containing models with the Psyker, Daemon, or "
     "Corrupted special rules (or Enemy HQ units), this model gains Preferred Enemy (Target Unit) and Hatred (Target "
     "Unit).", "order Malagra", ["Preferred Enemy (X)", "Hatred (X)"]),
    ("Auto-Simulacra & Power-Conduit", 15, "At the start of each friendly Movement phase, roll a D6; on a 5+, this "
     "model restores 1 lost Wound (up to its starting maximum). In addition, friendly models with the Battlesmith (X) "
     "special rule within 3\" add +1 to their Battlesmith rolls when repairing this model (to a maximum of 2+).",
     "order Macrotek", []),
    ("Phased Plasma-Fusil & Targeting Array", 20, "All Volkite, Plasma, Conversion, and Graviton weapons equipped by "
     "this model add +4\" to their maximum range and may re-roll Gets Hot rolls of 1.", "order Myrmidax", []),
    ("Infernal Warp-Capacitor", 25, "Traitor only. The model gains the Corrupted sub-type, Fear (1), and a 5+ "
     "Invulnerable Save against all shooting and melee attacks. However, when reduced to 0 Wounds, add +2\" to the "
     "radius of its Unstable Arc-Reactor explosion (inflicting hits on all units within 8\" instead of 6\").",
     "infernal", ["Fear (X)"]),
]
QUESTORIS_UPGRADE = [
    ("Questoris Household Bondsman-Rig", 15, "Replaces the standard Mechanicum pilot with a bonded Knight Household "
     "Aspirant or Sacristan Bondsman. This unit gains the Questoris Familia faction keyword and the Line unit "
     "sub-type, and may be selected as a Troops choice instead of its normal Force Organisation Chart slot. However, "
     "it retains (or gains) the Support Squad special rule (meaning it cannot be used to fulfil compulsory Troops "
     "selections in a detachment). In addition, while within 12\" of a friendly Knight unit (any model with the "
     "Knight Unit Type), this unit may use that Knight's Leadership characteristic for Morale and Pinning tests and "
     "gains Counter-Attack (1).", None, ["Counter-Attack (X)"])]
WORLD_EATERS_UPGRADES = [
    ("Butcher's Nails Neural-Shunt", 20, "The pilot's Butcher's Nails are wired directly into the walker's hydraulic "
     "manifolds. The model gains Rage (2) and Fearless, and ignores the -1\" penalty to Charge distance rolls from "
     "Clumsy Hydraulic Actuators (it still suffers the -1\" penalty to Run moves and cannot make Sweeping Advances). "
     "However, if the model is within 12\" of an eligible enemy unit at the start of its Assault phase and did not "
     "fire a Heavy weapon in the preceding Shooting phase, it must declare a Charge if able.", None,
     ["Rage (X)", "Fearless"]),
    ("Goreslick Siege-Ram", 15, "Fitted with serrated dozer-blades and pressurised blood-drains, the model gains "
     "Hammer of Wrath (2) resolved at Strength 8, AP 3, and may re-roll failed Dangerous Terrain tests.", None,
     ["Hammer of Wrath (X)"]),
    ("Berserker Overdrive Manifolds", 20, "Once per game, at the start of your Assault phase, you may overcharge this "
     "model's thermal reactor; until the end of that phase, add +1 to its Initiative and Attacks characteristics. At "
     "the end of that Assault phase, roll a D6: on a 1, the model suffers 1 unsaved Wound with no saves allowed as "
     "its cooling vents rupture.", None, []),
]
CAEDERE = ("Caedere Shock-Lances / Harvester Blades", 10, "Whenever an enemy unit fails a Morale check within 6\" of "
           "this model, or is reduced to below half its starting models in melee by this model, this model gains "
           "Hatred (Everything) until the end of the turn.", "we")
IRON_WARRIORS_UPGRADES = [
    ("Olympian Ablative Siege-Mantlets", 20, "Thick, bolted-on iron plates shield the walker's vulnerable leg joints "
     "and reactor housing. Enemy ranged attacks targeting this model subtract -1 from their Strength characteristic "
     "when resolving To Wound rolls against Blast or Barrage weapons, and the model gains Armoured Ceramite "
     "(preventing enemy weapons with Armourbane (Melta) from rolling an extra D6 at half range).", None, []),
    ("Iron-Fire Targeter-Cogitators", 15, "Linked directly into Perturabo's automated artillery grid, this model may "
     "re-roll To Hit rolls of 1 when firing Heavy or Ordnance weapons, and ignores negative Ballistic Skill modifiers "
     "caused by Night Fighting.", None, []),
    ("Expendable Vanguard Manifolds", 15, "The pilot is locked inside a welded-shut cockpit with over-pressurised "
     "fuel injectors. The model ignores the -1\" penalty to Run moves from Clumsy Hydraulic Actuators (it still "
     "suffers -1\" to Charge rolls and cannot make Sweeping Advances), and when reduced to 0 Wounds, its reactor "
     "explosion increases to Strength 9, AP 4 out to 8\" (or Strength 10, AP 3 out to 8\" for a Furibundus-Pattern).",
     None, []),
]


def imperial_upgrades(caedere):
    ups = [("High Techno-Arcana Chassis Upgrade", TECHNO_ARCANA, "mech"),
           ("Questoris Household Upgrade", QUESTORIS_UPGRADE, "mech or questoris"),
           ("XII Legion Chassis Upgrade", WORLD_EATERS_UPGRADES, "we"),
           ("IV Legion Chassis Upgrade", IRON_WARRIORS_UPGRADES, "iw")]
    return ups, [CAEDERE] if caedere else []


COMMON = [("Relic (X)", "Relic (2)"), ("Support Squad", None)]


def imperial_specs():
    lucifer_ups, lucifer_opts = imperial_upgrades(True)
    carapace = [("Havoc Launcher", 10, None), ("Dreadnought Extra Armour", 15, None),
                ("Protodreadnought Helical Targeting Array", 15, None), ("Carapace Phosphex Discharger", 15, "iw")]
    return [
        {"name": "Lucifer-Pattern Protodreadnought", "model": "Lucifer-Pattern Protodreadnought", "slot": "Elites",
         "type": "Armiger", "stats": ["7", "4", "4", "7", "7", "5", "3", "3", "8", "3+"], "max": 3,
         "unit_pts": 5, "model_pts": 120, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Arc-Reactor", None), ("Clumsy Hydraulic Actuators", None)],
         "arms": [("Arm Weapon (1)", lucifer_arm()), ("Arm Weapon (2)", lucifer_arm())],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)],
         "upgrades": lucifer_ups, "unit_options": lucifer_opts},
        {"name": "Furibundus-Pattern Protodreadnought", "model": "Furibundus-Pattern Protodreadnought",
         "slot": "Heavy Support", "type": "Armiger (Heavy)",
         "stats": ["6", "4", "4", "8", "8", "6", "2", "3", "8", "3+"], "max": 2, "unit_pts": 5, "model_pts": 175,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Dual-Core Reactor", None), ("Clumsy Hydraulic Actuators", None),
                            ("Siege-Breaker Chassis", None)],
         "arms": [("Arm Weapon (1)", furibundus_arm()), ("Arm Weapon (2)", furibundus_arm())],
         "carapace": [("Carapace Weapon", [("Carapace Phosphex Discharger", 15, None), ("Havoc Launcher", 10, None)], 1),
                      ("Carapace & Chassis Upgrades", [("Dreadnought Extra Armour", 15, None),
                                                       ("Protodreadnought Helical Targeting Array", 15, None)], None)],
         "upgrades": lucifer_ups, "unit_options": lucifer_opts},
        {"name": "Unification-Pattern Protodreadnought", "model": "Unification-Pattern Protodreadnought",
         "slot": "Heavy Support", "type": "Armiger (Heavy)",
         "stats": ["6", "3", "4", "7", "7", "6", "3", "2", "8", "3+"], "max": 2, "unit_pts": 5, "model_pts": 135,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Arc-Reactor", None), ("Clumsy Hydraulic Actuators", None),
                            ("Recoil-Braced Firing Stance", None)],
         "arms": [("Primary Gun Arm", unification_arm("primary")), ("Missile Pod Arm", unification_arm("missile"))],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)],
         "upgrades": imperial_upgrades(False)[0], "unit_options": []},
    ]


# ---- writing the Imperial units into the official files ------------------------------------------------------------

def catalogues():
    """(file, with Legiones Astartes (X), shows the Questoris upgrade's Troops slot)"""
    out = [(f, True, False) for f in sorted(glob.glob("2022 - LA - *.cat")) + ["Shattered Legions.cat"]]
    out += [("2022 - BG - Blackshields.cat", False, False), ("2022 - Mechanicum.cat", False, True),
            ("2022 - Questoris Household.cat", False, True), ("2022 - Imperialis Militia.cat", False, False)]
    return out


def root_link(f, unit, slot, legion, questoris):
    uid = unit.get("id")
    l = et.E("entryLink", id=mid(f, uid, "root"), name=unit.get("name"), hidden=False, collective=False, import_=False,
             targetId=uid, type="selectionEntry")
    if legion:
        el(el(l, "infoLinks"), "infoLink", id=mid(f, uid, "legion"), name=LEGIONES_ASTARTES[1], hidden=False,
           targetId=LEGIONES_ASTARTES[0], type="rule")
    if questoris:
        # the Bondsman-Rig moves the squadron to Troops and gives it the Line Sub-type
        rig = mid("imperial", "wargear", "Questoris Household Bondsman-Rig")
        troops = bc.SLOTS["Troops"][0]
        mods = el(l, "modifiers")
        for kind, value in (("remove", bc.SLOTS[slot][0][0]), ("add", troops[0]), ("set-primary", troops[0]),
                            ("add", LINE[0])):
            m = el(mods, "modifier", type=kind, field="category", value=value)
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid, childId=rig,
               shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    cats = el(l, "categoryLinks")
    for cid, cname, primary in bc.SLOTS[slot][:1]:
        el(cats, "categoryLink", id=mid(f, uid, "slot"), name=cname, hidden=False, targetId=cid, primary=primary)
    el(cats, "categoryLink", id=mid(f, uid, "unit"), name=bc.UNIT_CATEGORY[1], hidden=False,
       targetId=bc.UNIT_CATEGORY[0], primary=False)
    return l


def insert_top(text, container, elements):
    """Elements at the end of the catalogue's own (top-level) container."""
    m = list(re.finditer(rf"{re.escape(text.nl)}  </{container}>", text.s))
    if len(m) != 1:
        sys.exit(f"{text.path}: {len(m)} top-level {container}")
    i = m[0].start()
    text.s = text.s[:i] + "".join(text.nl + et.xml(e, 2).replace("\n", text.nl) for e in elements) + text.s[i:]


def main():
    lib = et.Text(LIBRARY)
    if "Lucifer-Pattern Protodreadnought" in lib.s:
        sys.exit(f"{LIBRARY} already has the Protodreadnoughts")
    entries, rules = index([LIBRARY, GST])
    ctx = Ctx("imperial", entries, rules)
    imperial_weapons(ctx)
    specs = imperial_specs()
    units = [unit_entry(ctx, s) for s in specs]
    insert_top(lib, "sharedSelectionEntries", ctx.new + units)
    lib.bump("catalogue")
    lib.save()
    print(f"{LIBRARY}: {len(units)} units, {len(ctx.new)} weapons and upgrades")
    for f, legion, questoris in catalogues():
        t = et.Text(f)
        insert_top(t, "entryLinks", [root_link(f, u, s["slot"], legion, questoris) for u, s in zip(units, specs)])
        t.bump("catalogue")
        t.save()
    print(f"root entries in {len(catalogues())} catalogues")


# ---- the Leagues of Votann, at build time --------------------------------------------------------------------------

VOID_ARMOUR = EXTRA_ARMOUR
INBUILT_VOTANN = [("Magma-cutter", 5, "Magma-cutter"), ("EtaCarn plasma gun", 10, "EtaCarn plasma gun"),
                  ("Graviton Gun", 15, "Graviton Gun"), ("Volkanite disintegrator", 15, "Volkanite disintegrator")]
LEAGUE_UPGRADES = [
    ("Ancestor-Linked Cogitators", 15, "When resolving shooting attacks or close-combat attacks against an enemy unit "
     "that has at least 1 Judgement Token, this model treats that enemy unit as having +1 additional Judgement Token "
     "(to a maximum of 2). In addition, this model may re-roll failed Morale and Pinning tests.",
     "league Greater Thurian League", []),
    ("Overcharged Hydraulic Rams", 20, "This model ignores the -1\" penalty to Charge distance rolls from Heavy "
     "Hydraulic Pistons (it still suffers the -1\" penalty to Run moves), and gains Hammer of Wrath (2) and Furious "
     "Charge (1) on any turn in which it successfully completes a Charge.", "league Kronus Hegemony",
     ["Hammer of Wrath (X)", "Furious Charge (X)"]),
    ("Void-Drift Thruster Vanes", 15, "This model gains the Scout and Move Through Cover special rules, and "
     "automatically passes all Dangerous Terrain tests.", "league Trans-Hyperian Alliance",
     ["Scout", "Move Through Cover"]),
    ("Ablative Bastion-Plates", 20, "This model reduces the Strength of all incoming ranged attacks from Strength 8 or "
     "higher by -1 (to a minimum of 7) when resolving To Wound rolls, and gains Feel No Pain (6+) (or improves an "
     "existing Feel No Pain (X) roll by +1, to a maximum of 4+).", "league Urani-Surtr Regulates",
     ["Feel No Pain (X)"]),
    ("Master-Forged Weavefield Capacitors", 25, "This model gains a 5+ Invulnerable Save against shooting attacks (if "
     "upgraded with Void-Hardened Extra Armour, its Invulnerable Save against melee attacks remains 6+). In addition, "
     "all Beam, Conversion, Magma, Plasma, and Volkanite ranged weapons equipped by this model add +4\" to their "
     "maximum range.", "league Ymyr Conglomerate", []),
]


def votann_weapons(ctx):
    """The Votann weapons the rigs name that the catalogue does not have, profiled as their Imperial counterparts."""
    weapon(ctx, "Gravis concussion gauntlet", [(None, "-", "9", "2", "Melee, Brutal (2), Concussive (1)")])
    weapon(ctx, "Gravis plasma axe", [(None, "-", "10", "2", "Melee, Armourbane (Melee), Murderous Strike (5+)")])
    weapon(ctx, "Cthonian mining drill", [(None, "-", "12", "2", "Melee, Armourbane (Melee)")])
    weapon(ctx, "Heavy seismic drill", [(None, "-", "12", "2", "Melee, Armourbane (Melee)")])
    weapon(ctx, "Cthonian siege claw", [(None, "-", "10", "2", "Melee, Brutal (3)")])
    weapon(ctx, "Magma-cutter", [(None, "Template", "5", "4", "Assault 1")])
    weapon(ctx, "Heavy magma-cutter", [(None, "Template", "5", "4", "Assault 1")])
    weapon(ctx, "Heavy bolt cannon", [(None, '48"', "5", "4", "Heavy 6, Rupture (6+)")])
    weapon(ctx, "Twin-linked heavy bolt cannon", [(None, '48"', "5", "4", "Heavy 6, Rupture (6+), Twin-linked")])
    weapon(ctx, "Magna-rail cannon", [(None, '48"', "9", "2", "Heavy 2, Sunder")])
    weapon(ctx, "Twin-linked autoch-pattern bolter", [(None, '24"', "4", "5", "Rapid Fire, Rupture (6+), Twin-linked")])
    weapon(ctx, "Twin-linked L7 missile pod", [
        ("Twin-linked L7 missile pod - Frag", '48"', "4", "6", 'Heavy 1, Blast (3"), Pinning, Twin-linked'),
        ("Twin-linked L7 missile pod - Krak", '48"', "8", "3", "Heavy 1, Twin-linked")])
    weapon(ctx, "Heavy graviton bombard", [(None, '18"', "†", "4", 'Heavy 1, Large Blast (5"), Graviton Collapse, '
                                                                   "Torsion Crusher, Ignores Cover, Concussive (1), "
                                                                   "Haywire")])
    weapon(ctx, "Twin-linked volkanite disintegrator", [(None, '24"', "5", "4", "Assault 2, Breaching (6+), Shred, "
                                                                                "Twin-linked")])
    weapon(ctx, "Subterranean mole-mortar", [(None, '24"', "6", "4", 'Heavy 1, Barrage, Large Blast (5"), Pinning, '
                                                                     "One Shot")])
    wargear(ctx, "Void-Hardened Extra Armour", VOID_ARMOUR)
    wargear(ctx, "Pan Spectral Targeting Array", TARGETING, ["Skyfire", "Interceptor"])


def votann_specs():
    def gun(n, c):
        return (n, c, [n], None, None)

    ancestor = [("Gravis concussion gauntlet", 0, ["Gravis concussion gauntlet"],
                 inbuilt("Autoch-pattern combi-bolter", INBUILT_VOTANN), None),
                ("Gravis plasma axe", 10, ["Gravis plasma axe"], inbuilt("Autoch-pattern combi-bolter", INBUILT_VOTANN),
                 None),
                gun("HYLas rotary cannon", 5), gun("Heavy bolt cannon", 10), gun("L7 missile launcher", 15),
                gun("Magna-rail cannon", 15), gun("Graviton blast cannon", 15), gun("SP conversion beamer", 20),
                ("Cthonian mining drill with in-built heavy magma-cutter", 15,
                 ["Cthonian mining drill", "Heavy magma-cutter"], None, None)]
    strider = [("Cthonian siege claw", 0, ["Cthonian siege claw"],
                inbuilt("Twin-linked autoch-pattern bolter", INBUILT_VOTANN), None),
               ("Heavy seismic drill", 10, ["Heavy seismic drill"],
                inbuilt("Twin-linked autoch-pattern bolter", INBUILT_VOTANN), None),
               gun("Twin-linked HYLas rotary cannon", 10), gun("Twin-linked heavy bolt cannon", 15),
               gun("Twin-linked L7 missile pod", 25), gun("Twin-linked magna-rail cannon", 25),
               gun("Heavy graviton bombard", 25), gun("Heavy volkanite disintegrator", 25),
               gun("SP heavy conversion beamer", 20)]

    def ballistic(base):
        if base == "primary":
            costs = [("HYLas rotary cannon", 0), ("Heavy bolt cannon", 5), ("EtaCarn plasma beamer", 10),
                     ("Twin-linked volkanite disintegrator", 10), ("L7 missile launcher", 10), ("Magna-rail cannon", 15)]
        else:
            costs = [("L7 missile launcher", 0), ("HYLas rotary cannon", -10), ("Heavy bolt cannon", -5),
                     ("EtaCarn plasma beamer", 0), ("Twin-linked volkanite disintegrator", 0), ("Magna-rail cannon", 5)]
        return [gun(n, c) for n, c in costs]

    carapace = [("MATR autocannon", 10, None), ("Void-Hardened Extra Armour", 15, None),
                ("Pan Spectral Targeting Array", 15, None)]
    common = [("Eye of the Ancestors", None), ("League (X)", None)] + COMMON
    leagues = [("League Upgrade", LEAGUE_UPGRADES, None)]
    return [
        {"name": "Ironkin Ancestor-Rig", "model": "Ironkin Ancestor-Rig", "slot": "Elites", "type": "Armiger",
         "stats": ["7", "4", "4", "7", "7", "5", "3", "3", "8", "3+"], "max": 3, "unit_pts": 5, "model_pts": 120,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Darkstar-Core", None), ("Heavy Hydraulic Pistons", None)],
         "arms": [("Arm Weapon (1)", ancestor), ("Arm Weapon (2)", ancestor)],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)], "upgrades": leagues},
        {"name": "Cthonian Siege-Strider", "model": "Cthonian Siege-Strider", "slot": "Heavy Support",
         "type": "Armiger (Heavy)", "stats": ["6", "4", "4", "8", "8", "6", "2", "3", "8", "3+"], "max": 2,
         "unit_pts": 5, "model_pts": 175, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Dual-Core Reactor", None), ("Heavy Hydraulic Pistons", None),
                            ("Subterranean Siege-Chassis", None)],
         "arms": [("Arm Weapon (1)", strider), ("Arm Weapon (2)", strider)],
         "carapace": [("Carapace Weapon", [("Subterranean mole-mortar", 15, None), ("MATR autocannon", 10, None)], 1),
                      ("Carapace & Chassis Upgrades", carapace[1:], None)], "upgrades": leagues},
        {"name": "Brôkhyr Ballistic Strider", "model": "Brôkhyr Ballistic Strider", "slot": "Heavy Support",
         "type": "Armiger (Heavy)", "stats": ["6", "3", "4", "7", "7", "6", "3", "2", "8", "3+"], "max": 2,
         "unit_pts": 5, "model_pts": 135, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Darkstar-Core", None), ("Heavy Hydraulic Pistons", None),
                            ("Recoil-Braced Firing Stance", None)],
         "arms": [("Primary Gun Arm", ballistic("primary")), ("Missile Pod Arm", ballistic("missile"))],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)], "upgrades": leagues},
    ]


def apply(b):
    """build_catalogue.py's hook for the Leagues of Votann: the rigs, their weapons and their root entries."""
    entries = {norm(e.get("name")): e.get("id") for e in b.shared_entries.findall("selectionEntry")}
    rules = {norm(r.get("name")): r.get("id") for r in b.shared_rules.findall("rule")}
    gst_entries, gst_rules = index([GST])
    for k, v in gst_entries.items():
        entries.setdefault(k, v)
    for k, v in gst_rules.items():
        rules.setdefault(k, v)
    ctx = Ctx("votann", entries, rules)
    votann_weapons(ctx)
    specs = votann_specs()
    units = [unit_entry(ctx, s) for s in specs]
    b.shared_entries.extend(ctx.new + units)
    links = b.root.find("entryLinks")
    for u, s in zip(units, specs):
        l = el(links, "entryLink", import_=True, name=u.get("name"), hidden=False, id=mid("votann", u.get("id"), "root"),
               type="selectionEntry", targetId=u.get("id"))
        cats = el(l, "categoryLinks")
        cid, cname, _ = bc.SLOTS[s["slot"]][0]
        el(cats, "categoryLink", targetId=cid, id=mid("votann", u.get("id"), "slot"), primary=True, name=cname)
        el(cats, "categoryLink", targetId=bc.UNIT_CATEGORY[0], id=mid("votann", u.get("id"), "unit"), primary=False,
           name=bc.UNIT_CATEGORY[1])


if __name__ == "__main__":
    main()
