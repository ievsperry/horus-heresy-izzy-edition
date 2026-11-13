#!/usr/bin/env python3
"""Add the Titan Legions expansion to the official Titan Legions catalogue.

usage: python3 homebrew/add_titan_legions.py

The doc (homebrew/source/titan-legions.md) is read by build_catalogue.py's Builder, and its units move into
2022 - Titan Legions.cat as text, linked to the official rules and wargear wherever those exist. It also writes:

- the Moderati Recon Foot-Patrols (Fast Attack), Enginseer Field-Repair Team (Elites) and Secutarii Ballistarii
  (Heavy Support), shown only in a Titan Maniple, with their Dedicated Transports by size (a Triaros Armoured
  Conveyor, or the doc's Termite Assault Drill);
- the Titan Maniple's Expanded Maniple Support: +2 Elites, +2 Fast Attack and +2 Heavy Support while the Maniple
  has a Rite of War, and its Titans then outside the 25% Lords of War limit;
- the three Rites of War in a Rite of War entry (Titan Maniple only): an error without a Secutarii Axiarch or a
  Titan (a Warhound for the Vanguard), with a barred unit or slot, or with an Allied Detachment (Ordo Destructor);
  the extra Troops choices (Line where the Rite says so, Compulsory for the Vanguard's Moderati), the Peltasts' and
  Hoplites' Line, the Moderati's Support Squad dropped and the Termite for Secutarii Infantry of ten or fewer
  (Ordo Destructor);
- the two Advanced Reactions on the army's Divisio Tactica entry, and the three Warlord Traits as a Titan Legions
  choice in the Mech Library's Warlord Traits (for the Axiarch and the Titans).

Under a Rite the Warlord must be the Axiarch or a Titan: the official HQs from LI - Assassins and Agents keep their
Warlord choice (rule text). It refuses to run on a catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, child, el  # noqa: E402
from expansion_tools import E, Text, mid  # noqa: E402

CAT = "2022 - Titan Legions.cat"
CAT_ID = "c01b-0224-f806-0d23"
LIBRARY = "2022 - Mech Library.cat"
DOC = "homebrew/source/titan-legions.md"
et.configure(CAT, [LIBRARY, "2022 - LI - Assassins.cat"], DOC, "Titan Legions", "titan legions expansion")

MANIPLE = "aebe-bed9-b32f-a8ea"  # the Titan Maniple force
ALLIED = "d4f2-6da5-b6de-06ec"
MIN_TROOP_LOW = ("4086-0589-f010-e688", "Titan Legion Min Troop/LoW")  # the Maniple's compulsory choice
LOW_LIMIT = "2eaf-32d6-9d1d-d906"  # LoW & Primarchs (25% Limit)
LINE = "6399-5c65-7833-1025"
RITE_CATEGORY = ("d494-e450-d4aa-579a", "Rite of War:")
CATS = {"Elites": "7aee-565f-b0ae-294e", "Troops": "9b5d-fac7-799b-d7e7", "Fast Attack": "20ef-cd01-a8da-376e",
        "Heavy Support": "7031-469a-1aeb-eab0", "Fortification": "a24f-12d8-36c1-f477"}
REACTION = ("90b9-7fab-87db-aed3", "Reactions", "c627-4637-8de5-65fb")
DIVISIO_LINK = "6b36-d1b3-cba5-f217"  # the army's Divisio Tactica: The Titan Legions entry
DIVISIO = "47f0-bba9-6d89-9baa"
TRAITS_GROUP = "1ebb-8e01-7d58-9d99"  # Mech Library: Warlord Traits (the Axiarch's and the Titans')
TRIAROS = "2484-a122-76a2-b142"
AXIARCH = "b08e-55fe-3e1d-913b"
HOPLITE, PELTAST = "f4cc-a854-5467-45cf", "4fc3-7259-f9b0-71cd"
TITANS = {"Warlord Battle Titan": ("d737-baca-32e7-8da6", "0283-c466-47b4-de8f"),
          "Warbringer Nemesis Titan": ("3dd1-77d8-4289-b745", "d6ad-baec-87f6-e839"),
          "Warhound Scout Titan": ("841c-c2f5-9817-3061", "61a7-4c8e-1ef8-84cc"),
          "Reaver Battle Titan": ("2dbc-7655-bb05-ab89", "c8ee-7d52-39c1-17d4")}  # unit, root link
MOD, ENG, BAL, TERMITE = ("Moderati Recon Foot-Patrols", "Enginseer Field-Repair Team", "Secutarii Ballistarii",
                          "Termite Assault Drill")
RITES = {
    "Iron Phalanx of the God-Engines": dict(
        need=[AXIARCH] + [t for t, _ in TITANS.values()], line=[HOPLITE, PELTAST], troops=[ENG],
        bans_slots=["Fortification"]),
    "Vanguard Reconnaissance Maniple": dict(
        need=[AXIARCH, TITANS["Warhound Scout Titan"][0]], line=[PELTAST], compulsory_troops=[MOD],
        bans=[TITANS[n][0] for n in ("Warlord Battle Titan", "Warbringer Nemesis Titan", "Reaver Battle Titan")],
        bans_slots=["Fortification"]),
    "Ordo Destructor Siege Cohort": dict(
        need=[AXIARCH] + [t for t, _ in TITANS.values()], troops=[BAL], no_allies=True, termite=True),
}


def doc_sections():
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


def plain(lines):
    out = []
    for l in lines:
        l = l.strip()
        if not l or (l.startswith("*") and l.endswith("*") and not l.startswith("**")):
            continue
        out.append(l[2:] if l.startswith("- ") else l)
    return "\n".join(out)


def rite_parts(lines):
    parts, cur = {}, None
    for l in lines:
        m = re.match(r"\*\*(Prerequisites|Effects|Limitations)\*\*", l)
        if m:
            cur = m.group(1)
            parts[cur] = []
        elif cur and l.startswith("- "):
            parts[cur].append("• " + l[2:].strip())
    return {k: "\n".join(v) for k, v in parts.items()}


def cond(parent, childId, kind="atLeast", value=1, scope="force", field="selections", forces=False):
    el(child(parent, "conditions"), "condition", type=kind, value=value, field=field, scope=scope, childId=childId,
       shared=True, includeChildSelections=True, includeChildForces=forces, percentValue=False)


def modifier(parent, field, value, kind="set"):
    return el(child(parent, "modifiers"), "modifier", type=kind, field=field, value=value)


def in_maniple_only(e, comment):
    m = modifier(e, "hidden", "true")
    el(m, "comment").text = comment
    el(child(m, "conditions"), "condition", type="notInstanceOf", value=0, field="selections", scope="ancestor",
       childId=MANIPLE, shared=True, percentValue=False, includeChildSelections=False, includeChildForces=False)


def any_rite(parent, rite_ids):
    if len(rite_ids) == 1:
        cond(parent, rite_ids[0])
    else:
        g = el(child(parent, "conditionGroups"), "conditionGroup", type="or")
        for r in rite_ids:
            cond(g, r)


def profile(type_, name, text, key):
    p = E("profile", id=mid(key, "profile", name), name=name, hidden=False, typeId=type_[0], typeName=type_[1])
    el(el(p, "characteristics"), "characteristic", name="Text" if type_ == et.WARLORD_TRAIT else "Description",
       typeId=type_[2]).text = text
    return p


def rite_link(uid, name, rids, key, compulsory):
    """A hidden extra root choice of a unit as Troops, shown while one of the Rites is chosen."""
    e = E("entryLink", import_=True, name=name, hidden=True, id=mid("rite troops", key), type="selectionEntry",
          targetId=uid)
    any_rite(modifier(e, "hidden", "false"), rids)
    cats = child(e, "categoryLinks")
    cats.append(E("categoryLink", id=mid("rite troops", key, "unit"), name=et.UNIT[1], hidden=False,
                  targetId=et.UNIT[0], primary=False))
    cats.append(E("categoryLink", id=mid("rite troops", key, "troops"), name="Troops:", hidden=False,
                  targetId=CATS["Troops"], primary=True))
    if compulsory:
        cats.append(E("categoryLink", id=mid("rite troops", key, "compulsory"), name=MIN_TROOP_LOW[1], hidden=False,
                      targetId=MIN_TROOP_LOW[0], primary=False))
    in_maniple_only(e, "Titan Legions: Titan Maniple only")
    return e


def add_root(text_file, container, elements):
    """Add to a top-level section of the catalogue, making the section (before </catalogue>) if it has none."""
    if re.search(rf"{re.escape(text_file.nl)}  <{container}>", text_file.s):
        text_file.add(CAT_ID, container, elements)
        return
    i = text_file.s.rindex("</catalogue>")
    body = "".join(text_file.nl + et.xml(e, 2).replace("\n", text_file.nl) for e in elements)
    text_file.s = text_file.s[:i] + f"  <{container}>{body}{text_file.nl}  </{container}>{text_file.nl}" + text_file.s[i:]


def main():
    cat, lib = Text(CAT), Text(LIBRARY)
    if mid("rite of war") in cat.s:
        sys.exit(f"{CAT} already has the Titan Legions expansion")
    doc = doc_sections()
    idx = et.official_index()
    b, root = et.build()
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx)
    by_name = {u.get("name"): u for u in units}
    uid = {n: u.get("id") for n, u in by_name.items()}
    ds_by = {d["name"]: d for d in b.datasheets}

    # ---- units: categories, transports, root links (Titan Maniple only)
    roots = []
    root_of = {}
    for u in units:
        n = u.get("name")
        et.drop_unit_category(u)
        if ds_by[n]["slot"] == "Dedicated Transports":
            continue
        link = et.root_link(u, ds_by[n])
        in_maniple_only(link, "Titan Legions: Titan Maniple only")
        roots.append(link)
        root_of[n] = link
    termite = uid[TERMITE]
    et.transport_group(by_name[MOD], [(TERMITE, termite, 10, None)], "dt")
    et.transport_group(by_name[ENG], [("Triaros Armoured Conveyor", TRIAROS, 10, None), (TERMITE, termite, 10, None)],
                       "dt")
    bal_dt = et.transport_group(by_name[BAL], [("Triaros Armoured Conveyor", TRIAROS, 10, None),
                                               (TERMITE, termite, 10, None)], "dt")

    # ---- Rites of War
    rite_text = doc["Rites of War"]
    group = E("selectionEntryGroup", id=mid("rites"), name="Rites of War", hidden=False, collective=False, import_=True)
    add_constraint(group, "max", 1, mid("rites", "max"))
    rite_ids = {}
    for name, spec in RITES.items():
        rid = mid("rite", name)
        rite_ids[name] = rid
        e = el(child(group, "selectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name,
               hidden=False, id=rid)
        for part, text in rite_parts(rite_text[name]).items():
            el(el(child(e, "rules"), "rule", id=mid(rid, part), name=part, hidden=False), "description").text = text
        bc.add_cost(e, 0)
        lim = add_constraint(e, "max", 1, mid(rid, "limits"))
        g = el(child(modifier(e, lim, 0), "conditionGroups"), "conditionGroup", type="and")
        for n in spec["need"]:  # an Axiarch or a Titan
            cond(g, n, "lessThan")
        if spec.get("bans") or spec.get("bans_slots"):
            g = el(child(modifier(e, lim, 0), "conditionGroups"), "conditionGroup", type="or")
            for t in spec.get("bans", []):
                cond(g, t)
            for s in spec.get("bans_slots", []):
                cond(g, CATS[s])
        if spec.get("no_allies"):
            cond(modifier(e, lim, 0), ALLIED, field="forces", scope="roster", forces=True)
    rite_root = E("selectionEntry", type="upgrade", import_=True, name="Rite of War", hidden=False, id=mid("rite of war"))
    add_constraint(rite_root, "max", 1, mid("rite of war", "max"), scope="force", children=True)
    in_maniple_only(rite_root, "Rites of War: Titan Maniple only")
    child(rite_root, "categoryLinks").append(E("categoryLink", id=mid("rite of war", "category"), name=RITE_CATEGORY[1],
                                               hidden=False, targetId=RITE_CATEGORY[0], primary=True))
    child(rite_root, "selectionEntryGroups").append(group)
    bc.add_cost(rite_root, 0)
    all_rites = list(rite_ids.values())

    # extra Troops choices
    where = lambda key, n: [rite_ids[r] for r, s in RITES.items() if n in s.get(key, [])]
    for n in sorted({x for s in RITES.values() for x in s.get("troops", [])}):
        roots.append(rite_link(uid[n], n, where("troops", n), n, compulsory=False))
    for n in sorted({x for s in RITES.values() for x in s.get("compulsory_troops", [])}):
        roots.append(rite_link(uid[n], n, where("compulsory_troops", n), n + " compulsory", compulsory=True))
        any_rite(modifier(by_name[n], "category", LINE, "add"), where("compulsory_troops", n))
        for il in by_name[n].findall("infoLinks/infoLink"):
            if il.get("name") == "Support Squad":  # Outriders of the Legion: no Support Squad
                any_rite(modifier(il, "hidden", "true"), where("compulsory_troops", n))
    # Line for the official Peltasts and Hoplites
    official_mods = {}
    for unit_id in (HOPLITE, PELTAST):
        rids = where("line", unit_id)
        if rids:
            m = E("modifier", type="add", field="category", value=LINE)
            any_rite(m, rids)
            official_mods.setdefault(unit_id, []).append(m)
    # Subterranean Assault: the Termite for Secutarii Infantry of ten or fewer (Ordo Destructor)
    ordo = [rite_ids[r] for r, s in RITES.items() if s.get("termite")]
    tl = next(l for l in bal_dt.findall("entryLinks/entryLink") if l.get("targetId") == termite)
    tl.set("hidden", "true")
    any_rite(modifier(tl, "hidden", "false"), ordo)
    mods = tl.find("modifiers")  # hidden again past ten models: after the Rite's reveal
    first = mods[0]
    mods.remove(first)
    mods.append(first)
    official_groups = {}
    for unit_id, key in ((HOPLITE, "hoplite"), (PELTAST, "peltast")):
        g = E("selectionEntryGroup", id=mid(key, "subterranean"), name="Dedicated Transport (Subterranean Assault)",
              hidden=True, collective=False, import_=True)
        any_rite(modifier(g, "hidden", "false"), ordo)
        add_constraint(g, "max", 1, mid(key, "subterranean", "max"))
        l = el(child(g, "entryLinks"), "entryLink", import_=True, name=TERMITE, hidden=False, id=mid(key, "termite"),
               type="selectionEntry", targetId=termite)
        add_constraint(l, "max", 1, mid(key, "termite", "max"))
        et.models_over(l, unit_id, 10, key)
        official_groups[unit_id] = [g]

    # ---- the Titan Maniple: Expanded Maniple Support and the Lords of War limit under a Rite
    force_cats = []
    for slot in ("Elites", "Fast Attack", "Heavy Support"):
        c = E("categoryLink", id=mid("maniple", slot), name=f"{slot}:", hidden=False, targetId=CATS[slot], primary=False)
        cid = add_constraint(c, "max", 0, mid("maniple", slot, "max"), scope="force", children=True)
        m = modifier(c, cid, 2)
        el(m, "comment").text = "Expanded Maniple Support: with a Rite of War"
        cond(m, rite_root.get("id"))
        force_cats.append(c)
    low_mods = {}
    for _, link_id in TITANS.values():
        m = E("modifier", type="remove", field="category", value=LOW_LIMIT)
        el(m, "comment").text = "Titan Maniple with a Rite of War: Titans outside the 25% Lords of War limit"
        cond(m, rite_root.get("id"))
        low_mods[link_id] = [m]

    # ---- Advanced Reactions and Warlord Traits
    reactions = [profile(REACTION, f"Advanced Reaction: {n}", plain(lines), n)
                 for n, lines in doc["Advanced Reactions"].items()]
    traits = E("selectionEntryGroup", id=mid("warlord traits"), name="Titan Legions", hidden=True, collective=False,
               import_=True)
    m = modifier(traits, "hidden", "false")
    cond(m, DIVISIO, "equalTo")
    add_constraint(traits, "max", 1, mid("warlord traits", "max"))
    for n, lines in doc["Warlord Traits"].items():
        t = el(child(traits, "selectionEntries"), "selectionEntry", type="upgrade", import_=True, name=n, hidden=False,
               id=mid("trait", n))
        el(t, "profiles").append(profile(et.WARLORD_TRAIT, n, plain(lines), n))
        bc.add_cost(t, 0)

    # ---- write
    for unit_id, ms in official_mods.items():
        cat.add(unit_id, "modifiers", ms)
    for unit_id, gs in official_groups.items():
        cat.add(unit_id, "selectionEntryGroups", gs)
    for link_id, ms in low_mods.items():
        cat.add(link_id, "modifiers", ms)
    cat.add(MANIPLE, "categoryLinks", force_cats)
    cat.add(DIVISIO_LINK, "profiles", reactions)
    add_root(cat, "entryLinks", roots)
    add_root(cat, "sharedSelectionEntries", units + keep_entries)
    if keep_groups:
        add_root(cat, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        add_root(cat, "sharedRules", keep_rules)
    add_root(cat, "selectionEntries", [rite_root])
    lib.add(TRAITS_GROUP, "selectionEntryGroups", [traits])
    cat.bump("catalogue")
    lib.bump("catalogue")
    cat.save()
    lib.save()
    print(f"{CAT}: {len(units)} units, {len(keep_entries)} entries, {len(RITES)} Rites of War, "
          f"{len(reactions)} Advanced Reactions; {LIBRARY}: {len(doc['Warlord Traits'])} Warlord Traits")


if __name__ == "__main__":
    main()
