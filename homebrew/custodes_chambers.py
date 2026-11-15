#!/usr/bin/env python3
"""Enforce the two Chamber of the Golden Host limitations that compare counts, in the official LI - Custodes
catalogue.

usage: python3 homebrew/custodes_chambers.py

- Hykanatoi: "The Detachment may not include more Vehicle and Dreadnought units than units without those Unit
  Types." The catalogue already puts every Vehicle and Dreadnought unit in the "Vehicle or Dreadnought (Hykanatoi)"
  category, so the Chamber's limit of one goes up by one for each unit in the Detachment and down by two for each
  unit in that category: it fails exactly when they outnumber the rest.
- Kataphraktoi: "The Detachment may not include more Fast Attack and Heavy Support choices combined than Troops
  choices." Up by one per Troops choice, down by one per Fast Attack or Heavy Support choice.

Only the Detachment's own units are counted (a model entry may carry the Unit category too). Running it again
changes nothing."""
import sys

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
from expansion_tools import E, Text  # noqa: E402

CAT = "2022 - LI - Custodes.cat"
UNIT = "36c3-e85e-97cc-c503"         # Unit:
HYKANATOI_CAT = "b4f1-e2b7-7a58-9a8d"  # Vehicle or Dreadnought (Hykanatoi)
TROOPS, FAST, HEAVY = "9b5d-fac7-799b-d7e7", "20ef-cd01-a8da-376e", "7031-469a-1aeb-eab0"
CHAMBERS = {
    "Hykanatoi": ("3293-b6a4-bfc2-2818", [(UNIT, "increment", 1), (HYKANATOI_CAT, "decrement", 2)],
                  "may not include more Vehicle and Dreadnought units than units without those Unit Types"),
    "Kataphraktoi": ("782b-fe10-5981-04be", [(TROOPS, "increment", 1), (FAST, "decrement", 1), (HEAVY, "decrement", 1)],
                     "may not include more Fast Attack and Heavy Support choices combined than Troops choices"),
}


def main():
    cat = Text(CAT)
    n = 0
    for name, (eid, counts, text) in CHAMBERS.items():
        cid = bc.make_id("custodes chamber", name, "compare", "max")
        if cid in cat.s:
            continue
        c = E("constraint", type="max", value=1, field="selections", scope="parent", shared=True, id=cid,
              percentValue=False, includeChildSelections=False, includeChildForces=False)
        mods = []
        for i, (child_id, kind, value) in enumerate(counts):
            m = E("modifier", type=kind, field=cid, value=value)
            if i == 0:
                bc.el(m, "comment").text = f"Chamber of the Golden Host: {name}: {text}"
            bc.el(bc.el(m, "repeats"), "repeat", field="selections", scope="force", value=1, percentValue=False,
                  shared=True, includeChildSelections=False, includeChildForces=False, childId=child_id, repeats=1,
                  roundUp=False)
            mods.append(m)
        cat.add(eid, "constraints", [c])
        cat.add(eid, "modifiers", mods)
        n += 1
    if n:
        cat.bump("catalogue")
        cat.save()
    print(f"{CAT}: {n} Chamber limits added")


if __name__ == "__main__":
    main()
