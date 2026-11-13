"""Grey Knights: the official 2.0 units the doc's "Units to take from the official 2.0 books" table names, called by
build_catalogue.py for that faction.

The units link the Legions Astartes library's own entries, so their profiles, wargear and options stay the
official ones. Each gains the doc's Grey Knights rules and pays for them per model:

- Dreadnoughts (Castra Ferrum, the 2.0 Mk IV-pattern Legion Dreadnought, and Contemptor) are piloted by Grey
  Knights: Psyker sub-type, Brotherhood of Psykers, Legiones Astartes (Grey Knights), Brotherhood (X) and The
  Aegis, +25 points per Dreadnought.
- Land Raiders (Proteus Carrier and Phobos) and the Rhino: Brotherhood (X), The Aegis and Legiones Astartes (Grey
  Knights), +10 points per Land Raider and +5 points per Rhino. The Rhino is the Dedicated Transport of the units whose datasheet offers one.

2.0 has no Razorback, so the doc's "Rhino or Razorback" is the Rhino.

Brotherhood of Psykers gives the Dreadnoughts the Psyker sub-type only (Liber Daemonicus): they know no powers.
A Dreadnought Talon may take a Teleport Harness (the doc's wargear: Deep Strike) for +40 points per Dreadnought,
and the Teleport Harness links the game system's Deep Strike rule.

Grey Knights take only their own six Rites of War; gk_rites adds the slots, Line, Support Squad, compulsory-Troops,
ban and Teleport Assault effects the builder's Rite reading misses for their wording.

The Rites of War that bar these kinds of unit bar the official ones too: Purifier Crusade (no Land Raiders) hides
the official Land Raiders, and Teleport Assault (no Dedicated Transports) hides the Rhino.

Every model with Master of the Legion (but the Grand Master in Nemesis Dreadknight) may take a Brotherhood
Command Squad, Terminator Command Squad or Tartaros Command Squad as a Retinue (no Force Organisation slot), as an official
Legion leader takes a Command Squad; the Aegis Captain may take an Aegis Bastion Squad instead.

The 0-1 Purifier Bladeguard Squad has no limit in a Detachment whose Brotherhood is the 8th.

Characters bound to a Brotherhood (Stern, Voldus and the founding Grand Masters) are an error in a Detachment of
another Brotherhood.

Grey Knights are always Loyalist: a force that picks the Traitor allegiance may not take the Grey Knights army
entry (BattleScribe reports it as over its limit)."""
import re

from build_catalogue import PTS, SLOTS, TYPE_CATEGORIES, UNIT_CATEGORY, add_constraint, child, el, make_id

LIBRARY = ("6393-649c-7213-a327", "Legions Astartes")
# (shown name, Legions Astartes entry, points per model, the entries that are its models). A Proteus Carrier
# Squadron's tanks (a Proteus Carrier or a Phobos) are upgrades rather than models, so each is counted by its id.
DREADNOUGHTS = [("Castra Ferrum Dreadnought Talon", "daf7-b23b-5474-5836", 25, ["5524-7631-a4d9-9cf9"]),
                ("Contemptor Dreadnought Talon", "d664-5692-cd41-f9be", 25, ["b9fd-2c7d-ab6a-89af"])]
LAND_RAIDERS = [("Land Raider Proteus Carrier Squadron", "b6cd-dd1a-6b2c-41d6", 10,
                 ["c123-bdc6-a6ba-79a2", "048e-67cc-d24d-9f46"]),
                ("Land Raider Phobos Squadron", "681a-7426-96af-caac", 10, ["8bf3-9b8d-578a-38f1"])]
RHINO = ("Rhino Transport", "03f1-8ed9-9867-8d18", 5)
DREADNOUGHT_POWERS = []  # Brotherhood of Psykers grants no powers
DEEP_STRIKE = "f1e1-986f-c783-ca9e"  # the game system's Deep Strike rule
TRAITOR = "f9c0-0c5a-3e24-58c7"  # the game system's Traitor allegiance entry
HARNESS_POINTS = 40  # per Dreadnought
TRANSPORTED = ["Purifier Squad", "Strike Squad", "Purgation Squad"]  # "may take a Rhino or Razorback"


