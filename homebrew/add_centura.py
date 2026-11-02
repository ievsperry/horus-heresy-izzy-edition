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
from xml.sax.saxutils import escape

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


DOC_ENTRIES = []  # every Builder entry, for the options to copy weapons the doc defines

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
            DOC_ENTRIES.extend(root.find("sharedSelectionEntries"))
            consularis_links(b, entries)
            return fill_empty(b, root, key) | profile_owners(root)

        cat, b, entries, units, roots, keep = am.transplant_into(path, legion_text(legion, sec),
                                                                 f"Legiones Astartes ({legion})", key, hook)
        cat.save()
        print(f"{path}: {len(units)} units, {len(keep)} entries")
        if legion == "Iron Warriors":
            print(f"  Rhino Castellan on {rhino_castellan(path)} units")


# ---- Rites of War (the game system's pick)


RITES = "cf3e-1d75-6f91-651f"
LEGION_CODES = {"Dark Angels": "DA", "Emperor's Children": "EC", "Iron Warriors": "IW", "White Scars": "WS",
                "Space Wolves": "SW", "Imperial Fists": "IF", "Night Lords": "NL", "Blood Angels": "BA",
                "Iron Hands": "IH", "World Eaters": "WE", "Ultramarines": "UM", "Death Guard": "DG",
                "Thousand Sons": "TS", "Sons of Horus": "SoH", "Word Bearers": "WB", "Salamanders": "SAL",
                "Raven Guard": "RG", "Alpha Legion": "AL"}
MODIFIED_RITES = {"Angel's Wrath": "ed1f-9473-df70-4544", "Fury of the Ancients": "b5b7-3410-a8e5-95a6",
                  "Pride of the Legion": "4ca1-b02c-e2c7-5f09", "Sky-Hunter Phalanx": "2c36-fde3-14ed-4db4"}


def rite_text(body):
    """A Rite's block as the game system words its Rites: 'Effects' and 'Limitations' with bullets, its own
    special rules after them."""
    out = []
    for ln in body.split("\n"):
        ln = ln.strip()
        if not ln or re.fullmatch(r"\*[^*].*\*", ln):
            continue
        m = re.fullmatch(r"\*\*(Effects|Limitations)\*\*", ln)
        if m:
            out.append(m.group(1))
        elif ln.startswith("- "):
            out.append("• " + bc.strip_md(ln[2:]).replace("*", ""))
        else:
            out.append(bc.strip_md(ln).replace("*", ""))
    return "\n".join(out)


