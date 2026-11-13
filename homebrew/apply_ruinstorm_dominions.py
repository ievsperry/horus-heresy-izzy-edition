#!/usr/bin/env python3
"""Apply the Ætheric Dominions, Advanced Reactions and Warlord Traits of homebrew/source/ruinstorm.md.

usage: python3 homebrew/apply_ruinstorm_dominions.py

- Daemon Library.cat: each of the eight Ætheric Dominions (which every army that picks one uses: Daemons of the
  Ruinstorm, Bound Daemons, Word Bearers, Legiones Astartes, Imperialis Militia) takes the doc's Detachment Ability
  and Restriction as its rule, links the special rules it gives, and shows its Advanced Reaction. The official
  Infernal Tempest Elemental Eruption weapon goes. Two Restrictions are checked: Heedless Slaughter is an error in a
  Daemons of the Ruinstorm Detachment with a Psyker (in any other army, only with a Psyker in the same unit), and
  Ravenous Dissolution in an Allied Detachment or an army that has one.
- 2022 - Daemons - Daemons of the Ruinstorm.cat: the Empyric Surge Advanced Reaction on the army's Ætheric Dominion
  entry, and the Warlord Traits: the three generic traits and each Dominion's trait (shown, and allowed, only in a
  Detachment of that Dominion) replace the official Ruinstorm and generic traits. The Arch-Daemon, a Warlord only for
  the Maw of Annihilation, takes them too.

Edits are made as text, so each file keeps its own formatting. It refuses to run twice."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import el, make_id, norm  # noqa: E402
from expansion_tools import E, Text  # noqa: E402

LIBRARY = "Daemon Library.cat"
CAT = "2022 - Daemons - Daemons of the Ruinstorm.cat"
DOC = "homebrew/source/ruinstorm.md"
REACTION = ("90b9-7fab-87db-aed3", "Reactions", "c627-4637-8de5-65fb")
WARLORD_TRAIT = et.WARLORD_TRAIT
PSYKER_CATEGORY = "6e0c-29ba-a445-8321"
RUINSTORM_FACTION = "afca-3047-fb26-d097"  # the game system's Daemons of the Ruinstorm army entry
ALLIED = "d4f2-6da5-b6de-06ec"
DOMINIONS = {"Heedless Slaughter": "3d70-1d54-a791-ac60", "Putrid Corruption": "b7db-bf16-47c5-dc05",
             "Infernal Tempest": "e4fb-66cd-e07d-609b", "Rapturous Sensation": "1214-3abe-c6d1-2038",
             "Encroaching Ruin": "ca6c-e8cf-7bc1-eaa0", "Malevolent Artifice": "9508-8124-d34a-500a",
             "Ravenous Dissolution": "945c-b969-75eb-19d9", "Formless Distortion": "8ed0-3582-f536-c48e"}
# the special rules each Detachment Ability gives, as shown
GIVES = {"Heedless Slaughter": [("Rage (X)", "Rage (2)"), ("Furious Charge (X)", "Furious Charge (1)")],
         "Putrid Corruption": [("Feel No Pain (X)", "Feel No Pain (5+)")],
         "Infernal Tempest": [],
         "Rapturous Sensation": [("Fleet (X)", "Fleet (2)"), ("Rending (X)", "Rending (6+)")],
         "Encroaching Ruin": [("Armourbane (X)", "Armourbane (Melee)"), ("Sunder", None),
                              ("Move Through Cover", None)],
         "Malevolent Artifice": [("It Will Not Die (X)", "It Will Not Die (5+)")],
         "Ravenous Dissolution": [("Hatred (X)", "Hatred (Everything)")],
         "Formless Distortion": [("Shrouded (X)", "Shrouded (6+)")]}
ARMY_DOMINION = "f6d5-4f8d-7bcc-1405"  # the Ruinstorm army's Ætheric Dominion (Whole Army) entry
TRAITS_GROUP, TRAITS_INNER, GENERIC_LINK = "2f76-74c1-d329-d3ab", "9bab-545c-9f9d-e018", "3c07-396e-92c6-905b"
ARCH_DAEMON = "1fbb-b82e-ae1e-5a12"


def mid(*parts):
    return make_id("ruinstorm dominions", *parts)


def doc():
    """{'## title': {'### title': [lines]}}."""
    out, top, sub = {}, None, None
    for line in open(DOC, encoding="utf-8").read().splitlines():
        if line.startswith("## "):
            top, sub = line[3:].strip(), None
            out[top] = {}
        elif line.startswith("### ") and top:
            sub = line[4:].strip()
            out[top][sub] = []
        elif top and sub:
            out[top][sub].append(line)
    return out


def dominion_parts(lines):
    """Detachment Ability, Restriction, (reaction name, text), (trait name, text) of a Dominion."""
    text = "\n".join(lines)
    ability = re.search(r"\*\*Detachment Ability:\*\* (.+)", text).group(1).strip()
    restriction = re.search(r"\*\*Restriction:\*\* (.+)", text).group(1).strip()
    m = re.search(r"\*\*Advanced Reaction: (.+?)\*\*\n\n((?:- .+\n?)+)", text)
    reaction = (m.group(1).strip(), "\n".join(l[2:] for l in m.group(2).strip().splitlines()))
    m = re.search(r"\*\*Warlord Trait: (.+?)\*\*\n\n(.+)", text)
    trait = (m.group(1).strip(), m.group(2).strip())
    return ability, restriction, reaction, trait


def plain(lines):
    """A section's body without its italic flavour line or bullets' dashes."""
    out = []
    for l in lines:
        l = l.strip()
        if not l or (l.startswith("*") and l.endswith("*") and not l.startswith("**")):
            continue
        out.append(l[2:] if l.startswith("- ") else l)
    return "\n".join(out)


def profile(type_, name, text, key):
    p = E("profile", id=mid(key, "profile", name), name=name, hidden=False, typeId=type_[0], typeName=type_[1])
    el(el(p, "characteristics"), "characteristic", name="Text" if type_ == WARLORD_TRAIT else "Description",
       typeId=type_[2]).text = text
    return p


def replace_block(text_file, eid, fn):
    """Parse the element with this id, change it with fn, and write it back in place at its own indent."""
    start, end, indent, _ = text_file.block(eid)
    e = ET.fromstring(text_file.s[start:end].replace(text_file.nl, "\n"))
    fn(e)
    new = et.xml(e, indent // 2).lstrip(" ").replace("\n", text_file.nl)
    text_file.s = text_file.s[:start] + new + text_file.s[end:]


def cond(parent, childId, kind="atLeast", value=1, scope="force", field="selections", forces=False):
    el(bc.child(parent, "conditions"), "condition", type=kind, value=value, field=field, scope=scope,
       childId=childId, shared=True, includeChildSelections=True, includeChildForces=forces, percentValue=False)


def main():
    lib, cat = Text(LIBRARY), Text(CAT)
    if mid("trait", "Lord of the Unstable Veil") in cat.s:
        sys.exit(f"{CAT} already has the Ætheric Dominion changes")
    d = doc()
    rules_idx = {}
    for f in (LIBRARY, et.GST):
        root = ET.parse(f).getroot()
        for r in root.iter():
            if r.tag.endswith("}rule") and r.get("name"):
                rules_idx.setdefault(norm(r.get("name")), r.get("id"))

    # ---- the Dominions (Daemon Library)
    traits = {}
    for name, eid in DOMINIONS.items():
        ability, restriction, reaction, trait = dominion_parts(d["Ætheric Dominions"][name])
        traits[name] = trait

        def change(e, name=name, ability=ability, restriction=restriction, reaction=reaction):
            rule = e.find("rules/rule")
            rule.find("description").text = f"Detachment Ability: {ability}\n\nRestriction: {restriction}"
            rule.attrib.pop("page", None)
            rule.attrib.pop("publicationId", None)
            for tag in ("infoLinks", "selectionEntries", "profiles"):
                old = e.find(tag)
                if old is not None:
                    e.remove(old)
            links = el(e, "infoLinks")
            for rname, shown in GIVES[name]:
                il = el(links, "infoLink", id=mid(name, "gives", rname), name=rname, hidden=False,
                        targetId=rules_idx[norm(rname)], type="rule")
                if shown:
                    el(el(il, "modifiers"), "modifier", type="set", field="name", value=shown)
            if not len(links):
                e.remove(links)
            el(e, "profiles").append(profile(REACTION, f"Advanced Reaction: {reaction[0]}", reaction[1], name))
            cmax = next(c for c in e.findall("constraints/constraint") if c.get("type") == "max")
            mods = bc.child(e, "modifiers")
            if name == "Heedless Slaughter":
                # a Daemons of the Ruinstorm Detachment may have no Psyker; in any other army a Psyker may be in the
                # Detachment but not in the unit with this Dominion
                m = el(mods, "modifier", type="set", field=cmax.get("id"), value=0)
                el(m, "comment").text = ("Heedless Slaughter: no Psykers in a Daemons of the Ruinstorm Detachment, "
                                         "or in the unit elsewhere")
                g = el(el(m, "conditionGroups"), "conditionGroup", type="or")
                cond(g, PSYKER_CATEGORY, scope="parent")
                ruinstorm = el(bc.child(g, "conditionGroups"), "conditionGroup", type="and")
                cond(ruinstorm, RUINSTORM_FACTION)
                cond(ruinstorm, PSYKER_CATEGORY)
            if name == "Ravenous Dissolution":  # no Allied Detachment, and never one itself
                m = el(mods, "modifier", type="set", field=cmax.get("id"), value=0)
                el(m, "comment").text = "Ravenous Dissolution: no Allied Detachment"
                g = el(el(m, "conditionGroups"), "conditionGroup", type="or")
                cond(g, ALLIED, field="forces", scope="roster", forces=True)
                el(bc.child(g, "conditions"), "condition", type="instanceOf", value=0, field="selections",
                   scope="ancestor", childId=ALLIED, shared=True, percentValue=False, includeChildSelections=False,
                   includeChildForces=False)
        replace_block(lib, eid, change)

    # ---- Empyric Surge (every Daemons of the Ruinstorm unit)
    surge_name, surge_lines = next(iter(d["Advanced Reactions"].items()))
    cat.add(ARMY_DOMINION, "profiles", [profile(REACTION, f"Advanced Reaction: {surge_name}", plain(surge_lines),
                                                "army")])

    # ---- Warlord Traits: the generic three and the Detachment's Dominion trait
    def new_traits(inner):
        for e in list(inner.find("selectionEntries")):
            inner.find("selectionEntries").remove(e)
        entries = inner.find("selectionEntries")
        for tname, lines in d["Warlord Traits"].items():
            t = el(entries, "selectionEntry", type="upgrade", import_=True, name=tname, hidden=False,
                   id=mid("trait", tname))
            el(t, "profiles").append(profile(WARLORD_TRAIT, tname, plain(lines), tname))
            bc.add_cost(t, 0)
        for dom, (tname, text) in traits.items():
            t = el(entries, "selectionEntry", type="upgrade", import_=True, name=tname, hidden=False,
                   id=mid("trait", tname))
            cid = bc.add_constraint(t, "max", 1, mid("trait", tname, "max"))
            for field, value in (("hidden", "true"), (cid, 0)):
                m = el(bc.child(t, "modifiers"), "modifier", type="set", field=field, value=value)
                cond(m, DOMINIONS[dom], "lessThan")
            el(t, "profiles").append(profile(WARLORD_TRAIT, tname, f"{dom} only. {text}", tname))
            bc.add_cost(t, 0)
    replace_block(cat, TRAITS_INNER, new_traits)
    cat.remove(GENERIC_LINK)  # the generic traits are replaced as well
    link = E("entryLink", import_=True, name="Warlord Traits (Ruinstorm Daemons)", hidden=False,
             type="selectionEntryGroup", id=mid("arch-daemon traits"), targetId=TRAITS_GROUP)
    cat.add(ARCH_DAEMON, "entryLinks", [link])

    lib.bump("catalogue")
    cat.bump("catalogue")
    lib.save()
    cat.save()
    print(f"{LIBRARY}: 8 Ætheric Dominions replaced; {CAT}: Empyric Surge, "
          f"{len(d['Warlord Traits']) + len(traits)} Warlord Traits")


if __name__ == "__main__":
    main()
