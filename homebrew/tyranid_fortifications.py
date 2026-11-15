"""Tyranids: a Hive Fleet Enhancement on a Bio-Fortification only in a Detachment of its Hive Fleet.

Called by build_catalogue.py for that faction. Each enhancement (written under "## Bio-Fortification Wargear"
and offered on every Bio-Fortification) is hidden unless the Detachment has chosen its Hive Fleet, and is an
error if taken in a Detachment of another Hive Fleet.
"""
from build_catalogue import add_constraint, child, el, make_id

ENHANCEMENTS = {"Seismic Tremor-Roots": "Behemoth", "Pheromone Trail Beacon": "Kraken",
                "Dominion Synapse Node": "Leviathan", "Shadow in the Warp Emitter": "Kronos",
                "Chitinous Tunnel-Network": "Jormungandr", "Endless Brood-Vats": "Hydra"}


def apply(b):
    fleets = {e.get("id") for e in b.root.iter("selectionEntry")}
    done = set()
    for e in b.shared_entries.iter("selectionEntry"):
        fleet = ENHANCEMENTS.get(e.get("name"))
        if not fleet or e.get("id") in done:
            continue
        fid = make_id("fleet", b.faction, fleet)
        if fid not in fleets:
            b.problems.append(f"Hive Fleet Enhancement: no Hive Fleet '{fleet}'")
            continue
        done.add(e.get("id"))
        m = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
        el(el(m, "conditions"), "condition", type="lessThan", value=1, field="selections", scope="force",
           childId=fid, shared=True, includeChildSelections=True, includeChildForces=False)
        cid = add_constraint(e, "max", 0, make_id(e.get("id"), "fleet only"))
        m = el(child(e, "modifiers"), "modifier", type="set", field=cid, value=1)
        el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
           childId=fid, shared=True, includeChildSelections=True, includeChildForces=False)
    missing = set(ENHANCEMENTS) - {e.get("name") for e in b.shared_entries.iter("selectionEntry") if e.get("id") in done}
    if missing:
        b.problems.append(f"Hive Fleet Enhancements not found: {sorted(missing)}")
