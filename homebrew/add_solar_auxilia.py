#!/usr/bin/env python3
"""Add the Liber Imperatus Solar Auxilia expansion to the official Solar Auxilia catalogue.

usage: python3 homebrew/add_solar_auxilia.py

The doc (homebrew/source/solar-auxilia.md, from the Claude Doc "Solar Auxilia Horus Heresy 2.0 - Homebrew Conversion")
is read by build_catalogue.py's Builder; its units move into 2022 - LI - Solar Auxilia.cat as text, linked to the
official entries wherever the catalogue, its libraries or the game system already have them (see
expansion_tools.py). On top of the units this writes:

- the new Tercios (Breacher, Infantry Support, Carnodon, Light Armoured, Verticalis Drop) as the official Tercios are
  built, one choice holding up to three Sections, and the Sabre Battery in the official Artillery Tercio;
- the Sections' Dedicated Transports, by size, hidden in a Zone Mortalis force as the official Sections' are;
- the eight new Cohort Doctrines in the official Cohort Doctrines pick, the slots they open (Possessed Auxilia as
  Troops and so on) and the doc's additions to Iron and Siege Pattern Cohorts;
- the Armoured Marshal upgrades on the vehicles that may take them, and the new Warlord Traits;
- the doc's extra options on official units (Companion and Tactical Command Sections, the Veletaris Sections,
  Arvus Transport, Armoured Command Section, Leman Russ, Macharius, Malcador, Valdor, Crassus).

It refuses to run on a catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, add_cost, add_rule, child, el, norm  # noqa: E402
from expansion_tools import E, Text, any_entry, deep, link_el, link_named, mid, model_entry  # noqa: E402

CAT = "2022 - LI - Solar Auxilia.cat"
DOC = "homebrew/source/solar-auxilia.md"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]
et.configure(CAT, LIBS, DOC, "Solar Auxilia", "solar auxilia expansion")
C = et.NS["cat"]

# What the Builder cannot place, and this script does instead
ALLOWED = [r"rule 'Cohort Doctrines'", r"Possessed Auxilia: exchange of 'Lasrifle'",  # the Greater Possessed has none
           r"Deathstrike", r"Manticore"]

COHORT_DOCTRINES = "9da6-635b-fa1d-2c2b"
WARLORD = "0176-56a3-d590-b103"
MECH_WARLORD_TRAITS = "1ebb-8e01-7d58-9d99"
TRAITOR, LOYALIST = "f9c0-0c5a-3e24-58c7", "d0b6-712f-0b12-a308"
MORTALIS = et.MORTALIS
AUROX, DRACOSAN, ARVUS, TERMITE = "071b-79e5-7b5b-c9cd", "496b-a01b-3726-0a44", "5041-9403-02b7-af14", "b4b5-9c0a-9e86-3d38"
CARNODON_STRIKE = "2918-e98d-0ab1-811b"
ARTILLERY_BATTERIES = "Artillery Batteries"  # the official Artillery Tercio's pick of batteries
SUB_TYPES = {"Light": ("bff2-ae16-74a8-8712", "Light Sub-type"), "Automata": ("d8ab-8e21-e193-63ba", "Automata Unit Type"),
             "Hover": ("3a7a-8bb7-b0d3-e2e7", "Hover Sub-type"), "Reinforced": ("9b0d-738c-10e4-4ec1", "Reinforced Sub-type")}

# "### Auxilia Breacher Tercio": the Tercio, its slot, whether it is Compulsory Troops, and its units
# [(Section, least, most)], the last group being "1-3 ... in any combination"
TERCIOS = [
    ("Breacher Tercio", "Troops", True,
     [("Breacher Command Section", 0, 1)], [("Breacher Section", 1, 3)], []),
    ("Infantry Support Tercio", "Troops", False,
     [("Ancillary Command Section", 0, 1)], [("Heavy Weapons Section", 0, 3), ("Pioneer Section", 0, 3),
                                             ("Special Weapons Section", 0, 3)], []),
    ("Carnodon Tercio", "Fast Attack", False,
     [("Carnodon Command Section", 0, 1)], [("Carnodon Strike Squadron", 1, 3)], []),
    ("Light Armoured Tercio", "Fast Attack", False,
     [("Salamander Command Vehicle", 0, 1)], [("Salamander Scout Squadron", 0, 3), ("Pegasus Assault Squadron", 0, 3)], []),
    ("Verticalis Drop Tercio", "Fast Attack", False,
     [("Verticalis Drop Command Section", 0, 1)], [("Verticalis Drop Section", 1, 3)],
     [("Verticalis Drop Sentinel Squadron", 0, 1)]),
]
SECTIONS = {n for t in TERCIOS for part in t[3:] for n, _, _ in part} | {"Sabre Battery"}
TRANSPORTS = {"Chimera Transport"}  # Dedicated Transports only
INFANTRY_SECTIONS = ["Breacher Command Section", "Breacher Section", "Ancillary Command Section", "Heavy Weapons Section",
                     "Pioneer Section", "Special Weapons Section"]


def short(name):
    """'Solar Auxilia Breacher Section' is 'Breacher Section', as the official catalogue names its units."""
    return re.sub(r"^Solar Auxilia ", "", name)


def build():
    text = open(DOC, encoding="utf-8").read()
    first = next(l for l in text.splitlines() if l.startswith("# "))[2:].strip()
    b = bc.Builder(first, "Solar Auxilia", text)
    root = b.build()
    bad = [p for p in b.problems if not any(re.search(a, p) for a in ALLOWED)]
    if bad:
        sys.exit("the doc does not build cleanly:\n  " + "\n  ".join(bad))
    return b, root


def split_profiles(b, root, weapon, names, key):
    """The doc's armoury gives a Deathstrike's warheads and a Manticore's missiles as profiles of one weapon: each
    becomes an entry of its own, by its profile's name after the dash."""
    w = root.find(f"sharedSelectionEntries/selectionEntry[@id='{b.weapons[norm(weapon)]}']")
    out = {}
    for p in w.findall("profiles/profile"):
        name = p.get("name").split(" – ")[-1].split(" - ")[-1]
        if names and name not in names:
            continue
        e = el(root.find("sharedSelectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name,
               hidden=False, id=mid(key, name))
        child(e, "profiles").append(deep(p))
        for il in w.findall("infoLinks/infoLink"):
            if il.get("name").split(" (")[0] in p.find("characteristics").findall("characteristic")[3].text:
                child(e, "infoLinks").append(deep(il))
        for x in e.iter():
            if x.get("id") and x is not e:
                x.set("id", mid(e.get("id"), x.get("id")))
        add_cost(e, 0)
        out[name] = e.get("id")
    return out


def special_cases(b, root, entries):
    unit = lambda n: entries[b.units[n]]

    # Ireton MaSade: the Cohort Doctrines pick, and his own Warlord Trait
    iu = unit("Lord Marshal Ireton MaSade")
    for il in list(iu.iter("infoLink")):
        if il.get("name") == "Cohort Doctrines":
            for p in iu.iter():
                if il in list(p):
                    p.remove(il)
    me = model_entry(iu, "Ireton MaSade")
    el(child(me, "entryLinks"), "entryLink", import_=True, name="Cohort Doctrines", hidden=False,
       id=mid(me.get("id"), "doctrines"), type="selectionEntryGroup", targetId=COHORT_DOCTRINES)
    et.warlord_trait(me, "Master of the Battlefield", (
        "As Warlord, Ireton MaSade automatically has this trait and no other.\n"
        "• After both sides have deployed (including Infiltrators and Scouts) and any roll to Seize the Initiative, but "
        "before the game begins, the Controlling Player may redeploy up to three of their units within the mission's "
        "limits. They may go into Reserves but not into a Deep Strike, Subterranean or Flanking Assault. Each Tercio unit "
        "counts separately and may ignore the normal Tercio deployment rules when redeployed.\n"
        "• Before deployment, the Controlling Player picks one phase. While MaSade lives, the army gains one extra "
        "Reaction in that phase of the opponent's turn."), me.get("id"))

    # Deathstrike: "must take one warhead for its Deathstrike Missile"
    du = unit("Solar Auxilia Deathstrike Missile Platform")
    warheads = split_profiles(b, root, "Deathstrike", None, "deathstrike")
    for l in list(du.iter("entryLink")):
        target = entries.get(l.get("targetId"))
        name = target.get("name") if target is not None else ""
        if name in warheads:
            l.set("targetId", warheads[name])
        elif name == "Centreline Mounted Deathstrike Missile":
            for p in du.iter():
                if l in list(p):
                    p.remove(l)
    for g in du.iter("selectionEntryGroup"):
        if any(l.get("targetId") in warheads.values() for l in g.iter("entryLink")):
            g.set("name", "Deathstrike Missile Warhead")
            if g.find("constraints/constraint[@type='min']") is None:
                add_constraint(g, "min", 1, mid(g.get("id"), "min"))

    # Manticore: four missiles, any of them swapped for another kind
    mu = unit("Solar Auxilia Manticore Missile Tank Battery")
    missiles = split_profiles(b, root, "Manticore", None, "manticore")
    me = model_entry(mu, "Auxilia Manticore Missile Tank")
    for l in list(me.iter("entryLink")):
        target = entries.get(l.get("targetId"))
        if target is not None and target.get("name", "").startswith("Turret Mounted Manticore Missile Launcher"):
            for p in me.iter():
                if l in list(p):
                    p.remove(l)
    g = el(child(me, "selectionEntryGroups"), "selectionEntryGroup", name="Manticore Missiles", hidden=False,
           id=mid(me.get("id"), "missiles"), defaultSelectionEntryId=mid(me.get("id"), "missiles", "Manticore Missile"))
    add_constraint(g, "min", 4, mid(me.get("id"), "missiles min"))
    add_constraint(g, "max", 4, mid(me.get("id"), "missiles max"))
    for name, eid in missiles.items():
        l = el(child(g, "entryLinks"), "entryLink", import_=True, name=name, hidden=False,
               id=mid(me.get("id"), "missiles", name), type="selectionEntry", targetId=eid)
        add_constraint(l, "max", 4, mid(l.get("id"), "max"))
    add_rule(me, "Manticore Missile Launcher", "A Manticore Missile Launcher carries four missiles and may fire only "
             "one of them in each Shooting Attack.", me.get("id"))


def tercio(name, parts, key):
    """A Tercio: one unit holding up to three Sections, the last part being 'in any combination'."""
    uid = mid("tercio", name)
    u = E("selectionEntry", id=uid, name=name, hidden=False, collective=False, import_=True, type="unit")
    outer = el(el(u, "selectionEntryGroups"), "selectionEntryGroup", name="Units (no more than three)", hidden=False,
               id=mid(uid, "units"))
    add_constraint(outer, "min", 1, mid(uid, "units min"))
    add_constraint(outer, "max", 3, mid(uid, "units max"))
    for i, part in enumerate(parts):
        if not part:
            continue
        holder = outer
        if len(part) > 1 or part[0][1]:  # "1-3 Breacher Sections", "1-3 Heavy Weapons, Pioneer or Special Weapons"
            holder = el(child(outer, "selectionEntryGroups"), "selectionEntryGroup", name="Sections", hidden=False,
                        id=mid(uid, "part", str(i)))
            add_constraint(holder, "min", max(p[1] for p in part) if len(part) == 1 else 1, mid(uid, "part min", str(i)))
            add_constraint(holder, "max", 3, mid(uid, "part max", str(i)))
        for sname, lo, hi, target in part:
            l = el(child(holder, "entryLinks"), "entryLink", import_=True, name=sname, hidden=False,
                   id=mid(uid, "member", sname), type="selectionEntry", targetId=target)
            add_constraint(l, "max", hi, mid(uid, "member max", sname))
    add_cost(u, 0)
    return u


def sections_transports(b, entries):
    """'Dedicated Transport (infantry sections in this section unless noted)': no more than ten models, an Aurox or a
    Termite Assault Drill; twelve, a Chimera; any size, a Dracosan or a Hades Breaching Drill. The Verticalis Drop
    Command Section at any size, and a Drop Section of ten or fewer: an Arvus Transport or a Kelaino."""
    chimera = b.units["Solar Auxilia Chimera Transport"]
    hades = b.units["Solar Auxilia Hades Breaching Drill"]
    kelaino = b.units["Solar Auxilia Kelaino Squadron"]
    for n in INFANTRY_SECTIONS:
        g = et.transport_group(entries[b.units["Solar Auxilia " + n]],
                               [("Aurox Transport", AUROX, 10, None), ("Termite Assault Drill", TERMITE, 10, None),
                                ("Chimera Transport", chimera, 12, None), ("Dracosan Armoured Transport", DRACOSAN, None, None),
                                ("Hades Breaching Drill", hades, None, None)], "dt", name="Dedicated Transports")
        hide_in_mortalis(g)
    for n, most in (("Verticalis Drop Command Section", None), ("Verticalis Drop Section", 10)):
        g = et.transport_group(entries[b.units["Solar Auxilia " + n]],
                               [("Arvus Transport", ARVUS, most, None), ("Kelaino Squadron", kelaino, most, None)], "dt",
                               name="Dedicated Transports")
        hide_in_mortalis(g)


def hide_in_mortalis(e):
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
    el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force", childId=MORTALIS,
       shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)


