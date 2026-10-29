#!/usr/bin/env python3
"""Add the Liber Imperatus Sisters of Silence expansion to the official Sisters of Silence catalogue.

usage: python3 homebrew/add_sisters_of_silence.py

The doc (homebrew/source/sisters-of-silence.md, from the Claude Doc "Sisters of Silence Horus Heresy 2.0 - Homebrew
Conversion") is read by build_catalogue.py's Builder, which turns its datasheets into unit entries. Those units are
then moved into 2022 - LI - Sisters Of Silence.cat as text, so the official file keeps its own formatting:

- every weapon, piece of wargear and rule the official catalogue, the libraries it imports or the game system
  already has is linked there (Vratine Bolter, Execution Blade, Silent Sisterhood (X)); only what exists nowhere it
  can reach (Indictor Axe, Iliastus Accelerator Cannon Arrays, Enhanced Arachnus Blaze Cannon) is added;
- each unit takes its Silent Sisterhood Chamber the way the official units do (the Chamber's category, which the
  Chamber limits count, and its required Silent Sisterhood (Chamber of X) entry) and the Anathema Sub-type;
- root entries, Dedicated Transports (the Silent Sisterhood Grav-Rhino and Rhino for the official Cadres too), the
  two-pistol swaps, Sikari Dar's Warlord Trait, Fast Attack and Chamber allowances, and the doc's extra options on
  official units (Knight Abyssal, Knight Centura, Questora, Raptora, Eradicator, Knight Vestal, Subjugator) are
  written as the doc gives them.

It refuses to run on a catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, child, el, norm  # noqa: E402
from expansion_tools import (E, Text, any_entry, deep, find_in, link_el, link_named, mid, model_entry,  # noqa: E402
                             models_over, official_units, transport_group)

CAT = "2022 - LI - Sisters Of Silence.cat"
GST = et.GST
DOC = "homebrew/source/sisters-of-silence.md"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]  # the libraries the catalogue imports
FACTION = "Sisters of Silence"
NS = et.NS
et.configure(CAT, LIBS, DOC, FACTION, "sisters of silence expansion")

SILENT_SISTERHOOD_RULE = "1d8d-3038-9267-6f1b"
CHAMBERS = {  # Chamber -> (its category, its Silent Sisterhood (Chamber of X) entry)
    "Judgement": ("b71a-371d-4401-9dc0", "ade4-0f3a-c307-9dc2"),
    "Oblivion": ("a7e3-4559-7267-8bf6", "7856-71cb-a1fb-bc43"),
    "Vigilance": ("b6d7-6924-37fb-dd32", "7b50-6b5d-e6f9-420b"),
}
CHAMBER_LIMITS = {"Judgement": "07d4-6a38-eebd-9b05", "Oblivion": "9794-28b4-6125-880c"}
# an HQ of these Chambers lets the Detachment take four units of its Chamber
CHAMBER_HQ = {"Judgement": ("a9b6-f66f-e8ee-553e", "Judgement HQ"), "Oblivion": ("b760-8313-847f-1afa", "Obivion HQ")}
# Sub-types the official units carry as categories, beyond those build_catalogue.py gives every list
SUB_TYPES = {"Anathema": ("7e5d-d73e-8ff4-7345", "Anathema Sub-type"), "Light": ("bff2-ae16-74a8-8712", "Light Sub-type"),
             "Automata": ("d8ab-8e21-e193-63ba", "Automata Unit Type"), "Hover": ("3a7a-8bb7-b0d3-e2e7", "Hover Sub-type"),
             "Reinforced": ("9b0d-738c-10e4-4ec1", "Reinforced Sub-type")}
SUB_TYPE_RULES = {"Anathema": ("e2d9-fe0d-1717-3a37", "Anathema Sub-type"),
                  "Sycophantica": ("686b-5574-5cfd-f24a", "Sycophantica Unit Sub-type")}
KHARON, TERMITE = "16fa-53b2-b57b-ec25", "b3bd-c23c-aca6-f883"
CRUSADE_FAST_ATTACK = "5474-d2f8-4d1d-66be"  # the Crusade chart's Fast Attack maximum
PURSUER = "db4a-57f3-f451-da91"


def dress_unit(unit, ds):
    """Chamber, Sub-type categories and rules, the way the official units have them."""
    uid = unit.get("id")
    cats = et.drop_unit_category(unit)
    chamber = next((m.group(1) for r in ds["rules"] for m in [re.match(r"Silent Sisterhood \(Chamber of (\w+)\)", r)] if m), None)
    if chamber:
        cat, entry = CHAMBERS[chamber]
        el(cats, "categoryLink", targetId=cat, id=mid(uid, "chamber"), primary=False,
           name=f"Silent Sisterhood (Chamber of {chamber})")
        link = el(child(unit, "entryLinks"), "entryLink", import_=True, name=f"Silent Sisterhood (Chamber of {chamber})",
                  hidden=False, id=mid(uid, "chamber link"), type="selectionEntry", targetId=entry)
        add_constraint(link, "min", 1, mid(uid, "chamber min"))
        if ds["slot"] == "HQ" and chamber in CHAMBER_HQ:
            el(cats, "categoryLink", targetId=CHAMBER_HQ[chamber][0], id=mid(uid, "chamber hq"), primary=False,
               name=CHAMBER_HQ[chamber][1])
    et.add_types(unit, SUB_TYPES, SUB_TYPE_RULES)


# ---- the doc's special cases, on the Builder's units before they move


def two_pistols(b, me, singles_group, pair_group, pair_names):
    """A model with two Bolt Pistols: a group of exactly two holding the pistols and the one-pistol swaps, and a
    group of at most one for the swaps of both pistols, which empties the first."""
    pistol = b.find_weapon("Bolt Pistol")[0]
    gs = child(me, "selectionEntryGroups")
    if singles_group is None:
        singles_group = el(gs, "selectionEntryGroup", name="Bolt Pistols", hidden=False, id=mid(me.get("id"), "pistols"))
        add_constraint(singles_group, "min", 2, mid(me.get("id"), "pistols min"))
        add_constraint(singles_group, "max", 2, mid(me.get("id"), "pistols max"))
    singles_group.set("name", "Bolt Pistols")
    old = link_named(singles_group, "Two Bolt Pistols")
    if old is not None:
        singles_group.find("entryLinks").remove(old)
    link = el(child(singles_group, "entryLinks"), "entryLink", import_=True, name="Bolt Pistol", hidden=False,
              id=mid(me.get("id"), "pistol"), type="selectionEntry", targetId=pistol)
    add_constraint(link, "max", 2, mid(me.get("id"), "pistol max"))
    singles_group.set("defaultSelectionEntryId", link.get("id"))
    if pair_group is None:
        pair_group = el(gs, "selectionEntryGroup", name="Exchange both Bolt Pistols", hidden=False,
                        id=mid(me.get("id"), "pair"))
    pair_group.set("name", "Exchange both Bolt Pistols")
    pair_group.attrib.pop("defaultSelectionEntryId", None)
    for c in list(child(pair_group, "constraints")):
        pair_group.find("constraints").remove(c)
    add_constraint(pair_group, "max", 1, mid(me.get("id"), "pair max"))
    for l in list(child(singles_group, "entryLinks")) + list(child(pair_group, "entryLinks")):
        if l.get("name") in pair_names:  # both pistols for one of these
            (singles_group.find("entryLinks") if l in singles_group.find("entryLinks") else pair_group.find("entryLinks")).remove(l)
            pair_group.find("entryLinks").append(l)
            for c in l.findall("constraints/constraint[@type='max']"):
                c.set("value", "1")
        elif l.get("name") == "Two Bolt Pistols":
            pair_group.find("entryLinks").remove(l)
    clear_when_any(singles_group, [l.get("targetId") for l in pair_group.findall("entryLinks/entryLink")], me.get("id"))


def clear_when_any(group, targets, scope):
    et.clear_when_any(group, targets, scope)


def special_cases(b, entries, ds_by_name):
    unit = lambda n: entries[b.units[n]]
    groups = lambda me: {g.get("name"): g for g in me.findall("selectionEntryGroups/selectionEntryGroup")}

    # Knight Ensign: "either or both Bolt Pistols" for a pistol each, "both Bolt Pistols" for one weapon
    me = model_entry(unit("Knight Ensign Covenant"), "Knight Ensign")
    g = groups(me)["Exchange Bolt Pistols"]
    two_pistols(b, me, g, None, {"Bolter", "Magna Combi-Weapon", "Minor Combi-Weapon", "Vratine Bolter"})

    # Perditors: "its two Bolt Pistols" for one of a pair's swaps; for every five models, one Perditor swaps one
    # Bolt Pistol for a heavy weapon
    for name in ("Perditor", "Perditor Mistress"):
        me = model_entry(unit("Perditor Cadre"), name)
        gs = groups(me)
        two_pistols(b, me, gs.get("Exchange Bolt Pistol"), gs["Exchange two Bolt Pistols"],
                    {"Two Hand Flamers", "Two Needle Pistols", "Vratine Bolter", "Vratine Grenade Launcher"})

    # Caedecii: "One model may exchange ... for: Sinistrae Magnificat (one per unit)" in either weapon's swap; "Any
    # model without a Sinistrae Magnificat may take one of" a Spiculus Bolt Launcher or Vratine Missile Launcher
    cu = unit("Caedecius Exoframe Cadre")
    uid = cu.get("id")
    me = model_entry(cu, "Caedecii Exoframe")
    gs = me.find("selectionEntryGroups")
    either = next(g for g in gs if " or " in g.get("name", ""))  # "its ... Vratine Bolter or Vratine Bolt Cannon for"
    gs.remove(either)
    sub = next(g for g in either.iter("selectionEntryGroup") if g is not either)
    subs = []
    for g in [g for g in gs if g.get("name", "").startswith("Exchange ")]:
        copy = deep(sub)
        for x in copy.iter():
            if x.get("id"):
                x.set("id", mid(g.get("id"), x.get("id")))
        for x in copy.iter():  # its constraints' modifiers follow the new ids
            if x.get("field") and x.get("field") not in ("selections", "hidden", bc.PTS):
                x.set("field", mid(g.get("id"), x.get("field")))
        child(g, "selectionEntryGroups").append(copy)
        subs.append(copy)
    sinistrae = next(l.get("targetId") for g in subs for l in g.iter("entryLink") if l.get("name") == "Sinistrae Magnificat")
    for g in subs:
        for other in subs:
            if other is not g:
                c = g.find("constraints/constraint[@type='max']")
                mod = el(child(g, "modifiers"), "modifier", type="decrement", field=c.get("id"), value=1)
                el(el(mod, "repeats"), "repeat", field="selections", scope=uid, childId=other.get("id"), value=1,
                   percentValue=False, shared=True, includeChildSelections=True, includeChildForces=False, repeats=1,
                   roundUp=False)
    opts = next(g for g in cu.findall("selectionEntryGroups/selectionEntryGroup")
                if any(l.get("name") == "Spiculus Bolt Launcher" for l in g.iter("entryLink")))
    for holder in [opts] + opts.findall("entryLinks/entryLink"):
        for c in holder.findall("constraints/constraint[@type='max']"):
            mod = el(child(holder, "modifiers"), "modifier", type="decrement", field=c.get("id"), value=1)
            el(el(mod, "repeats"), "repeat", field="selections", scope=uid, childId=sinistrae, value=1,
               percentValue=False, shared=True, includeChildSelections=True, includeChildForces=False, repeats=1,
               roundUp=False)

    # The Missile Launcher option is the game system's Missile Launcher, its Psyk-Out and Rad Missiles and a
    # Suspensor Web
    ml = b.find_weapon("Missile Launcher")
    gst_ml = official_index_cache["entry"].get("missile launcher")
    for e in entries.values():
        if e.get("name") == "Missile Launcher" and e.find("entryLinks") is not None and gst_ml:
            l = el(e.find("entryLinks"), "entryLink", import_=True, name="Missile Launcher", hidden=False,
                   id=mid(e.get("id"), "gst missile launcher"), type="selectionEntry", targetId=gst_ml)
            add_constraint(l, "min", 1, mid(l.get("id"), "min"))
            add_constraint(l, "max", 1, mid(l.get("id"), "max"))

    # Sikari Dar: Eater of Daemons, and the Warlord whenever she is in the Primary Detachment
    su = unit("Sikari Dar")
    me = model_entry(su, "Sikari Dar")
    trait = ("If Sikari Dar is in the army's Primary Detachment she must be the army's Warlord, and as Warlord she "
             "automatically has this trait and no other. The first time any enemy unit with the Corrupted, Daemon or "
             "Psyker Sub-type comes within 12\" of her for any reason, it must take a Leadership test. If it fails, all "
             "its models suffer -1 WS, BS and Initiative until the end of the next Game Turn. Each unit only tests "
             "once, but any number of units may trigger it.")
    p = et.warlord_trait(me, "Eater of Daemons", trait, me.get("id"))
    p.set("id", mid(me.get("id"), "trait"))
    wl = link_named(me, "Warlord")
    if wl is not None:
        cmin = add_constraint(wl, "min", 0, mid(wl.get("id"), "primary"))
        mod = el(child(wl, "modifiers"), "modifier", type="set", field=cmin, value=1)
        el(el(mod, "conditions"), "condition", type="notInstanceOf", value=0, field="selections", scope="ancestor",
           childId=bc.ALLIED_DETACHMENT, shared=True, includeChildSelections=True, includeChildForces=False,
           percentValue=False)


official_index_cache = {}


def existing_units(cat, b):
    """The doc's extra options on official units."""
    units = official_units()
    c = NS["cat"]
    tag = lambda x, t: x.tag == c + t
    axe = b.weapons[norm("Indictor Axe")]

    # Knight Abyssal and Knight Centura: "may exchange her Execution Blade and/or Bolt Pistol for: Indictor Axe"
    for name in ("Knight Abyssal", "Knight Centura"):
        u = units[name]
        for gname in ("1) Melee Weapon", "2) Ranged Weapon"):
            g = find_in(u, lambda x: tag(x, "selectionEntryGroup") and x.get("name") == gname)
            cat.add(g.get("id"), "entryLinks", [link_el("Indictor Axe", axe, g.get("id"), mx=1, pts=0)])

    # Questora Cadre: "Any model may exchange its Vratine Bolter for one of" (priced per model, like its other swaps)
    u = units["Questora Cadre"]
    g = find_in(u, lambda x: tag(x, "selectionEntryGroup") and x.get("name", "").startswith("Any model in the unit may exchange"))
    cat.add(g.get("id"), "entryLinks", [link_el(n, any_entry(n), g.get("id"), pts=p, per_model_of=u.get("id"))
                                        for n, p in (("Magna Combi-Weapon", 10), ("Meltagun", 15),
                                                     ("Minor Combi-Weapon", 5), ("Plasma Gun", 10))])

    # Raptora Cadre: "Any model may exchange its Execution Blade for one of"
    u = units["Raptora Cadre"]
    g = find_in(u, lambda x: tag(x, "selectionEntryGroup") and x.get("name", "").startswith("May exchange their Execution blades"))
    cat.add(g.get("id"), "entryLinks", [link_el("Charnabal Weapon", any_entry("Charnabal Weapon"), g.get("id"), mx=1, pts=0),
                                        link_el("Indictor Axe", axe, g.get("id"), mx=1, pts=0),
                                        link_el("Power Weapon", any_entry("Power Weapon"), g.get("id"), mx=1, pts=0)])

    # Eradicator Cadre: "Any model may exchange its Vratine Bolter for: Assault Needler"
    u = units["Eradicator Cadre"]
    for g in [x for x in u.iter(c + "selectionEntryGroup") if x.get("name", "").startswith("May exchange their Vratine bolter")]:
        cat.add(g.get("id"), "entryLinks", [link_el("Assault Needler", any_entry("Assault Needler"), g.get("id"), mx=1, pts=5)])

    # Knight Vestal Covenant: "Any Knight Vestal may exchange her Vratine Armour for: Artificer Armour"
    u = units["Knight Vestal Covenant"]
    me = find_in(u, lambda x: tag(x, "selectionEntry") and x.get("name") == "Knight Vestal")
    armour = find_in(me, lambda x: tag(x, "entryLink") and x.get("name") == "Vratine Armour")
    g = E("selectionEntryGroup", id=mid(me.get("id"), "armour"), name="3) Armour", hidden=False, collective=False,
          import_=True, defaultSelectionEntryId=mid(me.get("id"), "armour", "Vratine Armour"))
    add_constraint(g, "min", 1, mid(me.get("id"), "armour min"))
    add_constraint(g, "max", 1, mid(me.get("id"), "armour max"))
    el(g, "entryLinks").extend([link_el("Vratine Armour", armour.get("targetId"), mid(me.get("id"), "armour"), mx=1),
                                link_el("Artificer Armour", any_entry("Artificer Armour"), mid(me.get("id"), "armour"),
                                        mx=1, pts=10)])
    start, end, _, _ = cat.block(armour.get("id"))
    line = cat.s.rfind("\n", 0, start) + 1
    cat.s = cat.s[:line] + cat.s[cat.s.index("\n", end) + 1:]  # the armour is now the group's default
    cat.add(me.get("id"), "selectionEntryGroups", [g])

    # Subjugator Cadre: "Any model may take one of: Charnabal Weapon, Power Weapon"
    u = units["Subjugator Cadre"]
    for mname in ("Subjugator", "Subjugator Mistress"):
        me = find_in(u, lambda x: tag(x, "selectionEntry") and x.get("name") == mname)
        g = E("selectionEntryGroup", id=mid(me.get("id"), "take"), name="May take one of", hidden=False,
              collective=False, import_=True)
        add_constraint(g, "max", 1, mid(me.get("id"), "take max"))
        el(g, "entryLinks").extend([link_el(n, any_entry(n), mid(me.get("id"), "take"), mx=1, pts=10)
                                    for n in ("Charnabal Weapon", "Power Weapon")])
        cat.add(me.get("id"), "selectionEntryGroups", [g])

    # The official Cadres that may take a Silent Sisterhood Grav-Rhino or Rhino, if they fit (Transport Capacity 12)
    for name in ("Eradicator Cadre", "Expurgator Cadre", "Firebrand Cadre", "Oblivion Knights", "Prosecutor Cadre",
                 "Pursuer Cadre", "Questora Cadre", "Raptora Cadre", "Sanctioner Cadre", "Vigilator Cadre"):
        u = units[name]
        uid = u.get("id")
        kharon = find_in(u, lambda x: tag(x, "entryLink") and x.get("targetId") == KHARON)
        rhinos = []
        for tname in ("Silent Sisterhood Grav-Rhino Transport", "Silent Sisterhood Rhino Transport"):
            l = link_el(tname, b.units[tname], mid(uid, "rhino"), mx=1)
            models_over(l, uid, 12, "rhino")
            rhinos.append(l)
        group_parent = next((p for p in u.iter(c + "selectionEntryGroup")
                             if any(x.get("id") == kharon.get("id") for x in p.iter(c + "entryLink"))), None)
        if group_parent is not None:  # Raptora: "2) Dedicated Transport", one of
            cat.add(group_parent.get("id"), "entryLinks", rhinos)
            continue
        g = E("selectionEntryGroup", id=mid(uid, "rhino group"), name="Dedicated Transport (Silent Sisterhood Rhinos)",
              hidden=False, collective=False, import_=True)
        gmax = add_constraint(g, "max", 1, mid(uid, "rhino group max"))
        el(g, "entryLinks").extend(rhinos)
        # the Kharon Pattern Acquisitor or a Rhino, not both
        mod = el(el(g, "modifiers"), "modifier", type="set", field=gmax, value=0)
        el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid, childId=KHARON,
           shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        cat.add(uid, "selectionEntryGroups", [g])
        kmax = kharon.find(f"{c}constraints/{c}constraint[@type='max']").get("id")
        mod = E("modifier", type="set", field=kmax, value=0)
        cg = el(el(mod, "conditionGroups"), "conditionGroup", type="or")
        for l in rhinos:
            el(child(cg, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid,
               childId=l.get("targetId"), shared=True, includeChildSelections=True, includeChildForces=False,
               percentValue=False)
        cat.add(kharon.get("id"), "modifiers", [mod])


def chamber_allowances(cat, gst, sikari):
    """Sikari Dar: up to two extra Fast Attack choices, which must be Pursuer Cadres, outside the Chamber limits."""
    for i in (1, 2):
        mod = E("modifier", type="increment", field=CHAMBER_LIMITS["Oblivion"], value=1)
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="and"), "conditions")
        el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=sikari, shared=True,
           includeChildSelections=True, includeChildForces=False, percentValue=False)
        el(conds, "condition", type="atLeast", value=i, field="selections", scope="force", childId=PURSUER, shared=True,
           includeChildSelections=True, includeChildForces=False, percentValue=False)
        cat.add(CHAMBERS["Oblivion"][0], "modifiers", [mod])
        mod = deep(mod)
        mod.set("field", CRUSADE_FAST_ATTACK)
        gst.add(gst_fast_attack_link(gst), "modifiers", [mod])


