"""Drukhari: a Sub-Faction Enhancement on a Drukhari Fortification only in a Detachment of its Sub-faction.

Called by build_catalogue.py for that faction. Each enhancement (written under "## Wargear" and offered on every
Drukhari Fortification) is hidden unless the Detachment has chosen its Sub-faction (Kabals, Wych Cults or
Haemonculus Covens), and is an error if taken in a Detachment of another Sub-faction.

A Realspace Raiders Detachment (Kabal, Wych Cult or Haemonculus Coven) may take only the Dread-Pod Drop-Turret or the
Razor-Blade Barricade as its Fortification: the other Drukhari Fortifications are hidden there, and an error if taken.

A Fortification with the Flesh-Crafted Carapace adds 1 to its Front, Side and Rear Armour Values on its profile
(to a maximum of 12).
"""
from build_catalogue import add_constraint, child, el, make_id

ENHANCEMENTS = {"Splinter-Rack Munitions": "Kabals", "Combat-Drug Atomisers": "Wych Cults",
                "Flesh-Crafted Carapace": "Haemonculus Covens"}


REALSPACE = ["Drukhari Realspace Raiders: Kabal Detachment", "Drukhari Realspace Raiders: Wych Cult Detachment",
             "Drukhari Realspace Raiders: Haemonculus Coven Detachment"]
NOT_IN_REALSPACE = ["Torture-Spire", "Kabalite Blade-Bastion", "Void-Raptor Sky-Dock", "Grand Kabalite Terror-Spire",
                    "Dark-Light Shadow-Pylon"]


def realspace_limits(b):
    fids = [make_id("force", b.faction, n) for n in REALSPACE]
    for link in b.root.find("entryLinks"):
        if link.get("name") not in NOT_IN_REALSPACE:
            continue
        cid = add_constraint(link, "max", -1, make_id(link.get("id"), "not in realspace"), scope="force",
                             children=True)
        for field, value in (("hidden", "true"), (cid, 0)):
            m = el(child(link, "modifiers"), "modifier", type="set", field=field, value=value)
            conds = el(el(el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
            for fid in fids:
                el(conds, "condition", type="instanceOf", value=1, field="selections", scope="ancestor",
                   childId=fid, shared=True, includeChildSelections=True, includeChildForces=False)


def carapace(b):
    """Flesh-Crafted Carapace: +1 Front, Side and Rear Armour on the Fortification's profile while it is taken."""
    for u in b.shared_entries.iter("selectionEntry"):
        if u.get("type") != "unit":
            continue
        link = next((l for l in u.iter("entryLink") if l.get("name") == "Flesh-Crafted Carapace"), None)
        if link is None:
            continue
        for prof in u.iter("profile"):
            for ch in prof.iter("characteristic"):
                if ch.get("name") not in ("Front", "Side", "Rear") or not (ch.text or "").strip().isdigit():
                    continue
                if int(ch.text) >= 12:
                    continue
                m = el(child(prof, "modifiers"), "modifier", type="increment", field=ch.get("typeId"), value=1)
                el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections",
                   scope=u.get("id"), childId=link.get("targetId"), shared=True, includeChildSelections=True,
                   includeChildForces=False)


def apply(b):
    realspace_limits(b)
    carapace(b)
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
