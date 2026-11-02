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
    text = text.replace("| – Up to one additional ", "| – Up to 1 additional ")
    text = text.replace("Sonic Shrieker Surgical Augment", "Sonic Shriekers")
    text = text.replace("Achea Pattern Force Weapon", "Achea Force Sword")  # its default (Liber Hereticus)
    text = text.replace("Legion Shamshir Jetbike", "Shamshir Jetbike")
    # Wind Rider Brethren: a Scimitar Jetbike whose in-built heavy bolter is a volkite culverin
    text = text.replace("- Legion Scimitar Jetbike (with in-built Volkite Culverin, replacing its usual Heavy Bolter)\n",
                        "- Scimitar Jetbike\n- Volkite Culverin\n")
    text = text.replace("may exchange its jetbike's in-built Volkite Culverin for a:", "may exchange its Volkite Culverin for a:")
    # Varagyr: "one of the following: Frost Axe, Frost Sword or Frost Claw" is the Frost Blade the options exchange
    text = text.replace("- One of the following: Frost Axe, Frost Sword or Frost Claw\n", "- Frost Sword\n")
    text = text.replace("| **Any model in the unit may exchange his Frost Blade for a:** |  |\n",
                        "| **Any model in the unit may exchange his Frost Sword for a:** |  |\n| – Frost Axe | Free |\n"
                        "| – Frost Claw | Free |\n")
    text = text.replace("| **The Thegn Tartaros may exchange his Frost Blade for a:** |",
                        "| **The Thegn Tartaros may exchange his Frost Sword for a:** |")
    text = text.replace("Phosphex Canister Shot\\*", "Phosphex Canister Shot")
    text = text.replace("- Hit and Run\n", "- Hit & Run\n")
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
    am.MOUNT = am.MOUNT.replace("Arm)", "Arm|Wing \\(Front\\))")
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
        w = re.match(r".+? with (.+)$", name)  # "Missile Launcher with Eclipse Missiles": the munition
        if w and not w.group(1).endswith(" Shells"):
            t = am.weapon_target(b, root, re.sub(am.MOUNT, "", w.group(1)), key)
            if t:
                bc.child(e, "entryLinks").append(et.link_el(w.group(1), t, e.get("id"), mn=1, mx=1))
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
            continue
        if e.get("type") == "upgrade" and not re.match(r"(Up to|One|Two) ", name):
            bc.add_rule(e, name, "Named in Liber Centura but not defined in it (see the doc's Rules Checklist).",
                        e.get("id"))
    return made


def profile_owners(root):
    """The Builder's entries whose profiles another entry links to ('The Chirurgeon' wargear shows the weapon's
    profile): they travel with the expansion."""
    owner = {p.get("id"): e.get("id") for e in root.find("sharedSelectionEntries") for p in e.iter("profile")}
    return {owner[l.get("targetId")] for l in root.iter("infoLink")
            if l.get("type") == "profile" and l.get("targetId") in owner}


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


# ---- the Legion-specific units


# units a Legion's catalogue already has: left as they are
LEGION_EXISTING = {"Blood Angels": ("Sanguinary Guard",)}
FAST_ATTACK = ("Wind Rider Brethren", "Ar'Kan Attack Speeder", "Darkwing Gunship", "Raptors, Mutated",
               "Raptors, Proto-Astartes")
HEAVY_SUPPORT = ("Firestorm Bombard Squadron", "Infernus Predator Squadron")
DEDICATED = ("Rhino Castellan",)


def legion_sections():
    """[(Legion name, section text)] for the doc's Legion-specific sections."""
    text = doc()
    i = text.index("## Legion-Specific Rules and Units")
    j = text.index("## Armoury of the Legions")
    parts = re.split(r"^### [IVXL]+ – (.+)$", text[i:j], flags=re.M)
    return [(parts[k].strip(), parts[k + 1]) for k in range(1, len(parts), 2)]


def infer_slot(name, body):
    """The doc gives no Force Organisation slot for these: characters are HQ choices, vehicles and bikes Fast Attack
    or Heavy Support, and the rest (squads) Elites."""
    if name in FAST_ATTACK:
        return "Fast Attack"
    if name in HEAVY_SUPPORT:
        return "Heavy Support"
    if name in DEDICATED:
        return "Dedicated Transport"
    types = re.search(r"\*\*Unit Type\*\*\n\n(.*?)\n\n", body, re.S)
    types = types.group(1) if types else ""
    if "Primarch" in types:
        return "Lords of War"
    if "Unique" in types and ("Character" in types):
        return "HQ"
    return "Elites"


