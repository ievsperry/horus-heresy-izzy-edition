#!/usr/bin/env python3
"""Add the Liber Centura expansion (the Claude Doc "Liber Centura for The Horus Heresy 2.0 — Homebrew Conversion",
kept as homebrew/source/centura.md) to the Legiones Astartes catalogues: its units for every Legion into the
Legiones Astartes library, its Legion-specific units into each Legion's catalogue. Run it after the doc's special
rules are in additional-special-rules.md and the game system (homebrew/add_gst_rules.py).

usage: python3 homebrew/add_centura.py

It refuses to run on catalogues that already have the expansion."""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_mechanicum as am  # noqa: E402  (the shared transplant pipeline)
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import norm  # noqa: E402

DOC = "homebrew/source/centura.md"
LIBRARY = "2022 - Legiones Astartes.cat"
SLOT_HEADS = ("HQ", "Elites", "Troops", "Fast Attack", "Heavy Support", "Lords of War", "Fortifications")


def doc():
    return open(DOC, encoding="utf-8").read()


def section(text, heading):
    """The text of a '## heading' section, up to the next '## '."""
    i = text.index(f"\n## {heading}\n")
    j = text.find("\n## ", i + 5)
    return text[i:j if j > 0 else len(text)]


def wargear_items(sec):
    """The doc's wargear paragraphs ('**Name.** text') as one '#### Name' item each, as the Builder reads them."""
    out = []
    for ln in sec.split("\n"):
        m = re.match(r"\*\*(.+?)\.\*\*\s*(.*)$", ln)
        if m:
            name = re.sub(r" \((?:[^()]*)\)$", "", m.group(1))  # "(Blood Angels)", "(Omegon, Alpha Legion)"
            out += [f"#### {name}", "", m.group(2), ""]
        elif ln.startswith("### "):
            continue
        else:
            out.append(ln)
    return "\n".join(out)


def armoury(text):
    """The Armoury with its weapon rows named as the datasheets name them ('Calibanite Greatsword (Luther; Dark
    Angels)' -> 'Calibanite Greatsword'), and its range-banded rows one profile each."""
    sec = section(text, "Armoury of the Legions")
    rows = []
    for ln in sec.split("\n"):
        m = re.match(r"\| ([^|]+?) \|", ln)
        if m and m.group(1) not in ("Weapon", "---"):
            name = re.sub(r" \([^()]*\)(?= – | \||$)", "", m.group(1))
            ln = ln.replace(f"| {m.group(1)} |", f"| {name} |", 1)
        rows.append(ln)
    return "\n".join(rows)


# Units the Legiones Astartes library already has (from the Saturnine conversion doc, which Liber Centura's
# Saturnine datasheets follow): left as they are
EXISTING = ("Praetor in Saturnine Terminator Armour", "Saturnine Terminator Squad", "Saturnine Dreadnought")

# the doc's names for official items, as the official catalogues name them
RENAMES = {
    "Legion Indomitus Terminator Armour": "Indomitus Terminator Armour",
    "Legion Cataphractii Terminator Armour": "Cataphractii Terminator Armour",
    "Legion Tartaros Terminator Armour": "Tartaros Terminator Armour",
    "Legion Warhawk Jump Pack": "Warhawk Jump Pack",
    "Legion Spatha Combat Bike": "Spatha Combat Bike",
}


def drop_datasheets(units, names):
    for n in names:
        m = re.search(r"^### (?:0-\d+ )?" + re.escape(n) + r" — .*?(?=^##)", units, re.M | re.S)
        if m:
            units = units[:m.start()] + units[m.end():]
    return units