def rule_id(b, name):
    r = b.shared_rules.find(f"rule[@name='{name}']")
    return r.get("id")


def grey_knights_rules(b, e, key, psyker):
    names = (["Brotherhood of Psykers"] if psyker else []) + ["Brotherhood (X)", "The Aegis",
                                                             "Legiones Astartes (Grey Knights)"]
    for n in names:
        el(child(e, "infoLinks"), "infoLink", name=n, id=make_id(key, "rule", n), hidden=False,
           targetId=rule_id(b, n), type="rule")
    if psyker:
        cat, cname = TYPE_CATEGORIES["Psyker"]
        el(child(e, "categoryLinks"), "categoryLink", targetId=cat, id=make_id(key, "cat", cat), primary=False,
           name=cname)


def surcharge(e, target, points, models=()):
    """The Grey Knights rules' cost: points for each of the unit's models (a Rhino is the unit itself)."""
    if not models:
        el(child(e, "modifiers"), "modifier", type="increment", field=PTS, value=points)
    for m in models:
        mod = el(child(e, "modifiers"), "modifier", type="increment", field=PTS, value=points)
        el(el(mod, "repeats"), "repeat", field="selections", scope=target, value=1, percentValue=False, shared=True,
           includeChildSelections=True, includeChildForces=False, childId=m, repeats=1, roundUp=False)


def barred_by(b, e, rite):
    """Hidden while the force has chosen that Rite of War."""
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
    b.rite_condition(mod, make_id("rite", b.faction, rite))


def official_unit(b, links, name, target, points, models, psyker, slot):
    key = make_id("official unit", b.faction, name)
    e = el(links, "entryLink", import_=True, name=name, hidden=False, id=key, type="selectionEntry",
           targetId=target)
    surcharge(e, target, points, models)
    grey_knights_rules(b, e, key, psyker)
    for cat, cname, primary in SLOTS[slot] + [UNIT_CATEGORY + (False,)]:
        el(child(e, "categoryLinks"), "categoryLink", targetId=cat, id=make_id(key, "cat", cat), primary=primary,
           name=cname)
    return e


def teleport_harness(b, e, target, models):
    """The doc's Teleport Harness for a Dreadnought Talon: one per unit, +40 points for each Dreadnought in it."""
    harness = b.shared_entries.find("selectionEntry[@name='Teleport Harness']")
    lid = make_id(e.get("id"), "teleport harness")
    g = el(child(e, "selectionEntryGroups"), "selectionEntryGroup", name="Teleport Harness", hidden=False,
           id=make_id(lid, "group"))
    add_constraint(g, "max", 1, lid + "group")
    l = el(child(g, "entryLinks"), "entryLink", import_=True, name="Teleport Harness", hidden=False, id=lid,
           type="selectionEntry", targetId=harness.get("id"))
    add_constraint(l, "max", 1, lid)
    for m in models:
        mod = el(child(l, "modifiers"), "modifier", type="increment", field=PTS, value=HARNESS_POINTS)
        el(el(mod, "repeats"), "repeat", field="selections", scope=target, value=1, percentValue=False, shared=True,
           includeChildSelections=True, includeChildForces=False, childId=m, repeats=1, roundUp=False)


def loyalist_only(b):
    """Every model with Master of the Legion (but the Grand Master in Nemesis Dreadknight) may take a Brotherhood
Command Squad, Terminator Command Squad or Tartaros Command Squad as a Retinue (no Force Organisation slot), as an official
Legion leader takes a Command Squad; the Aegis Captain may take an Aegis Bastion Squad instead.

The 0-1 Purifier Bladeguard Squad has no limit in a Detachment whose Brotherhood is the 8th.

Characters bound to a Brotherhood (Stern, Voldus and the founding Grand Masters) are an error in a Detachment of
another Brotherhood.

Grey Knights are always Loyalist: with Traitor chosen in the force, the army entry may not be taken."""
    army = b.root.find(f"selectionEntries/selectionEntry[@id='{make_id('army', b.faction)}']")
    cmax = next(c for c in army.findall("constraints/constraint") if c.get("type") == "max")
    m = el(child(army, "modifiers"), "modifier", type="set", field=cmax.get("id"), value=0)
    el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
       childId=TRAITOR, shared=True, includeChildSelections=True, includeChildForces=False)


