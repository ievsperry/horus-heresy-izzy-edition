#!/usr/bin/env python3
"""Add Liber Centura's 0-1 Sanguinary Guard (homebrew/source/centura.md, IX – Blood Angels) to
2022 - LA - Blood Angels.cat, beside the official Sanguinary Guard Squad.

usage: python3 homebrew/add_centura_sanguinary_guard.py

The doc makes it a Retinue Squad only (Sanguinary Retinue), so it has no root entry: it is a choice in the Blood
Angels leaders' Retinue pick, shown when the leader is Sanguinius or has a Warhawk Jump Pack, and at most one per
army. "Master of the Legion" and the deployment rules are its rule text. add_centura.py leaves it out
(LEGION_EXISTING). It refuses to run twice."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_centura as ac  # noqa: E402
import add_mechanicum as am  # noqa: E402
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402

LEGION = "Blood Angels"
NAME = "Sanguinary Guard"
RETINUE = "6307-ed53-0ac4-0212"  # the Blood Angels leaders' Retinue pick
SANGUINIUS = "2c54-82c1-c1e4-3aee"
WARHAWK = ["a298-8584-70ed-18ce", "e7bc-371f-3d14-4968"]  # Warhawk Jump Pack (Blood Angels, library)


def main():
    path = ac.legion_file(LEGION)
    sec = dict(ac.legion_sections())[LEGION]
    others = tuple(m.group(1) for m in re.finditer(r"^#### (?:0-\d+ )?([^\n]+?) — \d+ pts$", sec, re.M)
                   if m.group(1) != NAME)
    ac.LEGION_EXISTING = {LEGION: others}  # only the Sanguinary Guard
    am.ALLOWED = ac.ALLOWED + ac.LEGION_ALLOWED
    am.LIBS = [ac.LIBRARY, "2022 - Mech Library.cat"]
    key = f"liber centura {LEGION} sanguinary guard"
    if et.make_id(key, "retinue") in open(path, encoding="utf-8").read():
        sys.exit(f"{path} already has the Liber Centura Sanguinary Guard")

    def hook(b, root, entries):
        ac.DOC_ENTRIES.extend(root.find("sharedSelectionEntries"))
        ac.consularis_links(b, entries)
        return ac.fill_empty(b, root, key) | ac.profile_owners(root)

    cat, b, entries, units, roots, keep = am.transplant_into(path, ac.legion_text(LEGION, sec),
                                                             f"Legiones Astartes ({LEGION})", key, hook)
    if [u.get("name") for u in units] != [NAME]:
        sys.exit(f"expected only the {NAME}, built {[u.get('name') for u in units]}")
    unit = units[0]
    for r in roots:  # a Retinue Squad: no Force Organisation slot of its own
        cat.remove(r.get("id"))
    lid = et.make_id(key, "retinue")
    link = et.E("entryLink", id=lid, name=f"{NAME} (Liber Centura)", hidden=True, collective=False, import_=True,
                targetId=unit.get("id"), type="selectionEntry")
    bc.add_constraint(link, "max", 1, lid + "army", scope="roster", children=True)
    m = bc.el(bc.el(link, "modifiers"), "modifier", type="set", field="hidden", value="false")
    bc.el(m, "comment").text = "Sanguinary Retinue: led by Sanguinius or a model with a Warhawk Jump Pack"
    g = bc.el(bc.el(m, "conditionGroups"), "conditionGroup", type="or")
    conds = bc.el(g, "conditions")
    bc.el(conds, "condition", type="instanceOf", value=1, field="selections", scope="parent", childId=SANGUINIUS,
          shared=True, includeChildSelections=False, includeChildForces=False, percentValue=False)
    for w in WARHAWK:
        bc.el(conds, "condition", type="atLeast", value=1, field="selections", scope="parent", childId=w,
              shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    cat.add(RETINUE, "entryLinks", [link])
    cat.bump("catalogue")
    cat.save()
    print(f"{path}: {NAME} (Liber Centura) in the Retinue pick, {len(keep)} entries")


if __name__ == "__main__":
    main()