def fixes(text):
    """Datasheet lines made plain for the Builder."""
    # "(Legion Veteran Sergeant only)" weapons are read as in place of the squad's; the Sergeant keeps his Bolter
    text = text.replace("- Bolt Pistol (Legion Veteran Sergeant only)\n- Bolter\n- Frag Grenades\n"
                        "- Krak Grenades (Legion Veteran Sergeant only)\n- Power Armour\n",
                        "- Legion Novitiate: Bolter, Frag Grenades, Power Armour\n"
                        "- Legion Veteran Sergeant: Bolt Pistol, Bolter, Frag Grenades, Krak Grenades, Power Armour\n")
    # the Saturnine Terminator Armour special rule is the armour
    text = text.replace("- Saturnine Terminator armour\n", "")
    # the official Earthshaker Cannon, and the doc's Airburst Shells as a weapon of their own
    text = text.replace("- Emplacement-Mounted Earthshaker Cannon (with Earthshaker and Airburst Shells)\n",
                        "- Earthshaker Cannon\n- Earthshaker Airburst Shells\n")
    text = text.replace("| Earthshaker Cannon – Airburst Shells |", "| Earthshaker Airburst Shells |")
    text = text.replace("- Fire Point (One Per Hull Arc, 4)\n", "")  # the profile's Fire Points
    # extra models the Builder reads as "Up to N additional X"
    text = text.replace("| – One additional Havoc Master |", "| – Up to 1 additional Havoc Master |")
    text = text.replace("| – Up to one additional Legion ", "| – Up to 1 additional Legion ")
    text = text.replace("Phosphex Canister Shot\\*", "Phosphex Canister Shot")
    for a, b in RENAMES.items():
        text = text.replace(a, b)
    return text


def generic_text():
    """The doc as the Builder reads it, for the units every Legion may take."""
    text = doc()
    title = text.split("\n", 1)[0]
    units = section(text, "Units")
    units = re.sub(r"^### (" + "|".join(SLOT_HEADS) + r")$", r"## \1", units, flags=re.M)
    units = units.replace("\n## Units\n", "\n")
    units = drop_datasheets(units, EXISTING)
    rules = section(text, "Legiones Special Rules").replace("## Legiones Special Rules", "## Army-wide Special Rules")
    wargear = wargear_items(section(text, "Legiones Wargear").split("### Legion-Specific Wargear")[0])
    return fixes("\n".join([title, rules, units, armoury(text), wargear]))


# official items the doc names but does not define: linked (or copied) by tidy()
ALLOWED = [r"wargear '(Ferromantic Deflector|Gravis Power Fist with in-built Combi-Bolter|Cataphractii Terminator "
           r"Armour|Tartaros Terminator Armour)'"]


def setup():
    et.SLOTS.setdefault("Fortifications", [("a24f-12d8-36c1-f477", "Fortification:", True)])
    am.DOC = DOC
    am.LIBS = ["2022 - Mech Library.cat"]
    am.ALLOWED = ALLOWED


CONSULARIS = "3cbf-9466-2558-2c22"  # the official Legiones Consularis pick


def doc_paragraphs(prefix):
    """{name: text} for the doc's '**<prefix>Name.** *flavour* text' paragraphs, flavour left out."""
    out = {}
    for m in re.finditer(r"^\*\*" + re.escape(prefix) + r"(.+?)\.\*\* (?:\*[^*]+\* )?(.+)$", doc(), re.M):
        out[m.group(1)] = m.group(2)
    return out


def profile_anywhere(name):
    """A profile of this name in any official file (wargear held only inline, such as the Ferromantic Deflector)."""
    import glob
    for f in ["2022 - Horus Heresy.gst"] + sorted(glob.glob("2022 - *.cat")):
        for p in ET.parse(f).getroot().iter():
            if p.tag.endswith("}profile") and norm(p.get("name") or "") == norm(name):
                return p
    return None


