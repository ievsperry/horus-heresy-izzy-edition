"""Necrons: the Armour changes of the Necron Fortifications' options, on their profiles.

Called by build_catalogue.py for that faction. A Necron Obelisk upgraded to a Fortified Obelisk (by taking a
twin-linked tesla destructor or heavy gauss cannon) has Front, Side and Rear Armour 12; a Fortification with
Reinforced Necrodermis Plating has 13. set_armour() also serves the Tyranid and Votann Fortifications' armour options.
"""
from build_catalogue import child, el

# unit: {option taken: armour}
ARMOUR = {"Necron Obelisk": {"Twin-linked tesla destructor": 12, "Heavy gauss cannon": 12},
          "Summoning Core": {"Reinforced Necrodermis Plating": 13},
          "Greater Summoning Core": {"Reinforced Necrodermis Plating": 13},
          "Tomb-World Phase-Projector": {"Reinforced Necrodermis Plating": 13}}


def apply(b):
    set_armour(b, ARMOUR, "Necron")


def set_armour(b, table, label):
    """table: {unit: {option taken: armour for Front, Side and Rear, or {"Rear": 14, ...}}}."""
    done = set()
    for u in b.shared_entries.iter("selectionEntry"):
        opts = table.get(u.get("name"))
        if u.get("type") != "unit" or not opts:
            continue
        for l in u.iter("entryLink"):
            value = opts.get(l.get("name"))
            if value is None:
                continue
            done.add((u.get("name"), l.get("name")))
            sides = value if isinstance(value, dict) else {k: value for k in ("Front", "Side", "Rear")}
            for prof in u.iter("profile"):
                for ch in prof.iter("characteristic"):
                    if ch.get("name") in sides:
                        m = el(child(prof, "modifiers"), "modifier", type="set", field=ch.get("typeId"),
                               value=sides[ch.get("name")])
                        el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections",
                           scope=u.get("id"), childId=l.get("targetId"), shared=True,
                           includeChildSelections=True, includeChildForces=False)
    missing = {(u, o) for u, opts in table.items() for o in opts} - done
    if missing:
        b.problems.append(f"{label} Fortification armour options not found: {sorted(missing)}")
