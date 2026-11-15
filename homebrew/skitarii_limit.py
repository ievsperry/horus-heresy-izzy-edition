#!/usr/bin/env python3
"""Enforce the Skitarii Sub-type's limit in the official Mechanicum catalogue: "A Detachment may not include more
models with this Sub-type than without it, unless its Compulsory HQ choice has the Skitarii Sub-type."

usage: python3 homebrew/skitarii_limit.py

Every unit with the Skitarii Sub-type rule gets a limit on itself (so it applies wherever the unit is linked): it
starts at the number of that unit in the Detachment, goes up by one for every model in the Detachment and down by two
for every Skitarii model, so it fails exactly when Skitarii models outnumber the rest. A Skitarii HQ (Sicarian
Clademaster, Skitarii Centurius) in the Detachment lifts it; the apps cannot tell which HQ fills the Compulsory slot,
so any Skitarii HQ counts. Running it again changes nothing."""
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
from expansion_tools import E, Text  # noqa: E402

CAT = "2022 - Mechanicum.cat"
SKITARII_RULE = "92de-76e6-4fff-843b"  # the game system's Skitarii Sub-type rule
HQ_SLOT = "4f85-eb33-30c9-8f51"


def repeat(m, child_id):
    bc.el(bc.el(m, "repeats"), "repeat", field="selections", scope="force", value=1, percentValue=False, shared=True,
          includeChildSelections=True, includeChildForces=False, childId=child_id, repeats=1, roundUp=False)


def main():
    cat = Text(CAT)
    root = ET.fromstring(cat.s.encode("utf-8"))
    C = root.tag.split("}")[0] + "}"
    units = [e for e in root.iter(C + "selectionEntry") if e.get("type") == "unit"
             and any(il.get("targetId") == SKITARII_RULE for il in e.iter(C + "infoLink"))]
    models = [m.get("id") for u in units for m in u.iter(C + "selectionEntry") if m.get("type") == "model"]
    hqs = [u.get("id") for u in units
           if any(l.get("targetId") == u.get("id") and any(c.get("targetId") == HQ_SLOT for c in l.iter(C + "categoryLink"))
                  for l in root.iter(C + "entryLink"))]
    n = 0
    for u in units:
        uid = u.get("id")
        cid = bc.make_id("skitarii limit", uid, "max")
        if cid in cat.s:
            continue
        c = E("constraint", type="max", value=0, field="selections", scope="force", shared=True, id=cid,
              percentValue=False, includeChildSelections=True, includeChildForces=False)
        mods = []
        m = E("modifier", type="increment", field=cid, value=1)
        bc.el(m, "comment").text = ("Skitarii: no more models with this Sub-type than without it in the Detachment, "
                                    "unless a Skitarii HQ is there")
        repeat(m, uid)
        mods.append(m)
        m = E("modifier", type="increment", field=cid, value=1)
        repeat(m, "model")
        mods.append(m)
        for mid in models:
            m = E("modifier", type="decrement", field=cid, value=2)
            repeat(m, mid)
            mods.append(m)
        m = E("modifier", type="set", field=cid, value=-1)
        g = bc.el(bc.el(bc.el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
        for h in hqs:
            bc.el(g, "condition", type="atLeast", value=1, field="selections", scope="force", childId=h, shared=True,
                  includeChildSelections=True, includeChildForces=False, percentValue=False)
        mods.append(m)
        cat.add(uid, "constraints", [c])
        cat.add(uid, "modifiers", mods)
        n += 1
    if n:
        cat.bump("catalogue")
        cat.save()
    print(f"{CAT}: Skitarii limit on {n} units ({len(models)} Skitarii models, HQs: {len(hqs)})")


if __name__ == "__main__":
    main()
