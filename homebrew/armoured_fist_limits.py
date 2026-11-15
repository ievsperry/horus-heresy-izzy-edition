#!/usr/bin/env python3
"""Enforce what can be checked of the Armoured Fist Pattern Cohorts Cohort Doctrine (Liber Panoptica Expansion FAQ)
in the official LI - Solar Auxilia catalogue.

usage: python3 homebrew/armoured_fist_limits.py

- "the army may not take Fortifications": an error on the Doctrine while the roster has a Fortification choice;
- "The Detachment may not include models with Movement 0 or '-'": an error on the Doctrine while the Detachment has
  any model whose profile's Movement is 0 or '-' (the guns of the Artillery Tercio and Artillery Battery);
- Auxilia Armoured Tercios gain Line "as Compulsory Troops in a Primary Detachment": the Line it already gains as
  Compulsory Troops now also needs the Crusade Force Organisation Chart (the Primary Detachment).

"Infantry units must start embarked or in Reserves" is about play and stays rule text. Running it again changes
nothing."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
from expansion_tools import E, Text  # noqa: E402

CAT = "2022 - LI - Solar Auxilia.cat"
DOCTRINE = "1974-9f9a-5b14-e449"      # Armoured Fist Pattern Cohorts (Check Limitations manually)
TROOPS_ENTRY = "b35c-9232-1993-823c"  # Armoured Fist - Auxilia Armoured Tercio
FORTIFICATION = "a24f-12d8-36c1-f477"
CRUSADE = "d926-652f-8436-30ce"       # 1. Crusade Force Organisation Chart: the Primary Detachment
LINE = "6399-5c65-7833-1025"
COMPULSORY_TROOPS = "8f42-a824-fb5f-8fea"


def error(cat, key, comment, conditions):
    """A limit of one on the Doctrine that drops to none while any of the conditions holds."""
    cid = bc.make_id("armoured fist", key, "max")
    if cid in cat.s:
        return 0
    c = E("constraint", type="max", value=1, field="selections", scope="parent", shared=True, id=cid,
          percentValue=False, includeChildSelections=False, includeChildForces=False)
    m = E("modifier", type="set", field=cid, value=0)
    bc.el(m, "comment").text = comment
    g = bc.el(bc.el(bc.el(m, "conditionGroups"), "conditionGroup", type="or"), "conditions")
    for kind, scope, child_id, forces in conditions:
        bc.el(g, "condition", type=kind, value=1, field="selections", scope=scope, childId=child_id, shared=True,
              includeChildSelections=True, includeChildForces=forces, percentValue=False)
    cat.add(DOCTRINE, "constraints", [c])
    cat.add(DOCTRINE, "modifiers", [m])
    return 1


def main():
    cat = Text(CAT)
    root = ET.fromstring(cat.s.encode("utf-8"))
    C = root.tag.split("}")[0] + "}"
    n = error(cat, "no fortifications", "Armoured Fist Pattern Cohorts: the army may not take Fortifications",
              [("atLeast", "roster", FORTIFICATION, True)])
    static = sorted({m.get("id") for m in root.iter(C + "selectionEntry") if m.get("type") == "model"
                     and any((ch.text or "").strip() in ("0", "-", "–") for p in m.findall(f"{C}profiles/{C}profile")
                             for ch in p.iter(C + "characteristic") if ch.get("name") in ("M", "Move", "Movement"))})
    n += error(cat, "no movement 0", "Armoured Fist Pattern Cohorts: no models with Movement 0 or '-'",
               [("atLeast", "force", mid, False) for mid in static])
    # Line only as Compulsory Troops in the Primary Detachment
    a, b, _, _ = cat.block(TROOPS_ENTRY)
    body = cat.s[a:b]
    line = re.search(r'(<modifier type="add" field="category" value="%s">\s*<conditions>)(\s*)(<condition [^>]*childId="%s"[^>]*/>)'
                     % (LINE, COMPULSORY_TROOPS), body)
    if line and CRUSADE not in body[line.start():body.index("</modifier>", line.start())]:
        cond = (f'<condition type="instanceOf" value="1" field="selections" scope="ancestor" childId="{CRUSADE}" '
                f'shared="true" percentValue="false" includeChildSelections="false" includeChildForces="false"/>')
        body = body[:line.end()] + line.group(2) + cond + body[line.end():]
        cat.s = cat.s[:a] + body + cat.s[b:]
        n += 1
    if n:
        cat.bump("catalogue")
        cat.save()
    print(f"{CAT}: {n} Armoured Fist changes ({len(static)} models with Movement 0 or '-')")


if __name__ == "__main__":
    main()