COMMAND_SQUADS = ["Brotherhood Command Squad", "Brotherhood Terminator Command Squad",
                  "Brotherhood Tartaros Command Squad"]
NO_RETINUE = ["Grand Master in Nemesis Dreadknight"]  # infantry may not join a Dreadknight


def retinues(b):
    """Retinue Squads, as an official Legion leader takes a Command Squad: every model with Master of the Legion
    (but the Grand Master in Nemesis Dreadknight) has a "Retinue" group in his own entry holding the three Command
    Squads, and the Aegis Captain the Aegis Bastion Squad too, so a Retinue uses no Force Organisation slot. The
    Command Squads are HQ choices as well; the Aegis Bastion Squad's 0-1 limit is on the squad, so a Detachment
    has one at most, however it is taken."""
    squads = [b.units[n] for n in COMMAND_SQUADS]
    for link in b.root.find("entryLinks"):  # HQ choices, but with no Warlord they never fill a Compulsory HQ slot
        if link.get("targetId") in squads:
            for c in link.findall("categoryLinks/categoryLink"):
                if c.get("name", "").startswith("Compulsory"):
                    link.find("categoryLinks").remove(c)
    bastion = b.units["Aegis Bastion Squad"]
    squad = b.shared_entries.find(f"selectionEntry[@id='{bastion}']")
    add_constraint(squad, "max", 1, make_id(bastion, "one per force"), scope="force", children=True)
    for ds in b.datasheets:
        if "Master of the Legion" not in ds["rules"] or ds["name"] in NO_RETINUE:
            continue
        lead = b.shared_entries.find(f"selectionEntry[@id='{b.units[ds['name']]}']")
        gid = make_id(lead.get("id"), "retinue")
        g = el(child(lead, "selectionEntryGroups"), "selectionEntryGroup", name="Retinue", hidden=False, id=gid)
        add_constraint(g, "max", 1, gid + "max")
        for sid in squads + ([bastion] if ds["name"] == "Aegis Captain" else []):
            s = b.shared_entries.find(f"selectionEntry[@id='{sid}']")
            el(child(g, "entryLinks"), "entryLink", import_=True, name=s.get("name"), hidden=False,
               id=make_id(gid, s.get("name")), type="selectionEntry", targetId=sid)


def purifier_bladeguard(b):
    """The 0-1 Purifier Bladeguard Squad is not limited to one in a Detachment whose Brotherhood is the 8th."""
    uid = b.units["Purifier Bladeguard Squad"]
    eighth = next(e.get("id") for e in b.root.iter("selectionEntry") if e.get("name", "").startswith("8th Brotherhood"))
    for link in b.root.find("entryLinks"):
        if link.get("targetId") != uid:
            continue
        for c in link.findall("constraints/constraint"):
            if c.get("type") == "max" and c.get("scope") == "force":
                m = el(child(link, "modifiers"), "modifier", type="set", field=c.get("id"), value=-1)
                el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
                   childId=eighth, shared=True, includeChildSelections=True, includeChildForces=False)


BROTHERHOOD_ONLY = {"Brother-Captain Stern": ["3rd"], "Grand Master Voldus": ["3rd"], "Grand Master Koios": ["1st"],
                    "Grand Master Satre": ["2nd"], "Grand Master Iapto": ["3rd"], "Grand Master Yotun": ["4th"],
                    "Grand Master Epimetheus": ["5th"], "Grand Master Ogen": ["6th"],
                    "Grand Master Khyron": ["7th", "8th"]}


def brotherhood_only(b):
    """Characters bound to a Brotherhood (Stern and Voldus the 3rd, each founding Grand Master his own) are always
    shown, but may be taken only in a Detachment whose Brotherhood is one of theirs: elsewhere they are over their
    limit (max 0), which BattleScribe and New Recruit report as an error."""
    ids = {e.get("name", "").split(" ")[0]: e.get("id") for e in b.root.iter("selectionEntry")
           if re.match(r"\d(st|nd|rd|th) Brotherhood", e.get("name", ""))}
    for name, nths in BROTHERHOOD_ONLY.items():
        uid = b.units[name]
        for link in b.root.find("entryLinks"):
            if link.get("targetId") != uid:
                continue
            add_constraint(link, "max", 0, make_id(link.get("id"), "brotherhood only"), scope="force", children=True)
            cmax = link.findall("constraints/constraint")[-1]
            for n in nths:  # one plain modifier per Brotherhood (Khyron has two)
                m = el(child(link, "modifiers"), "modifier", type="set", field=cmax.get("id"), value=1)
                el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
                   childId=ids[n], shared=True, includeChildSelections=True, includeChildForces=False)


