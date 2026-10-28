"""Traders Militant army-building limits, called by build_catalogue.py for that faction.

Every Detachment has one faction selection (the Allegiance-category entry each catalogue requires in a force:
"Mechanicum", "XIII: Ultramarines", a homebrew army entry), so the army's Detachments are counted by those
selections across the roster:

- Each Warrant of Trade carries its Limitations as limits on the Warrant itself, so the app flags the Warrant
  the army breaks.
- The Aegis Militant Detachment may include one Knights Errant, Divisio Assassinorum or Cults Abominatio unit
  as a non-Compulsory Elites choice.
- The army may include one Allied Detachment for every 1,000 points of its points limit, plus the Detachment a
  Warrant's Effects add."""
import glob
import os
import xml.etree.ElementTree as ET

from build_catalogue import PTS, UNIT_CATEGORY, add_constraint, add_cost, add_rule, child, el, make_id

NS = "{http://www.battlescribe.net/schema/catalogueSchema}"
ALLEGIANCE = "e90d-e5a8-f42d-da84"
ALLIED = "d4f2-6da5-b6de-06ec"
LORD_OF_WAR = "58a7-8821-3cd9-c73"
XENOS_ARMY = "3c8e-5a1d-9b47-e2f0"  # on the army entry of every Faction that may select the Xenos Allegiance
LOYALIST, TRAITOR = "d0b6-712f-0b12-a308", "f9c0-0c5a-3e24-58c7"
LEGACIES = "d344-d97b-4687-8a62"  # the roster's Legacies of the Age of Darkness option
ELITES = ("7aee-565f-b0ae-294e", "Elites:")

AGENTS_OF_THE_EMPEROR = ["e0d0-c905-b01e-fc15", "4d60-2ab7-244f-3414"]  # Legio Custodes, Sisters of Silence
AGENTS_OF_THE_WARMASTER = ["afca-3047-fb26-d097", "d601-e213-fa45-8ee8"]  # Ruinstorm Daemons, Bound Daemons
AGENTS = AGENTS_OF_THE_EMPEROR + AGENTS_OF_THE_WARMASTER
MECHANICUM = ["ddf5-d792-3146-6e9a"]
# Solar Auxilia, Imperialis Militia and the homebrew Astra Militarum
IMPERIAL_ARMY = ["f689-fd0d-ffb0-c255", "5522-4fd9-12d5-460afds", "dc0d-35ba-0d83-561a"]

# The units the Aegis Militant Detachment may take as its extra Elites choice, from LI - Assassins and Agents,
# shown to the Allegiance the official catalogues show them to: (name, entry, Allegiance, Legacies only)
AGENT_LIBRARY = ("4c88-1a81-7e53-0a67", "LI - Assassins and Agents")
AGENT_UNITS = [("Clade Assassins (Loyalist)", "7363-5a05-4102-24fa", LOYALIST, False),
               ("Cults Abominatio", "4a00-03d4-a850-884b", TRAITOR, False),
               ("Nathaniel Garro", "0583-258d-f0a0-2170", LOYALIST, True),
               ("Tylos Rubio", "56bf-2c6d-a0fa-a145", LOYALIST, True)]


def faction_entries(own_id, own_name):
    """{catalogue file: faction selection id} for every other catalogue that has one."""
    out = {}
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "*.cat"))):
        root = ET.parse(f).getroot()
        if root.get("id") == own_id or (root.get("name") or "").startswith(own_name) or root.get("library") == "true":
            continue
        for tag in ("entryLinks", "selectionEntries"):
            for e in root.findall(f"{NS}{tag}/*"):
                if any(c.get("targetId") == ALLEGIANCE and c.get("primary") == "true"
                       for c in e.findall(f"{NS}categoryLinks/{NS}categoryLink")) and any(
                        c.get("type") == "min" and c.get("value") == "1" for c in e.findall(f"{NS}constraints/{NS}constraint")):
                    out[os.path.basename(f)] = e.get("targetId") or e.get("id")
    return out


def count(childId, field="selections"):
    """Attributes for counting selections of an entry or category (or Detachments of a forceEntry) in the roster."""
    return dict(field=field, scope="roster", childId=childId, shared=True, includeChildSelections=True,
                includeChildForces=field == "forces")


def condition(parent, kind, value, childId, field="selections"):
    el(parent, "condition", type=kind, value=value, percentValue=False, **count(childId, field))


def limit(entry, key, base, rule):
    """A limit on the entry itself, starting at base: the entry (one selection) breaks it when it falls below 1."""
    cid = add_constraint(entry, "max", base, key)
    c = entry.find(f"constraints/constraint[@id='{cid}']")
    el(c, "comment").text = rule
    return cid


