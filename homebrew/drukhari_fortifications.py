"""Drukhari: a Sub-Faction Enhancement on a Drukhari Fortification only in a Detachment of its Sub-faction.

Called by build_catalogue.py for that faction. Each enhancement (written under "## Wargear" and offered on every
Drukhari Fortification) is hidden unless the Detachment has chosen its Sub-faction (Kabals, Wych Cults or
Haemonculus Covens), and is an error if taken in a Detachment of another Sub-faction.
"""
from build_catalogue import add_constraint, child, el, make_id

ENHANCEMENTS = {"Splinter-Rack Munitions": "Kabals", "Combat-Drug Atomisers": "Wych Cults",
                "Flesh-Crafted Carapace": "Haemonculus Covens"}


def apply(b):
    subs = {e.get("id") for e in b.root.iter("selectionEntry")}
    done = set()
    for e in b.shared_entries.iter("selectionEntry"):
        sub = ENHANCEMENTS.get(e.get("name"))
        if not sub or e.get("id") in done:
            continue
        sid = make_id("fleet", b.faction, sub)
        if sid not in subs:
            b.problems.append(f"Sub-Faction Enhancement: no Sub-faction '{sub}'")
            continue
        done.add(e.get("id"))
        m = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
        el(el(m, "conditions"), "condition", type="lessThan", value=1, field="selections", scope="force",
           childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
        cid = add_constraint(e, "max", 0, make_id(e.get("id"), "sub-faction only"))
        m = el(child(e, "modifiers"), "modifier", type="set", field=cid, value=1)
        el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
           childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
    missing = set(ENHANCEMENTS) - {e.get("name") for e in b.shared_entries.iter("selectionEntry")
                                   if e.get("id") in done}
    if missing:
        b.problems.append(f"Sub-Faction Enhancements not found: {sorted(missing)}")
