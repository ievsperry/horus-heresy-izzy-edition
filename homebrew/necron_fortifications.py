"""Necrons: the Armour changes of the Necron Fortifications' options, on their profiles.

Called by build_catalogue.py for that faction. A Necron Obelisk upgraded to a Fortified Obelisk (by taking a
twin-linked tesla destructor or heavy gauss cannon) has Front, Side and Rear Armour 12; a Fortification with
Reinforced Necrodermis Plating has 13.
"""
from build_catalogue import child, el

# unit: {option taken: armour}
ARMOUR = {"Necron Obelisk": {"Twin-linked tesla destructor": 12, "Heavy gauss cannon": 12},
          "Summoning Core": {"Reinforced Necrodermis Plating": 13},
          "Greater Summoning Core": {"Reinforced Necrodermis Plating": 13}}


def apply(b):
    done = set()
    for u in b.shared_entries.iter("selectionEntry"):
        opts = ARMOUR.get(u.get("name"))
        if u.get("type") != "unit" or not opts:
            continue
        for l in u.iter("entryLink"):
            value = opts.get(l.get("name"))
            if value is None:
                continue
            done.add((u.get("name"), l.get("name")))
            for prof in u.iter("profile"):
                for ch in prof.iter("characteristic"):
                    if ch.get("name") in ("Front", "Side", "Rear"):
                        m = el(child(prof, "modifiers"), "modifier", type="set", field=ch.get("typeId"), value=value)
                        el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections",
                           scope=u.get("id"), childId=l.get("targetId"), shared=True,
                           includeChildSelections=True, includeChildForces=False)
    missing = {(u, o) for u, opts in ARMOUR.items() for o in opts} - done
    if missing:
        b.problems.append(f"Necron Fortification armour options not found: {sorted(missing)}")
