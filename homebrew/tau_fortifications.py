"""T'au Empire: a Sept Enhancement on a T'au Fortification only in a Detachment of its Sept.

Called from tau_rites.apply (the faction's hook in build_catalogue.py). Each enhancement (written under "### Items"
and offered on every T'au Fortification) is hidden unless the Detachment has chosen its Sept, and is an error if
taken in a Detachment of another Sept.
"""
from build_catalogue import add_constraint, child, el, make_id

ENHANCEMENTS = {"Coordinated Fire-Control": "T'au Sept", "Hot-Blooded Thrust-Relays": "Vior'la",
                "Experimental Weapon Accelerators": "Bork'an", "Urban Camouflage Matrix": "Sa'cea",
                "Close-Quarters Sensor-Grid": "Farsight Enclaves"}


def apply(b):
    septs = {e.get("id") for e in b.root.iter("selectionEntry")}
    done = set()
    for e in b.shared_entries.iter("selectionEntry"):
        sept = ENHANCEMENTS.get(e.get("name"))
        if not sept or e.get("id") in done:
            continue
        sid = make_id("fleet", b.faction, sept)
        if sid not in septs:
            b.problems.append(f"Sept Enhancement: no Sept '{sept}'")
            continue
        done.add(e.get("id"))
        m = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
        el(el(m, "conditions"), "condition", type="lessThan", value=1, field="selections", scope="force",
           childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
        cid = add_constraint(e, "max", 0, make_id(e.get("id"), "sept only"))
        m = el(child(e, "modifiers"), "modifier", type="set", field=cid, value=1)
        el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
           childId=sid, shared=True, includeChildSelections=True, includeChildForces=False)
    missing = set(ENHANCEMENTS) - {e.get("name") for e in b.shared_entries.iter("selectionEntry")
                                   if e.get("id") in done}
    if missing:
        b.problems.append(f"Sept Enhancements not found: {sorted(missing)}")