FOUNDERS = ["Supreme Grand Master Janus", "Grand Master Koios", "Grand Master Satre", "Grand Master Iapto",
            "Grand Master Yotun", "Grand Master Epimetheus", "Grand Master Ogen", "Grand Master Khyron"]
RITE_LEADERS = {"Paladin Retinue": FOUNDERS, "Teleport Assault": FOUNDERS, "Purifier Crusade": ["Aegis Captain"]}


def rite_leaders(b):
    """Janus and the founding Grand Masters count as Grand Masters, and the Aegis Captain as a Brother-Captain, for
    the Rites' prerequisites: their Warlord option is not barred while that Rite is chosen."""
    for rite, leaders in RITE_LEADERS.items():
        rid = next(e.get("id") for e in b.root.iter("selectionEntry") if e.get("name") == rite)
        for name in leaders:
            unit = b.shared_entries.find(f"selectionEntry[@id='{b.units[name]}']")
            for link in unit.iter("entryLink"):
                if link.get("name") != "Warlord":
                    continue
                mods = link.find("modifiers")
                for m in list(mods if mods is not None else []):
                    if any(c.get("childId") == rid for c in m.iter("condition")):
                        mods.remove(m)


# The Grey Knights' own Rites of War (the generic Legion ones are not offered). The builder reads the slots, bans
# and Warlord from the md; what its reading misses for these Rites' wording is done here, unit by unit.
CHAMPION_TROOPS = ["Paladin Squad", "Aegis Bastion Squad"]  # Elites squads all in Terminator armour
CHAMPION_HEAVY = ["Aegis Bastion Squad"]  # all in Aegis-Cataphractii
CHAMPION_FAST = ["Brotherhood Tartaros Command Squad"]  # all in Aegis Tartaros (Interceptor Terminators are FA already)
COMPULSORY_ONLY = {  # Rite: the only units that may fill its Compulsory Troops
    "Prognosticar Vanguard": ["Prognosticar Vanguard Squad", "Watcher-in-the-Veil Squad"],
    "Purifier Crusade": ["Purifier Squad", "Purifier Bladeguard Squad"],
    "Paladin Retinue": ["Paladin Squad"],
    "Nemesis Strike": ["Strike Squad", "Brotherhood Terminator Squad"],
    "Champions of Titan": CHAMPION_TROOPS + ["Brotherhood Terminator Squad"],
}
RITE_BANS = {  # Rite: units it bars (the official Dreadnoughts and Land Raiders by their link names)
    "Purifier Crusade": ["Dreadknight Talon", "Grey Knight Dreadlancer Talon", "Grand Master in Nemesis Dreadknight",
                         "Castra Ferrum Dreadnought Talon", "Contemptor Dreadnought Talon", "Land Raider Crusader",
                         "Land Raider Redeemer", "Land Raider Proteus Carrier Squadron", "Land Raider Phobos Squadron"],
    "Paladin Retinue": ["Strike Squad", "Interceptor Squad", "Purgation Squad"],
}
SINGLE_SLOTS = {"Purifier Crusade": ["Heavy Support"], "Paladin Retinue": ["Fast Attack", "Heavy Support"]}
LINE_UNITS = {"Purifier Crusade": ["Purifier Squad", "Purifier Bladeguard Squad"], "Paladin Retinue": ["Paladin Squad"],
              "Nemesis Strike": ["Grey Knight Dreadlancer Talon"], "Champions of Titan": CHAMPION_TROOPS}
TERMINATOR_WORDS = ("terminator armour", "cataphractii", "tartaros")


