#!/usr/bin/env python3
"""Give the Solar Auxilia Praetorian Heavy Tank Squadron its turret weapon.

usage: python3 homebrew/fix_solar_auxilia_links.py

add_solar_auxilia.py left "Turret Mounted Oppressor Cannon with Co-axial Autocannon" as an empty entry: the doc only
names it, and the Solar Auxilia catalogue has no Oppressor Cannon. It becomes the Oppressor Cannon (the doc's
armoury profile: 72", S10, AP2, Heavy 2, Brutal (3), Sunder) and the game system's Autocannon, as the Imperialis
Militia catalogue builds the same option. It does nothing once the entry has content."""
import sys

sys.path.insert(0, "homebrew")
from build_catalogue import make_id  # noqa: E402

CAT = "2022 - LI - Solar Auxilia.cat"
EID = "3db2-9119-847d-45cb"
NAME = "Turret Mounted Oppressor Cannon with Co-axial Autocannon"
AUTOCANNON = "56b3-de09-9fea-deb6"  # the game system's
BRUTAL, SUNDER = "5079-1fec-d32b-8b84", "20e2-75cf-bc16-cd8f"
WEAPON = ("1a1a-e592-2849-a5c0", [("Range", "95ba-cda7-b831-6066", '72"'), ("Strength", "24d9-b8e1-a355-2458", "10"),
                                  ("AP", "f7a6-e0d8-7973-cd8d", "2"),
                                  ("Type", "2f86-c8b4-b3b4-3ff9", "Heavy 2, Brutal (3), Sunder")])
PTS = "d2ee-04cb-5f8a-2642"


def main():
    s = open(CAT, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    old = f'<selectionEntry type="upgrade" import="true" name="{NAME}" hidden="false" id="{EID}"/>'
    i = s.find(old)
    if i < 0:
        sys.exit(f"{CAT}: the {NAME} entry already has content")
    pad = " " * (i - s.rfind("\n", 0, i) - 1)

    def k(*p):
        return make_id("solar auxilia oppressor", *p)
    chars = "".join(f'{nl}{pad}        <characteristic name="{n}" typeId="{t}">{v.replace(chr(34), "&quot;")}'
                    f'</characteristic>' for n, t, v in WEAPON[1])
    cons = "".join(f'{nl}{pad}        <constraint type="{t}" value="1" field="selections" scope="parent" shared="true" '
                   f'id="{k(t)}" percentValue="false" includeChildSelections="false" includeChildForces="false"/>'
                   for t in ("min", "max"))
    new = (f'<selectionEntry type="upgrade" import="true" name="{NAME}" hidden="false" id="{EID}">'
           f'{nl}{pad}  <profiles>'
           f'{nl}{pad}    <profile name="Oppressor Cannon" typeId="{WEAPON[0]}" typeName="Weapon" hidden="false" id="{k("profile")}">'
           f'{nl}{pad}      <characteristics>{chars}{nl}{pad}      </characteristics>'
           f'{nl}{pad}    </profile>'
           f'{nl}{pad}  </profiles>'
           f'{nl}{pad}  <infoLinks>'
           f'{nl}{pad}    <infoLink name="Brutal (X)" hidden="false" id="{k("brutal")}" targetId="{BRUTAL}" type="rule">'
           f'{nl}{pad}      <modifiers>{nl}{pad}        <modifier type="set" field="name" value="Brutal (3)"/>'
           f'{nl}{pad}      </modifiers>'
           f'{nl}{pad}    </infoLink>'
           f'{nl}{pad}    <infoLink name="Sunder" hidden="false" id="{k("sunder")}" targetId="{SUNDER}" type="rule"/>'
           f'{nl}{pad}  </infoLinks>'
           f'{nl}{pad}  <entryLinks>'
           f'{nl}{pad}    <entryLink import="true" name="Co-axial Autocannon" hidden="false" id="{k("autocannon")}" '
           f'type="selectionEntry" targetId="{AUTOCANNON}">'
           f'{nl}{pad}      <constraints>{cons}{nl}{pad}      </constraints>'
           f'{nl}{pad}    </entryLink>'
           f'{nl}{pad}  </entryLinks>'
           f'{nl}{pad}  <costs>{nl}{pad}    <cost name="Pts" typeId="{PTS}" value="0"/>{nl}{pad}  </costs>'
           f'{nl}{pad}</selectionEntry>')
    open(CAT, "w", encoding="utf-8", newline="").write(s[:i] + new + s[i + len(old):])


if __name__ == "__main__":
    main()
