#!/usr/bin/env python3
"""Make the Power Pack available to Imperialis Militia Infantry Characters under the Kinfolk Helots Provenance.

usage: python3 homebrew/add_power_pack.py

The Power Pack and its weapons are shared entries of the game system (added by add_gst_weapons.py from the Power
Pack Weapons section of additional-weapons.md). This script lets a model take up to two different Power Pack
weapons (each at most once) at their points costs, and links the Power Pack to every Imperialis Militia model with the Infantry Unit
Type and Character Sub-type, hidden unless its Detachment has the Kinfolk Helots Provenance. Running it again
changes nothing."""
import re
import sys

sys.path.insert(0, "homebrew")
from faq_tools import GST, Ops, make_id  # noqa: E402

POWER_PACK = "e4f0-85a6-7252-4b76"
KINFOLK_HELOTS = "2bd7-54d3-b0a9-1e44"
COSTS = {"Circular Stone Saw": 5, "Gem Extractor": 10, "Kinfolk Arc Welder": 15, "Stone Burner": 10}
DESC = ("A model with a Power Pack may take up to two different weapons from the following list: Circular Stone Saw "
        "(+5 points), Gem Extractor (+10 points), Kinfolk Arc Welder (+15 points) and Stone Burner (+10 points). "
        "Only a model with both the Infantry Unit Type and the Character Sub-type, in a Detachment with the Kinfolk "
        "Helots Provenance, may take a Power Pack.")
MODELS = [
    ("IM - Force Commander", "1) Force Commander"),
    ("IM - Medicae Detachment", "Militia Medicae w/ Autopistol"),
    ("IM - Discipline Master Cadre", "Discipline Master"),
    ("IM - Command Cadre", "1) Militia Lieutenant"),
    ("IM - Infantry Squad", "Sergeant"),
    ("IM - Levy Squad", "Levy Sergeant"),
    ("IM - Grenadier Squad", "1) Grenadier Sergeant"),
    ("IM - Reconnaissance Squad", "Scout Sergeant"),
    ("IM - Ogryn Brute Squad", "Ogryn Boss"),
    ("IM - Rogue Psyker", "Rogue Psyker"),
]


def main():
    o = Ops()

    def power_pack():
        s = o.F.text[GST]
        nl = o.F.nl(GST)
        st = s.index(f'<selectionEntry id="{POWER_PACK}"')
        en = s.index("</selectionEntry>", s.index("</selectionEntryGroups>", st))
        b = s[st:en]
        b = re.sub(r'(<characteristic name="Description"[^>]*>)[^<]*(</characteristic>)',
                   lambda m: m.group(1) + DESC + m.group(2), b, count=1)

        def one_each(m):
            link = m.group(0)
            name = re.search(r'name="([^"]+)"', link).group(1)
            link = re.sub(r'(<cost [^>]*value=")[^"]*(")', lambda c: c.group(1) + str(COSTS[name]) + c.group(2),
                          link, count=1)
            if "<constraints>" in link:
                return link
            ind = m.group(1)
            lid = re.search(r'id="([^"]+)"', link).group(1)
            c = (f'{ind}  <constraints>{nl}{ind}    <constraint type="max" value="1" field="selections" scope="parent" '
                 f'shared="true" id="{make_id("power pack max", lid)}" includeChildSelections="false"/>{nl}'
                 f'{ind}  </constraints>{nl}')
            return link.replace(f"{ind}  <costs>", c + f"{ind}  <costs>", 1)
        b = re.sub(r'([ \t]*)<entryLink [^>]*>.*?</entryLink>', one_each, b, flags=re.S)
        if b != s[st:en]:
            o.F.replace(GST, st, en, b, "Power Pack: two different weapons")
    o.run("power pack", power_pack)

    for unit, model in MODELS:
        def go(unit=unit, model=model):
            p, sp = o.at("Imperialis Militia", unit, model)
            s = o.F.text[p]
            if POWER_PACK in s[sp[0]:sp[1]]:
                return
            nl = o.F.nl(p)
            ind = o.F.indent_of(p, sp[0]) + "    "
            x = (f'<entryLink id="{make_id("power pack link", unit, model)}" name="Power Pack" hidden="true" '
                 f'collective="false" import="true" targetId="{POWER_PACK}" type="selectionEntry">{nl}'
                 f'{ind}  <modifiers>{nl}'
                 f'{ind}    <modifier type="set" field="hidden" value="false">{nl}'
                 f'{ind}      <conditions>{nl}'
                 f'{ind}        <condition field="selections" scope="force" value="1" percentValue="false" shared="true" '
                 f'includeChildSelections="true" includeChildForces="false" childId="{KINFOLK_HELOTS}" type="atLeast"/>{nl}'
                 f'{ind}      </conditions>{nl}'
                 f'{ind}    </modifier>{nl}'
                 f'{ind}  </modifiers>{nl}'
                 f'{ind}  <constraints>{nl}'
                 f'{ind}    <constraint field="selections" scope="parent" value="1" percentValue="false" shared="true" '
                 f'includeChildSelections="false" includeChildForces="false" id="{make_id("power pack link max", unit, model)}" '
                 f'type="max"/>{nl}'
                 f'{ind}  </constraints>{nl}'
                 f'{ind}</entryLink>')
            o.F.insert_child(p, sp, "entryLinks", [x], f"{unit} > {model}: + Power Pack")
        o.run(f"{unit} > {model}", go)
    o.report()


if __name__ == "__main__":
    main()