# ---- naming what an option gives


class Items:
    """Option items by name, as entries: the official ones where they exist, the Builder's otherwise (which then
    travel with the expansion)."""

    MOUNTS = r"^(?:Turret|Centreline|Hull \(Front\)|Pintle|Sponson|Co-axial) Mounted "

    def __init__(self, b):
        self.b = b
        self.extra = set()

    def __call__(self, name):
        b = self.b
        side = re.match(r"One Side \(Left\) and One Side \(Right\) Mounted (.+)$", name)
        if side:  # "One Side (Left) and One Side (Right) Mounted Multi-Melta": two of them
            wid = b.find_weapon(side.group(1))[0]
            return self.keep(b.wrapper_entry(name, wid, 2, None))
        n = re.sub(self.MOUNTS, "", name)
        n = re.sub(r"^Two (\w+ )?Mounted ", "Two ", n)
        n = re.sub(r"\bone Co-axial ", "", n)
        official = any_entry(n, required=False)
        if official:
            return official
        if " and " in n and "(with" not in n:
            return self.keep(b.wrapper_entry(n, None, 1, None))
        return self.keep(b.option_target(n, mid("item", n))[0])

    def keep(self, eid):
        self.extra.add(eid)
        return eid

    def final(self, eid):
        """After transplant(): the id the catalogue uses."""
        return et.cfg.remap.get(eid, eid)


