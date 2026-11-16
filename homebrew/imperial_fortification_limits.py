#!/usr/bin/env python3
"""Enforce the restrictions of the Imperial and Traitor Fortifications in 2022 - Horus Heresy.gst.

usage: python3 homebrew/imperial_fortification_limits.py

Orbital Strike Coordinates (Orbital Uplink Bunker) is "Legiones Astartes and Solar Auxilia only": it is hidden, and an
error if taken, in a Detachment that holds none of their army-wide entries (the eighteen Legions, the Blackshields,
the Shattered Legions and the Solar Auxilia). Which armies may take the Fortifications at all is set by
faction_fortifications.py. Running it again replaces what it added before."""
import re
import sys

sys.path.insert(0, "homebrew")
from build_catalogue import el  # noqa: E402
from expansion_tools import E, Text, mid  # noqa: E402
import expansion_tools as et  # noqa: E402

GST = et.GST
STRIKE = "a7ca-e0f7-f61c-1be0"  # Orbital Strike Coordinates
COMMENT = "Legiones Astartes and Solar Auxilia only"
# the army-wide entry a Detachment of each army holds
ARMIES = {
    "b2b4-2198-0b90-dd9f": "I: Dark Angels", "d744-9ab9-93ab-ce79": "III: Emperor's Children",
    "5f54-457a-fbb9-6730": "IV: Iron Warriors", "e01e-5cdd-e512-8353": "V: White Scars",
    "4916-965e-8339-44f6": "VI: Space Wolves", "a0e1-f2c4-8bcd-0723": "VII: Imperial Fists",
    "b28b-71f7-e4f4-8f9c": "VIII: Night Lords", "296e-301e-3ce1-1c15": "IX: Blood Angels",
    "bfc9-c99c-bf8a-3917": "X: Iron Hands", "90ee-77dd-1b7f-ddfe": "XII: World Eaters",
    "8e0f-3552-8842-f281": "XIII: Ultramarines", "dd1f-1c51-706c-e5f7": "XIV: Death Guard",
    "21c3-2f28-7820-e51a": "XV: Thousand Sons", "01b4-57c7-bf61-2abf": "XVI: Sons of Horus",
    "9dbf-0760-d7ae-f125": "XVII: Word Bearers", "c805-ca3a-ff93-5e2f": "XVIII: Salamanders",
    "dc34-fe08-dd44-fb99": "XIX: Raven Guard", "c0df-c1fa-5ddc-9ee5": "XX: Alpha Legion",
    "ae4a-f95c-968e-eb46": "Blackshields", "9950-2cd2-fd88-9bb1": "Shattered Legions",
    "f689-fd0d-ffb0-c255": "Solar Auxilia"}


def condition(parent, cid, kind):
    el(parent, "condition", type=kind, value=1, field="selections", scope="force", childId=cid, shared=True,
       includeChildSelections=True, includeChildForces=False)


def main():
    et.configure(GST, [], None, "Imperial Fortifications", "imperial-fortifications")
    gst = Text(GST)
    if f'id="{STRIKE}"' not in gst.s:
        sys.exit(f"{GST} has no Orbital Strike Coordinates: run add_imperial_fortifications.py first")
    old = gst.s
    # take out what an earlier run added
    start, end, _, _ = gst.block(STRIKE)
    body = gst.s[start:end]
    body = re.sub(r'\s*<modifier [^>]*>\s*<comment>' + COMMENT + r'</comment>.*?</modifier>', "", body, flags=re.S)
    body = re.sub(r'\s*<constraint [^>]*id="' + mid(STRIKE, "army only", "max") + r'"[^>]*/>', "", body)
    body = re.sub(r'\s*<(modifiers|constraints)>\s*</\1>', "", body)
    gst.s = gst.s[:start] + body + gst.s[end:]

    cid = mid(STRIKE, "army only", "max")
    con = E("constraint", type="max", value=0, field="selections", scope="force", shared=True, id=cid,
            percentValue=False, includeChildSelections=True, includeChildForces=False)
    hide = E("modifier", type="set", field="hidden", value="true")
    el(hide, "comment").text = COMMENT
    group = el(el(hide, "conditionGroups"), "conditionGroup", type="and")
    conds = el(group, "conditions")
    allow = E("modifier", type="set", field=cid, value=-1)
    el(allow, "comment").text = COMMENT
    any_conds = el(el(el(allow, "conditionGroups"), "conditionGroup", type="or"), "conditions")
    for aid in ARMIES:
        condition(conds, aid, "lessThan")
        condition(any_conds, aid, "atLeast")
    gst.add(STRIKE, "modifiers", [hide, allow])
    gst.add(STRIKE, "constraints", [con])
    if gst.s != old:
        gst.save()
        print(f"{GST}: Orbital Strike Coordinates limited to {len(ARMIES)} armies")


if __name__ == "__main__":
    main()
