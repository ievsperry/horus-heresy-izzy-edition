#!/usr/bin/env python3
"""Point five option groups' default pick at their standard option.

usage: python3 homebrew/fix_default_picks.py

The Imperialis Militia, Sisters of Silence and Solar Auxilia expansion scripts gave these groups a default made from
the option's name, but the options were made (or later relinked) under other ids, so the default pointed at
nothing and nothing was preselected. Each now defaults to its standard option. The groups that upstream BSData
left the same way are not touched. Running it again changes nothing."""
import re
import sys

sys.path.insert(0, "homebrew")
from expansion_tools import Text  # noqa: E402

FIXES = {  # catalogue: [(group id, the option it should default to)]
    "2022 - Imperialis Militia.cat": [("a86d-1c48-c664-a817", "Hull (Front) Mounted Heavy Stubber")],  # Arvus
    "2022 - LI - Sisters Of Silence.cat": [("c49c-61a1-786c-a537", "Vratine Armour")],  # Knight Vestal
    "2022 - LI - Solar Auxilia.cat": [("fc55-3631-83c5-c935", "Hull (Front) Mounted Heavy Stubber"),
                                      ("3fab-0193-7d8f-1896", "Battle Cannon"),  # Armoured Command Section
                                      ("fc19-d82c-0c83-9c84", "Neutron Beam Laser")],  # Valdor Tank Destroyer
}


def main():
    for f, groups in FIXES.items():
        cat = Text(f)
        n = 0
        for gid, option in groups:
            a, b, _, _ = cat.block(gid)
            body = cat.s[a:b]
            link = re.search(r'<entryLink [^>]*name="%s"[^>]*>' % re.escape(option), body)
            lid = re.search(r'\bid="([^"]+)"', link.group(0)).group(1)
            new = re.sub(r'defaultSelectionEntryId="[^"]*"', f'defaultSelectionEntryId="{lid}"', body, count=1)
            if new != body:
                cat.s = cat.s[:a] + new + cat.s[b:]
                n += 1
        if n:
            cat.bump("catalogue")
            cat.save()
        print(f"{f}: {n} default picks fixed")


if __name__ == "__main__":
    main()