def legion_text(legion, sec):
    """A Legion's section as the Builder reads it: its special rules as the army-wide rules, its fixed Warlord
    Traits, its datasheets under the slots inferred for them, and the Armoury and Wargear."""
    text = doc()
    title = text.split("\n", 1)[0]
    rules, traits = [], []
    m = re.search(r"^#### [^\n]+ Special Rules\n(.*?)(?=^#### |\Z)", sec, re.M | re.S)
    for ln in (m.group(1) if m else "").split("\n"):
        w = re.match(r"\*\*Warlord: (.+?)\.\*\* (.*)$", ln)
        if w:
            traits.append(f"### Warlord: {w.group(1)}\n\n{w.group(2)}\n")
        elif ln.startswith("**") and "Not defined in Liber Centura" not in ln:
            rules.append(ln)
    slots = {}
    skip = LEGION_EXISTING.get(legion, ())
    for d in re.finditer(r"^#### ((?:0-\d+ )?([^\n]+?)) — (\d+) pts\n(.*?)(?=^#### |\Z)", sec, re.M | re.S):
        if d.group(2) in skip:
            continue
        slot = infer_slot(d.group(2), d.group(4))
        if slot == "Dedicated Transport":
            slot = "Elites"  # built as a unit; dedicated_transports() takes its root link away
        slots.setdefault(slot, []).append(f"### {d.group(1)} — {d.group(3)} pts\n{d.group(4)}")
    # the Legion's own wargear ("#### Magma Plating"), beside the Armoury's
    gear = []
    for g in re.finditer(r"^#### ([^\n]+)\n(.*?)(?=^#### |\Z)", sec, re.M | re.S):
        if re.search(r" — \d+ pts$|Special Rules$|^Legiones Consularis|^Rite of War|^Additional Options|"
                     r"Psychic Disciplines$|Sub-type$|\(\+\d+ points\)$", g.group(1)):
            continue
        if re.search(r"^\| Weapon \| (Upgrades to|Exchanged for) \|", g.group(2), re.M):
            continue  # an upgrade table ("Xenobane Cannons"): options on the units, not an item
        gear.append(f"#### {g.group(1)}\n" + re.sub(r"^\*[^*\n]+\*$", "", g.group(2), flags=re.M))
    order = ("HQ", "Elites", "Troops", "Fast Attack", "Heavy Support", "Lords of War")
    units = "\n".join(f"## {s}\n\n" + "\n".join(slots[s]) for s in order if s in slots)
    wargear = wargear_items(section(text, "Legiones Wargear"))
    out = [title, "## Army-wide Special Rules\n\n" + "\n\n".join(rules)]
    if traits:
        out.append("## Warlord Traits\n\n" + "\n".join(traits))
    out += [units, armoury(text), wargear + "\n" + "\n".join(gear)]
    return fixes("\n".join(out))


def rhino_castellan(path):
    """'A Rhino Castellan may be taken instead of a Legion Rhino Transport as a Dedicated Transport by any unit that
    could take one': a pick on the Iron Warriors catalogue's links to those units, and no root link of its own."""
    cat = et.Text(path)
    root = ET.fromstring(cat.s.encode("utf-8"))
    C = et.NS["cat"]
    castellan = next(e for e in root.find(C + "sharedSelectionEntries") if e.get("name") == "Rhino Castellan")
    lib = ET.parse(LIBRARY).getroot()
    rhino_units = {u.get("id") for u in lib.find(C + "sharedSelectionEntries")
                   if any(l.get("name") in ("Legion Rhino Transport", "Rhino Transport") for l in u.iter(C + "entryLink"))}
    n = 0
    for link in root.find(C + "entryLinks"):
        if link.get("targetId") == castellan.get("id"):
            cat.remove(link.get("id"))
        elif link.get("targetId") in rhino_units:
            g = et.E("selectionEntryGroup", id=et.mid(link.get("id"), "castellan"), name="Dedicated Transport (Iron Warriors)",
                     hidden=False, collective=False, import_=True)
            bc.add_constraint(g, "max", 1, et.mid(link.get("id"), "castellan max"))
            bc.child(g, "entryLinks").append(et.link_el("Rhino Castellan", castellan.get("id"), et.mid(link.get("id"),
                                                                                                    "castellan"), mx=1))
            cat.add(link.get("id"), "selectionEntryGroups", [g])
            n += 1
    cat.save()
    return n


LEGION_ALLOWED = [r"is not defined in the doc", r"has no weapon", r"matches no wargear"]


def legion_file(legion):
    return f"2022 - LA - {legion}.cat"


def add_legions():
    """Each Legion's own units into its catalogue."""
    am.ALLOWED = ALLOWED + LEGION_ALLOWED
    am.LIBS = [LIBRARY, "2022 - Mech Library.cat"]
    for legion, sec in legion_sections():
        path = legion_file(legion)
        key = f"liber centura {legion}"

        def hook(b, root, entries, key=key):
            consularis_links(b, entries)
            return fill_empty(b, root, key) | profile_owners(root)

        cat, b, entries, units, roots, keep = am.transplant_into(path, legion_text(legion, sec),
                                                                 f"Legiones Astartes ({legion})", key, hook)
        cat.save()
        print(f"{path}: {len(units)} units, {len(keep)} entries")
        if legion == "Iron Warriors":
            print(f"  Rhino Castellan on {rhino_castellan(path)} units")


def main():
    setup()
    if 'name="Legion Indomitus Praetor"' in open(LIBRARY, encoding="utf-8").read():
        sys.exit(f"{LIBRARY} already has the Liber Centura expansion")

    def hook(b, root, entries):
        consularis_links(b, entries)
        return fill_empty(b, root, "liber centura") | profile_owners(root)

    cat, b, entries, units, roots, keep = am.transplant_into(LIBRARY, generic_text(), "Legiones Astartes",
                                                             "liber centura", hook)
    cat.save()
    print(f"{LIBRARY}: {len(units)} units, {len(keep)} entries")
    add_legions()


if __name__ == "__main__" and sys.argv[1:2] == ["--legion-check"]:
    setup()
    for legion, sec in legion_sections():
        t = legion_text(legion, sec)
        b = bc.Builder("Liber Centura", f"Legiones Astartes ({legion})", t)
        b.build()
        print(legion, len(b.datasheets), [p for p in b.problems])
elif __name__ == "__main__":
    main()
