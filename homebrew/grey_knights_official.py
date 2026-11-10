"""Grey Knights: the official 2.0 units the doc's "Units to take from the official 2.0 books" table names, called by
build_catalogue.py for that faction.

The units link the Legions Astartes library's own entries, so their profiles, wargear and options stay the
official ones. Each gains the doc's Grey Knights rules and pays for them per model:

- Dreadnoughts (Castra Ferrum, the 2.0 Mk IV-pattern Legion Dreadnought, and Contemptor) are piloted by Grey
  Knights: Psyker sub-type, Brotherhood of Psykers, Daemon Hunters, Brotherhood (X) and Aegis, +25 points per
  Dreadnought.
- Land Raiders (Proteus Carrier and Phobos) and the Rhino: Brotherhood (X) and Aegis, +10 points per Land Raider
  and +5 points per Rhino. The Rhino is the Dedicated Transport of the units whose datasheet offers one.

2.0 has no Razorback, so the doc's "Rhino or Razorback" is the Rhino."""
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
TRANSPORTED = ["Purifier Squad", "Strike Squad", "Purgation Squad"]  # "may take a Rhino or Razorback"


def rule_id(b, name):
    r = b.shared_rules.find(f"rule[@name='{name}']")
    return r.get("id")


def grey_knights_rules(b, e, key, psyker):
    names = (["Brotherhood of Psykers", "Daemon Hunters"] if psyker else []) + ["Brotherhood (X)", "Aegis"]
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


def official_unit(b, links, name, target, points, models, psyker, slot):
    key = make_id("official unit", b.faction, name)
    e = el(links, "entryLink", import_=True, name=name, hidden=False, id=key, type="selectionEntry",
           targetId=target)
    surcharge(e, target, points, models)
    grey_knights_rules(b, e, key, psyker)
    for cat, cname, primary in SLOTS[slot] + [UNIT_CATEGORY + (False,)]:
        el(child(e, "categoryLinks"), "categoryLink", targetId=cat, id=make_id(key, "cat", cat), primary=primary,
           name=cname)


def apply(b):
    el(child(b.root, "catalogueLinks"), "catalogueLink", name=LIBRARY[1], targetId=LIBRARY[0], type="catalogue",
       importRootEntries=False, id=make_id("library", b.faction, LIBRARY[1]))
    links = child(b.root, "entryLinks")
    for name, target, points, models in DREADNOUGHTS:
        official_unit(b, links, name, target, points, models, True, "Heavy Support")
    for name, target, points, models in LAND_RAIDERS:
        official_unit(b, links, name, target, points, models, False, "Heavy Support")
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
