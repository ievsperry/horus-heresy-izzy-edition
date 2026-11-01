#!/usr/bin/env python3
"""Build Homebrew - Armies of Dark Compliance.cat from the official Imperialis Militia and Legiones Astartes lists.

usage: python3 homebrew/build_dark_compliance.py

An Army of Dark Compliance (Liber Imperatus, homebrew/source/imperialis-militia.md) is a Primary Detachment on the
Crusade Force Organisation Chart built from both the Legiones Astartes and Imperialis Militia army lists. The
catalogue links both lists (so their units, wargear and rules are shared, not copied) and gives the Detachment its
own root entries:

- "Army of Dark Compliance", the Detachment's faction choice: the Imperialis Militia faction entry and one Legion
  (so every Legiones Astartes unit has the same Legion), with the Detachment's rules and The Warmaster's Due. It is an
  error in a Loyalist army or in any Detachment but a Crusade Force Organisation Chart;
- every Imperialis Militia root entry (Provenances of War come with the Force Commander as normal). A unit with the
  Militia Sub-type and no Independent Character may take Expendable (and loses the Line Sub-type); a Militia unit
  may not hold the Warlord;
- the Legiones Astartes units every Legion's catalogue has (no Primarchs, no Legion-specific units, no Rites of
  War), each with The Warmaster's Due.

The other limits (at most as many Legiones Astartes units as Militia and Third-Line units, no Allied Detachment of
the same Faction, no Legiones Hereticus models) are rule text on the Detachment entry. Running it again rebuilds the
catalogue with the same ids; its revision goes up by one."""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
from build_catalogue import add_constraint, add_cost, add_rule, child, el, make_id  # noqa: E402

OUT = "Homebrew - Armies of Dark Compliance.cat"
IM = "2022 - Imperialis Militia.cat"
LA_LIBRARY = "2022 - Legiones Astartes.cat"
GST = "2022 - Horus Heresy.gst"
DOC = "homebrew/source/imperialis-militia.md"
C = "{http://www.battlescribe.net/schema/catalogueSchema}"
G = "{http://www.battlescribe.net/schema/gameSystemSchema}"
CAT_ID = make_id("armies of dark compliance", "catalogue")

IM_FACTION = "5522-4fd9-12d5-460afds"   # the game system's Imperialis Militia faction entry
LEGION_GROUP = "4a48-4935-246d-0c2e"    # the game system's Legion pick
ALLEGIANCE_CAT = ("e90d-e5a8-f42d-da84", "Allegiance:")
LOYALIST = "d0b6-712f-0b12-a308"
CRUSADE = "d926-652f-8436-30ce"         # 1. Crusade Force Organisation Chart
WARLORD = "0176-56a3-d590-b103"
LINE = "6399-5c65-7833-1025"            # Line Sub-type category
LA_TEMPLATE = "2022 - LA - Sons of Horus.cat"  # the generic Legion entries are taken from a Legion's catalogue


def mid(*parts):
    return make_id("armies of dark compliance", *parts)


def strip_ns(e):
    for x in e.iter():
        x.tag = x.tag.split("}")[-1]
        x.attrib.pop("publicationId", None)
        x.attrib.pop("page", None)
    return e


def copy_link(link, key):
    """A root entry of another catalogue as one of this catalogue's: fresh ids, the modifiers that name its
    constraints following them."""
    c = strip_ns(ET.fromstring(ET.tostring(link)))
    ids = {}
    for x in c.iter():
        if x.get("id"):
            ids[x.get("id")] = mid(key, x.get("id"))
            x.set("id", ids[x.get("id")])
    for x in c.iter():
        if x.get("field") in ids:
            x.set("field", ids[x.get("field")])
    return c


def doc_section():
    text = open(DOC, encoding="utf-8").read()
    i = text.index("## Armies of Dark Compliance")
    j = text.index("\n## ", i + 5)
    lines = text[i:j].split("\n")[1:]
    out = []
    for l in lines:
        s = l.strip()
        if not s or s.startswith("*"):
            continue
        if s.startswith("- "):
            out.append("• " + bc.strip_md(s[2:]))
        else:
            out.append(("\n" if out else "") + bc.strip_md(s))
    return "\n".join(out).strip()


def all_ids():
    ids = set()
    for f in [GST] + glob.glob("*.cat"):
        if f == OUT:
            continue
        ids |= set(re.findall(r'\sid="([^"]+)"', open(f, encoding="utf-8").read()))
    return ids


