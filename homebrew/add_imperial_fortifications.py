#!/usr/bin/env python3
"""Add the Imperial and Traitor Fortifications (homebrew/source/imperial-fortifications.md) to 2022 - Horus Heresy.gst.

usage: python3 homebrew/add_imperial_fortifications.py

The doc's four Fortifications (Strategic Listening Post, Automated Sentry Turret Battery, Thermo-Plasma Conduit
Tower, Orbital Uplink Bunker) become Fortification choices in the game system beside its standard Fortifications,
so every army may take them. faction_fortifications.py hides them from the armies the doc leaves out (the Xenos
armies, the Daemons of the Ruinstorm, Necrons, Leagues of Votann and Rillietann). Reinforced Armoured Plating sets the
Fortification's Front, Side and Rear Armour to 13 on its profile. It refuses to run twice."""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import expansion_tools as et  # noqa: E402
from build_catalogue import child, el  # noqa: E402
from expansion_tools import Text, mid  # noqa: E402

DOC = "homebrew/source/imperial-fortifications.md"
GST = et.GST
GST_ID = "28d4-bd2e-4858-ece6"
FORTIFICATION = ("a24f-12d8-36c1-f477", "Fortification:")
ARMOUR = {"Front", "Side", "Rear"}


def plating(unit):
    """Reinforced Armoured Plating: Front, Side and Rear Armour 13 on the profile while it is taken."""
    link = next((l for l in unit.iter("entryLink") if l.get("name") == "Reinforced Armoured Plating"), None)
    if link is None:
        return
    for prof in unit.iter("profile"):
        for ch in prof.iter("characteristic"):
            if ch.get("name") in ARMOUR:
                m = el(child(prof, "modifiers"), "modifier", type="set", field=ch.get("typeId"), value=13)
                el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections",
                   scope=unit.get("id"), childId=link.get("targetId"), shared=True, includeChildSelections=True,
                   includeChildForces=False)


def twin_linked(units, gst_entries):
    """A "Twin-linked X" the builder linked to the single X: link the game system's own Twin-linked X instead."""
    by_name = {e.get("name").lower(): e.get("id") for e in gst_entries}
    names = {e.get("id"): e.get("name") for e in gst_entries}
    for u in units:
        for l in u.iter("entryLink"):
            want = l.get("name", "").lower()
            if want.startswith("twin-linked ") and not names.get(l.get("targetId"), "").lower().startswith("twin"):
                if want in by_name:
                    l.set("targetId", by_name[want])


def main():
    et.configure(GST, [], DOC, "Imperial Fortifications", "imperial-fortifications")
    b, root = et.build()
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    forts = [entries[b.units[d["name"]]] for d in b.datasheets if d["slot"] == "Fortifications"]
    if len(forts) != 4:
        sys.exit(f"expected 4 Fortifications in the doc, found {len(forts)}")
    gst = Text(GST)
    if f'name="{forts[0].get("name")}"' in gst.s:
        sys.exit(f"{GST} already has the Imperial Fortifications")
    idx = et.official_index()
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx, units=forts)

    gst_entries = list(ET.parse(GST).getroot().find(et.NS["gst"] + "sharedSelectionEntries"))
    twin_linked(units, gst_entries)
    roots = []
    for u in units:
        uid = u.get("id")
        et.drop_unit_category(u)
        for il in list(u.iter("infoLink")):  # no faction rule (Xenos) on a game system entry
            if il.get("name") == "Xenos":
                for p in u.iter():
                    if il in list(p):
                        p.remove(il)
        plating(u)
        link = et.E("entryLink", id=mid(uid, "root"), name=u.get("name"), hidden=False, collective=False,
                    import_=True, targetId=uid, type="selectionEntry")
        lc = el(link, "categoryLinks")
        el(lc, "categoryLink", id=mid(uid, "root", "unit"), name=et.UNIT[1], hidden=False, targetId=et.UNIT[0],
           primary=False)
        el(lc, "categoryLink", id=mid(uid, "root", "fortification"), name=FORTIFICATION[1], hidden=False,
           targetId=FORTIFICATION[0], primary=True)
        roots.append(link)

    gst.add(GST_ID, "entryLinks", roots)
    gst.add(GST_ID, "sharedSelectionEntries", units + keep_entries)
    if keep_groups:
        gst.add(GST_ID, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        gst.add(GST_ID, "sharedRules", keep_rules)
    gst.bump("gameSystem")
    gst.save()
    print(f"{GST}: {len(units)} Fortifications, {len(keep_entries)} entries, {len(keep_groups)} groups, "
          f"{len(keep_rules)} rules added")
    for r in roots:
        print(f'  "{r.get("id")}": "{r.get("name")}"')


if __name__ == "__main__":
    main()
