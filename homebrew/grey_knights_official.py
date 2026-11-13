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

The Rites of War that bar these kinds of unit bar the official ones too: Purifier Crusade (no Land Raiders) hides
the official Land Raiders, and Teleport Assault (no Dedicated Transports) hides the Rhino.

The Aegis Captain may take an Aegis Bastion Squad as a Retinue (no Force Organisation slot), as an official
Legion leader takes a Command Squad.

The 0-1 Purifier Bladeguard Squad has no limit in a Detachment whose Brotherhood is the 8th.

Brother-Captain Stern and Grand Master Voldus show only in a Detachment whose Brotherhood is the 3rd.

Grey Knights are always Loyalist: a force that picks the Traitor allegiance may not take the Grey Knights army
entry (BattleScribe reports it as over its limit)."""
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
    """The Aegis Captain may take an Aegis Bastion Squad as a Retinue (no Force Organisation slot), as an official
Legion leader takes a Command Squad.

The 0-1 Purifier Bladeguard Squad has no limit in a Detachment whose Brotherhood is the 8th.

Brother-Captain Stern and Grand Master Voldus show only in a Detachment whose Brotherhood is the 3rd.

Grey Knights are always Loyalist: with Traitor chosen in the force, the army entry may not be taken."""
    army = b.root.find(f"selectionEntries/selectionEntry[@id='{make_id('army', b.faction)}']")
    cmax = next(c for c in army.findall("constraints/constraint") if c.get("type") == "max")
    m = el(child(army, "modifiers"), "modifier", type="set", field=cmax.get("id"), value=0)
    el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
       childId=TRAITOR, shared=True, includeChildSelections=True, includeChildForces=False)


def aegis_retinue(b):
    """The Aegis Captain takes an Aegis Bastion Squad as his Retinue, as an official Legion leader takes a
    Command Squad: a "Retinue" group in his own entry, so the squad uses no Force Organisation slot. The
    squad's "0-1" limit is on the squad itself, so a Detachment has one at most, however it is taken."""
    cap = b.shared_entries.find(f"selectionEntry[@id='{b.units['Aegis Captain']}']")
    sid = b.units["Aegis Bastion Squad"]
    squad = b.shared_entries.find(f"selectionEntry[@id='{sid}']")
    gid = make_id(cap.get("id"), "retinue")
    g = el(child(cap, "selectionEntryGroups"), "selectionEntryGroup", name="Retinue", hidden=False, id=gid)
    add_constraint(g, "max", 1, gid + "max")
    el(child(g, "entryLinks"), "entryLink", import_=True, name=squad.get("name"), hidden=False,
       id=make_id(gid, "squad"), type="selectionEntry", targetId=sid)
    add_constraint(squad, "max", 1, make_id(sid, "one per force"), scope="force", children=True)


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


def third_brotherhood_only(b):
    """Brother-Captain Stern and Grand Master Voldus may only join the 3rd Brotherhood: they show only in a
    Detachment whose Brotherhood is the 3rd."""
    third = next(e.get("id") for e in b.root.iter("selectionEntry") if e.get("name", "").startswith("3rd Brotherhood"))
    for name in ("Brother-Captain Stern", "Grand Master Voldus"):
        uid = b.units[name]
        for link in b.root.find("entryLinks"):
            if link.get("targetId") != uid:
                continue
            link.set("hidden", "true")
            m = el(child(link, "modifiers"), "modifier", type="set", field="hidden", value="false")
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
               childId=third, shared=True, includeChildSelections=True, includeChildForces=False)


def apply(b):
    loyalist_only(b)
    aegis_retinue(b)
    purifier_bladeguard(b)
    third_brotherhood_only(b)
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