def unit_types(unit):
    return " ".join(c.text or "" for c in unit.iter(C + "characteristic") if c.get("name") == "Unit Type")


def main():
    gst = ET.parse(GST).getroot()
    rules = {r.get("name"): r.get("id") for r in gst.iter(G + "rule")}
    warmaster = rules["The Warmaster's Due"]
    im = ET.parse(IM).getroot()
    im_head = re.search(r"<catalogue [^>]*>", open(IM, encoding="utf-8").read()).group(0)
    gs_rev = re.search(r'gameSystemRevision="(\d+)"', im_head).group(1)
    old_rev = 0
    if os.path.exists(OUT):
        old_rev = int(re.search(r'<catalogue [^>]*?revision="(\d+)"', open(OUT, encoding="utf-8").read()).group(1))

    cat = ET.Element("catalogue", {"xmlns": C[1:-1], "id": CAT_ID, "name": "Homebrew - Armies of Dark Compliance",
                                   "revision": str(old_rev + 1), "battleScribeVersion": "2.03", "library": "false",
                                   "gameSystemId": "28d4-bd2e-4858-ece6", "gameSystemRevision": gs_rev,
                                   "type": "catalogue", "authorName": "Isaac"})
    roots = el(cat, "entryLinks")
    shared = el(cat, "sharedSelectionEntries")

    # Expendable, as the Imperialis Militia rule has it, and losing the Line Sub-type
    expendable_text = next(r.find(C + "description").text for r in im.iter(C + "rule") if r.get("name") == "Expendable")
    exp = el(shared, "selectionEntry", type="upgrade", import_=True, name="Expendable", hidden=False,
             id=mid("expendable"))
    add_rule(exp, "Expendable", expendable_text + "\n\nArmies of Dark Compliance: a unit given Expendable loses the "
             "Line Sub-type.", exp.get("id"))
    add_cost(exp, 0)

    # the Detachment's faction choice
    adc = el(shared, "selectionEntry", type="upgrade", import_=True, name="Army of Dark Compliance", hidden=False,
             id=mid("detachment"))
    add_rule(adc, "Army of Dark Compliance", doc_section(), adc.get("id"))
    el(child(adc, "infoLinks"), "infoLink", name="The Warmaster's Due", id=mid("detachment", "warmaster"),
       hidden=False, targetId=warmaster, type="rule")
    links = child(adc, "entryLinks")
    f = el(links, "entryLink", import_=True, name="Imperialis Militia", hidden=False, id=mid("detachment", "militia"),
           type="selectionEntry", targetId=IM_FACTION)
    add_constraint(f, "min", 1, mid("detachment", "militia min"))
    add_constraint(f, "max", 1, mid("detachment", "militia max"))
    el(links, "entryLink", import_=True, name="Legion", hidden=False, id=mid("detachment", "legion"),
       type="selectionEntryGroup", targetId=LEGION_GROUP)
    add_cost(adc, 0)
    r = el(roots, "entryLink", import_=False, name="Army of Dark Compliance", hidden=False, id=mid("root", "detachment"),
           type="selectionEntry", targetId=adc.get("id"))
    add_constraint(r, "min", 1, mid("root", "detachment", "min"))
    cmax = add_constraint(r, "max", 1, mid("root", "detachment", "max"))
    # "the army must be Traitor"; "may only be a Primary Detachment ... using the Crusade Force Organisation Chart"
    mod = el(el(r, "modifiers"), "modifier", type="set", field=cmax, value=0)
    cg = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
    el(cg, "condition", type="atLeast", value=1, field="selections", scope="roster", childId=LOYALIST, shared=True,
       includeChildSelections=True, includeChildForces=True, percentValue=False)
    el(cg, "condition", type="notInstanceOf", value=0, field="selections", scope="ancestor", childId=CRUSADE,
       shared=True, includeChildSelections=False, includeChildForces=False, percentValue=False)
    el(el(r, "categoryLinks"), "categoryLink", id=mid("root", "detachment", "cat"), name=ALLEGIANCE_CAT[1],
       hidden=False, targetId=ALLEGIANCE_CAT[0], primary=True)

    # the Imperialis Militia root entries
    im_units = {e.get("id"): e for e in im.find(C + "sharedSelectionEntries")}
    taken = set()
    for l in im.find(C + "entryLinks"):
        if l.get("targetId") == IM_FACTION:
            continue
        c = copy_link(l, "im")
        u = im_units.get(l.get("targetId"))
        if u is not None and u.get("type") == "unit":
            types = unit_types(u)
            if "Militia" in types:
                uid = u.get("id")
                if "Independent Character" not in types:
                    el(child(c, "entryLinks"), "entryLink", import_=True, name="Expendable", hidden=False,
                       id=mid(c.get("id"), "expendable"), type="selectionEntry", targetId=exp.get("id")).append(
                        ET.Element("constraints"))
                    add_constraint(c.find("entryLinks/entryLink[@name='Expendable']"), "max", 1,
                                   mid(c.get("id"), "expendable max"))
                    mod = el(child(c, "modifiers"), "modifier", type="remove", field="category", value=LINE)
                    el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid,
                       childId=exp.get("id"), shared=True, includeChildSelections=True, includeChildForces=False,
                       percentValue=False)
                # "the Warlord must be a model with Legiones Astartes (X)"
                wmax = add_constraint(c, "max", -1, mid(c.get("id"), "no warlord"))
                mod = el(child(c, "modifiers"), "modifier", type="set", field=wmax, value=0)
                el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid,
                   childId=WARLORD, shared=True, includeChildSelections=True, includeChildForces=False,
                   percentValue=False)
        roots.append(c)
        taken.add(l.get("targetId"))

    # the Legiones Astartes units every Legion has
    legion_cats = sorted(glob.glob("2022 - LA - *.cat"))
    common = set.intersection(*[{l.get("targetId") for l in ET.parse(p).getroot().find(C + "entryLinks")}
                                for p in legion_cats])
    known = all_ids()
    template = ET.parse(LA_TEMPLATE).getroot()
    for l in template.find(C + "entryLinks"):
        t = l.get("targetId")
        if t not in common or t in taken:
            continue
        c = copy_link(l, "la")
        # conditions on what only the Legion's own catalogue has
        for parent in list(c.iter()):
            for cond in list(parent):
                if cond.tag == "condition" and cond.get("childId") not in known | {"model", "unit", "upgrade", "any"}:
                    parent.remove(cond)
        for mods in list(c.iter("modifiers")):
            for m in list(mods):
                if not list(m.iter("condition")) and (m.find("conditions") is not None or m.find("conditionGroups") is not None):
                    mods.remove(m)
        el(child(c, "infoLinks"), "infoLink", name="The Warmaster's Due", id=mid(c.get("id"), "warmaster"),
           hidden=False, targetId=warmaster, type="rule")
        roots.append(c)
        taken.add(t)

    # the lists it is built from, and the libraries they use
    links = el(cat, "catalogueLinks")
    im_links = {c.get("name"): c for c in im.iter(C + "catalogueLink")}
    for name, target, imports in [("Imperialis Militia", im.get("id"), False),
                                  ("Legions Astartes", ET.parse(LA_LIBRARY).getroot().get("id"), False)] + [
            (n, c.get("targetId"), c.get("importRootEntries") == "true") for n, c in im_links.items()]:
        a = {"id": mid("link", name), "name": name, "targetId": target, "type": "catalogue"}
        if imports:
            a["importRootEntries"] = "true"
        el(links, "catalogueLink", **a)

    ET.indent(cat, space="  ")
    for x in cat.iter():
        for k in list(x.attrib):
            if x.attrib[k] is True or x.attrib[k] is False:
                x.attrib[k] = "true" if x.attrib[k] else "false"
    bc_order(cat)
    text = ET.tostring(cat, encoding="unicode").replace(f' xmlns:ns0="{C[1:-1]}"', "").replace(" />", "/>")
    open(OUT, "w", encoding="utf-8", newline="\n").write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' +
                                                       text + "\n")
    print(f"wrote {OUT}: revision {old_rev + 1}, {len(list(roots))} root entries")


def bc_order(e):
    """Children in the order the schema wants."""
    order = bc.ENTRY_ORDER + ["description", "repeats", "conditions", "conditionGroups", "catalogueLinks"]
    kids = list(e)
    o = bc.MODIFIER_ORDER if e.tag in ("modifier", "conditionGroup") else order
    if kids and all(k.tag in o for k in kids):
        kids.sort(key=lambda k: o.index(k.tag))
        for k in list(e):
            e.remove(k)
        e.extend(kids)
    for k in kids:
        bc_order(k)


if __name__ == "__main__":
    main()