def fill_empty(b, root, key):
    """What the Builder left empty: the official items it names (in-built weapons, Quad Launcher shells, wargear an
    official catalogue holds only inline), the Pater Consularis upgrades (their text from the doc), and the
    Master-Crafted options (the rule)."""
    gst = bc.load_gst_rules()
    pater = doc_paragraphs("Pater Consularis: ")
    made = set()
    for e in list(root.find("sharedSelectionEntries")):
        if any(e.find(t) is not None for t in ("profiles", "entryLinks", "infoLinks", "rules", "selectionEntries")):
            continue
        name = e.get("name")
        m = re.match(r"Pater Consularis (.+)$", name)
        if m and m.group(1) in pater:
            bc.add_rule(e, f"Pater Consularis: {m.group(1)}", pater[m.group(1)], e.get("id"))
            continue
        if "master-crafted" in norm(name):
            rid, rname = gst["master-crafted"]
            bc.el(bc.child(e, "infoLinks"), "infoLink", name=rname, id=et.mid(e.get("id"), "mc"), hidden=False,
                  targetId=rid, type="rule")
            weapon = re.sub(r"(?i)^master-crafted ", "", name)
            if weapon != name:
                t = am.weapon_target(b, root, weapon, key)
                if t:
                    bc.child(e, "entryLinks").append(et.link_el(weapon, t, e.get("id"), mn=1, mx=1))
                    made.add(t)
            continue
        shells = re.match(r"(?:Centreline Mounted )?(?:Quad Launcher with )?(\w+) Shells$", name)
        tries = [re.sub(r"^In-built ", "", name)] + ([f"Quad Launcher - {shells.group(1)}"] if shells else [])
        if name == "Phosphex Canister Shot":
            tries.append("Phosphex Canister Shot (Rapier)")
        target = next((t for t in (am.weapon_target(b, root, x, key) for x in tries) if t), None)
        if target:
            bc.child(e, "entryLinks").append(et.link_el(tries[-1] if shells else tries[0], target, e.get("id"),
                                                        mn=1, mx=1))
            made.add(target)
            continue
        p = profile_anywhere(name)
        if p is not None:
            c = et.deep(p)
            for x in c.iter():
                x.tag = x.tag.split("}")[-1]
                for a in ("publicationId", "page"):
                    x.attrib.pop(a, None)
                if x.tag == "modifierGroup":
                    x.attrib.pop("type", None)  # not in the schema (an official file's slip)
                if x.get("id"):
                    x.set("id", et.mid(key, name, x.get("id")))
            bc.child(e, "profiles").append(c)
    return made


def consularis_links(b, entries):
    """'May select one Legiones Consularis upgrade (see Liber Astartes)': the official pick, in place of the
    Builder's list of the upgrades by name."""
    for ds in b.datasheets:
        u = entries[b.units[ds["name"]]]
        for parent in u.iter():
            groups = parent.find("selectionEntryGroups")
            if groups is None:
                continue
            for g in list(groups):
                names = [l.get("name") for l in g.iter("entryLink")] + [x.get("name") for x in g.iter("selectionEntry")]
                if names and all(re.match(r"Legion (Forge Lord|Mortificator|Siege Breaker|Champion|Chaplain|Delegatus|"
                                          r"Esoterist|Herald|Librarian|Primus Medicae|Master of Signals|Armistos|"
                                          r"Moritat|Praevian|Saboteur|Vigilator|Pathfinder|Centurion)$", n)
                                 for n in names):
                    groups.remove(g)
                    links = bc.child(parent, "entryLinks")
                    bc.el(links, "entryLink", import_=True, name="Legiones Consularis", hidden=False,
                          id=et.mid(u.get("id"), "consularis"), type="selectionEntryGroup", targetId=CONSULARIS)


def main():
    setup()
    if 'name="Legion Indomitus Praetor"' in open(LIBRARY, encoding="utf-8").read():
        sys.exit(f"{LIBRARY} already has the Liber Centura expansion")

    def hook(b, root, entries):
        consularis_links(b, entries)
        return fill_empty(b, root, "liber centura")

    cat, b, entries, units, roots, keep = am.transplant_into(LIBRARY, generic_text(), "Legiones Astartes",
                                                             "liber centura", hook)
    cat.save()
    print(f"{LIBRARY}: {len(units)} units, {len(keep)} entries")


if __name__ == "__main__":
    main()
