#!/usr/bin/env python3
"""Hide the standard Fortifications in 2022 - Horus Heresy.gst from armies that take their own instead.

usage: python3 homebrew/faction_fortifications.py [game system]

Tyranid Detachments take Bio-Fortifications (homebrew/source/tyranids.md), Ork Detachments take Ork
Fortifications (homebrew/source/orks.md) and Daemons of the Ruinstorm
Detachments take Daemonic Fortifications (homebrew/add_ruinstorm.py), so each of the game system's own
Fortification entries is hidden in a Detachment holding either faction's army-wide entry. Running it again
changes nothing; a new faction is added to FACTIONS and the script run again (its old modifier is replaced)."""
import re
import sys

GST = sys.argv[1] if len(sys.argv) > 1 else "2022 - Horus Heresy.gst"
FORTIFICATIONS = {
    "39b5-294b-f075-d42d": "Fortified Wall (Strongpoint)", "7488-dcd5-3230-57d7": "Imperial Bunker",
    "427d-eb8e-dbbd-87a2": "Defence Line", "ffeb-34e6-ea59-170c": "Firestorm Redoubt",
    "c3fd-09fe-2ac7-2183": "Vengeance Weapon Battery", "f1d1-ca61-ae6b-4d33": "Void Shield Generator",
    "026e-1405-50cc-e19b": "Skyshield Landing Pad", "dd67-c6ce-04e4-8dc2": "Fortress Of Redemption",
    "d8a1-2527-d538-bdfb": "Aquila Strongpoint", "01dc-d34a-1988-3919": "Primus Redoubt",
    "91a3-bce0-aa49-e830": "Hammerfall Bunker"}
# the army-wide entry every Detachment of the faction holds
FACTIONS = {"b0ce-f3f1-c16f-86d1": "Tyranids", "afca-3047-fb26-d097": "Daemons of the Ruinstorm",
            "adbe-53b5-788c-2bbb": "Orks"}
COMMENT = "Hidden for armies with their own Fortifications"


def modifier(ind, nl):
    conds = "".join(
        f'{ind}      <condition type="atLeast" value="1" field="selections" scope="force" childId="{cid}" '
        f'shared="true" includeChildSelections="true" includeChildForces="false"/>{nl}' for cid in FACTIONS)
    return (f'{ind}<modifier type="set" field="hidden" value="true">{nl}'
            f'{ind}  <comment>{COMMENT}: {", ".join(FACTIONS.values())}</comment>{nl}'
            f'{ind}  <conditionGroups>{nl}{ind}    <conditionGroup type="or">{nl}{ind}      <conditions>{nl}'
            + conds.replace(f"{ind}      <condition", f"{ind}        <condition") +
            f'{ind}      </conditions>{nl}{ind}    </conditionGroup>{nl}{ind}  </conditionGroups>{nl}'
            f'{ind}</modifier>{nl}')


def main():
    s = open(GST, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    old = s
    for eid, name in FORTIFICATIONS.items():
        m = re.search(rf'<entryLink [^>]*id="{eid}"[^>]*>', s)
        if not m or f'name="{name}"' not in m.group(0):
            sys.exit(f"no Fortification link {name} ({eid})")
        end = s.index("</entryLink>", m.end())
        body = s[m.end():end]
        # take out a modifier this script added before
        body = re.sub(rf'[ \t]*<modifier type="set" field="hidden" value="true">{nl}[ \t]*<comment>{COMMENT}.*?'
                      rf'</modifier>{nl}', "", body, flags=re.S)
        mm = re.search(r"([ \t]*)<modifiers>" + nl, body)
        if mm:
            at = mm.end()
            body = body[:at] + modifier(mm.group(1) + "  ", nl) + body[at:]
        else:
            ind = re.search(r"\n([ \t]*)<entryLink ", s[:m.end()][::-1][::-1][s.rfind("\n", 0, m.start()):m.end()])
            ind = (ind.group(1) if ind else "    ") + "  "
            body = nl + f"{ind}<modifiers>{nl}" + modifier(ind + "  ", nl) + f"{ind}</modifiers>" + body
        s = s[:m.end()] + body + s[end:]
    if s != old:
        r = re.search(r'<gameSystem [^>]*?revision="(\d+)"', s)
        s = s[:r.start(1)] + str(int(r.group(1)) + 1) + s[r.end(1):]
        open(GST, "w", encoding="utf-8", newline="").write(s)
        print(f"{GST}: standard Fortifications hidden for {', '.join(FACTIONS.values())}")
    else:
        print(f"{GST}: no change")


if __name__ == "__main__":
    main()
