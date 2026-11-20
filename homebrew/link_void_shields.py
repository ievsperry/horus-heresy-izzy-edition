#!/usr/bin/env python3
"""Link the game system's Void Shields rule to the void shield wargear made by scripts that do not run again.

The builder links it itself (a wargear text giving "Void Shield(s) (Armour Value 12)" or "(AV 12)"); the entries
written into the official files by add_imperial_fortifications.py and add_ruinstorm_fortifications.py were made
before that, so this adds the link to them: the game system's Void Shield and Auxiliary Void Shield, and the Ruinstorm
Reinforced Void-Veil. Running it again changes nothing.

usage: python3 homebrew/link_void_shields.py"""
import sys

sys.path.insert(0, "homebrew")
import expansion_tools as et  # noqa: E402
from build_catalogue import make_id  # noqa: E402

VOID_SHIELDS = "c503-f5b8-3da0-16e6"     # the game system's rule
ENTRIES = {"2022 - Horus Heresy.gst": [("f6af-b72a-b86e-2785", "gameSystem"), ("1a21-147a-da4f-0fdb", "gameSystem")],
           "2022 - Daemons - Daemons of the Ruinstorm.cat": [("b991-d2a9-0f97-5d99", "catalogue")]}


def main():
    for path, entries in ENTRIES.items():
        t = et.Text(path)
        changed = False
        for eid, root in entries:
            start, end, _, _ = t.block(eid)
            if f'targetId="{VOID_SHIELDS}"' in t.s[start:end]:
                continue
            link = et.E("infoLink", name="Void Shields", id=make_id(eid, "void shields rule"), hidden=False,
                        targetId=VOID_SHIELDS, type="rule")
            t.add(eid, "infoLinks", [link])
            changed = True
        if changed:
            t.bump(root)
            t.save()
            print(f"{path}: Void Shields rule linked")


if __name__ == "__main__":
    main()