def gk_rites(b):
    rites = {r["name"]: r for r in b.rite_specs}
    links = b.root.find("entryLinks")
    ds_by = {d["name"]: d for d in b.datasheets}
    unit = lambda n: b.shared_entries.find(f"selectionEntry[@id='{b.units[n]}']")
    compulsory = next(c for c in SLOTS["Troops"] if c[1] == "Compulsory Troops:")[0]

    def has_cat(link, cat):
        return any(c.get("targetId") == cat for c in link.findall("categoryLinks/categoryLink"))

    def rite_links(name):
        return [l for l in links if l.get("name") == name]

    def slot(rite, name, s, comp):
        """The Rite's own link for the unit in slot s: the builder's if it made one, else a new one."""
        own = make_id("rite root", b.faction, rite["name"], name)
        mine = next((l for l in links if l.get("id") == own and has_cat(l, SLOTS[s][0][0])), None)
        if mine is None:
            if any(l.get("id") == own for l in links):  # the Rite's link for another slot: this one is the second
                before = len(links)
                b.rite_slot(links, rite, ds_by[name], b.units[name], s, comp)
                e = links[before]
                e.set("id", make_id(own, s))
                for c in e.iter("categoryLink"):
                    c.set("id", make_id(c.get("id"), s))
                return
            b.rite_slot(links, rite, ds_by[name], b.units[name], s, comp)
        elif comp and s == "Troops" and not has_cat(mine, compulsory):
            el(child(mine, "categoryLinks"), "categoryLink", targetId=compulsory, id=make_id(own, "compulsory"),
               primary=False, name="Compulsory Troops:")

    def error(rite, key, conds):
        entry = b.root.find(f"selectionEntries/selectionEntry//selectionEntry[@id='{rite['id']}']")
        cid = add_constraint(entry, "max", 1, make_id(rite["id"], "gk limit", key))
        mod = el(child(entry, "modifiers"), "modifier", type="set", field=cid, value=0)
        grp = el(el(mod, "conditionGroups"), "conditionGroup", type="or")
        conds(el(grp, "conditions"))

    # Champions of Titan: Terminator squads as Troops, Cataphractii as Heavy Support, Tartaros as Fast Attack;
    # every unit must be in Terminator armour
    rite = rites["Champions of Titan"]
    for n in CHAMPION_TROOPS:
        slot(rite, n, "Troops", True)
    for n in CHAMPION_HEAVY:
        slot(rite, n, "Heavy Support", False)
    for n in CHAMPION_FAST:
        slot(rite, n, "Fast Attack", False)
    termi = {d["name"] for d in b.datasheets
             if any(w in " ".join(map(str, d["wargear"] + d["options"])).lower() for w in TERMINATOR_WORDS)}
    others = sorted({l.get("targetId") for l in links if l.get("name") not in termi})
    error(rite, "terminators", lambda c: [el(c, "condition", type="atLeast", value=1, field="selections", scope="force",
          childId=t, shared=True, includeChildSelections=True, includeChildForces=False) for t in others])

    # Prognosticar Vanguard: Support Squad (no Compulsory Troops slot) but under this Rite; Exactors as Troops
    rite = rites["Prognosticar Vanguard"]
    for n in COMPULSORY_ONLY["Prognosticar Vanguard"]:
        for l in rite_links(n):
            for c in l.findall("categoryLinks/categoryLink"):
                if c.get("targetId") == compulsory:
                    l.find("categoryLinks").remove(c)
            b.rite_condition(el(child(l, "modifiers"), "modifier", type="add", field="category", value=compulsory), rite["id"])
        for il in unit(n).findall("infoLinks/infoLink"):
            if il.get("name") == "Support Squad":
                b.rite_condition(el(child(il, "modifiers"), "modifier", type="set", field="hidden", value="true"), rite["id"])
    slot(rite, "Exactor Squad", "Troops", False)
    # Purifier Crusade and Paladin Retinue: their Troops may fill the compulsory slots
    for n in LINE_UNITS["Purifier Crusade"]:
        slot(rites["Purifier Crusade"], n, "Troops", True)
    slot(rites["Paladin Retinue"], "Paladin Squad", "Troops", True)

    # the Troops a Rite's Compulsory Troops must be
    for name, allowed in COMPULSORY_ONLY.items():
        rite = rites[name]
        for l in links:
            if l.get("name") not in allowed and (has_cat(l, compulsory) or l.get("name") in ("Prognosticar Vanguard Squad",
                                                                                            "Watcher-in-the-Veil Squad")):
                b.rite_condition(el(child(l, "modifiers"), "modifier", type="remove", field="category", value=compulsory),
                                 rite["id"])
    for name, units in LINE_UNITS.items():
        for n in units:
            b.rite_line(unit(n), rites[name]["id"])
    for name, banned in RITE_BANS.items():
        rite = rites[name]
        for l in links:
            if l.get("name") in banned:
                b.rite_condition(el(child(l, "modifiers"), "modifier", type="set", field="hidden", value="true"), rite["id"])
        ids = sorted({l.get("targetId") for l in links if l.get("name") in banned})
        error(rite, "bans", lambda c, ids=ids: [el(c, "condition", type="atLeast", value=1, field="selections",
              scope="force", childId=t, shared=True, includeChildSelections=True, includeChildForces=False) for t in ids])
    for name, slots in SINGLE_SLOTS.items():
        for s in slots:
            b.rite_error(rites[name], "one " + s, lambda c, cat=SLOTS[s][0][0]: el(c, "condition", type="greaterThan",
                value=1, field="selections", scope="force", childId=cat, shared=True, includeChildSelections=True,
                includeChildForces=False))

    # Teleport Assault: Infantry and Dreadknights without personal teleporters gain the rule; Dreadknights alone
    rite = rites["Teleport Assault"]
    for d in b.datasheets:
        kit = " ".join(map(str, d["wargear"])).lower()
        if "personal teleporter" in kit or not any(re.search(r"\b(Infantry|Armiger)\b", t) for t in d["types"]):
            continue
        b.rite_rule(unit(d["name"]), b.units[d["name"]], rite["id"], "Teleport Assault")
    for n in ("Dreadknight Talon", "Grey Knight Dreadlancer Talon"):
        b.rite_size(unit(n), rite["id"], 1)


