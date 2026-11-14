#!/usr/bin/env python3
"""Add the Corrupted Clade Assassins (Agents of the Warmaster) to LI - Assassins and Agents, and link them from every
official catalogue that links the Cults Abominatio.

usage: python3 homebrew/add_corrupted_assassins.py

The doc (homebrew/source/corrupted-assassins.md) is read by build_catalogue.py's Builder; its six Clades move into
2022 - LI - Assassins.cat as text, each with the Character category, and at most one of each Clade in a Detachment.
They are taken as one "Corrupted Clade Assassins" Elites choice (a pick of one Clade, as the official Clade Assassins
(Loyalist) are), shown only in a Traitor Detachment. A Detachment may take one, or three in an Army of Dark
Compliance or with The Coils of the Hydra (Alpha Legion) or The Black Reaving (Sons of Horus) Rite of War.

The homebrew Traders Militant and Armies of Dark Compliance catalogues are built by their own scripts:
traders_militant_limits.py links the choice there, and build_dark_compliance.py copies the Imperialis Militia link,
so rebuild both after running this. It refuses to run on a library that already has the Clades."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, child, el  # noqa: E402
from expansion_tools import E, Text, mid  # noqa: E402

LIBRARY = "2022 - LI - Assassins.cat"
LIBRARY_ID = "4c88-1a81-7e53-0a67"
DOC = "homebrew/source/corrupted-assassins.md"
et.configure(LIBRARY, [], DOC, "Corrupted Clade Assassins", "corrupted clade assassins")

CHARACTER = ("f75a-d5c1-59ba-5c5a", "Character")
TRAITOR = "f9c0-0c5a-3e24-58c7"  # the Traitor allegiance
ELITES = ("7aee-565f-b0ae-294e", "Elites:")
# up to three in a Detachment with one of these: The Coils of the Hydra, The Black Reaving, Army of Dark Compliance
THREE_WITH = ["1af3-e23e-8831-e011", "e6ec-f3e6-760c-f9bb", "12cc-71f9-31de-349a"]
# the official catalogues that link the Cults Abominatio (the homebrew ones are built by their own scripts)
CATALOGUES = ["2022 - Daemons - Daemons of the Ruinstorm.cat", "2022 - Imperialis Militia.cat",
              "2022 - LI - Solar Auxilia.cat", "2022 - Legiones Astartes.cat", "2022 - Mechanicum.cat",
              "2022 - Questoris Household.cat", "2022 - Titan Legions.cat"]
CHOICE = mid("choice")  # the Corrupted Clade Assassins entry other catalogues link


def cond(parent, childId, kind="atLeast", value=1, scope="force"):
    el(child(parent, "conditions"), "condition", type=kind, value=value, field="selections", scope=scope,
       childId=childId, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)


def root_link(cat_name):
    """The catalogue's Elites choice, shown only in a Traitor Detachment."""
    key = re.sub(r"\W+", " ", cat_name).strip().lower()
    l = E("entryLink", import_=True, name="Corrupted Clade Assassins", hidden=False, id=mid("root", key),
          type="selectionEntry", targetId=CHOICE)
    m = el(child(l, "modifiers"), "modifier", type="set", field="hidden", value="true")
    el(m, "comment").text = "Agents of the Warmaster: Traitor Detachments only"
    cond(m, TRAITOR, "equalTo", 0)
    cats = child(l, "categoryLinks")
    cats.append(E("categoryLink", id=mid("root", key, "unit"), name=et.UNIT[1], hidden=False, targetId=et.UNIT[0],
                  primary=False))
    cats.append(E("categoryLink", id=mid("root", key, "elites"), name=ELITES[1], hidden=False, targetId=ELITES[0],
                  primary=True))
    return l


def main():
    lib = Text(LIBRARY)
    if CHOICE in lib.s:
        sys.exit(f"{LIBRARY} already has the Corrupted Clade Assassins")
    idx = et.official_index()
    b, root = et.build()
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx)
    for u in units:
        cats = et.drop_unit_category(u)
        cats.append(E("categoryLink", id=mid(u.get("id"), "character"), name=CHARACTER[1], hidden=False,
                      targetId=CHARACTER[0], primary=False))
        add_constraint(u, "max", 1, mid(u.get("id"), "one per detachment"), scope="force", children=True)

    # the Elites choice: a pick of one Clade, one choice per Detachment (three with the Rites or Dark Compliance)
    choice = E("selectionEntry", type="upgrade", import_=True, name="Corrupted Clade Assassins", hidden=False, id=CHOICE)
    cid = add_constraint(choice, "max", 1, mid("choice", "max"), scope="force", children=True)
    m = el(child(choice, "modifiers"), "modifier", type="set", field=cid, value=3)
    el(m, "comment").text = "Up to three with The Coils of the Hydra, The Black Reaving or an Army of Dark Compliance"
    g = el(child(m, "conditionGroups"), "conditionGroup", type="or")
    for t in THREE_WITH:
        cond(g, t)
    grp = el(child(choice, "selectionEntryGroups"), "selectionEntryGroup", name="Corrupted Clade Assassins",
             hidden=False, id=mid("choice", "clades"))
    add_constraint(grp, "min", 1, mid("choice", "clades", "min"))
    add_constraint(grp, "max", 1, mid("choice", "clades", "max"))
    for u in units:
        el(child(grp, "entryLinks"), "entryLink", import_=True, name=u.get("name"), hidden=False,
           id=mid("choice", u.get("name")), type="selectionEntry", targetId=u.get("id"))
    bc.add_cost(choice, 0)

    lib.add(LIBRARY_ID, "sharedSelectionEntries", units + keep_entries + [choice])
    if keep_groups:
        lib.add(LIBRARY_ID, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        lib.add(LIBRARY_ID, "sharedRules", keep_rules)
    lib.bump("catalogue")
    lib.save()
    for f in CATALOGUES:
        cat = Text(f)
        cat_id = re.search(r'<catalogue [^>]*?\bid="([^"]+)"', cat.s).group(1)
        cat.add(cat_id, "entryLinks", [root_link(f)])
        cat.bump("catalogue")
        cat.save()
    print(f"{LIBRARY}: {len(units)} Clades, {len(keep_entries)} entries, {len(keep_rules)} rules; "
          f"linked from {len(CATALOGUES)} catalogues")


if __name__ == "__main__":
    main()