# ---- Cohort Doctrines


def doctrine_text(lines):
    """'Effects' and 'Limitations' lists, as the official doctrines write them."""
    out, cur = [], None
    for l in lines:
        s = l.strip()
        if s in ("Effects", "Limitations"):
            out.append(("head", s))
        elif s.startswith("- "):
            out.append(("item", "• " + bc.strip_md(s[2:])))
    text = ""
    for kind, t in out:
        text += ("\n\n" if kind == "head" and text else "\n" if text else "") + t
    return text


def doctrines(b, cat, roots_by_unit):
    """The new Cohort Doctrines in the official pick, with the slots they open; the doc's additions to Iron and Siege
    Pattern Cohorts."""
    sec = next(s for s in b.sections if s["title"] == "Cohort Doctrines")
    ids = {}
    entries = []
    for sub in sec["subs"]:
        m = re.match(r"Cohort Doctrine: (.+)", sub["title"])
        if not m:
            continue
        name = m.group(1)
        eid = mid("doctrine", name)
        ids[name] = eid
        e = E("selectionEntry", id=eid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
        add_rule(e, name, doctrine_text(sub["lines"]), eid)
        add_cost(e, 0)
        cond = None
        if name == "Apostle Pattern Cohorts":  # "The Detachment must have the Traitor Allegiance"
            cond = ("equalTo", 0, TRAITOR, "force")
        elif name == "Legion-Sworn Cohorts":  # "Only an Allied Detachment may take this Cohort Doctrine"
            cond = ("notInstanceOf", 0, bc.ALLIED_DETACHMENT, "ancestor")
        elif name == "Scourge Pattern Cohorts":  # "Only a Primary Detachment may take this Doctrine"
            cond = ("instanceOf", 0, bc.ALLIED_DETACHMENT, "ancestor")
        if cond:
            mod = el(el(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
            el(el(mod, "conditions"), "condition", type=cond[0], value=cond[1], field="selections", scope=cond[3],
               childId=cond[2], shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        entries.append(e)
    cat.add(COHORT_DOCTRINES, "selectionEntries", entries)

    # "Iron Pattern Cohorts" and "Siege Pattern Cohorts" gain the doc's effects
    table = next(l for l in sec["subs"] if l["title"] == "Modifications to Existing Cohort Doctrines")
    added = {r[0]: r[1] for h, rows in bc.section_tables({"lines": table["lines"], "subs": []}) for r in rows}
    root = ET.parse(CAT).getroot()
    for name, text in added.items():
        entry = next(x for x in root.iter(C + "selectionEntry") if x.get("name", "").startswith(name.replace("Cohorts", "Cohort")))
        rule = entry.find(f"{C}rules/{C}rule")
        start, end, _, _ = cat.block(rule.get("id"))
        body = cat.s[start:end]
        j = body.index("</description>")
        body = body[:j] + f"{cat.nl}{cat.nl}Liber Imperatus addition{cat.nl}• " + text.replace("&", "&amp;") + body[j:]
        cat.s = cat.s[:start] + body + cat.s[end:]

    # the slots the Doctrines open: (Doctrine, unit id, unit name, slot)
    return ids


def doctrine_links(ids, opens):
    """'Possessed Auxilia may be taken as Troops': a root entry in that slot, shown while the Detachment uses it."""
    out = []
    for doctrine, uid, name, slot in opens:
        unit = E("selectionEntry", id=uid, name=name)
        e = et.root_link(unit, None, slot=slot, name=name, key="doctrine " + doctrine)
        e.set("hidden", "true")
        mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
        el(el(mod, "conditions"), "condition", type="equalTo", value=1, field="selections", scope="force",
           childId=ids[doctrine], shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        out.append(e)
    return out


# ---- Armoured Marshals


MARSHALS = {
    "Armoured Fist Marshal": ("Commanders famed for the precision with which they wielded their vehicles' firepower.",
                              "• The model may make the Concentrated Fire Advanced Reaction.\n"
                              "• It may take a Nuncio-Vox for +10 points and a Cognis-Signum for +15 points."),
    "Dictatii Marshal": ("Only one per army.",
                         "• The model gains Void Shields (2), +1 BS and +2 Hull Points.\n"
                         "• Friendly Solar Auxilia models within 12\" automatically pass Morale and Pinning tests.\n"
                         "• The model has a Flare Shield at no cost, and may not buy one from any other source."),
    "Ordnance Corps Marshal": ("Masters of long-range firepower who could call down a creeping barrage from every gun in "
                               "range.", "• The model gains Blitz Barrage and has a Nuncio-Vox."),
}
MARSHAL_NOTE = ("An Armoured Marshal is an upgrade for a Vehicle with the Imperial Army (Solar Auxilia) Faction and "
                "Sub-faction. No model may take more than one, but several models may each take one, within each "
                "upgrade's own limits. An upgrade uses no Force Organisation slot. A Marshal bought for a Lord of War "
                "counts towards that slot's cost for the 25% Lords of War and Primarch limit.")


def marshal_entries(items):
    gst_rules = bc.load_gst_rules()
    out = {}
    for name, (flavour, text) in MARSHALS.items():
        eid = mid("marshal", name)
        e = E("selectionEntry", id=eid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
        add_rule(e, name, MARSHAL_NOTE + "\n\n" + text, eid)
        if name == "Armoured Fist Marshal":
            el(child(e, "infoLinks"), "infoLink", name="Concentrated Fire", id=mid(eid, "reaction"), hidden=False,
               targetId=gst_rules["concentrated fire"][0], type="rule")
            g = el(el(e, "selectionEntryGroups"), "selectionEntryGroup", name="May take", hidden=False, id=mid(eid, "take"))
            for n, p in (("Nuncio-Vox", 10), ("Cognis-Signum", 15)):
                child(g, "entryLinks").append(link_el(n, items(n), mid(eid, "take"), mx=1, pts=p))
        elif name == "Dictatii Marshal":
            add_constraint(e, "max", 1, mid(eid, "army"), scope="roster", children=True)
            child(e, "entryLinks").append(link_el("Flare Shield", items("Flare Shield"), eid, mn=1, mx=1))
            el(child(e, "infoLinks"), "infoLink", name="Void Shields (X)", id=mid(eid, "void"), hidden=False,
               targetId=gst_rules["void shields"][0], type="rule").append(
                E("modifiers"))
            vs = e.find("infoLinks/infoLink[@name='Void Shields (X)']")
            el(vs.find("modifiers"), "modifier", type="set", field="name", value="Void Shields (2)")
        else:
            el(child(e, "infoLinks"), "infoLink", name="Blitz Barrage", id=mid(eid, "barrage"), hidden=False,
               targetId=gst_rules["blitz barrage"][0], type="rule")
            child(e, "entryLinks").append(link_el("Nuncio-Vox", items("Nuncio-Vox"), eid, mn=1, mx=1))
        add_cost(e, 0)
        out[name] = e
    return out


def marshal_group(model_id, offers, unit_id, single=False):
    """'Armoured Marshal': one of the upgrades this vehicle may take, at its cost: [(name, entry id, cost)]."""
    g = E("selectionEntryGroup", id=mid(model_id, "marshal"), name="Armoured Marshal", hidden=False, collective=False,
          import_=True)
    add_constraint(g, "max", 1, mid(model_id, "marshal max"))
    for name, eid, pts in offers:
        l = link_el(name, eid, mid(model_id, "marshal"), mx=1, pts=pts)
        if single:  # "A single-model Macharius ... Squadron"
            et.models_over(l, unit_id, 1)
        child(g, "entryLinks").append(l)
    return g


def vehicle_profile_mods(model_id, dictatii, profile_id):
    """The Dictatii Marshal's +1 BS and +2 Hull Points, shown on the vehicle once taken."""
    mods = []
    for field, value in (("51fb-b7d9-aa59-863d", 1), ("a76c-83b1-602f-9e62", 2)):
        mod = E("modifier", type="increment", field=field, value=value)
        el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=model_id,
           childId=dictatii, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
        mods.append(mod)
    return mods


# ---- Warlord Traits


def warlord_traits(b, steel_fury):
    """'A Solar Auxilia Warlord may take one of these instead of a Core Rulebook Warlord Trait'."""
    sec = next(s for s in b.sections if s["title"] == "Warlord Traits")
    rows = [r for h, rs in bc.section_tables(sec) for r in rs]
    gid = mid("warlord traits")
    g = E("selectionEntryGroup", id=gid, name="Warlord Traits (Solar Auxilia)", hidden=True, collective=False, import_=True)
    cmax = add_constraint(g, "max", 1, mid(gid, "max"))
    mod = el(el(g, "modifiers"), "modifier", type="set", field="hidden", value="false")
    el(el(mod, "conditions"), "condition", type="greaterThan", value=0, field="selections", scope="parent",
       childId=WARLORD, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    mod = el(g.find("modifiers"), "modifier", type="set", field=cmax, value=0)  # or one of the others, not both
    el(el(mod, "conditions"), "condition", type="greaterThan", value=0, field="selections", scope="parent",
       childId=MECH_WARLORD_TRAITS, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    for name, text in rows:
        if "Ireton MaSade only" in name:
            continue  # on his datasheet
        shown = re.sub(r"\s*\(.*\)$", "", name)
        e = el(el(g, "selectionEntries") if g.find("selectionEntries") is None else g.find("selectionEntries"),
               "selectionEntry", type="upgrade", import_=True, name=shown, hidden=False, id=mid(gid, shown))
        et.warlord_trait(e, shown, text, e.get("id"))
        add_constraint(e, "max", 1, mid(e.get("id"), "max"))
        add_cost(e, 0)
        if "Steel Fury" in name:  # "(Steel Fury Pattern Cohorts only)"
            e.set("hidden", "true")
            m = el(el(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
            el(el(m, "conditions"), "condition", type="equalTo", value=1, field="selections", scope="force",
               childId=steel_fury, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    return g


# ---- the doc's extra options on official units


def official_root():
    return ET.parse(CAT).getroot()


def named(root, name, tag="selectionEntry", within=None):
    return next(x for x in (within if within is not None else root).iter(C + tag) if x.get("name") == name)


def copy_official(e, key):
    """An official element as a new one: out of the catalogue namespace, with fresh ids (and the modifiers that
    name its constraints following them)."""
    c = deep(e)
    ids = {}
    for x in c.iter():
        x.tag = x.tag.split("}")[-1]
        for a in ("publicationId", "page"):
            x.attrib.pop(a, None)
        if x.get("id"):
            ids[x.get("id")] = mid(key, x.get("id"))
            x.set("id", ids[x.get("id")])
    for x in c.iter():
        if x.get("field") in ids:
            x.set("field", ids[x.get("field")])
    return c


class Ops:
    """Edits to the official file, made once the expansion's ids are final."""

    def __init__(self):
        self.ops = []

    def add(self, eid, container, elements):
        self.ops.append(("add", eid, container, elements))

    def remove(self, eid):
        self.ops.append(("remove", eid))

    def run(self, cat, items):
        for op in self.ops:
            if op[0] == "add":
                for e in op[3]:
                    for x in e.iter():
                        for a in ("targetId", "childId"):
                            if x.get(a):
                                x.set(a, items.final(x.get(a)))
                cat.add(op[1], op[2], op[3])
            else:
                cat.remove(op[1])


def swap_group(name, key, default_name, default_target, offers, items):
    """A pick of exactly one, its default the weapon the model starts with: [(item, cost)]."""
    g = E("selectionEntryGroup", id=mid(key, name), name=name, hidden=False, collective=False, import_=True,
          defaultSelectionEntryId=mid(key, name, default_name))
    add_constraint(g, "min", 1, mid(key, name, "min"))
    add_constraint(g, "max", 1, mid(key, name, "max"))
    links = el(g, "entryLinks")
    links.append(link_el(default_name, default_target, mid(key, name), mx=1))
    for n, p in offers:
        if norm(n) != norm(default_name):
            links.append(link_el(n, items(n), mid(key, name), mx=1, pts=p))
    return g


def take_group(name, key, offers, items, most=None):
    g = E("selectionEntryGroup", id=mid(key, name), name=name, hidden=False, collective=False, import_=True)
    if most:
        add_constraint(g, "max", most, mid(key, name, "max"))
    for n, p in offers:
        child(g, "entryLinks").append(link_el(n, items(n), mid(key, name), mx=1, pts=p))
    return g


def unit_wide(name, text, parts, items):
    """A whole-unit exchange ('The entire unit may exchange its Void Armour for: Heavy Void Armour'), kept as one
    upgrade with its rule and the wargear it gives."""
    eid = mid("unit wide", name)
    e = E("selectionEntry", id=eid, name=name, hidden=False, collective=False, import_=True, type="upgrade")
    add_rule(e, name, text, eid)
    for p in parts:
        child(e, "entryLinks").append(link_el(p, items(p), eid, mn=1, mx=1))
    add_cost(e, 0)
    return e


def existing_units(items, shared):
    root = official_root()
    ops = Ops()
    lasrifle = [("Charnabal Weapon and Hot-Shot Laspistol", 10), ("Hot-Shot Lasgun", 5),
                ("Power Weapon and Hot-Shot Laspistol", 10), ("Storm Axe", 10)]
    heavy_void = unit_wide("Heavy Void Armour (entire unit)", "Every model in the unit exchanges its Void Armour for "
                           "Heavy Void Armour.", ["Heavy Void Armour"], items)
    shared.append(heavy_void)

    # Companion and Tactical Command Sections: "Any model may exchange its Lasrifle for one of"; "The entire unit
    # may exchange its Void Armour for: Heavy Void Armour"
    for sname in ("Tactical Command Section", "Companion Sections"):
        sec = named(root, sname)
        for g in [x for x in sec.iter(C + "selectionEntryGroup") if x.get("name") == "May exchange Lasrifle for:"]:
            ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=p) for n, p in lasrifle])
        ops.add(sec.get("id"), "entryLinks", [link_el(heavy_void.get("name"), heavy_void.get("id"), sec.get("id"), mx=1, pts=30)])

    # Veletaris Sections: each Veletarii loadout is its own entry, so the new loadouts are new entries beside them
    def loadouts(sname, base_name, weapon, offers):
        sec = named(root, sname)
        base = named(root, base_name, within=sec)
        group = next(g for g in sec.iter(C + "selectionEntryGroup") if any(x is base for x in g.iter(C + "selectionEntry")))
        base_cost = float(base.find(f"{C}costs/{C}cost").get("value"))
        new = []
        for n, p in offers:
            c = copy_official(base, mid(sname, n))
            c.set("name", f"Veletarii w/ {n}")
            c.find("costs/cost").set("value", str(base_cost + p))
            for l in c.iter("entryLink"):
                if l.get("name") == weapon:
                    l.set("name", re.sub(r"\s*\(with .*\)$", "", n))
                    l.set("targetId", items(n))
            new.append(c)
        ops.add(group.get("id"), "selectionEntries", new)

    def prime_weapons(sname, prime, offers):
        sec = named(root, sname)
        p = named(root, prime, within=sec)
        g = next(x for x in p.iter(C + "selectionEntryGroup") if x.get("name") == "Weapons")
        ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=c) for n, c in offers])

    command = [("Hot-Shot Lasgun", 2), ("Power Weapon and Blast Pistol", 5), ("Power Weapon and Hot-Shot Laspistol", 5),
               ("Storm Axe", 5)]
    loadouts("Veletaris Command Section", "Veletarii w/ Volkite Charger", "Volkite Charger", command)
    prime_weapons("Veletaris Command Section", "Veletarii First Prime", command)
    loadouts("Veletaris Storm Section", "Veletarii w/ Volkite Charger", "Volkite Charger", command[:3])
    prime_weapons("Veletaris Storm Section", "Veletarii Prime", [("Hot-Shot Lasgun", 2)])
    vanguard = [("Hot-Shot Volley Gun (with Suspensor Web)", 10), ("Multi-Laser (with Suspensor Web)", 5),
                ("Volkite Caliver", 5)]
    loadouts("Veletaris Vanguard Section", "Veletarii w/ Rotor Cannon", "Rotor Cannon", vanguard)
    prime_weapons("Veletaris Vanguard Section", "Veletarii Prime", [("Heavy Flamer", 0)] + vanguard)

    # Arvus Transport: its hull weapon, a twin-linked weapon, a Flare Shield
    arvus = next(x for x in root.iter(C + "selectionEntry") if x.get("id") == ARVUS)
    stubber = named(root, "Hull (Front) Mounted Heavy Stubber", "entryLink", arvus)
    ops.remove(stubber.get("id"))
    twin = unit_wide("Twin-Linked (one ranged weapon)", "One of the Arvus Transport's ranged weapons gains Twin-linked.",
                     [], items)
    shared.append(twin)
    ops.add(ARVUS, "selectionEntryGroups", [
        swap_group("Hull (Front) Mounted weapon", ARVUS, "Hull (Front) Mounted Heavy Stubber", stubber.get("targetId"),
                   [("Hull (Front) Mounted Autocannon", 10), ("Hull (Front) Mounted Lascannon", 15),
                    ("Hull (Front) Mounted Multi-Laser", 10)], items)])
    ops.add(ARVUS, "entryLinks", [link_el(twin.get("name"), twin.get("id"), ARVUS, mx=1, pts=10),
                                  link_el("Flare Shield", items("Flare Shield"), ARVUS, mx=1, pts=20)])

    # Armoured Command Section: the Leman Russ Command Tank's Turret Mounted Battle Cannon
    acs = named(root, "Armoured Command Section")
    tank = named(root, "Leman Russ Command Tank", within=acs)
    cannon = named(root, "Battle Cannon", "entryLink", tank)
    ops.remove(cannon.get("id"))
    ops.add(tank.get("id"), "selectionEntryGroups", [swap_group("Turret Mounted weapon", tank.get("id"), "Battle Cannon",
            cannon.get("targetId"), [(n, 0) for n in (
                "Turret Mounted Conflagration Projector", "Turret Mounted Demolisher Cannon",
                "Turret Mounted Eradicator Nova Cannon", "Turret Mounted Executioner Plasma Cannon",
                "Turret Mounted Exterminator Autocannon", "Turret Mounted Gravis Heavy Lascannon",
                "Turret Mounted Punisher Rotary Cannon", "Turret Mounted Vanquisher Battle Cannon and one Co-axial Autocannon",
                "Turret Mounted Volkite Macro-Saker")], items)])

    # Leman Russ Squadrons: whole-squadron turret swaps, priced per tank
    for uname, offers in (("Leman Russ Assault Squadron", [("Turret Mounted Punisher Rotary Cannon", 15)]),
                          ("Leman Russ Strike Squadron", [("Turret Mounted Conflagration Projector", 20),
                                                          ("Turret Mounted Eradicator Nova Cannon", 0)])):
        u = named(root, uname)
        g = next(x for x in u.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("1) All models may exchange"))
        ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=p, per_model_of=u.get("id"))
                                            for n, p in offers])

    # Macharius: its hull weapon, both sponsons, a Dozer Blade or Flare Shield
    mu = named(root, "Macharius Heavy Tank Squadron")
    tank = named(root, "Macharius Heavy Tank", within=mu)
    hull = take_group("Hull (Front) Mounted weapon (replaces its Twin-Linked Heavy Stubber)", tank.get("id"), [
        ("Hull (Front) Mounted Gravis Melta Cannon", 25), ("Hull (Front) Mounted Twin-Linked Autocannon", 10),
        ("Hull (Front) Mounted Twin-Linked Heavy Bolter", 5), ("Hull (Front) Mounted Twin-Linked Heavy Flamer", 0),
        ("Hull (Front) Mounted Twin-Linked Lascannon", 20), ("Hull (Front) Mounted Twin-Linked Multi-Laser", 5),
        ("Hull (Front) Mounted Twin-Linked Plasma Cannon", 15)], items, most=1)
    sponsons = take_group("Sponson weapons (replace both Heavy Stubbers)", tank.get("id"), [
        ("Two Sponson Mounted Autocannons", 10), ("Two Sponson Mounted Heavy Bolters", 5),
        ("Two Sponson Mounted Heavy Flamers", 0), ("Two Sponson Mounted Lascannons", 25),
        ("Two Sponson Mounted Multi-Lasers", 5), ("Two Sponson Mounted Multi-Meltas", 20),
        ("Two Sponson Mounted Plasma Cannons", 15)], items, most=1)
    extras = take_group("May take any of", tank.get("id"), [("Dozer Blade", 5), ("Flare Shield", 25)], items)
    add_rule(extras, "Flare Shield", "If one Macharius takes a Flare Shield, all models in the unit must take it.",
             extras.get("id"))
    ops.add(tank.get("id"), "selectionEntryGroups", [hull, sponsons, extras])
    for l in [x for x in tank.findall(f"{C}entryLinks/{C}entryLink") if x.get("name") == "Heavy Stubber"]:
        mods = []
        for c in l.findall(f"{C}constraints/{C}constraint"):
            mod = E("modifier", type="set", field=c.get("id"), value=0)
            cg = el(el(mod, "conditionGroups"), "conditionGroup", type="or")
            for s in sponsons.findall("entryLinks/entryLink"):
                el(child(cg, "conditions"), "condition", type="atLeast", value=1, field="selections",
                   scope=tank.get("id"), childId=s.get("targetId"), shared=True, includeChildSelections=True,
                   includeChildForces=False, percentValue=False)
            mods.append(mod)
        ops.add(l.get("id"), "modifiers", mods)

    # Malcador: Side Mounted Multi-Meltas or Plasma Cannons; a Siege Retrofit
    mal = named(root, "Malcador Heavy Tank Squadron")
    tank = named(root, "Malcador Heavy Tank", within=mal)
    g = next(x for x in tank.iter(C + "selectionEntryGroup") if x.get("name", "").startswith("3) May exchange its Hull (Left)"))
    ops.add(g.get("id"), "entryLinks", [link_el(n, items(n), g.get("id"), mx=1, pts=p) for n, p in (
        ("One Side (Left) and One Side (Right) Mounted Multi-Melta", 20),
        ("One Side (Left) and One Side (Right) Mounted Plasma Cannon", 15))])
    ops.add(tank.get("id"), "selectionEntryGroups", [take_group("May take", tank.get("id"), [("Siege Retrofit", 75)], items)])

    # Valdor: a second tank, and its Neutron Beam Laser
    val = named(root, "Valdor Tank Destroyer Squadron")
    tank = named(root, "Valdor Tank Destroyer", within=val)
    laser = named(root, "Neutron Beam Laser", "entryLink", tank)
    ops.remove(laser.get("id"))
    ops.add(tank.get("id"), "selectionEntryGroups", [swap_group("Centreline Mounted weapon", tank.get("id"),
            "Neutron Beam Laser", laser.get("targetId"), [("Centreline Mounted Conversion Destructor", 75),
                                                          ("Centreline Mounted Graviton Annihilator", 25),
                                                          ("Centreline Mounted Volkite Curtall", 35)], items)])
    return ops, val, tank


def valdor_second_tank(cat, val, tank):
    """'The squadron may include: Up to 1 additional Valdor Tank Destroyer (+235 points)': each tank costs 235, the
    squadron the rest of its 250."""
    start, end, indent, _ = cat.block(tank.get("id"))
    body = cat.s[start:end]
    mx = next(c for c in tank.findall(f"{C}constraints/{C}constraint") if c.get("type") == "max")
    body = re.sub(rf'(<constraint [^>]*value=")1("[^>]*id="{mx.get("id")}")', r"\g<1>2\2", body)
    body = re.sub(rf'(<constraint [^>]*id="{mx.get("id")}"[^>]*value=")1(")', r"\g<1>2\2", body)
    cat.s = cat.s[:start] + body + cat.s[end:]
    cat.add(tank.get("id"), "costs", [E("cost", name="Pts", typeId=bc.PTS, value="235.0")])
    start, end, indent, _ = cat.block(val.get("id"))
    body = cat.s[start:end]
    pad = " " * (indent + 4)
    body = re.sub(rf'({re.escape(cat.nl)}{pad}<cost name="Pts" typeId="{bc.PTS}" value=")250(\.0)?(")',
                  r"\g<1>15\3", body, count=1)
    cat.s = cat.s[:start] + body + cat.s[end:]


# ---- putting it together


def marshals_on_official(cat, ops, marshals):
    """The vehicles that may take an Armoured Marshal, at the cost the doc gives."""
    root = official_root()
    fist, dictatii, ordnance = (marshals[n].get("id") for n in MARSHALS)
    eligible = [  # (unit, model or None for the unit itself, [(marshal, id, cost)], single-model only)
        ("Armoured Command Section", "Leman Russ Command Tank", [("Armoured Fist Marshal", fist, 50)], False),
        ("Malcador Heavy Tank Squadron", "Malcador Heavy Tank", [("Armoured Fist Marshal", fist, 50)], False),
        ("Macharius Heavy Tank Squadron", "Macharius Heavy Tank", [("Dictatii Marshal", dictatii, 75)], True),
        ("Armoured Battery", "Auxilia Basilisks", [("Ordnance Corps Marshal", ordnance, 50)], False),
        ("Minotaur Battery", "Minotaur", [("Ordnance Corps Marshal", ordnance, 50)], False),
        ("Praetor Armoured Assault Launcher", None, [("Ordnance Corps Marshal", ordnance, 75)], False),
    ] + [(n, None, [("Dictatii Marshal", dictatii, 100)], False)
         for n in ("Banehammer", "Baneblade", "Shadowsword", "Stormblade", "Stormhammer", "Stormlord", "Stormsword")]
    done = []
    for uname, mname, offers, single in eligible:
        u = next((x for x in root.find(C + "sharedSelectionEntries") if x.get("name") == uname
                  and x.get("type") in ("unit", "upgrade")), None)  # the Stormhammer is kept as an upgrade
        if u is None:
            continue
        holder = named(root, mname, within=u) if mname else u
        ops.add(holder.get("id"), "selectionEntryGroups", [marshal_group(holder.get("id"), offers, u.get("id"), single)])
        if any(n == "Dictatii Marshal" for n, _, _ in offers):
            for p in holder.findall(f"{C}profiles/{C}profile"):
                if p.get("typeName") == "Vehicle":
                    ops.add(p.get("id"), "modifiers", vehicle_profile_mods(holder.get("id"), dictatii, p.get("id")))
        done.append(uname)
    return done


def main():
    cat = Text(CAT)
    if 'name="Breacher Tercio"' in cat.s:
        sys.exit(f"{CAT} already has the Solar Auxilia expansion")
    idx = et.official_index()
    b, root = build()
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    unit = lambda n: entries[b.units[n]]
    special_cases(b, root, entries)

    # Ireton MaSade's Extremis Warsuit "uses the Mechanised profile"
    iu = unit("Lord Marshal Ireton MaSade")
    mech = model_entry(iu, "Ireton MaSade Mechanised")
    iu.find("selectionEntries").remove(mech)
    suit = next(e for e in entries.values() if e.get("name", "").startswith("Extremis Warsuit"))
    child(suit, "profiles").append(mech.find("profiles/profile"))
    et.rename(root, suit, "Extremis Warsuit")
    for l in list(iu.iter("entryLink")):  # he has Master of the Battlefield and no other trait
        if l.get("name") == "Warlord Traits":
            for p in iu.iter():
                if l in list(p):
                    p.remove(l)

    # "A model with this Special Rule must select one Core Psychic Discipline" (or Anathemata, Apostle Pattern)
    me = model_entry(unit("Solar Auxilia Battle Psyker"), "Auxilia Battle Psyker")
    g = el(child(me, "selectionEntryGroups"), "selectionEntryGroup", name="Battle Psyker: Psychic Discipline",
           hidden=False, id=mid(me.get("id"), "discipline"))
    add_constraint(g, "min", 1, mid(me.get("id"), "discipline min"))
    add_constraint(g, "max", 1, mid(me.get("id"), "discipline max"))
    for d in ("Biomancy", "Divination", "Pyromancy", "Telekinesis", "Telepathy", "Thaumaturgy", "Anathemata"):
        l = el(child(g, "entryLinks"), "entryLink", import_=True, name=f"Psychic Discipline: {d}", hidden=False,
               id=mid(me.get("id"), "discipline", d), type="selectionEntry", targetId=any_entry(f"Psychic Discipline: {d}"))
        add_constraint(l, "max", 1, mid(l.get("id"), "max"))
        if d == "Anathemata":
            l.set("hidden", "true")
            m = el(el(l, "modifiers"), "modifier", type="set", field="hidden", value="false")
            el(el(m, "conditions"), "condition", type="equalTo", value=1, field="selections", scope="force",
               childId=mid("doctrine", "Apostle Pattern Cohorts"), shared=True, includeChildSelections=True,
               includeChildForces=False, percentValue=False)

    sections_transports(b, entries)
    items = Items(b)
    marshals = marshal_entries(items)
    fist, dictatii, ordnance = (marshals[n].get("id") for n in MARSHALS)
    for uname, mname, offer, single in (
            ("Solar Auxilia Carnodon Command Section", None, ("Armoured Fist Marshal", fist, 50), False),
            ("Solar Auxilia Praetorian Heavy Tank Squadron", None, ("Dictatii Marshal", dictatii, 75), True),
            ("Solar Auxilia Manticore Missile Tank Battery", None, ("Ordnance Corps Marshal", ordnance, 50), False)):
        u = unit(uname)
        for m in [x for x in u.iter("selectionEntry") if x.get("type") == "model"]:
            child(m, "selectionEntryGroups").append(marshal_group(m.get("id"), [offer], u.get("id"), single))
            if offer[0] == "Dictatii Marshal":
                p = m.find("profiles/profile")
                child(p, "modifiers").extend(vehicle_profile_mods(m.get("id"), dictatii, p.get("id")))

    # new characters take their Warlord Trait as the official Solar Auxilia ones do
    traits = warlord_traits(b, mid("doctrine", "Steel Fury Pattern Cohorts"))
    for l in root.iter("entryLink"):
        if l.get("name") == "Warlord Traits" and l.get("type") == "selectionEntryGroup":
            l.set("targetId", MECH_WARLORD_TRAITS)
    for p in list(root.iter()):
        links = p.find("entryLinks")
        if links is not None and any(l.get("targetId") == MECH_WARLORD_TRAITS for l in links):
            el(links, "entryLink", import_=True, name=traits.get("name"), hidden=False, id=mid(p.get("id"), "sa traits"),
               type="selectionEntryGroup", targetId=traits.get("id"))

    shared = list(marshals.values())
    ops, val, val_tank = existing_units(items, shared)
    official = official_root()
    for p in official.iter():
        links = p.find(C + "entryLinks")
        if links is not None and any(l.get("targetId") == MECH_WARLORD_TRAITS for l in links):
            ops.add(p.get("id"), "entryLinks", [E("entryLink", id=mid(p.get("id"), "sa traits"), name=traits.get("name"),
                                                  hidden=False, collective=False, import_=True, targetId=traits.get("id"),
                                                  type="selectionEntryGroup")])

    # the doc's units under the official catalogue's names
    for ds in b.datasheets:
        e = entries[b.units[ds["name"]]]
        et.rename(root, e, short(ds["name"]))
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx, extra_ids=items.extra)
    by_name = {short(ds["name"]): (entries[b.units[ds["name"]]], ds) for ds in b.datasheets}
    roots = []
    for name, (u, ds) in by_name.items():
        et.drop_unit_category(u)
        et.add_types(u, SUB_TYPES)
        if name not in SECTIONS and name not in TRANSPORTS:
            roots.append(et.root_link(u, ds))

    tercios = []
    for tname, slot, compulsory, *parts in TERCIOS:
        resolved = [[(n, lo, hi, CARNODON_STRIKE if n == "Carnodon Strike Squadron" else by_name[n][0].get("id"))
                     for n, lo, hi in part] for part in parts]
        t = tercio(tname, resolved, tname)
        tercios.append(t)
        roots.append(et.root_link(t, None, slot=slot if compulsory else
                                  ("Troops (non-Compulsory)" if slot == "Troops" else slot)))
    tercio_ids = {t.get("name"): t.get("id") for t in tercios}

    # "0-3 Solar Auxilia Sabre Batteries" in the official Artillery Tercio
    art = official_root()
    batteries = named(art, ARTILLERY_BATTERIES, "selectionEntryGroup", named(art, "Artillery Tercio"))
    sabre = by_name["Sabre Battery"][0].get("id")
    ops.add(batteries.get("id"), "entryLinks", [link_el("Sabre Battery", sabre, batteries.get("id"), mx=3)])

    ids = doctrines(b, cat, by_name)
    opens = [("Apostle Pattern Cohorts", by_name["Possessed Auxilia"][0].get("id"), "Possessed Auxilia", "Troops (non-Compulsory)"),
             ("Linebreaker Pattern Cohorts", by_name["Furibundus Dreadnought Talon"][0].get("id"),
              "Furibundus Dreadnought Talon", "Troops"),
             ("Linebreaker Pattern Cohorts", by_name["Extremis Boarding Rig Section"][0].get("id"),
              "Extremis Boarding Rig Section", "Troops"),
             ("Pioneer Companies", by_name["Aethon Heavy Sentinel Squadron"][0].get("id"), "Aethon Heavy Sentinel Squadron",
              "Troops (non-Compulsory)"),
             ("Pioneer Companies", tercio_ids["Infantry Support Tercio"], "Infantry Support Tercio", "Troops"),
             ("Scourge Pattern Cohorts", by_name["Hellhound Flame Tank Squadron"][0].get("id"),
              "Hellhound Flame Tank Squadron", "Troops (non-Compulsory)"),
             ("Steel Fury Pattern Cohorts", named(art, "Macharius Heavy Tank Squadron").get("id"),
              "Macharius Heavy Tank Squadron", "Elites"),
             ("Valkyria Pattern Cohorts", by_name["Aello Gunship Squadron"][0].get("id"), "Aello Gunship Squadron",
              "Heavy Support")]
    roots += doctrine_links(ids, opens)

    marshals_on_official(cat, ops, marshals)
    ops.run(cat, items)
    valdor_second_tank(cat, val, val_tank)
    for e in shared:
        for x in e.iter():
            for a in ("targetId", "childId"):
                if x.get(a):
                    x.set(a, items.final(x.get(a)))
    cat.add_top("entryLinks", roots)
    cat.add_top("sharedSelectionEntries", units + tercios + keep_entries + shared)
    cat.add_top("sharedSelectionEntryGroups", keep_groups + [traits])
    if keep_rules:
        cat.add_top("sharedRules", keep_rules)
    cat.bump("catalogue")
    cat.save()
    print(f"{CAT}: {len(units)} units, {len(tercios)} Tercios, {len(keep_entries) + len(shared)} entries, "
          f"{len(keep_groups) + 1} groups, {len(keep_rules)} rules added")


et.SLOTS["Troops (non-Compulsory)"] = [("9b5d-fac7-799b-d7e7", "Troops:", True)]

if __name__ == "__main__":
    main()