def gst_fast_attack_link(gst):
    i = gst.s.index(f'id="{CRUSADE_FAST_ATTACK}"')
    j = gst.s.rfind("<categoryLink ", 0, i)
    return re.search(r'id="([^"]+)"', gst.s[j:]).group(1)


def main():
    cat = Text(CAT)
    if mid("unit", "done") in cat.s or 'name="Sikari Dar"' in cat.s:
        sys.exit(f"{CAT} already has the Sisters of Silence expansion")
    official_index_cache.update(et.official_index())
    b, root = et.build()
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    ds_by_name = {ds["name"]: ds for ds in b.datasheets}
    special_cases(b, entries, ds_by_name)
    # the Builder's own "Dedicated Transport" picks knew only the doc's transports
    grav, rhino = b.units["Silent Sisterhood Grav-Rhino Transport"], b.units["Silent Sisterhood Rhino Transport"]
    harness = b.find_upgrade("Venatari Jump Harnesses") or b.upgrades.get(norm("Venatari Jump Harnesses"))
    transport_group(entries[b.units["Indictor Cadre"]], [("Kharon Pattern Acquistor", KHARON, 5, None)], "dt")
    transport_group(entries[b.units["Perditor Cadre"]],
                    [("Kharon Pattern Acquistor", KHARON, None, harness),
                     ("Silent Sisterhood Grav-Rhino Transport", grav, 10, harness),
                     ("Silent Sisterhood Rhino Transport", rhino, 10, harness),
                     ("Termite Assault Drill", TERMITE, 10, harness)], "dt")
    transport_group(entries[b.units["Shrike Cadre"]],
                    [("Kharon Pattern Acquistor", KHARON, None, None),
                     ("Silent Sisterhood Grav-Rhino Transport", grav, 10, None),
                     ("Silent Sisterhood Rhino Transport", rhino, 10, None)], "dt")
    for e in entries.values():
        # "Missile Launcher" in the doc's armoury is only its Psyk-Out and Rad Missiles: kept as their own entry
        # beside the game system's Missile Launcher
        if e.get("name") == "Missile Launcher" and e.find("profiles") is not None:
            e.set("name", "Psyk-Out and Rad Missiles")
        if e.get("name") == "Nightfall (Sikari Dar)":
            et.rename(root, e, "Nightfall")
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, official_index_cache)
    roots = []
    for u in units:
        ds = next(d for d in b.datasheets if b.units[d["name"]] == u.get("id"))
        dress_unit(u, ds)
        if ds["slot"] != "Dedicated Transports":
            roots.append(et.root_link(u, ds))

    gst = Text(GST)
    existing_units(cat, b)
    chamber_allowances(cat, gst, b.units["Sikari Dar"])
    cat.add_top("entryLinks", roots)
    cat.add_top("sharedSelectionEntries", units + keep_entries)
    if keep_groups:
        cat.add_top("sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        cat.add_top("sharedRules", keep_rules)
    cat.bump("catalogue")
    gst.bump("gameSystem")
    cat.save()
    gst.save()
    print(f"{CAT}: {len(units)} units, {len(keep_entries)} entries, {len(keep_groups)} groups, {len(keep_rules)} rules added")


if __name__ == "__main__":
    main()
