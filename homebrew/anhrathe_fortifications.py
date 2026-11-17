"""Anhrathe: limits on the Anhrathe Fortifications the doc's wording alone cannot carry.

Called by build_catalogue.py for that faction. The Corsair Lance-Pod may exchange only two of its four
shuriken cannons for splinter cannons, so its swap allows at most two splinter cannons.
"""


def apply(b):
    for u in b.shared_entries.iter("selectionEntry"):
        if u.get("type") != "unit" or u.get("name") != "Corsair Lance-Pod":
            continue
        for g in u.iter("selectionEntryGroup"):
            if g.get("name") != "Exchange shuriken cannons":
                continue
            for link in g.iter("entryLink"):
                if link.get("name") == "Splinter cannon":
                    for c in link.iter("constraint"):
                        if c.get("type") == "max":
                            c.set("value", "2")
                    return
    b.problems.append("Corsair Lance-Pod: no splinter cannon swap to limit")
