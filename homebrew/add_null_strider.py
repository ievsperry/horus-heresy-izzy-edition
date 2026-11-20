#!/usr/bin/env python3
"""The Aegis-Pattern Null-Strider (homebrew/source/null-strider.md) in the Sisters of Silence catalogue.

A Fast Attack squadron of one to three Armigers (Anathema Sub-type), built as the Protodreadnoughts are
(protodreadnoughts.py's unit builder): one pick for each arm, the per-model Chassis Upgrades, and the Anathema Psykana
Chamber Assignment, a required pick for the whole squadron priced per model. Each Chamber upgrade carries its
Silent Sisterhood (Chamber of X) entry, and the squadron takes that Chamber's category, which the Chamber limits
count, as the official units do.

The official Twin-linked Adrathic Destructor, Searchlights, Smoke Launchers and the Chamber entries are linked; the
Snare Cannon arm is the official Snare Cannon, twin-linked. The rest is new: its weapons and wargear as shared
entries. Its rules are the official ones: Silent Sisterhood (X), the Anathema Sub-type, Hatred (X) (Psykers, Daemons,
Corrupted) and, on its weapons, Psy-shock.

usage: python3 homebrew/add_null_strider.py   (refuses to run twice)"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
import protodreadnoughts as pd  # noqa: E402
from build_catalogue import add_constraint, child, el, norm  # noqa: E402

CAT = "2022 - LI - Sisters Of Silence.cat"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]   # the libraries the catalogue imports
NAME = "Aegis-Pattern Null-Strider"
KEY = "null-strider"
CHAMBERS = {  # Chamber -> (its category, its Silent Sisterhood (Chamber of X) entry)
    "Judgement": ("b71a-371d-4401-9dc0", "ade4-0f3a-c307-9dc2"),
    "Oblivion": ("a7e3-4559-7267-8bf6", "7856-71cb-a1fb-bc43"),
    "Vigilance": ("b6d7-6924-37fb-dd32", "7b50-6b5d-e6f9-420b"),
}
ANATHEMA = ("7e5d-d73e-8ff4-7345", "Anathema Sub-type")
ANATHEMA_RULE = "c1fa-0ed8-94b3-a337"   # the game system's shared rule, as the official units link it

RULES = []   # its rules are the official ones (Silent Sisterhood (X), Anathema Sub-type, Psy-shock, Hatred (X))
CHASSIS = ("Grants a 6+ Invulnerable Save against all attacks and the Adamantium Will (5+) special rule (a 5+ "
           "Invulnerable Save against psychic powers and psychic weapons).")
CHAMBER_UPGRADES = [
    ("Judgement", "Chamber of Judgement – Pursuit-Cadre Telemetry", 15, "Gains Scout and Move Through Cover, and all "
     "Bolt, Flame, and Snare weapons equipped by this model gain Pinning (if they do not already possess it) and Shell "
     "Shock (1).", ["Scout", "Move Through Cover", "Pinning", "Shell Shock (X)"]),
    ("Oblivion", "Chamber of Oblivion – Blackstone Execution-Array", 20, "Increases Weapon Skill to 6 and Attacks to 4, "
     "and gains Murderous Strike (5+) and Hatred (Psykers & Daemons) in close combat.",
     ["Murderous Strike (X)", "Hatred (X)"]),
    ("Vigilance", "Chamber of Vigilance – Subjugation Ward-Plating", 20, "Improves Toughness to 7, gains Counter-Attack "
     "(1), and improves its Reinforced Vratine Chassis Invulnerable Save to 5+ and its Adamantium Will (5+) to "
     "Adamantium Will (4+).", ["Counter-Attack (X)"]),
]
CHASSIS_UPGRADES = [
    ("Null-Matrix Amplifier", 20, "Increases the range of its Anathema Sub-type Leadership penalty from 6\" to 12\", "
     "and enemy units with the "
     "Daemon or Corrupted sub-types within 12\" suffer a -1 penalty to their Invulnerable Saves (to a minimum of 6+).",
     []),
    ("Silent Pursuit Actuators", 15, "Grants Infiltrate and Scout.", ["Infiltrate", "Scout"]),
]


def weapons(ctx):
    pd.weapon(ctx, "Dread-Executioner Greatblade", [(None, "-", "+3", "2", "Melee, Rending (5+), Sudden Strike (1), "
                                                                            "Psy-shock")])
    pd.weapon(ctx, "Sanctified Power Claw", [(None, "-", "x2", "2", "Melee, Armourbane (Melee), Shred, Unwieldy")])
    pd.weapon(ctx, "Twin-linked Psyk-Out Bolt Cannon", [(None, '36"', "5", "4", "Heavy 4, Twin-linked, Psy-shock, "
                                                                                "Pinning")])
    pd.weapon(ctx, "Twin-linked Heavy Alchem-Flamer", [(None, "Template", "1", "3", "Assault 1, Twin-linked, "
                                                                                    "Poisoned (2+), Fleshbane")])
    # the official Snare Cannon, twin-linked
    pd.weapon(ctx, "Twin-linked Snare Cannon", [(None, '18"', "7", "-", "Heavy 3, Entangle (2), Twin-linked")])
    pd.weapon(ctx, "Psyk-Out Grenade Launchers", [(None, '12"', "3", "5", 'Assault 2, Blast (3"), Psy-shock, Pinning')])
    pd.wargear(ctx, "Reinforced Vratine Chassis", CHASSIS)
    for name, _, text, rules in CHASSIS_UPGRADES:
        pd.wargear(ctx, name, text, rules)


def spec():
    return {"name": NAME, "model": NAME, "slot": "Fast Attack", "type": "Armiger (Anathema Psykana)",
            "stats": ["9", "5", "4", "6", "6", "5", "5", "3", "9", "2+"], "max": 3, "unit_pts": 5, "model_pts": 150,
            "wargear": ["Reinforced Vratine Chassis", "Psyk-Out Grenade Launchers", "Searchlights", "Smoke Launchers"],
            "rules": [("Silent Sisterhood (X)", None), ("Hatred (X)", "Hatred (Psykers, Daemons, Corrupted)")],
            "arms": [("Close-Combat Arm", [("Dread-Executioner Greatblade", 0, ["Dread-Executioner Greatblade"], None,
                                            None),
                                           ("Sanctified Power Claw", 10, ["Sanctified Power Claw"], None, None)]),
                     ("Ranged Arm", [("Twin-linked Psyk-Out Bolt Cannon", 0, ["Twin-linked Psyk-Out Bolt Cannon"], None,
                                      None),
                                     ("Twin-linked Heavy Alchem-Flamer", 5, ["Twin-linked Heavy Alchem-Flamer"], None,
                                      None),
                                     ("Twin-Linked Adrathic Destructor", 20, ["Twin-Linked Adrathic Destructor"], None,
                                      None),
                                     ("Twin-linked Snare Cannon", 10, ["Twin-linked Snare Cannon"], None, None)])],
            "carapace": [("Chassis Upgrades", [(n, c, None) for n, c, _, _ in CHASSIS_UPGRADES], None)],
            "upgrades": [("Anathema Psykana Chamber Assignment",
                          [(name, pts, text, None, rules) for _, name, pts, text, rules in CHAMBER_UPGRADES], None)]}


def main():
    cat = et.Text(CAT)
    if f'name="{NAME}"' in cat.s:
        sys.exit(f"{CAT} already has the {NAME}")
    entries, rules = pd.index([pd.GST] + LIBS + [CAT])
    ctx = pd.Ctx(KEY, entries, rules)
    new_rules = []
    for name, text in RULES:
        r = ET.Element("rule", {"id": pd.mid(KEY, "rule", name), "name": name, "hidden": "false"})
        el(r, "description").text = text
        new_rules.append(r)
        rules[norm(name)] = r.get("id")
    weapons(ctx)
    s = spec()
    unit = pd.unit_entry(ctx, s)
    uid = unit.get("id")
    el(unit.find("categoryLinks"), "categoryLink", id=pd.mid(KEY, "cat", "anathema"), name=ANATHEMA[1], hidden=False,
       targetId=ANATHEMA[0], primary=False)
    el(unit.find("infoLinks"), "infoLink", id=pd.mid(KEY, "rule", "anathema"), name=ANATHEMA[1], hidden=False,
       targetId=ANATHEMA_RULE, type="rule")
    # the Chamber Assignment: required; each upgrade brings its Chamber's entry and the Chamber's category
    g = next(x for x in unit.find("selectionEntryGroups") if x.get("name") == "Anathema Psykana Chamber Assignment")
    add_constraint(g, "min", 1, pd.mid(KEY, "chamber", "min"))
    for chamber, name, *_ in CHAMBER_UPGRADES:
        cat_id, entry = CHAMBERS[chamber]
        up = next(e for e in ctx.new if e.get("name") == name)
        link = el(child(up, "entryLinks"), "entryLink", id=pd.mid(KEY, "chamber", chamber), import_=True, hidden=False,
                  collective=False, name=f"Silent Sisterhood (Chamber of {chamber})", targetId=entry,
                  type="selectionEntry")
        add_constraint(link, "min", 1, pd.mid(KEY, "chamber", chamber, "min"))
        mod = el(child(unit, "modifiers"), "modifier", type="add", field="category", value=cat_id)
        el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid,
           childId=up.get("id"), shared=True, includeChildSelections=True, includeChildForces=False,
           percentValue=False)
    root = et.E("entryLink", id=pd.mid(KEY, "root"), name=NAME, hidden=False, collective=False, import_=False,
                targetId=uid, type="selectionEntry")
    cats = el(root, "categoryLinks")
    el(cats, "categoryLink", id=pd.mid(KEY, "root", "unit"), name=bc.UNIT_CATEGORY[1], hidden=False,
       targetId=bc.UNIT_CATEGORY[0], primary=False)
    cid, cname, _ = bc.SLOTS["Fast Attack"][0]
    el(cats, "categoryLink", id=pd.mid(KEY, "root", "slot"), name=cname, hidden=False, targetId=cid, primary=True)
    cat.add_top("entryLinks", [root])
    cat.add_top("sharedSelectionEntries", ctx.new + [unit])
    cat.add_top("sharedRules", new_rules)
    cat.bump("catalogue")
    cat.save()
    print(f"{CAT}: {NAME}, {len(ctx.new)} weapons and upgrades, {len(new_rules)} rules")


if __name__ == "__main__":
    main()