def step(entry, cid, kind, value, childId, field="selections", every=1):
    """Raise or lower the limit once for every `every` selections (or Detachments) of childId."""
    mod = el(child(entry, "modifiers"), "modifier", type=kind, field=cid, value=value)
    el(el(mod, "repeats"), "repeat", value=every, percentValue=False, repeats=1, roundUp=False, **count(childId, field))
    return mod


def zero_if(entry, cid, groups, kind="or"):
    """Set the limit to 0 when any (or every) condition holds: [(type, value, childId), ...]."""
    mod = el(child(entry, "modifiers"), "modifier", type="set", field=cid, value=0)
    conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type=kind), "conditions")
    for t, v, c in groups:
        condition(conds, t, v, c)
    return mod


def apply(b):
    own = b.root.get("id")
    factions = faction_entries(own, b.root.get("name"))
    legions = [i for f, i in factions.items() if f.startswith("2022 - LA - ")
               or f in ("2022 - BG - Blackshields.cat", "Shattered Legions.cat")]
    force = b.root.find("forceEntries/forceEntry")
    warrants = {name: ids for name, ids in getattr(b, "rule_choice_ids", {}).items()}

    # Warrants of Trade: each Limitation, on the Warrant
    for eid in warrants.get("Warrant of Compliance", []):
        e = find(b, eid)
        cid = limit(e, eid + "xenos", 1, "The army may not include any Detachments from a Faction that may select "
                                         "the Xenos Allegiance.")
        zero_if(e, cid, [("atLeast", 1, XENOS_ARMY)])
        cid = limit(e, eid + "agents", 2, "No more than one Agents of the Emperor or Agents of the Warmaster Allied "
                                          "Detachment may be included.")
        for m in AGENTS:
            step(e, cid, "decrement", 1, m)
    for eid in warrants.get("Warrant of Conquest", []):
        e = find(b, eid)
        cid = limit(e, eid + "xenos", 2, "No more than one Xenos Detachment may be included.")
        step(e, cid, "decrement", 1, XENOS_ARMY)
        cid = limit(e, eid + "agents", 1, "The army may not include any Allied or Optional Detachments from the "
                                          "Agents of the Emperor or Agents of the Warmaster Factions.")
        zero_if(e, cid, [("atLeast", 1, m) for m in AGENTS])
    for eid in warrants.get("Warrant of Exploration", []):
        e = find(b, eid)
        cid = limit(e, eid + "xenos", 1, "The army must include one Detachment from a Faction that may select the "
                                         "Xenos Allegiance, and no more than one.")
        zero_if(e, cid, [("equalTo", 0, XENOS_ARMY), ("greaterThan", 1, XENOS_ARMY)])
        cid = limit(e, eid + "legions", 2, "The army may include only one Detachment from a Faction containing "
                                           "models with the Legiones Astartes (X) Special Rule.")
        for m in legions:
            step(e, cid, "decrement", 1, m)
        cid = limit(e, eid + "mechanicum", 3, "No more than two Mechanicum Detachments may be included.")
        for m in MECHANICUM:
            step(e, cid, "decrement", 1, m)
        cid = limit(e, eid + "agents", 1, "The Detachment may not include any Allied or Optional Detachments from "
                                          "the Agents of the Emperor or Agents of the Warmaster Factions.")
        zero_if(e, cid, [("atLeast", 1, m) for m in AGENTS])
    for eid in warrants.get("Warrant-Breaker", []):
        e = find(b, eid)
        # Allied and Optional Detachments, less those from Xenos or Imperial Army Factions, must be none
        cid = limit(e, eid + "factions", 1, "The army may only include Allied or Optional Detachments from Factions "
                                            "that may select the Xenos Allegiance, or from the Imperial Army Faction.")
        for m in [XENOS_ARMY] + IMPERIAL_ARMY:
            step(e, cid, "increment", 1, m)
        for f in (ALLIED, LORD_OF_WAR):
            step(e, cid, "decrement", 1, f, field="forces")
        cid = limit(e, eid + "twice", 1, "No Faction or Sub-faction may be selected more than twice.")
        zero_if(e, cid, [("greaterThan", 2, m) for m in sorted(set(factions.values()))])

    if force is None:
        return
    fid = force.get("id")
    cats = child(b.root, "categoryEntries")

    # One Knights Errant, Divisio Assassinorum or Cults Abominatio unit, as a non-Compulsory Elites choice
    agent_cat = make_id("category", b.faction, "Aegis Militant Agent")
    el(cats, "categoryEntry", name="Aegis Militant Agent", hidden=False, id=agent_cat)
    link = el(force.find("categoryLinks"), "categoryLink", name="Aegis Militant Agent", hidden=False,
              id=make_id(fid, "agent"), targetId=agent_cat, primary=False)
    add_constraint(link, "max", 1, fid + "agent max", scope="force", children=True)
    elites = force.find(f"categoryLinks/categoryLink[@targetId='{ELITES[0]}']")
    emin = elites.find("constraints/constraint[@type='min']").get("id")
    mod = el(child(elites, "modifiers"), "modifier", type="increment", field=emin, value=1)
    el(el(mod, "repeats"), "repeat", field="selections", scope="force", childId=agent_cat, value=1, percentValue=False,
       shared=True, includeChildSelections=True, includeChildForces=False, repeats=1, roundUp=False)
    el(child(b.root, "catalogueLinks"), "catalogueLink", name=AGENT_LIBRARY[1], targetId=AGENT_LIBRARY[0],
       type="catalogue", importRootEntries=False, id=make_id(own, "link", AGENT_LIBRARY[0]))
    links = child(b.root, "entryLinks")
    for name, target, side, legacy in AGENT_UNITS:
        lid = make_id("agent link", b.faction, name)
        e = el(links, "entryLink", import_=True, name=name, hidden=True, id=lid, type="selectionEntry", targetId=target)
        mod = el(el(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="and"), "conditions")
        el(conds, "condition", type="atLeast", value=1, field="selections", scope="force", childId=side, shared=True,
           includeChildSelections=True, includeChildForces=False)
        if legacy:
            el(conds, "condition", type="atLeast", value=1, field="selections", scope="roster", childId=LEGACIES,
               shared=True, includeChildSelections=True, includeChildForces=False)
        for cat, cname, primary in ((agent_cat, "Aegis Militant Agent", True), (ELITES[0], ELITES[1], False),
                                    UNIT_CATEGORY + (False,)):
            el(child(e, "categoryLinks"), "categoryLink", targetId=cat, id=make_id(lid, "cat", cat), primary=primary,
               name=cname)

    # One Allied Detachment for every 1,000 points, plus the Detachment a Warrant's Effects add
    limits_cat = make_id("category", b.faction, "Aegis Militant Limits")
    el(cats, "categoryEntry", name="Aegis Militant Limits", hidden=False, id=limits_cat)
    el(force.find("categoryLinks"), "categoryLink", name="Aegis Militant Limits", hidden=False,
       id=make_id(fid, "limits"), targetId=limits_cat, primary=False)
    eid = make_id("allied limit", b.faction)
    e = el(child(b.root, "selectionEntries"), "selectionEntry", type="upgrade", import_=True,
           name="Allied Detachments (one per 1,000 points)", hidden=False, id=eid, publicationId=b.pub_id)
    add_constraint(e, "min", 1, eid + "min", scope="force", children=True)
    add_constraint(e, "max", 1, eid + "max", scope="force", children=True)
    add_rule(e, "Allied Detachments", "The army may include one Allied Detachment for every 1,000 points (e.g. three "
             "at 3,000 points). A Warrant of Trade whose Effects let the army include a Detachment (Compliance: one "
             "Agents of the Emperor or Agents of the Warmaster Allied Detachment; Conquest: one Xenos Detachment; "
             "Exploration: up to two Mechanicum Detachments) allows that Detachment on top of this limit.", eid)
    el(el(e, "categoryLinks"), "categoryLink", targetId=limits_cat, id=make_id(eid, "cat"), primary=True,
       name="Aegis Militant Limits")
    cid = limit(e, eid + "allied", 1, "The army may include one Allied Detachment for every 1,000 points.")
    step(e, cid, "increment", 1, "any", field="limit::" + PTS, every=1000)
    step(e, cid, "decrement", 1, ALLIED, field="forces")
    for warrant, needs in (("Warrant of Compliance", [AGENTS]), ("Warrant of Conquest", [[XENOS_ARMY]]),
                           ("Warrant of Exploration", [MECHANICUM, MECHANICUM])):
        for i, markers in enumerate(needs):
            mod = el(child(e, "modifiers"), "modifier", type="increment", field=cid, value=1)
            outer = el(el(mod, "conditionGroups"), "conditionGroup", type="and")
            # the Warrant, on whichever unit took it
            wg = el(el(outer, "conditionGroups"), "conditionGroup", type="or")
            for w in warrants.get(warrant, []):
                condition(child(wg, "conditions"), "atLeast", 1, w)
            mg = el(child(outer, "conditionGroups"), "conditionGroup", type="or")
            for m in markers:  # the second Mechanicum Detachment needs two
                condition(child(mg, "conditions"), "greaterThan", i, m)
    add_cost(e, 0)


def find(b, eid):
    return next(x for x in b.shared_entries.iter("selectionEntry") if x.get("id") == eid)