def rites():
    """The doc's Rites of War in the game system's Rites of War pick (each Legion's shown only to that Legion, as
    the official ones are), and its additions to four official Unaligned Rites appended to their text."""
    G = et.NS["gst"]
    gst = et.Text(et.GST)
    groot = ET.fromstring(gst.s.encode("utf-8"))
    group = next(g for g in groot.iter(G + "selectionEntryGroup") if g.get("id") == RITES)
    existing = {e.get("name") for e in group.iter(G + "selectionEntry")}
    text = doc()
    blocks = [(None, m) for m in re.finditer(r"^#### Rite of War: ([^\n]+)\n(.*?)(?=^#{2,4} |\Z)",
                                              section(text, "Rites of War"), re.M | re.S)]
    for legion, sec in legion_sections():
        blocks += [(legion, m) for m in re.finditer(r"^#### Rite of War: ([^\n]+)\n(.*?)(?=^#### |\Z)", sec,
                                                    re.M | re.S)]
    new = []
    for legion, m in blocks:
        name = m.group(1).strip() + (f" ({LEGION_CODES[legion]})" if legion else "")
        if name in existing:
            continue
        rid = bc.make_id("centura rite", name)
        e = et.E("selectionEntry", id=rid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
        if legion:
            # the same gating as an official Rite of this Legion
            twin = next(x for x in group.iter(G + "selectionEntry") if x.get("name").endswith(f"({LEGION_CODES[legion]})"))
            mods = twin.find(G + "modifiers")
            if mods is not None:
                c = et.deep(mods)
                for x in c.iter():
                    x.tag = x.tag.split("}")[-1]
                    if x.get("id"):
                        x.set("id", bc.make_id(rid, x.get("id")))
                e.append(c)
        bc.add_rule(e, m.group(1).strip(), rite_text(m.group(2)), rid)
        bc.add_cost(e, 0)
        new.append(e)
    if new:
        gst.add(RITES, "selectionEntries", new)
    for name, eid in MODIFIED_RITES.items():
        add = re.search(r"^- \*\*" + re.escape(name) + r":\*\* (.+)$", text, re.M).group(1)
        start, end, _, _ = gst.block(eid)
        body = gst.s[start:end]
        if "Liber Centura:" in body:
            continue
        k = body.index("</description>")
        body = body[:k] + gst.nl + "Liber Centura: " + escape(add) + body[k:]
        gst.s = gst.s[:start] + body + gst.s[end:]
    gst.save()
    return len(new)


# Rites of War that move units to another slot: (Rite, catalogue, unit, slot, with Compulsory Troops)
RITE_SLOTS = [
    ("Destroyer Company", LIBRARY, "Destroyer Assault Squad", "Troops", True),
    ("Destroyer Company", LIBRARY, "Mortalis Destroyer Squad", "Troops", True),
    ("Storm-Lance Tumen", LIBRARY, "Outrider Squadron", "Troops", True),
    ("Storm-Lance Tumen", LIBRARY, "Spatha Attack Bike Squadron", "Troops", True),
    ("Fury of the Ancients", LIBRARY, "Castra Ferrum Dreadnought Talon", "Troops", True),
    ("Fury of the Ancients", LIBRARY, "Legion Contemptor-Cortus Dreadnought Talon", "Troops", True),
    ("Pride of the Legion", LIBRARY, "Legion Assault Veteran Squad", "Troops", True),
    ("Pride of the Legion", LIBRARY, "Saturnine Terminator Squad", "Heavy Support", False),
    ("The Iron Without (IW)", "2022 - LA - Iron Warriors.cat", "Heavy Support Squad", "Troops", False),
    ("Bolt From Blue Skies (WS)", "2022 - LA - White Scars.cat", "Outrider Squadron", "Troops", True),
    ("Bolt From Blue Skies (WS)", "2022 - LA - White Scars.cat", "Sky-Hunter Squadron", "Troops", True),
    ("The Gates of Hel (IH)", "2022 - LA - Iron Hands.cat", "Iron Revenants", "Troops", True),
    ("The Red Marked (UM)", "2022 - LA - Ultramarines.cat", "Red-Marked Squad", "Troops", True),
    ("Rukal Breacher Battalion (SoH)", "2022 - LA - Sons of Horus.cat", "Rukal Breacher Squad", "Troops", True),
]


def rite_id(name):
    official = {"Fury of the Ancients": MODIFIED_RITES["Fury of the Ancients"],
                "Pride of the Legion": MODIFIED_RITES["Pride of the Legion"]}
    return official.get(name) or bc.make_id("centura rite", name)


def rite_slots():
    """'X may be taken as Troops': as the official Rites do it, a second root link to the unit in that slot,
    shown only while the Detachment has the Rite."""
    C = et.NS["cat"]
    unit_ids = {}
    for f in {f for _, f, _, _, _ in RITE_SLOTS} | {LIBRARY}:
        unit_ids.update({(f, e.get("name")): e.get("id") for e in ET.parse(f).getroot().find(C + "sharedSelectionEntries")
                         if e.get("type") == "unit"})
    lib_units = {n: i for (f, n), i in unit_ids.items() if f == LIBRARY}
    by_file = {}
    for rite, f, unit, slot, compulsory in RITE_SLOTS:
        uid = unit_ids.get((f, unit)) or lib_units[unit]
        lid = bc.make_id("centura rite slot", rite, unit)
        l = et.E("entryLink", id=lid, name=unit, hidden=True, collective=False, import_=False, targetId=uid,
                 type="selectionEntry")
        mod = bc.el(bc.el(l, "modifiers"), "modifier", type="set", field="hidden", value="false")
        bc.el(bc.el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
              childId=rite_id(rite), shared=True, includeChildSelections=True, includeChildForces=False,
              percentValue=False)
        cats = bc.el(l, "categoryLinks")
        bc.el(cats, "categoryLink", id=bc.make_id(lid, "unit"), name="Unit:", hidden=False,
              targetId="36c3-e85e-97cc-c503", primary=False)
        for cid, cname, primary in et.SLOTS[slot]:
            if primary or (compulsory and "Compulsory" in cname):
                bc.el(cats, "categoryLink", id=bc.make_id(lid, cid), name=cname, hidden=False, targetId=cid,
                      primary=primary)
        by_file.setdefault(f, []).append(l)
    n = 0
    for f, links in by_file.items():
        cat = et.Text(f)
        links = [l for l in links if l.get("id") not in cat.s]
        if links:
            am.add_top(cat, "entryLinks", links)
            cat.save()
            n += len(links)
    return n


# ---- each Legion's weapon upgrades, beside the weapons they replace

# (Legion, weapon, upgrade, extra points, characters only, independent characters only)
SWAPS = [
    ("Dark Angels", "Gravis Bolt Cannon", "Gravis Xenobane Cannon", 5, False, False),
    ("Dark Angels", "Gravis Heavy Bolter Battery", "Gravis Xenobane Cannon Battery", 5, False, False),
    ("Dark Angels", "Heavy Bolter", "Xenobane Cannon", 2, False, False),
    ("Dark Angels", "Twin-Linked Heavy Bolter", "Twin-Linked Xenobane Cannon", 2, False, False),
    ("Iron Warriors", "Gravis Heavy Bolter Battery", "Gravis Shrapnel Cannon Battery", 10, False, False),
    ("Iron Warriors", "Twin-Linked Heavy Bolter", "Twin-Linked Shrapnel Cannon", 2, False, False),
    ("Salamanders", "Cyclonic Melta Lance", "Conflagration Melta Lance", 10, False, False),
    ("Salamanders", "Gravis Melta Cannon", "Conflagration Melta Cannon", 10, False, False),
    ("Salamanders", "Meltagun", "Conflagration Meltagun", 5, False, False),
    ("Salamanders", "Multi-Melta", "Conflagration Multi-Melta", 10, False, False),
    ("White Scars", "Power Glaive", "Power Tulwar", 0, True, False),
    ("Space Wolves", "Bolt Pistol", "Helfrost Pistol", 20, True, False),
    ("Iron Hands", "Power Weapon", "Medusan Zweihander", 10, True, False),
    ("Thousand Sons", "Achea Force Sword", "Achea Force Stave", 0, False, False),
    ("Blood Angels", "Warhawk Jump Pack", "Angelus Pattern Jump Pack", 25, False, True),
]


def doc_entries():
    """The Builder's entries for the whole doc (the weapons and wargear it defines)."""
    if not DOC_ENTRIES:
        texts = [("Legiones Astartes", generic_text())] + [(f"Legiones Astartes ({l})", legion_text(l, s_))
                                                           for l, s_ in legion_sections()]
        for faction, t in texts:
            b = bc.Builder("Liber Centura", faction, t)
            DOC_ENTRIES.extend(b.build().find("sharedSelectionEntries"))
    return DOC_ENTRIES


def swaps():
    """'Any model with Legiones Astartes (Salamanders) may exchange a Meltagun for a Conflagration Meltagun (+5)':
    the upgrade beside the weapon in every pick that offers it, in the library and the Legion's catalogue, shown
    only to that Legion (and only on characters where the doc says so). The upgrades are shared entries in the
    library, copied from the doc's profiles."""
    C = et.NS["cat"]
    et.configure(LIBRARY, am.LIBS, DOC, "", "liber centura swaps")
    ids = legion_ids()
    lib = et.Text(LIBRARY)
    lroot = ET.fromstring(lib.s.encode("utf-8"))
    shared = {e.get("name"): e.get("id") for e in lroot.find(C + "sharedSelectionEntries")}
    new, targets = [], {}
    for _, _, up, _, _, _ in SWAPS:
        if up in targets:
            continue
        if up in shared:
            targets[up] = shared[up]
            continue
        src = am.anywhere(up, doc_entries())
        if src is None:
            continue
        e = am.clone(src, up, bc.make_id("centura swap", up))
        e.set("id", bc.make_id("centura swap weapon", up))
        bc.add_cost(e, 0)
        new.append(e)
        targets[up] = e.get("id")
    if new:
        am.add_top(lib, "sharedSelectionEntries", new)
        lib.save()
    n = 0
    for f in [LIBRARY] + [legion_file(l) for l in sorted({x[0] for x in SWAPS})]:
        cat = et.Text(f)
        root = ET.fromstring(cat.s.encode("utf-8"))
        parent = {c: p_ for p_ in root.iter() for c in p_}
        def character(g, independent):
            x = g
            while x is not None:
                cats = [c.get("name") or "" for c in x.findall(f"{C}categoryLinks/{C}categoryLink")]
                types = [p_.findtext(f".//{C}characteristic[@name='Unit Type']") or "" for p_ in
                         x.findall(f"{C}profiles/{C}profile")]
                if any(("Independent Character" if independent else "Character") in t for t in cats + types):
                    return True
                x = parent.get(x)
            return False
        adds = []
        for g in root.iter(C + "selectionEntryGroup"):
            items = list(g.findall(f"{C}entryLinks/{C}entryLink")) + list(g.findall(f"{C}selectionEntries/{C}selectionEntry"))
            for legion, weapon, up, pts, chars, ics in SWAPS:
                if f != LIBRARY and f != legion_file(legion) or up not in targets:
                    continue
                if not any(am.bare(x.get("name") or "") == am.bare(weapon) for x in items):
                    continue
                if any(am.bare(x.get("name") or "") == am.bare(up) for x in items):
                    continue
                if (chars or ics) and not character(g, ics):
                    continue
                src = next(x for x in items if am.bare(x.get("name") or "") == am.bare(weapon))
                base = next((float(c.get("value")) for c in src.findall(f"{C}costs/{C}cost")), 0)
                lid = bc.make_id("centura swap", g.get("id"), up)
                if lid in cat.s:
                    continue
                l = et.E("entryLink", id=lid, name=up, hidden=False, collective=False, import_=True,
                         targetId=targets[up], type="selectionEntry")
                mod = bc.el(bc.el(l, "modifiers"), "modifier", type="set", field="hidden", value="true")
                bc.el(bc.el(mod, "conditions"), "condition", type="equalTo", value=0, field="selections",
                      scope="force", childId=ids[legion], shared=True, includeChildSelections=True,
                      includeChildForces=False, percentValue=False)
                mx = next((c for c in src.findall(f"{C}constraints/{C}constraint") if c.get("type") == "max"), None)
                if mx is not None:
                    bc.el(bc.child(l, "constraints"), "constraint", type="max", value=mx.get("value"),
                          field="selections", scope="parent", shared=True, id=bc.make_id(lid, "max"),
                          percentValue=False, includeChildSelections=False, includeChildForces=False)
                bc.add_cost(l, int(base + pts) if float(base + pts).is_integer() else base + pts)
                adds.append((g.get("id"), l))
        for gid, l in adds:
            start, end, indent, _ = cat.block(gid)
            body = cat.s[start:end]
            if "<entryLinks>" in body and not re.search(re.escape(cat.nl) + " " * (indent + 2) + "<entryLinks>", body):
                continue  # an official pick laid out irregularly: its own list could not be found
            cat.add(gid, "entryLinks", [l])
        if adds:
            cat.save()
            n += len(adds)
    return n


# ---- limits on the Additional Options, Magma Plating, the Saturnine Centurion's Consularis


# (catalogue, unit, option name, limit): "for every five models, one ..." (per5) or a fixed most
OPTION_LIMITS = [
    (LIBRARY, "Terminator Indomitus Squad", "Havoc Launcher", "per5"),
    (LIBRARY, "Terminator Indomitus Squad", "Plasma Blaster", "per5"),
    (LIBRARY, "Terminator Indomitus Squad", "Plasma Cannon", "per5"),
    ("2022 - LA - Iron Hands.cat", "Medusan Immortal Squad", "Power Weapon", "per5"),
    (LIBRARY, "Castra Ferrum Dreadnought Talon", "Hunter-Killer Missile", 2),
]
UP_TO_THREE = (LIBRARY, "Legion Primaris-Lightning Strike Fighter")


def option_limits():
    """'For every five models, one Legion Indomitus may take a Havoc Launcher': at most one per five models in the
    unit; 'up to two Hunter-Killer Missiles'; the Primaris-Lightning's 'up to three of the following'."""
    C = et.NS["cat"]
    n = 0
    for f in {x[0] for x in OPTION_LIMITS} | {UP_TO_THREE[0]}:
        cat = et.Text(f)
        root = ET.fromstring(cat.s.encode("utf-8"))
        units = {e.get("name"): e for e in root.find(C + "sharedSelectionEntries") if e.get("type") == "unit"}
        for f_, unit, option, limit in OPTION_LIMITS:
            if f_ != f:
                continue
            u = units[unit]
            for l in [x for x in u.iter(C + "entryLink") if x.get("id") in OPTION_IDS and x.get("name") == option]:
                cons = l.findall(f"{C}constraints/{C}constraint")
                if limit == "per5":
                    cid = bc.make_id(l.get("id"), "per five")
                    if cid in cat.s:
                        continue
                    c = et.E("constraint", type="max", value=0, field="selections", scope=u.get("id"), shared=True,
                             id=cid, percentValue=False, includeChildSelections=True, includeChildForces=False)
                    m = et.E("modifier", type="increment", field=cid, value=1)
                    bc.el(bc.el(m, "repeats"), "repeat", field="selections", scope=u.get("id"), value=5,
                          percentValue=False, shared=True, includeChildSelections=True, includeChildForces=False,
                          childId="model", repeats=1, roundUp=False)
                    cat.add(l.get("id"), "constraints", [c])
                    cat.add(l.get("id"), "modifiers", [m])
                else:
                    for c in cons:
                        if c.get("type") == "max" and c.get("value") != str(limit):
                            a, b_, _, _ = cat.block(c.get("id"))
                            cat.s = cat.s[:a] + re.sub(r'value="[^"]*"', f'value="{limit}"', cat.s[a:b_], 1) + cat.s[b_:]
                n += 1
        if f == UP_TO_THREE[0]:
            u = units[UP_TO_THREE[1]]
            g = next((x for x in u.iter(C + "selectionEntryGroup") if x.get("id") in OPTION_IDS), None)
            if g is not None and bc.make_id(g.get("id"), "up to three") not in cat.s:
                cat.add(g.get("id"), "constraints", [et.E("constraint", type="max", value=3, field="selections",
                                                          scope="parent", shared=True,
                                                          id=bc.make_id(g.get("id"), "up to three"),
                                                          percentValue=False, includeChildSelections=True,
                                                          includeChildForces=False)])
                n += 1
        cat.save()
    return n


def magma_plating():
    """'Any model with Legiones Astartes (Salamanders) and the Vehicle Unit Type may take Magma Plating for +15
    points': on every vehicle in the library and the Salamanders catalogue, shown only to the Salamanders."""
    C = et.NS["cat"]
    et.configure(LIBRARY, am.LIBS, DOC, "", "liber centura magma")
    sal = legion_ids()["Salamanders"]
    lib = et.Text(LIBRARY)
    mid_ = bc.make_id("centura magma plating")
    if mid_ not in lib.s:
        src = am.anywhere("Magma Plating", doc_entries())
        e = am.clone(src, "Magma Plating", "centura magma")
        e.set("id", mid_)
        bc.add_cost(e, 0)
        am.add_top(lib, "sharedSelectionEntries", [e])
        lib.save()
    n = 0
    for f in (LIBRARY, legion_file("Salamanders")):
        cat = et.Text(f)
        root = ET.fromstring(cat.s.encode("utf-8"))
        for e in root.find(C + "sharedSelectionEntries").iter(C + "selectionEntry"):
            if e.get("type") not in ("unit", "model"):
                continue
            if not any("Vehicle" in (p.get("typeName") or "") for p in e.findall(f"{C}profiles/{C}profile")):
                continue
            lid = bc.make_id("centura magma", e.get("id"))
            if lid in cat.s:
                continue
            l = et.link_el("Magma Plating", mid_, lid, mx=1, pts=15)
            l.set("id", lid)
            mod = bc.el(bc.child(l, "modifiers"), "modifier", type="set", field="hidden", value="true")
            bc.el(bc.el(mod, "conditions"), "condition", type="equalTo", value=0, field="selections", scope="force",
                  childId=sal, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
            start, end, indent, _ = cat.block(e.get("id"))
            body = cat.s[start:end]
            if "<entryLinks>" in body and not re.search(re.escape(cat.nl) + " " * (indent + 2) + "<entryLinks>", body):
                continue
            cat.add(e.get("id"), "entryLinks", [l])
            n += 1
        cat.save()
    return n


def saturnine_consularis():
    """The Centurion in Saturnine Terminator Armour 'may select one Legiones Consularis upgrade': Legion Forge Lord,
    Mortificator or Siege Breaker only, copies of the official upgrades, in place of the whole official pick."""
    C = et.NS["cat"]
    cat = et.Text(LIBRARY)
    root = ET.fromstring(cat.s.encode("utf-8"))
    u = next(e for e in root.find(C + "sharedSelectionEntries") if e.get("name") == "Centurion in Saturnine Terminator Armour")
    link = next((l for l in u.iter(C + "entryLink") if l.get("targetId") == CONSULARIS), None)
    if link is None:
        return 0
    owner = next(x for x in u.iter() if link in list(x))
    holder = next(x for x in u.iter() if owner in list(x))
    official = next(g for g in root.find(C + "sharedSelectionEntryGroups") if g.get("id") == CONSULARIS)
    pts = {"Forge Lord": 40, "Mortificator": 25, "Siege Breaker": 45}  # the datasheet's costs
    g = et.E("selectionEntryGroup", id=bc.make_id(u.get("id"), "saturnine consularis"), name="Legiones Consularis",
             hidden=False, collective=False, import_=True)
    bc.add_constraint(g, "max", 1, bc.make_id(u.get("id"), "saturnine consularis max"))
    for e in official.find(C + "selectionEntries"):
        if e.get("name") not in pts:
            continue
        c = et.deep(e)
        ids = {x.get("id"): bc.make_id("centura saturnine", x.get("id")) for x in c.iter() if x.get("id")}
        for x in c.iter():
            x.tag = x.tag.split("}")[-1]
            for a in ("id", "field", "childId", "targetId", "scope"):
                if x.get(a) in ids and not (a == "targetId" and x.tag in ("categoryLink", "infoLink", "entryLink")):
                    x.set(a, ids[x.get(a)])
        for cost in c.iter("cost"):
            if cost.get("name") == "Pts" and cost in list(c.find("costs") if c.find("costs") is not None else []):
                cost.set("value", str(pts[e.get("name")]))
        bc.child(g, "selectionEntries").append(c)
    cat.remove(link.get("id"))
    cat.add(holder.get("id"), "selectionEntryGroups", [g])
    cat.save()
    return 1


# ---- Legiones Consularis (the library's official pick)


TRAITOR, LOYALIST = "f9c0-0c5a-3e24-58c7", "d0b6-712f-0b12-a308"


def legion_ids():
    """{Legion: the game system's Legion choice ('IV: Iron Warriors'), the one the official catalogues gate on}."""
    G = et.NS["gst"]
    gst_text = open(et.GST, encoding="utf-8").read()
    lib_text = open(LIBRARY, encoding="utf-8").read()
    out = {}
    for e in ET.parse(et.GST).getroot().iter(G + "selectionEntry"):
        m = re.fullmatch(r"[IVXL]+: (.+)", e.get("name") or "")
        if m and m.group(1) in LEGION_CODES:
            uses = gst_text.count(f'childId="{e.get("id")}"') + lib_text.count(f'childId="{e.get("id")}"')
            if uses > out.get(m.group(1), (None, -1))[1]:
                out[m.group(1)] = (e.get("id"), uses)
    return {k: v[0] for k, v in out.items()}


def block_text(body):
    """A doc block's rules text: its paragraphs and bullets, the flavour line left out."""
    out = []
    for ln in body.split("\n"):
        ln = ln.strip()
        if not ln or re.fullmatch(r"\*[^*].*\*", ln) or ln.startswith("|"):
            continue
        out.append(("• " if ln.startswith("- ") else "") + bc.strip_md(re.sub(r"^- ", "", ln)).replace("*", ""))
    return "\n".join(out)


def consularis():
    """The doc's Legiones Consularis upgrades in the official pick: Lodge Master for a Traitor army, Terran-Born
    Crusader for a Loyalist one, each Legion's own for that Legion."""
    cat = et.Text(LIBRARY)
    if bc.make_id("centura consularis", "Lodge Master") in cat.s:
        return 0
    ids = legion_ids()
    blocks = [(None, m) for m in re.finditer(r"^#### Legiones Consularis: ([^\n]+?) \(\+(\d+) points\)\n(.*?)(?=^#{2,4} |\Z)",
                                              section(doc(), "Legiones Consularis and Pater Consularis"), re.M | re.S)]
    for legion, sec in legion_sections():
        blocks += [(legion, m) for m in re.finditer(r"^#### Legiones Consularis: ([^\n]+?) \(\+(\d+) points\)\n(.*?)"
                                                    r"(?=^#### |\Z)", sec, re.M | re.S)]
    new = []
    for legion, m in blocks:
        name, pts, body = m.group(1), int(m.group(2)), m.group(3)
        eid = bc.make_id("centura consularis", name)
        e = et.E("selectionEntry", id=eid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
        if legion:
            gate, kind = ids[legion], "equalTo"
        else:
            gate = TRAITOR if "Traitor allegiance" in body else LOYALIST if "Loyalist allegiance" in body else None
            kind = "equalTo"
        if gate:
            mod = bc.el(bc.child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
            bc.el(bc.el(mod, "conditions"), "condition", type=kind, value=0, field="selections", scope="force",
                  childId=gate, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        if re.search(r"Only one [^.]* may be taken per army", body):
            bc.add_constraint(e, "max", 1, bc.make_id(eid, "army"), scope="roster", children=True)
        bc.add_rule(e, f"Legiones Consularis: {name}", block_text(body), eid)
        bc.add_cost(e, pts)
        new.append(e)
    cat.add(CONSULARIS, "selectionEntries", new)
    cat.save()
    return len(new)


# ---- options on the official units, and each Legion's own upgrades


OPTION_TABLES = {
    LIBRARY: ["#### Additional Options for Existing HQ Units", "#### Additional Options for Existing Elites Units",
              "#### Additional Options for Existing Troops Units",
              "#### Additional Options for Existing Fast Attack Units",
              "#### Additional Options for Existing Heavy Support Units"],
    "2022 - LA - Iron Hands.cat": ["#### Additional Options for Existing Iron Hands Units"],
}
# the doc's names for the official units
UNIT_NAMES = {"Legion Castraferrum Dreadnought Talon": "Castra Ferrum Dreadnought Talon",
              "Legion Cataphractii Praetor": "Praetor, Cataphractii", "Legion Tartaros Praetor": "Praetor, Tartaros",
              "Legion Deredeo Dreadnought Talon": "Deredeo Dreadnought Talon",
              "Legion Land Raider Achilles": "Land Raider Achilles Squadron",
              "Legion Spatha Attack Bike Squadron": "Spatha Attack Bike Squadron",
              "Legion Tarantula Sentry Gun Battery": "Tarantula Sentry Gun Battery",
              "Legion Terminator Indomitus Squad": "Terminator Indomitus Squad",
              "Legion Whirlwind Squadron": "Whirlwind"}


def normalise(unit, option, cost):
    """A row in the wording plan_options reads ('Exchange X for Y', 'The unit may take X'); a list with a cost
    each ('Heavy Flamer (+5), Heavy Bolter (+10)') as one row per item."""
    o = re.sub(r"\s*\((?:see [^()]*|with in-built [^()]*)\)", "", option)
    listed = re.findall(r"([A-Z][^,():]+?) \(\+(\d+)(?:, [^)]*)?\)", o)
    if len(listed) > 1:
        head = re.match(r"(Deployment option): ", o)
        mount = re.search(r"take one (Pintle Mounted) ", o)
        out = []
        for item, pts in listed:
            item = re.sub(r"^(?:or |.*?: |.*?take one )", "", item.strip())
            if mount and not item.startswith(mount.group(1)):
                item = f"{mount.group(1)} {item}"
            item = re.sub(r"Combi-Weapon of any type", "Combi-Weapon", item)
            out.append((unit, f"Deployment option: {item}" if head else f"The unit may take {item}", f"+{pts} points"))
        return out
    o = re.sub(r"^For every (?:five|5) models, one [\w -]+? may ", "Any model may ", o)
    o = re.sub(r", (?:instead of|fired by) .*$", "", o)
    m = re.match(r"(?:Any|One) [\w -]+? may (?:exchange|replace) (?:its |his |their |all four )?(?:attack bike's )?(.+?) "
                 r"(?:for|with) (?:an? )?(.+)$", o)
    if m:
        return [(unit, f"Exchange {m.group(1)} for {m.group(2)}", cost)]
    m = re.match(r"Replace an? (.+?) (?:with in-built Combi-Bolter )?or an? .+? with an? (.+)$", o)
    if m:  # "Replace a Gravis Power Fist with in-built Combi-Bolter or a Gravis Bolt Cannon with a ...": the arm
        return [(unit, f"Exchange {m.group(1)} for {m.group(2)}", cost)]
    m = re.match(r"(?:Any|One) [\w -]+? may take (?:up to \w+ |an? )?(.+)$", o)
    if m:
        return [(unit, f"The unit may take {re.sub(r's$', '', m.group(1)) if 'Missiles' in m.group(1) else m.group(1)}",
                 cost)]
    return [(unit, o, cost)]


OPTION_IDS = set()  # the ids options() wrote


def options(doc_entries):
    notes = []
    before = {f: set(re.findall(r'\sid="([^"]+)"', open(f, encoding="utf-8").read())) for f in OPTION_TABLES}
    for path, heads in OPTION_TABLES.items():
        et.configure(path, am.LIBS, DOC, "", "liber centura options")
        rows = [r for h in heads for u, o, c in am.option_rows(h) for r in normalise(UNIT_NAMES.get(u, u), o, c)]
        am.apply_ops(am.plan_options(rows, [path], doc_entries, notes))
    for f in OPTION_TABLES:
        OPTION_IDS.update(set(re.findall(r'\sid="([^"]+)"', open(f, encoding="utf-8").read())) - before[f])
    return notes


def table_text(body):
    """A Legion upgrade block's text, its upgrade table as bullets ('Heavy Bolter: Xenobane Cannon, +2 points per
    weapon')."""
    out = []
    for ln in body.split("\n"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")] if ln.startswith("|") else None
        if cells and cells[0] not in ("Weapon", "Unit") and not set(cells[0]) <= {"-"}:
            out.append(f"• {cells[0]}: {cells[1]}" + (f", {cells[2]}" if len(cells) > 2 else ""))
        elif not cells:
            out.append(ln)
    return block_text("\n".join(out))


def legion_upgrades():
    """Each Legion's own upgrades the doc gives for any of its units (Xenobane Cannons, Power Tulwars, Magma
    Plating, The Keys of Hel...): their text on the Legion's entry in its catalogue, where the Legion is chosen."""
    n = 0
    for legion, sec in legion_sections():
        path = legion_file(legion)
        cat = et.Text(path)
        root = ET.fromstring(cat.s.encode("utf-8"))
        C = et.NS["cat"]
        entry = next((l for l in root.find(C + "entryLinks") if re.fullmatch(r"[IVXL]+: " + re.escape(legion),
                                                                              l.get("name") or "")), None)
        if entry is None:
            continue
        rules = []
        for g in re.finditer(r"^#### ([^\n]+)\n(.*?)(?=^#### |\Z)", sec, re.M | re.S):
            title = g.group(1)
            if re.search(r" — \d+ pts$|Special Rules$|^Legiones Consularis|^Rite of War", title):
                continue
            name = re.sub(r" \(\+\d+ points\)$", "", title)
            rid = bc.make_id("centura legion upgrade", legion, name)
            if rid in cat.s:
                continue
            r = et.E("rule", id=rid, name=f"Liber Centura: {name}", hidden=False)
            bc.el(r, "description").text = table_text(g.group(2))
            rules.append(r)
        if rules:
            cat.add(entry.get("id"), "rules", rules)
            cat.save()
            n += len(rules)
    return n


def main():
    setup()
    if 'name="Legion Indomitus Praetor"' in open(LIBRARY, encoding="utf-8").read():
        sys.exit(f"{LIBRARY} already has the Liber Centura expansion")

    def hook(b, root, entries):
        DOC_ENTRIES.extend(root.find("sharedSelectionEntries"))
        consularis_links(b, entries)
        return fill_empty(b, root, "liber centura") | profile_owners(root)

    cat, b, entries, units, roots, keep = am.transplant_into(LIBRARY, generic_text(), "Legiones Astartes",
                                                             "liber centura", hook)
    cat.save()
    print(f"{LIBRARY}: {len(units)} units, {len(keep)} entries")
    add_legions()
    print(f"Rites of War: {rites()} added")
    print(f"Legiones Consularis: {consularis()} added")
    print(f"Rites of War slots: {rite_slots()} links")
    print(f"Legion weapon upgrades: {swaps()} options")
    for note in options(DOC_ENTRIES):
        print("  note:", note)
    print(f"Legion upgrades: {legion_upgrades()} rules on the Legions' entries")
    print(f"Option limits: {option_limits()}")
    print(f"Magma Plating: on {magma_plating()} vehicles")
    print(f"Saturnine Centurion Consularis: {saturnine_consularis()}")


if __name__ == "__main__" and sys.argv[1:2] == ["--legion-check"]:
    setup()
    for legion, sec in legion_sections():
        t = legion_text(legion, sec)
        b = bc.Builder("Liber Centura", f"Legiones Astartes ({legion})", t)
        b.build()
        print(legion, len(b.datasheets), [p for p in b.problems])
elif __name__ == "__main__":
    main()
