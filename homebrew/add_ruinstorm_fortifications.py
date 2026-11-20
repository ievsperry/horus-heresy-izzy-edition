#!/usr/bin/env python3
"""Add the Daemonic Fortifications (homebrew/source/ruinstorm.md, "## Fortifications") to
2022 - Daemons - Daemons of the Ruinstorm.cat.

usage: python3 homebrew/add_ruinstorm_fortifications.py

The doc's four Fortifications become Fortification choices with the Daemon Unit Type and Traitor. Each may take one
Ætheric Dominion Enhancement ("## Daemonic Fortification Wargear"), shown only with its Dominion and an error with
another. The game system's own Fortifications are hidden from a Ruinstorm Detachment by faction_fortifications.py.
Run again after a Fortification is added to the doc, it adds only that one; it refuses to run when there is
nothing new."""
import re
import sys

sys.path.insert(0, "homebrew")
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, child, el  # noqa: E402
from expansion_tools import Text, mid  # noqa: E402
import add_ruinstorm as ar  # noqa: E402

FORTIFICATION = ("a24f-12d8-36c1-f477", "Fortification:")
# the doc's enhancement, by the Dominion it needs
ENHANCEMENTS = {"Blood-Slicked Foundation": "Heedless Slaughter", "Festering Contagion": "Putrid Corruption",
                "Warp-Storm Conduit": "Infernal Tempest", "Cacophony of Excess": "Rapturous Sensation",
                "Reality-Fracture Anchor": "Encroaching Ruin", "Soul-Forge Furnace": "Malevolent Artifice",
                "Shifting Nightmare": "Formless Distortion", "Beacon of Undivided Chaos": "Ravenous Dissolution"}


def main():
    text = open(ar.DOC, encoding="utf-8").read()
    b, root = et.build(text)
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    forts = [entries[b.units[d["name"]]] for d in b.datasheets if d["slot"] == "Fortifications"]
    if not forts:
        sys.exit("no Fortifications in the doc")
    cat = Text(ar.CAT)
    present = {f.get("name") for f in forts if f'id="{f.get("id")}"' in cat.s}
    forts = [f for f in forts if f.get("name") not in present]   # a Fortification added to the doc since
    if not forts:
        sys.exit(f"{ar.CAT} already has the Daemonic Fortifications")
    idx = et.official_index()
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx, units=forts)
    existing = set(re.findall(r'\bid="([^"]+)"', cat.s))
    keep_entries = [e for e in keep_entries if e.get("id") not in existing]
    keep_groups = [g for g in keep_groups if g.get("id") not in existing]
    keep_rules = [r for r in keep_rules if r.get("id") not in existing]

    roots = []
    for u in units:
        uid = u.get("id")
        cats = et.drop_unit_category(u)
        cats.append(ar.category_link(*ar.DAEMON, uid))
        child(u, "infoLinks").append(ar.info_link("Traitor", ar.TRAITOR, uid))
        link = et.E("entryLink", id=mid(uid, "root"), name=u.get("name"), hidden=False, collective=False,
                    import_=False, targetId=uid, type="selectionEntry")
        lc = el(link, "categoryLinks")
        el(lc, "categoryLink", id=mid(uid, "root", "unit"), name=et.UNIT[1], hidden=False, targetId=et.UNIT[0],
           primary=False)
        el(lc, "categoryLink", id=mid(uid, "root", "fortification"), name=FORTIFICATION[1], hidden=False,
           targetId=FORTIFICATION[0], primary=True)
        et.fortification_categories(link, u)
        roots.append(link)

    found = set()
    for e in keep_entries:
        dom = ENHANCEMENTS.get(e.get("name"))
        if not dom:
            continue
        found.add(e.get("name"))
        did = ar.DOMINIONS[dom][0]
        m = ar.modifier(e, "hidden", "true")
        el(m, "comment").text = f"Ætheric Dominion Enhancement: {dom} only"
        ar.cond(m, did, kind="lessThan")
        cid = add_constraint(e, "max", 0, mid(e.get("id"), "dominion only"))
        ar.cond(ar.modifier(e, cid, 1), did)
    found |= {n for n in ENHANCEMENTS if f'name="{n}"' in cat.s}   # already there from an earlier run
    if found != set(ENHANCEMENTS):
        sys.exit(f"Enhancements not in the doc: {sorted(set(ENHANCEMENTS) - found)}")

    cat.add(ar.CAT_ID, "entryLinks", roots)
    cat.add(ar.CAT_ID, "sharedSelectionEntries", units + keep_entries)
    if keep_groups:
        cat.add(ar.CAT_ID, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        cat.add(ar.CAT_ID, "sharedRules", keep_rules)
    cat.bump("catalogue")
    cat.save()
    print(f"{ar.CAT}: {len(units)} Fortifications, {len(keep_entries)} entries, {len(keep_rules)} rules added")


if __name__ == "__main__":
    main()