def apply(b):
    loyalist_only(b)
    retinues(b)
    purifier_bladeguard(b)
    brotherhood_only(b)
    rite_leaders(b)
    gk_rites(b)
    harness = b.shared_entries.find("selectionEntry[@name='Teleport Harness']")
    el(child(harness, "infoLinks"), "infoLink", name="Deep Strike", id=make_id(harness.get("id"), "deep strike"),
       hidden=False, targetId=DEEP_STRIKE, type="rule")
    el(child(b.root, "catalogueLinks"), "catalogueLink", name=LIBRARY[1], targetId=LIBRARY[0], type="catalogue",
       importRootEntries=False, id=make_id("library", b.faction, LIBRARY[1]))
    links = child(b.root, "entryLinks")
    for name, target, points, models in DREADNOUGHTS:
        e = official_unit(b, links, name, target, points, models, True, "Heavy Support")
        teleport_harness(b, e, target, models)
        for pname, pid in b.powers + b.psychic_weapons:
            if pname in DREADNOUGHT_POWERS:
                b.link(child(e, "entryLinks"), pid, pname, make_id(e.get("id"), "powers"), count=1)
    for name, target, points, models in LAND_RAIDERS:
        barred_by(b, official_unit(b, links, name, target, points, models, False, "Heavy Support"), "Purifier Crusade")
    name, target, points = RHINO
    for unit_name in TRANSPORTED:
        uid = b.units[unit_name]
        unit = b.shared_entries.find(f"selectionEntry[@id='{uid}']")
        gid = make_id(uid, "dedicated transport")
        g = el(child(unit, "selectionEntryGroups"), "selectionEntryGroup", name="Dedicated Transport", hidden=False,
               id=gid)
        add_constraint(g, "max", 1, gid + "max")
        key = make_id(gid, "link", name)
        e = el(child(g, "entryLinks"), "entryLink", import_=True, name=name, hidden=False, id=key,
               type="selectionEntry", targetId=target)
        add_constraint(e, "max", 1, key + "max")
        surcharge(e, target, points)
        grey_knights_rules(b, e, key, False)
        barred_by(b, e, "Teleport Assault")
