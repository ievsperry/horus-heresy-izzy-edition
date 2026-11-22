#!/usr/bin/env python3
"""Protodreadnoughts (homebrew/source/protodreadnoughts.md).

The Lucifer-Pattern, Furibundus-Pattern and Unification-Pattern Protodreadnoughts go into the Mech Library, which
the Legiones Astartes, Mechanicum, Imperialis Militia and Questoris Household catalogues all import, and every one of
those catalogues (each Legion, Blackshields and Shattered Legions too) gets a root entry for them. Their options for
one army only are hidden in every other army:

- World Eaters and Iron Warriors: the XII and IV Legion chassis upgrades and weapons (by the Legion's faction entry);
- Mechanicum: the High Techno-Arcana chassis upgrades (by the Order of High Techno-arcana the force has taken; the
  Infernal Warp-Capacitor for a Traitor force with the Reductor Order or a Proscribed Order) and the Mechanicum
  weapon swaps;
- Mechanicum or Questoris Household: the Questoris Household Bondsman-Rig, which moves the squadron to Troops and
  gives it the Line Sub-type.

The Leagues of Votann's Ironkin Ancestor-Rig, Cthonian Siege-Strider and Brokhyr Ballistic Strider are added to that
catalogue each time it is built (apply(), named in build_catalogue.py's FACTION_LIMITS), with their League upgrades
shown only for the League the Detachment has chosen.

Every model's arm is one pick: a close combat arm carries its in-built weapon, which has a pick of its own, so an arm
exchanged for a gun loses its in-built weapon, as on the datasheets.

usage: python3 homebrew/protodreadnoughts.py             (adds the Imperial units; refuses to run twice)
       python3 homebrew/protodreadnoughts.py --update    (rebuilds them in place from this script's data)"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, add_cost, child, el, make_id, norm  # noqa: E402

GST = "2022 - Horus Heresy.gst"
LIBRARY = "2022 - Mech Library.cat"
NS = "{http://www.battlescribe.net/schema/catalogueSchema}"
GNS = "{http://www.battlescribe.net/schema/gameSystemSchema}"

WEAPON = ("1a1a-e592-2849-a5c0", "Weapon", [("Range", "95ba-cda7-b831-6066"), ("Strength", "24d9-b8e1-a355-2458"),
                                            ("AP", "f7a6-e0d8-7973-cd8d"), ("Type", "2f86-c8b4-b3b4-3ff9")])
WARGEAR = ("2a1f-7837-f0ef-be44", "Wargear Item", "Description", "347e-ee4a-764f-6be3")
UNIT_PROFILE = ("4bb2-cb95-e6c8-5a21", "Unit")
ARMIGER = ("41ff-7fc9-d4a0-da2", "Armiger Unit Type")
HEAVY = ("9231-183c-b97b-63f9", "Heavy Sub-type")
LINE = ("6399-5c65-7833-1025", "Line Sub-type")
LEGIONES_ASTARTES = ("ffcb-13b4-9b4c-84da", "Legiones Astartes (X)")

# faction selections (each catalogue's Allegiance entry) and the Orders of High/Proscribed Techno-arcana
WORLD_EATERS, IRON_WARRIORS = "90ee-77dd-1b7f-ddfe", "5f54-457a-fbb9-6730"
IRON_HANDS, SALAMANDERS, DEATH_GUARD = "bfc9-c99c-bf8a-3917", "c805-ca3a-ff93-5e2f", "dd1f-1c51-706c-e5f7"
IMPERIAL_FISTS, SPACE_WOLVES, DARK_ANGELS = "a0e1-f2c4-8bcd-0723", "4916-965e-8339-44f6", "b2b4-2198-0b90-dd9f"
WINGS = ["Deathwing", "Dreadwing", "Ironwing", "Ravenwing", "Firewing", "Stormwing"]
MECHANICUM, QUESTORIS = "ddf5-d792-3146-6e9a", "807e-0cf8-7f28-7b6d"
TRAITOR = "f9c0-0c5a-3e24-58c7"
EMPERORS_CHILDREN = ["3edc-a1b9-6dc6-b1ea", "268b-74a8-395f-6f27"]   # the Legion, and as Legion Hereticus
WHITE_SCARS, NIGHT_LORDS, BLOOD_ANGELS = "e01e-5cdd-e512-8353", "b28b-71f7-e4f4-8f9c", "296e-301e-3ce1-1c15"
ULTRAMARINES, THOUSAND_SONS, SONS_OF_HORUS = "8e0f-3552-8842-f281", "21c3-2f28-7820-e51a", "01b4-57c7-bf61-2abf"
WORD_BEARERS, RAVEN_GUARD, ALPHA_LEGION = "9dbf-0760-d7ae-f125", "dc34-fe08-dd44-fb99", "c0df-c1fa-5ddc-9ee5"
BLACKSHIELDS, SHATTERED_LEGIONS = "ae4a-f95c-968e-eb46", "9950-2cd2-fd88-9bb1"
MILITIA = "5522-4fd9-12d5-460afds"
PROVENANCES = {"legacy": "b669-a356-d5d1-53b8", "industrial": "db1f-6157-2c58-5ae5", "survivors": "08f1-5fe7-1d3a-7b35",
               "armoury": "4bcd-7022-cefc-04da", "omnissiah": "b4f0-1668-4106-7bd1"}   # the Provenances of War
ORDERS = {"Cybernetica": "9bcd-f556-5740-2f9f", "Lacrymaerta": "bd4b-63fa-928c-887d", "Macrotek": "1247-a94b-070d-2a7b",
          "Malagra": "5e62-8d7e-a487-0490", "Myrmidax": "8305-5ac6-f395-e570", "Reductor": "73dc-f5bb-be45-2547"}
PROSCRIBED = ["e033-44c5-e827-20ff", "d929-7702-8f4b-3393", "de6f-55bd-6647-586a"]  # Malefikite, Nekrotek, Malamina
LEAGUES = {"Greater Thurian League": "53a0-2151-818f-1792", "Kronus Hegemony": "c420-ead6-6567-06b5",
           "Trans-Hyperian Alliance": "f1d3-30f8-4eba-00eb", "Urani-Surtr Regulates": "6323-25ed-9221-9ff4",
           "Ymyr Conglomerate": "a97e-906d-8554-dab7"}

# who may see an option: a list of alternatives, each a list of selections the force must all have
SHOW = {None: None, "mech": [[MECHANICUM]], "we": [[WORLD_EATERS]], "iw": [[IRON_WARRIORS]],
        "mech or questoris": [[MECHANICUM], [QUESTORIS]],
        "infernal": [[TRAITOR, ORDERS["Reductor"]]] + [[TRAITOR, p] for p in PROSCRIBED]}
SHOW.update({"ih": [[IRON_HANDS]], "sal": [[SALAMANDERS]], "dg": [[DEATH_GUARD]], "if": [[IMPERIAL_FISTS]],
             "sw": [[SPACE_WOLVES]], "da": [[DARK_ANGELS]], "not dg": [[DEATH_GUARD]]})
# a Dark Angels option for one Hexagrammaton wing: the squadron must have taken that wing (("unit", id) is a selection
# in this unit, not the force)
SHOW.update({f"da {w.lower()}": [[DARK_ANGELS, ("unit", None, w)]] for w in WINGS})
SHOW.update({"ec": [[e] for e in EMPERORS_CHILDREN], "ws": [[WHITE_SCARS]], "nl": [[NIGHT_LORDS]],
             "um": [[ULTRAMARINES]], "ts": [[THOUSAND_SONS]], "wb": [[WORD_BEARERS]],
             "wb traitor": [[WORD_BEARERS, TRAITOR]], "rg": [[RAVEN_GUARD]], "ba": [[BLOOD_ANGELS]],
             "if or ba": [[IMPERIAL_FISTS], [BLOOD_ANGELS]], "soh": [[SONS_OF_HORUS]], "al": [[ALPHA_LEGION]],
             "soh or al": [[SONS_OF_HORUS], [ALPHA_LEGION]], "bs": [[BLACKSHIELDS], [SHATTERED_LEGIONS]],
             "militia": [[MILITIA]], "mech or omnissiah": [[MECHANICUM], [MILITIA, PROVENANCES["omnissiah"]]]})
SHOW.update({f"prov {k}": [[MILITIA, v]] for k, v in PROVENANCES.items()})
SHOW.update({f"order {k}": [[v]] for k, v in ORDERS.items()})
SHOW.update({f"league {k}": [[v]] for k, v in LEAGUES.items()})


def mid(*key):
    return make_id("protodreadnought", *key)


class Ctx:
    """What a build can link: entries and rules by name, and the new shared entries it makes."""

    def __init__(self, key, entries, rules):
        self.key, self.entries, self.rules, self.new = key, entries, rules, []

    def id(self, name):
        i = self.entries.get(norm(name))
        if i is None:
            sys.exit(f"{self.key}: no entry named {name}")
        return i


def index(files):
    entries, rules = {}, {}
    for f in files:
        root = ET.parse(f).getroot()
        ns = GNS if f.endswith(".gst") else NS
        for e in root.findall(f"{ns}sharedSelectionEntries/{ns}selectionEntry"):
            entries.setdefault(norm(e.get("name")), e.get("id"))
        # shared rules first: a rule link only reaches those, not a rule written inside an entry or category
        for r in root.findall(f"{ns}sharedRules/{ns}rule") + list(root.iter(f"{ns}rule")):
            rules.setdefault(norm(r.get("name")), r.get("id"))
    return entries, rules


CURRENT_UNIT = [None]           # the unit being built: the scope of ("unit", ...) conditions


def wing_id(w):
    return mid("imperial", "wargear", f"Hexagrammaton: {w}")


def show_if(e, who):
    """Hidden unless the force has one of the alternatives' selections (all of them); with "not ...", hidden when it
    does."""
    alts = SHOW[who]
    if not alts:
        return e
    hide = who.startswith("not ")
    if not hide:
        e.set("hidden", "true")
    for alt in alts:
        mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="true" if hide else "false")
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="and"), "conditions") if len(alt) > 1 \
            else el(mod, "conditions")
        for c in alt:
            scope, cid = ("force", c) if isinstance(c, str) else (CURRENT_UNIT[0], wing_id(c[2]))
            el(conds, "condition", type="atLeast", value=1, field="selections", scope=scope, childId=cid, shared=True,
               includeChildSelections=True, includeChildForces=False, percentValue=False)
    return e


def rule_links(ctx, e, text, key):
    """Info links for the special rules a weapon's Type names ("Brutal (2)" links Brutal (X), shown as Brutal (2))."""
    seen = {l.get("targetId") for l in e.iter("infoLink")}  # a rule another profile already links
    for tok in re.split(r",\s*|;\s*", re.sub(r"\.$", "", text)):
        tok = tok.strip().lstrip("†")
        base = re.sub(r"\s*\([^()]*\)$", "", tok)
        if not tok or re.match(r"(Melee|Assault|Heavy|Pistol|Rapid[- ]Fire|Ordnance|Salvo)\b", tok, re.I):
            continue
        for name in (tok, base + " (X)", base):
            rid = ctx.rules.get(norm(name))
            if rid and rid not in seen:
                seen.add(rid)
                link = el(child(e, "infoLinks"), "infoLink", id=mid(*key, "rule", name), name=name, hidden=False,
                          targetId=rid, type="rule")
                if name != tok:
                    el(el(link, "modifiers"), "modifier", type="set", field="name", value=tok)
                break


def weapon(ctx, name, profiles):
    """A new weapon: [(profile name or None, range, strength, AP, type)]."""
    key = (ctx.key, "weapon", name)
    e = ET.Element("selectionEntry", {"id": mid(*key), "name": name, "hidden": "false", "collective": "false",
                                      "import": "true", "type": "upgrade"})
    for pname, *chars in profiles:
        pname = pname or name
        p = el(child(e, "profiles"), "profile", id=mid(*key, pname), name=pname, hidden=False, typeId=WEAPON[0],
               typeName=WEAPON[1])
        cs = el(p, "characteristics")
        for (cname, cid), v in zip(WEAPON[2], chars):
            el(cs, "characteristic", name=cname, typeId=cid).text = v
        rule_links(ctx, e, chars[3], key)
    add_cost(e, 0)
    ctx.new.append(e)
    ctx.entries[norm(name)] = e.get("id")
    return e


LA_LIBRARY = "2022 - Legiones Astartes.cat"
# Official weapons that only the Legiones Astartes library has, which the Mech Library cannot link (it does not import
# that library): copied exactly (name, profile, rules), with ids of their own.
OFFICIAL_COPIES = {"Leviathan Siege Claw": "4838-a0ca-93d8-f6b2", "Leviathan Siege Drill": "d266-0d1e-b8e5-1e90",
                   "Shrapnel Cannon": "975e-14eb-caed-4b5b", "Twin-Linked Shrapnel Cannon": "f3c2-ec0b-748b-4b86",
                   "Dragon's Breath Heavy Flamer": "1a5c-0c5f-d798-a067", "Iliastus Assault Cannon": "10aa-3c70-2bbe-9509",
                   "Twin-linked Iliastus Assault Cannon": "6575-5c45-c419-9b47", "Plasma Repeater": "7aa4-cb4e-0e15-6213",
                   "Asphyx Bolt Cannon": "ebce-ebc9-8ff7-d42d", "Banestrike Bolt Cannon": "3bfb-69ae-691e-645c",
                   # the Imperialis Militia's own, which the Mech Library does not import either
                   "Heavy Mining Laser": ("2022 - Imperialis Militia.cat", "8d8f-0ec2-a041-bcac")}
DROP_RULES = {"7ca5-9127-867f-0a57"}           # the Hammer of Olympia Rite of War's reroll: not the weapon's own rule


def official_copy(ctx, name):
    """The Legiones Astartes library's weapon, copied into this library: its profiles, and its special rules (a
    rule the game system does not have goes with it, written into the copy); none of its Legion or Rite of War
    modifiers (the Protodreadnoughts' options say who may take it)."""
    source, sid = OFFICIAL_COPIES[name] if isinstance(OFFICIAL_COPIES[name], tuple) else (LA_LIBRARY, OFFICIAL_COPIES[name])
    root = ET.parse(source).getroot()
    rules = {r.get("id"): r for r in root.iter(f"{NS}rule")}
    src = next(e for e in root.iter(f"{NS}selectionEntry") if e.get("id") == sid)
    raw = ET.tostring(src, encoding="unicode").replace(NS, "").replace('xmlns:ns0="http://www.battlescribe.net/schema/catalogueSchema"', "")
    raw = re.sub(r"ns0:", "", raw)
    e = ET.fromstring(raw)
    for tag in ("modifiers", "categoryLinks", "constraints"):
        for c in e.findall(tag):
            e.remove(c)
    gst_rules = set(index([GST])[1].values())
    inline = []
    for il in list(e.iter("infoLinks")):
        for l in list(il):
            t = l.get("targetId")
            if t in DROP_RULES:
                il.remove(l)
            elif l.get("type") == "rule" and t not in gst_rules:
                il.remove(l)
                r = rules[t]
                d = r.find(f"{NS}description")
                inline.append((r.get("name"), d.text if d is not None else ""))
    if inline:
        rs = child(e, "rules")
        for rname, text in inline:
            r = el(rs, "rule", id=mid("official copy", sid, rname), name=rname, hidden=False)
            el(r, "description").text = text
    for x in e.iter():
        for a in ("publicationId", "page"):
            x.attrib.pop(a, None)
        if x.get("id"):
            x.set("id", mid("official copy", sid, x.get("id")))
    ctx.new.append(e)
    ctx.entries[norm(name)] = e.get("id")
    return e


def wargear(ctx, name, text, rules=()):
    key = (ctx.key, "wargear", name)
    e = ET.Element("selectionEntry", {"id": mid(*key), "name": name, "hidden": "false", "collective": "false",
                                      "import": "true", "type": "upgrade"})
    p = el(child(e, "profiles"), "profile", id=mid(*key, "profile"), name=name, hidden=False, typeId=WARGEAR[0],
           typeName=WARGEAR[1])
    el(el(p, "characteristics"), "characteristic", name=WARGEAR[2], typeId=WARGEAR[3]).text = text
    for r in rules:
        rid, shown, target = ctx.rules.get(norm(r)), None, r
        if not rid and "(" in r:                    # "Shrouded (5+)": link Shrouded (X), shown with its value
            target = r[:r.index("(")].strip() + " (X)"
            rid, shown = ctx.rules.get(norm(target)), r
        if rid:
            il = el(child(e, "infoLinks"), "infoLink", id=mid(*key, "rule", r), name=target, hidden=False,
                    targetId=rid, type="rule")
            if shown:
                el(el(il, "modifiers"), "modifier", type="set", field="name", value=shown)
    add_cost(e, 0)
    ctx.new.append(e)
    ctx.entries[norm(name)] = e.get("id")
    return e


# Existing weapons the options now link under their own names, and the names the options had when they linked this
# script's own copies: the ids are made from the old names, so saved rosters keep their picks.
ID_ALIAS = {"Leviathan Siege Claw": "Siege Claw", "Leviathan Siege Drill": "Siege Drill",
            "Cyclone Missile Launcher": "Cyclone Missile System", "Twin-Linked Shrapnel Cannon": "Twin-linked Shrapnel Cannon",
            "Phosphex Discharger": "Carapace Phosphex Discharger",
            "Dragon's Breath Heavy Flamer": "Heavy Dragon's Breath Flamer", "Plasma Repeater": "Twin-linked Plasma Repeater"}


def link(parent, ctx, name, key, cost=None, mn=None, mx=None, who=None, idname=None):
    n = idname or ID_ALIAS.get(name, name) if ctx.key == "imperial" else name
    l = el(child(parent, "entryLinks"), "entryLink", id=mid(*key, n), name=name, hidden=False, collective=False,
           import_=True, targetId=ctx.id(name), type="selectionEntry")
    if mn is not None:
        add_constraint(l, "min", mn, mid(*key, n, "min"))
    if mx is not None:
        add_constraint(l, "max", mx, mid(*key, n, "max"))
    if cost is not None:
        add_cost(l, cost)
    return show_if(l, who)


def group(parent, name, key, mn, mx):
    g = el(child(parent, "selectionEntryGroups"), "selectionEntryGroup", id=mid(*key), name=name, hidden=False,
           collective=False, import_=True)
    if mn:
        add_constraint(g, "min", mn, mid(*key, "min"))
    if mx:
        add_constraint(g, "max", mx, mid(*key, "max"))
    return g


def option(g, ctx, opt, key):
    """One choice in a pick: (label, cost, weapons, in-built pick or None, who). A label that is one weapon with
    nothing in-built is a plain link to it."""
    label, cost, weapons, inbuilt, who = opt[:5]
    idl = opt[5] if len(opt) > 5 else (ID_ALIAS.get(label, label) if ctx.key == "imperial" else label)
    if weapons == [label] and not inbuilt:
        return link(g, ctx, label, key, cost=cost, mx=1, who=who, idname=idl)
    e = el(child(g, "selectionEntries"), "selectionEntry", id=mid(*key, idl), name=label, hidden=False,
           collective=False, import_=True, type="upgrade")
    add_constraint(e, "max", 1, mid(*key, idl, "max"))
    for w in weapons:
        link(e, ctx, w, key + (idl,), mn=1, mx=1)
    if inbuilt:
        pick(e, ctx, "In-built weapon", inbuilt, key + (idl, "in-built"))
    add_cost(e, cost)
    return show_if(e, who)


def pick(parent, ctx, name, options, key, mn=1, mx=1):
    """A pick (one of the options, the first by default)."""
    g = group(parent, name, key, mn, mx)
    first = None
    for opt in options:
        o = option(g, ctx, opt, key)
        first = o if first is None else first
    if mn:
        g.set("defaultSelectionEntryId", first.get("id"))
    return g


def per_model(e, unit_id, pts):
    """A whole-unit pick priced per model."""
    add_cost(e, 0)
    mod = el(child(e, "modifiers"), "modifier", type="increment", field=bc.PTS, value=pts)
    el(el(mod, "repeats"), "repeat", field="selections", scope=unit_id, value=1, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="model", repeats=1, roundUp=False)


def upgrades(unit, ctx, name, items, key, who=None):
    """A pick of at most one whole-unit upgrade: [(name, pts per model, text, who, rules)]."""
    g = group(unit, name, key, 0, 1)
    show_if(g, who)
    for uname, pts, text, uwho, rules in items:
        if norm(uname) not in ctx.entries:
            wargear(ctx, uname, text, rules)
        l = el(child(g, "entryLinks"), "entryLink", id=mid(*key, uname), name=uname, hidden=False, collective=False,
               import_=True, targetId=ctx.id(uname), type="selectionEntry")
        add_constraint(l, "max", 1, mid(*key, uname, "max"))
        per_model(l, unit.get("id"), pts)
        show_if(l, uwho)
    return g


def unit_entry(ctx, spec):
    """A squadron of one model type, as the official Armiger and Dreadnought units are built."""
    key = (ctx.key, spec["name"])
    CURRENT_UNIT[0] = mid(*key, "unit")
    u = ET.Element("selectionEntry", {"id": mid(*key, "unit"), "name": spec["name"], "hidden": "false",
                                      "collective": "false", "import": "true", "type": "unit"})
    for r, shown in spec["rules"]:
        rid = ctx.rules.get(norm(r))
        if rid is None:
            sys.exit(f"{ctx.key}: no rule {r}")
        l = el(child(u, "infoLinks"), "infoLink", id=mid(*key, "rule", r), name=r, hidden=False, targetId=rid,
               type="rule")
        if shown:
            el(el(l, "modifiers"), "modifier", type="set", field="name", value=shown)
    cats = child(u, "categoryLinks")
    for cid, cname in [ARMIGER] + ([HEAVY] if "Heavy" in spec["type"] else []):
        el(cats, "categoryLink", id=mid(*key, "cat", cname), name=cname, hidden=False, targetId=cid, primary=False)
    m = el(child(u, "selectionEntries"), "selectionEntry", id=mid(*key, "model"), name=spec["model"], hidden=False,
           collective=False, import_=True, type="model")
    add_constraint(m, "min", 1, mid(*key, "model", "min"))
    add_constraint(m, "max", spec["max"], mid(*key, "model", "max"))
    p = el(child(m, "profiles"), "profile", id=mid(*key, "profile"), name=spec["model"], hidden=False,
           typeId=UNIT_PROFILE[0], typeName=UNIT_PROFILE[1])
    cs = el(p, "characteristics")
    for (cname, cid), v in zip(bc.UNIT_CHARS, [spec["type"]] + spec["stats"]):
        el(cs, "characteristic", name=cname, typeId=cid).text = v
    for w in spec["wargear"]:
        link(m, ctx, w, key + ("model",), mn=1, mx=1)
    for gname, opts in spec["arms"]:
        pick(m, ctx, gname, opts, key + (gname,))
    for name, cost, who in spec.get("model_options", []):
        # a weapon for both arms (the Raven Guard's Ravenspire Heavy Talons): taken, the arm picks are gone
        l = link(m, ctx, name, key + ("model option",), cost=cost, mx=1, who=who)
        for gname, _ in spec["arms"]:
            g = next(x for x in m.find("selectionEntryGroups") if x.get("id") == mid(*key, gname))
            for field, value in (("hidden", "true"), (mid(*key, gname, "min"), 0), (mid(*key, gname, "max"), 0)):
                mod = el(child(g, "modifiers"), "modifier", type="set", field=field, value=value)
                el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=m.get("id"),
                   childId=l.get("id"), shared=True, includeChildSelections=True, includeChildForces=False,
                   percentValue=False)
    for gname, opts, most in spec["carapace"]:
        g = group(m, gname, key + (gname,), 0, most)
        for name, cost, who in opts:
            link(g, ctx, name, key + (gname,), cost=cost, mx=1, who=who)
    add_cost(m, spec["model_pts"])
    add_cost(u, spec["unit_pts"])
    for gname, items, who in spec["upgrades"]:
        g = upgrades(u, ctx, gname, items, key + (gname,), who)
        if gname == "Hexagrammaton Sub-type":                     # one wing, which a Dark Angels squadron must choose
            cid = add_constraint(g, "min", 0, mid(*key, gname, "required"))
            m = el(child(g, "modifiers"), "modifier", type="set", field=cid, value=1)
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
               childId=DARK_ANGELS, shared=True, includeChildSelections=True, includeChildForces=False,
               percentValue=False)
    for name, pts, text, who in spec.get("unit_options", []):
        if norm(name) not in ctx.entries:
            wargear(ctx, name, text)
        l = link(u, ctx, name, key + ("unit option",), mx=1, who=who)
        per_model(l, u.get("id"), pts)
    return u


# ---- the datasheets ---------------------------------------------------------------------------------------------

EXTRA_ARMOUR = ("Grants a 2+ Armour Save and a 6+ Invulnerable Save against all shooting and melee attacks. In "
                "addition, enemy attacks targeting this model do not benefit from To Wound re-rolls granted by the "
                "Armourbane (X) special rule, and the value of any Brutal (X) special rule is reduced by 1 (to a "
                "minimum of 1).")
TARGETING = ("Grants Skyfire and Interceptor to all weapons fired by this model if it remained stationary in its "
             "preceding Movement phase.")
INBUILT_IMPERIAL = [("Heavy Flamer", 5, "Heavy Flamer"), ("Plasma Blaster", 10, "Plasma Blaster"),
                    ("Graviton Gun", 15, "Graviton Gun"), ("Meltagun", 15, "Meltagun")]


LEGION_INBUILT = [("Dragon's Breath Heavy Flamer", 10, "sal"), ("Heavy Alchem-Sprayer", 10, "dg"),
                  ("Plasma Caster", 10, "da"), ("Rad-Furnace Projector", 10, "prov armoury")]          # a Twin-linked Bolter's Dark Angels swap: the Plasma Repeater


def inbuilt(default, items, mech=False, legions=True):
    opts = [(default, 0, [default], None, None)] + [(n, c, [w], None, None) for n, c, w in items]
    if mech:
        opts += [("Volkite Charger", 5, ["Volkite Charger"], None, "mech"),
                 ("Phased Plasma-Fusil", 10, ["Phased Plasma-Fusil"], None, "mech")]
    if legions and items is INBUILT_IMPERIAL:
        for n, c, who in LEGION_INBUILT:
            if n == "Plasma Caster" and default == "Twin-linked Bolter":
                n = "Plasma Repeater"                    # the official (Dark Angels) Plasma Repeater
            opts.append((n, c, [n], None, who))
    return opts


def imperial_weapons(ctx):
    for name in OFFICIAL_COPIES:                       # the existing weapons the Mech Library cannot link
        official_copy(ctx, name)
    weapon(ctx, "Twin-linked Cyclone Missile Pod", [
        ("Twin-linked Cyclone Missile Pod - Frag", '48"', "4", "6", 'Heavy 1, Large Blast (5"), Pinning, Twin-linked'),
        ("Twin-linked Cyclone Missile Pod - Krak", '48"', "8", "3", "Heavy 2, Twin-linked")])
    weapon(ctx, "Twin-linked Gravis Lascannon", [(None, '48"', "9", "2", "Heavy 2, Sunder, Twin-linked")])
    if norm("Twin-linked Mauler Bolt Cannon") not in ctx.entries:
        weapon(ctx, "Twin-linked Mauler Bolt Cannon", [(None, '24"', "6", "4", "Heavy 4, Pinning, Twin-linked")])
    weapon(ctx, "Excoriator Chain-Cleaver", [(None, "-", "+2", "2", "Melee, Shred, Brutal (2), Unwieldy; a pair "
                                                                   "grants +1 Attack")])
    weapon(ctx, "Graviton Crusher-Claw", [(None, "-", "+2", "2", "Melee, Concussive (1), Haywire, Unwieldy")])
    # the Legions' weapons
    weapon(ctx, "Graviton Shredder-Cannon", [(None, '24"', "*", "4", 'Heavy 3, Blast (3"), Graviton Pulse, '
                                                                    "Concussive (1), Haywire")])
    weapon(ctx, "Cyber-Augmetic Siege Wrench", [(None, "-", "x2", "2", "Melee, Armourbane (Melee), Sunder, Unwieldy")])
    weapon(ctx, "Obsidian Thermal-Lance", [(None, '18"', "9", "1", "Heavy 1, Beam, Armourbane (Melta), Master-crafted")])
    weapon(ctx, "Heavy Alchem-Sprayer", [(None, "Template", "1", "3", 'Assault 1, Poisoned (2+), Fleshbane, '
                                                                      'Torrent (6")')])
    weapon(ctx, "Bile-Caster Mortar", [(None, '36"', "4", "4", 'Heavy 1, Blast (3"), Barrage, Poisoned (3+), Pinning')])
    weapon(ctx, "Solarite Siege-Fist", [(None, "-", "x2", "1", "Melee, Armourbane (Melee), Instant Death, Unwieldy")])
    weapon(ctx, "Great Frost-Cleaver", [(None, "-", "+3", "2", "Melee, Rending (5+), Shred, Brutal (2); a pair grants "
                                                               "+1 Attack")])
    weapon(ctx, "Helfrost Cannon", [(None, '24"', "8", "2", 'Heavy 1, Blast (3"), Helfrost (models suffering unsaved '
                                                            "wounds must pass a Strength test or be removed from play)")])
    weapon(ctx, "Plasma Caster", [(None, '18"', "7", "2", "Assault 2, Gets Hot, Breaching (4+)")])
    weapon(ctx, "Twin-linked Graviton Shredder-Cannon", [(None, '24"', "*", "4", 'Heavy 3, Blast (3"), Graviton Pulse, '
                                                                                "Concussive (1), Haywire, Twin-linked")])
    weapon(ctx, "Twin-linked Helfrost Cannon", [(None, '24"', "8", "2", 'Heavy 1, Blast (3"), Helfrost (models suffering '
                                                                        "unsaved wounds must pass a Strength test or be "
                                                                        "removed from play), Twin-linked")])
    weapon(ctx, "Molecular Acid-Cannon", [(None, '24"', "6", "2", 'Heavy 2, Blast (3"), Fleshbane, Armourbane (Ranged), '
                                                                  "Ignores Cover")])
    weapon(ctx, "Terranic Greatsword-Gauntlet", [(None, "-", "+2", "2", "Melee, Rending (5+), Murderous Strike (6+), "
                                                                        "Duellist's Edge (1)")])
    # the remaining Legions', the Blackshields' and the Imperialis Militia's
    weapon(ctx, "Kakophoni Heavy Blaster", [(None, '24"', "6", "3", "Heavy 3, Pinning, Shell Shock (1), Rending (6+)")])
    weapon(ctx, "Twin-linked Kakophoni Heavy Blaster", [(None, '24"', "6", "3", "Heavy 3, Pinning, Shell Shock (1), "
                                                                             "Rending (6+), Twin-linked")])
    weapon(ctx, "Cyber-Hawk Glaive", [(None, "-", "+2", "2", "Melee, Rending (5+), Reach (1), Sudden Strike (1)")])
    weapon(ctx, "Nostraman Chainglaive-Claw", [(None, "-", "+2", "2", "Melee, Rending (5+), Shred, Murderous Strike (6+)")])
    weapon(ctx, "Legatine Power Gladius-Fist", [(None, "-", "+3", "2", "Melee, Master-crafted, Duellist's Edge (1), "
                                                                       "Brutal (2)")])
    # the official Asphyx and Banestrike Bolt Cannons, twin-linked for the Furibundus's twin-linked bolt cannon arms
    weapon(ctx, "Twin-linked Asphyx Bolt Cannon", [(None, '24"', "6", "4", "Heavy 4, Shred, Twin-linked")])
    weapon(ctx, "Twin-linked Banestrike Bolt Cannon", [(None, '24"', "6", "4", "Heavy 4, Breaching (6+), Twin-linked")])
    weapon(ctx, "Warpfire Plasma Cannon", [(None, '36"', "7", "2", 'Heavy 1, Blast (3"), Gets Hot, Breaching (4+), '
                                                                  "Soulblaze")])
    weapon(ctx, "Ravenspire Heavy Talons", [(None, "-", "+2", "2", "Melee, Two-handed, Rending (5+), Shred, "
                                                                   "Sudden Strike (1)")])
    weapon(ctx, "Salvaged Heavy Chain-Cleaver", [(None, "-", "+2", "2", "Melee, Shred, Unwieldy")])
    weapon(ctx, "Rad-Furnace Projector", [(None, "Template", "3", "4", 'Assault 1, Fleshbane, Rad-Phage, Torrent (6")')])
    weapon(ctx, "Twin-linked Heavy Mining Laser", [(None, '24"', "9", "1", "Heavy 1, Exoshock (6+), Twin-linked")])
    wargear(ctx, "Dreadnought Extra Armour", EXTRA_ARMOUR)
    wargear(ctx, "Protodreadnought Helical Targeting Array", TARGETING, ["Skyfire", "Interceptor"])


def fist(name, cost, default_inbuilt):
    """A close combat arm with its in-built weapon."""
    return (name, cost, [name], inbuilt(default_inbuilt, INBUILT_IMPERIAL, mech=True), None)


def lucifer_arm():
    return [fist("Gravis Power Fist", 0, "Combi-bolter"),
            fist("Gravis Chainfist", 10, "Combi-bolter"),
            ("Gravis Bolt Cannon", 5, ["Gravis Bolt Cannon"], None, None),
            ("Gravis Autocannon", 10, ["Gravis Autocannon"], None, None),
            ("Cyclone Missile Launcher", 15, ["Cyclone Missile Launcher"], None, None),
            ("Gravis Lascannon", 15, ["Gravis Lascannon"], None, None),
            ("Gravis Melta Cannon", 15, ["Gravis Melta Cannon"], None, None),
            ("Heavy Conversion Beamer", 20, ["Heavy Conversion Beamer"], None, None),
            ("Siege Drill with in-built Heavy Flamer", 15, ["Leviathan Siege Drill", "Heavy Flamer"], None, None),
            # Mechanicum: a Mauler Bolt Cannon for the bolt cannon or autocannon (+5), a Kheres or Darkfire for the
            # lascannon (+15, +20)
            ("Mauler Bolt Cannon", 10, ["Mauler Bolt Cannon"], None, "mech or omnissiah"),
            ("Kheres Assault Cannon", 30, ["Kheres Assault Cannon"], None, "mech"),
            ("Darkfire Cannon", 35, ["Darkfire Cannon"], None, "mech"),
            ("Excoriator Chain-Cleaver", 15, ["Excoriator Chain-Cleaver"], inbuilt("Combi-bolter", INBUILT_IMPERIAL),
             "we"),
            ("Graviton Crusher-Claw", 15, ["Graviton Crusher-Claw"], inbuilt("Combi-bolter", INBUILT_IMPERIAL), "iw"),
            ("Shrapnel Cannon", 5, ["Shrapnel Cannon"], None, "iw")] + legion_arms("lucifer")


def furibundus_arm():
    return [("Leviathan Siege Claw", 0, ["Leviathan Siege Claw"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL, mech=True),
             None),
            ("Leviathan Siege Drill", 10, ["Leviathan Siege Drill"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL, mech=True),
             None),
            # the official Gravis Bolt Cannon and Gravis Autocannon are Twin-linked already
            ("Gravis Bolt Cannon", 10, ["Gravis Bolt Cannon"], None, None, "Twin-linked Gravis Bolt Cannon"),
            ("Gravis Autocannon", 15, ["Gravis Autocannon"], None, None, "Twin-linked Gravis Autocannon"),
            ("Twin-linked Cyclone Missile Pod", 25, ["Twin-linked Cyclone Missile Pod"], None, None),
            ("Twin-linked Gravis Lascannon", 25, ["Twin-linked Gravis Lascannon"], None, None),
            ("Cyclonic Melta Lance", 25, ["Cyclonic Melta Lance"], None, None),
            ("Grav-Flux Bombard", 25, ["Grav-Flux Bombard"], None, None),
            ("Heavy Conversion Beamer", 20, ["Heavy Conversion Beamer"], None, None),
            ("Twin-linked Mauler Bolt Cannon", 20, ["Twin-linked Mauler Bolt Cannon"], None, "mech"),
            ("Kheres Assault Cannon", 40, ["Kheres Assault Cannon"], None, "mech"),
            ("Darkfire Cannon", 45, ["Darkfire Cannon"], None, "mech"),
            ("Excoriator Chain-Cleaver", 15, ["Excoriator Chain-Cleaver"],
             inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL), "we"),
            ("Graviton Crusher-Claw", 15, ["Graviton Crusher-Claw"], inbuilt("Twin-linked Bolter", INBUILT_IMPERIAL),
             "iw"),
            ("Twin-Linked Shrapnel Cannon", 10, ["Twin-Linked Shrapnel Cannon"], None, "iw")] + legion_arms("furibundus")


def unification_arm(base):
    """The gun arms, priced from the arm's own weapon (the primary arm's Gravis Bolt Cannon, 0; the missile arm's
    Cyclone Missile System, 0)."""
    if base == "primary":
        costs = {"Gravis Bolt Cannon": 0, "Gravis Autocannon": 5, "Gravis Plasma Cannon": 10,
                 "Volkite Dual-Culverin": 10, "Cyclone Missile Launcher": 10, "Gravis Lascannon": 15}
        order = ["Gravis Bolt Cannon", "Gravis Autocannon", "Gravis Plasma Cannon", "Volkite Dual-Culverin",
                 "Cyclone Missile Launcher", "Gravis Lascannon"]
    else:
        costs = {"Cyclone Missile Launcher": 0, "Gravis Bolt Cannon": -10, "Gravis Autocannon": -5,
                 "Gravis Plasma Cannon": 0, "Volkite Dual-Culverin": 0, "Gravis Lascannon": 5}
        order = ["Cyclone Missile Launcher", "Gravis Bolt Cannon", "Gravis Autocannon", "Gravis Plasma Cannon",
                 "Volkite Dual-Culverin", "Gravis Lascannon"]
    out = [(n, costs[n], [n], None, None) for n in order]
    bolt, las = costs["Gravis Bolt Cannon"], costs["Gravis Lascannon"]
    out = out + [("Mauler Bolt Cannon", bolt + 5, ["Mauler Bolt Cannon"], None, "mech or omnissiah"),
                  ("Kheres Assault Cannon", las + 15, ["Kheres Assault Cannon"], None, "mech"),
                  ("Darkfire Cannon", las + 20, ["Darkfire Cannon"], None, "mech"),
                  ("Shrapnel Cannon", bolt, ["Shrapnel Cannon"], None, "iw"),
                  # Iron Hands: a Graviton Shredder-Cannon for the bolt cannon (+15); Imperial Fists: an Iliastus
                  # Assault Cannon for it (+10); Space Wolves: a Helfrost Cannon for the plasma cannon (+15)
                  ("Graviton Shredder-Cannon", bolt + 15, ["Graviton Shredder-Cannon"], None, "ih"),
                  ("Iliastus Assault Cannon", bolt + 10, ["Iliastus Assault Cannon"], None, "if or ba"),
                  ("Helfrost Cannon", costs["Gravis Plasma Cannon"] + 15, ["Helfrost Cannon"], None, "sw"),
                  # Emperor's Children, Thousand Sons, Sons of Horus and Alpha Legion: for the bolt cannon; Word
                  # Bearers: for the plasma cannon; Industrial Stronghold Militia: for the lascannon
                  ("Kakophoni Heavy Blaster", bolt + 15, ["Kakophoni Heavy Blaster"], None, "ec"),
                  ("Asphyx Bolt Cannon", bolt + 10, ["Asphyx Bolt Cannon"], None, "ts"),
                  ("Banestrike Bolt Cannon", bolt + 10, ["Banestrike Bolt Cannon"], None, "soh or al"),
                  ("Warpfire Plasma Cannon", costs["Gravis Plasma Cannon"] + 10, ["Warpfire Plasma Cannon"], None, "wb"),
                  ("Heavy Mining Laser", las + 10, ["Heavy Mining Laser"], None, "prov industrial")]
    # no swap costs less than nothing: the missile arm's cheaper guns are free
    return [(n, max(0, c), *rest) for n, c, *rest in out]


# the fist or claw swaps of the White Scars, Night Lords and Blackshields (the Ultramarines' replaces a fist only)
SHARED_MELEE = [("Cyber-Hawk Glaive", 15, "ws"), ("Nostraman Chainglaive-Claw", 10, "nl"),
                ("Salvaged Heavy Chain-Cleaver", 10, "bs")]


def legion_arms(pattern):
    """The Legions' arm swaps, priced from the arm's own weapon (the fist or claw, 0) through the weapon they replace:
    a Lucifer's Gravis Bolt Cannon is +5, its Gravis Melta Cannon +15; a Furibundus's Twin-linked Gravis Bolt Cannon
    +10, its Cyclonic Melta Lance +25 and its Heavy Conversion Beamer +20."""
    if pattern == "lucifer":
        cb, melee = "Combi-bolter", [("Cyber-Augmetic Siege Wrench", 10, "ih"), ("Solarite Siege-Fist", 15, "if"),
                                     ("Great Frost-Cleaver", 15, "sw"), ("Terranic Greatsword-Gauntlet", 10, "da deathwing"),
                                     ("Legatine Power Gladius-Fist", 10, "um")] + SHARED_MELEE
        guns = [("Graviton Shredder-Cannon", 5 + 15, "ih"), ("Obsidian Thermal-Lance", 15 + 15, "sal"),
                ("Iliastus Assault Cannon", 5 + 10, "if or ba"), ("Helfrost Cannon", 15 + 15, "sw"),
                ("Molecular Acid-Cannon", 15 + 20, "da dreadwing"),
                ("Kakophoni Heavy Blaster", 5 + 15, "ec"), ("Asphyx Bolt Cannon", 5 + 10, "ts"),
                ("Banestrike Bolt Cannon", 5 + 10, "soh or al"),
                ("Heavy Mining Laser", 15 + 10, "prov industrial")]       # for the lascannon or melta cannon
    else:
        cb, melee = "Twin-linked Bolter", [("Cyber-Augmetic Siege Wrench", 10, "ih"), ("Solarite Siege-Fist", 15, "if"),
                                           ("Great Frost-Cleaver", 15, "sw"),
                                           ("Terranic Greatsword-Gauntlet", 10, "da deathwing")] + SHARED_MELEE
        # twin-linked swaps cost twice the single one (as the Twin-linked Iliastus Assault Cannon does): the
        # Twin-linked Graviton Shredder-Cannon for the Twin-linked Gravis Bolt Cannon (+30), the Twin-linked Helfrost
        # Cannon for the Cyclonic Melta Lance (+30)
        guns = [("Obsidian Thermal-Lance", 25 + 15, "sal"), ("Twin-linked Iliastus Assault Cannon", 10 + 20, "if or ba"),
                ("Molecular Acid-Cannon", 20 + 20, "da dreadwing"),
                ("Twin-linked Graviton Shredder-Cannon", 10 + 30, "ih"), ("Twin-linked Helfrost Cannon", 25 + 30, "sw"),
                ("Twin-linked Kakophoni Heavy Blaster", 10 + 30, "ec"), ("Twin-linked Asphyx Bolt Cannon", 10 + 20, "ts"),
                ("Twin-linked Banestrike Bolt Cannon", 10 + 20, "soh or al"),
                ("Twin-linked Heavy Mining Laser", 25 + 20, "prov industrial")]   # for the Twin-linked Gravis Lascannon
    return ([(n, c, [n], inbuilt(cb, INBUILT_IMPERIAL), who) for n, c, who in melee] +
            [(n, c, [n], None, who) for n, c, who in guns])


TECHNO_ARCANA = [
    ("Cortex-Controller Slave-Node", 15, "Replaces the living pilot with a hard-wired Cybernetica Cortex; the model "
     "gains the Cybernetica unit sub-type, Fearless, and Programmed Behaviour (if not within 12\" of a friendly model "
     "with a Cortex Controller, it must fire at the nearest visible enemy unit and cannot make Reactions). While "
     "within 12\" of a friendly Cortex Controller, it adds +1 to its Ballistic Skill when making Interceptor "
     "Reactions.", "order Cybernetica", ["Fearless"]),
    ("Siege-Breaker Auspex & Shock-Prow", 20, "When resolving shooting or melee attacks against Fortifications, "
     "Buildings, or Vehicles, this model gains Sunder (re-rolling failed Armour Penetration rolls). In addition, it "
     "gains Hammer of Wrath (2) resolved at Strength 8, AP 3.", "order Reductor", ["Sunder", "Hammer of Wrath (X)"]),
    ("Bio-Augmetic Vat-Pilot", 20, "The living pilot is heavily fused into nutrient-stasis manifolds and sub-dermal "
     "flesh-grafts; the model gains Feel No Pain (5+) and It Will Not Die (5+).", "order Lacrymaerta",
     ["Feel No Pain (X)", "It Will Not Die (X)"]),
    ("Anima-Hunting Logic-Engine", 20, "When targeting enemy units containing models with the Psyker, Daemon, or "
     "Corrupted special rules (or Enemy HQ units), this model gains Preferred Enemy (Target Unit) and Hatred (Target "
     "Unit).", "order Malagra", ["Preferred Enemy (X)", "Hatred (X)"]),
    ("Auto-Simulacra & Power-Conduit", 15, "At the start of each friendly Movement phase, roll a D6; on a 5+, this "
     "model restores 1 lost Wound (up to its starting maximum). In addition, friendly models with the Battlesmith (X) "
     "special rule within 3\" add +1 to their Battlesmith rolls when repairing this model (to a maximum of 2+).",
     "order Macrotek", []),
    ("Phased Plasma-Fusil & Targeting Array", 20, "All Volkite, Plasma, Conversion, and Graviton weapons equipped by "
     "this model add +4\" to their maximum range and may re-roll Gets Hot rolls of 1.", "order Myrmidax", []),
    ("Infernal Warp-Capacitor", 25, "Traitor only. The model gains the Corrupted sub-type, Fear (1), and a 5+ "
     "Invulnerable Save against all shooting and melee attacks. However, when reduced to 0 Wounds, add +2\" to the "
     "radius of its Unstable Arc-Reactor explosion (inflicting hits on all units within 8\" instead of 6\").",
     "infernal", ["Fear (X)"]),
]
QUESTORIS_UPGRADE = [
    ("Questoris Household Bondsman-Rig", 15, "Replaces the standard Mechanicum pilot with a bonded Knight Household "
     "Aspirant or Sacristan Bondsman. This unit gains the Questoris Familia faction keyword and the Line unit "
     "sub-type, and may be selected as a Troops choice instead of its normal Force Organisation Chart slot. However, "
     "it retains (or gains) the Support Squad special rule (meaning it cannot be used to fulfil compulsory Troops "
     "selections in a detachment). In addition, while within 12\" of a friendly Knight unit (any model with the "
     "Knight Unit Type), this unit may use that Knight's Leadership characteristic for Morale and Pinning tests and "
     "gains Counter-Attack (1).", None, ["Counter-Attack (X)"])]
WORLD_EATERS_UPGRADES = [
    ("Butcher's Nails Neural-Shunt", 20, "The pilot's Butcher's Nails are wired directly into the walker's hydraulic "
     "manifolds. The model gains Rage (2) and Fearless, and ignores the -1\" penalty to Charge distance rolls from "
     "Clumsy Hydraulic Actuators (it still suffers the -1\" penalty to Run moves and cannot make Sweeping Advances). "
     "However, if the model is within 12\" of an eligible enemy unit at the start of its Assault phase and did not "
     "fire a Heavy weapon in the preceding Shooting phase, it must declare a Charge if able.", None,
     ["Rage (X)", "Fearless"]),
    ("Goreslick Siege-Ram", 15, "Fitted with serrated dozer-blades and pressurised blood-drains, the model gains "
     "Hammer of Wrath (2) resolved at Strength 8, AP 3, and may re-roll failed Dangerous Terrain tests.", None,
     ["Hammer of Wrath (X)"]),
    ("Berserker Overdrive Manifolds", 20, "Once per game, at the start of your Assault phase, you may overcharge this "
     "model's thermal reactor; until the end of that phase, add +1 to its Initiative and Attacks characteristics. At "
     "the end of that Assault phase, roll a D6: on a 1, the model suffers 1 unsaved Wound with no saves allowed as "
     "its cooling vents rupture.", None, []),
]
CAEDERE = ("Caedere Shock-Lances / Harvester Blades", 10, "Whenever an enemy unit fails a Morale check within 6\" of "
           "this model, or is reduced to below half its starting models in melee by this model, this model gains "
           "Hatred (Everything) until the end of the turn.", "we")
IRON_WARRIORS_UPGRADES = [
    ("Olympian Ablative Siege-Mantlets", 20, "Thick, bolted-on iron plates shield the walker's vulnerable leg joints "
     "and reactor housing. Enemy ranged attacks targeting this model subtract -1 from their Strength characteristic "
     "when resolving To Wound rolls against Blast or Barrage weapons, and the model gains Armoured Ceramite "
     "(preventing enemy weapons with Armourbane (Melta) from rolling an extra D6 at half range).", None, []),
    ("Iron-Fire Targeter-Cogitators", 15, "Linked directly into Perturabo's automated artillery grid, this model may "
     "re-roll To Hit rolls of 1 when firing Heavy or Ordnance weapons, and ignores negative Ballistic Skill modifiers "
     "caused by Night Fighting.", None, []),
    ("Expendable Vanguard Manifolds", 15, "The pilot is locked inside a welded-shut cockpit with over-pressurised "
     "fuel injectors. The model ignores the -1\" penalty to Run moves from Clumsy Hydraulic Actuators (it still "
     "suffers -1\" to Charge rolls and cannot make Sweeping Advances), and when reduced to 0 Wounds, its reactor "
     "explosion increases to Strength 9, AP 4 out to 8\" (or Strength 10, AP 3 out to 8\" for a Furibundus-Pattern).",
     None, []),
]


IRON_HANDS_UPGRADES = [
    ("Gorgon Cyber-Mantle Plating", 20, "Thick, interlocked plates of Gorgon-pattern ferro-ceramite reinforce the "
     "walker's chassis. The model gains It Will Not Die (5+) and Armoured Ceramite (preventing enemy weapons with "
     "Armourbane (Melta) from rolling an extra D6 at half range).", None, ["It Will Not Die (X)"]),
    ("Mind-Impulse Neural Hardwire", 15, "The pilot is permanently lobotomised and hard-wired directly into the "
     "walker's cogitator core. The model gains Fearless and Battlesmith (5+) (allowing it to repair 1 lost Wound on "
     "itself at the start of its Shooting phase instead of firing a weapon).", None, ["Fearless", "Battlesmith (X)"]),
    ("Medusan Graviton Capacitor", 20, "Linked to unstable Medusan gravity-coils, all Graviton and Conversion weapons "
     "equipped by this model add +6\" to their maximum range and gain Haywire (if they do not already possess it).",
     None, ["Haywire"]),
]
SALAMANDERS_UPGRADES = [
    ("Nocturnean Mantle-Shielding", 20, "Master-crafted refractory plates and heat-sinks insulate the walker's reactor "
     "and cockpit. The model gains It Will Not Die (5+) and Armoured Ceramite (preventing enemy weapons with "
     "Armourbane (Melta) from rolling an extra D6 at half range). In addition, the model does not automatically "
     "explode when reduced to 0 Wounds; instead, it only Explodes on a D6 roll of 5+.", None, ["It Will Not Die (X)"]),
    ("Drake-Scale Promethium Tanks", 15, "Pressurised auxiliary promethium reservoirs feed the walker's close-range "
     "weapons. All Flame and Melta weapons equipped by this model gain +1 Strength (to a maximum of 9) and Shred.",
     None, ["Shred"]),
    ("Forge-Master's Reinforced Pistons", 15, "Hand-balanced hydraulic actuators ease the strain on the walker's "
     "frame. The model ignores the -1\" penalty to Run moves from Clumsy Hydraulic Actuators (it still suffers -1\" to "
     "Charge rolls and cannot make Sweeping Advances) and gains Move Through Cover.", None, ["Move Through Cover"]),
]
DEATH_GUARD_UPGRADES = [
    ("Barbaran Chem-Sealed Hull", 20, "Hermetically welded hull seams and redundant atmospheric scrubbers protect the "
     "pilot and reactor. The model gains Feel No Pain (5+) against wounds caused by Poisoned (X), Fleshbane, Phosphex, "
     "and Rad weapons, and gains It Will Not Die (5+).", None, ["Feel No Pain (X)", "It Will Not Die (X)"]),
    ("Alchem-Reservoir Feed", 15, "Pressurised chemical tanks inject corrosive toxins into the walker's close-support "
     "weaponry. All Flamer weapons equipped by this model gain Poisoned (3+) and Fleshbane, and all Bolt or Autocannon "
     "weapons gain Poisoned (4+).", None, ["Poisoned (X)", "Fleshbane"]),
    ("Relentless Attrition Actuators", 15, "Over-built, low-gear hydraulic pistons sacrifice speed for unstoppable "
     "momentum. The model ignores negative modifiers to its Charge distance rolls caused by terrain or enemy special "
     "rules (though it still suffers the -1\" penalty from Clumsy Hydraulic Actuators), and reduces the Strength of "
     "incoming Blast and Template attacks by -1.", None, []),
]
IMPERIAL_FISTS_UPGRADES = [
    ("Phalanx Boarding-Bulwark", 20, "Heavy, curved boarding-shields bolted onto the walker's forward hull deflect "
     "incoming fire. The model gains a 5+ Invulnerable Save against shooting attacks originating within its Front Arc "
     "(improving to 4+ if upgraded with Dreadnought Extra Armour), and counts as providing Hard Cover (4+) to friendly "
     "Legiones Astartes Infantry models within 2\".", None, []),
    ("Inwit Ballistic-Sync Cogitator", 15, "Calibrated to VII Legion firing doctrine, this model may re-roll To Hit "
     "rolls of 1 when firing Bolt, Auto, or Missile weapons, and adds +1 to its Ballistic Skill when making Overwatch or "
     "Interceptor Reactions (to a maximum of BS 4).", None, []),
    ("Bastion-Anchor Clamps", 15, "Hydraulic ground-spikes lock the walker into place during defensive firefights. If "
     "this model remained stationary during its preceding Movement phase, it gains Counter-Attack (1) and adds +1 to "
     "its Toughness characteristic against shooting attacks until the start of its next Movement phase.", None,
     ["Counter-Attack (X)"]),
]
SPACE_WOLVES_UPGRADES = [
    ("Fenrisian Stalker-Actuators", 20, "Over-tuned leg pistons and stripped hull plating allow the walker to bound "
     "across broken ground. The model ignores the -1\" penalty to Run and Charge distance rolls from Clumsy Hydraulic "
     "Actuators, and gains Move Through Cover and Scout.", None, ["Move Through Cover", "Scout"]),
    ("Pack-Hunter Auspex Array", 15, "Linked to the sensory pack-net of nearby Grey Slayers, this model gains "
     "Counter-Attack (1) and Preferred Enemy (Infantry) in close combat. In addition, friendly Space Wolves Infantry "
     "units within 6\" may re-roll failed Charge distance rolls.", None, ["Counter-Attack (X)", "Preferred Enemy (X)"]),
    ("Wyrd-Rune Totem Plating", 15, "Etched with Fenrisian protective wards and wolf-pelt talismans, the model gains "
     "Adamantium Will (5+) (granting a 5+ Invulnerable Save against psychic powers and psychic weapons) and Feel No "
     "Pain (6+) in the Assault phase.", None, ["Feel No Pain (X)"]),
]
DARK_ANGELS_UPGRADES = [
    ("Ironwing Targeting Matrix", 15, "Ironwing only. Calibrated to First Legion armoured doctrine, this model adds +1 "
     "to To Hit rolls when firing at Vehicles, Dreadnoughts, Armigers, or Automata, and gains It Will Not Die (5+).",
     "da ironwing", ["It Will Not Die (X)"]),
    ("Dreadwing Stasis-Core Shroud", 20, "Dreadwing only. Fitted with forbidden dimensional baffles, enemy units "
     "declaring a Charge against this model subtract -2\" from their Charge distance rolls and reduce their Initiative "
     "characteristic by -1 (to a minimum of 1) while locked in combat with this model.", "da dreadwing", []),
    ("Deathwing Companions' Oath-Plate", 15, "Deathwing only. Adorned with bone-white heraldry and master-crafted "
     "relic plating, this model gains Fearless, Hatred (Everything) in close combat, and adds +1 to its Weapon Skill "
     "when fighting Characters or Dreadnoughts / Armigers.", "da deathwing", ["Fearless", "Hatred (X)"]),
]
EMPERORS_CHILDREN_UPGRADES = [
    ("Sonic Shrieker & Duellist Gyro-Stabilizers", 20, "Refined harmonic actuators eliminate the walker's "
     "sluggishness. The model ignores the -1\" penalty to Run and Charge rolls from Clumsy Hydraulic Actuators, gains +1 "
     "Initiative on a turn in which it charges, and forces enemy units within 6\" in the Assault phase to suffer a -1 "
     "penalty to their Weapon Skill (to a minimum of 1).", None, [])]
WHITE_SCARS_UPGRADES = [
    ("Chogorian Wind-Stride Manifolds", 20, "Stripped of excess dead-weight plating and tuned for rapid flanking "
     "strikes, the model adds +2\" to its Movement characteristic, ignores the -1\" penalty to Run and Charge rolls from "
     "Clumsy Hydraulic Actuators, and gains Outflank and Hit & Run.", None, ["Outflank", "Hit & Run"])]
NIGHT_LORDS_UPGRADES = [
    ("Terror-Vox & Flayed Trophy-Racks", 15, "Broadcasts deafening psycho-acoustic screams across the battlefield. The "
     "model gains Fear (1) and Night Vision, and adds +1 to To Wound rolls in close combat against any enemy unit that "
     "is Pinned or outnumbered by friendly models.", None, ["Fear (X)", "Night Vision"])]
BLOOD_ANGELS_UPGRADES = [
    ("Encarmine Thrust-Boosters", 20, "Auxiliary jump-stabilizer vents propel the walker forward during assaults. The "
     "model ignores the -1\" penalty to Charge distance rolls from Clumsy Hydraulic Actuators, gains Furious Charge (1), "
     "and adds +1 Attack on any turn in which it completes a Charge.", None, ["Furious Charge (X)"])]
ULTRAMARINES_UPGRADES = [
    ("Macragge Tactical Interlink", 15, "Slaved directly to the Legion's unified command grid, this model may re-roll "
     "To Hit rolls of 1 when targeting an enemy unit that has already been shot at by another friendly Ultramarines "
     "unit in the same Shooting phase, and gains Counter-Attack (1).", None, ["Counter-Attack (X)"])]
THOUSAND_SONS_UPGRADES = [
    ("Aether-Conductive Arcane Plating", 20, "Inscribed with Prosperine wards and psycho-reactive silver, the model "
     "gains Adamantium Will (5+) and a 5+ Invulnerable Save against shooting attacks. In addition, friendly Thousand "
     "Sons Psykers within 6\" may draw line of sight and measure range for Psychic Powers from this model.", None, [])]
SONS_OF_HORUS_UPGRADES = [
    ("Cthonian Reaver-Assault Pistons", 20, "Tuned for ruthless close-range spearhead decapitation strikes. The model "
     "ignores the -1\" penalty to Charge distance rolls from Clumsy Hydraulic Actuators, gains Preferred Enemy "
     "(Infantry) on any turn in which it charges, and may re-roll failed Morale tests.", None, ["Preferred Enemy (X)"])]
WORD_BEARERS_UPGRADES = [
    ("Colchisian Warp-Tainted Core", 20, "Traitor only. Empowered by dark pacts carved into the reactor housing, the "
     "model gains the Corrupted unit sub-type, Fear (1), and Feel No Pain (6+) (improving to 5+ if within 12\" of a "
     "friendly Chaplain, Diabolist, or Esoterist).", "wb traitor", ["Fear (X)", "Feel No Pain (X)"])]
RAVEN_GUARD_UPGRADES = [
    ("Deliverance Whisper-Baffles", 20, "Acoustic dampeners and infra-red baffling shroud the walker's heavy frame. The "
     "model gains Infiltrate (for Lucifer-Pattern only) or Scout (for Furibundus and Unification patterns), Move "
     "Through Cover, and Shrouded (6+) against shooting attacks made from more than 18\" away.", None,
     ["Infiltrate", "Scout", "Move Through Cover", "Shrouded (X)"])]
ALPHA_LEGION_UPGRADES = [
    ("Harrowing Ghost-Matrix", 20, "Spoofs enemy auspexes with false telemetry signatures. Enemy units firing at this "
     "model treat the range as +6\" further away than actual distance, and this model gains Scout and Counter-Attack "
     "(1).", None, ["Scout", "Counter-Attack (X)"])]
BLACKSHIELDS_UPGRADES = [
    ("Scavenged Patchwork Plate", 15, "Bolted together from salvaged armour plates of fallen foes, the model gains It "
     "Will Not Die (5+) and Hatred (Everything) in close combat.", None, ["It Will Not Die (X)", "Hatred (X)"])]
MILITIA_UPGRADES = [
    ("Agri-World / Industrial Over-Clock", 10, "Crude over-pressurized steam and promethium valves allow the walker to "
     "surge forward once per game; during one friendly Movement or Assault phase, add +2\" to its Movement or Charge "
     "roll, though it suffers 1 unsaved Wound on a D6 roll of 1 at the end of that phase.", None, []),
    ("Expeditionary Veteran Telemetry", 15, "Legacy of the Great Crusade only. Maintained by veteran Imperial Army "
     "enginseers since the earliest expansion fleets, the pilot and machine operate with practiced discipline. This "
     "model improves its Leadership characteristic to 9, may re-roll failed Morale and Pinning tests, and may re-roll "
     "To Hit rolls of 1 when firing at an enemy unit within 12\" of a friendly Militia Force Commander or Discipline "
     "Master.", "prov legacy", []),
    ("Sub-Surface Foundry Plating", 15, "Industrial Stronghold only. Forged in monumental planetary manufactoria using "
     "thick, crude slab-steel and heavy mining hydraulics. The model gains It Will Not Die (5+) and reduces the "
     "Strength of incoming Blast and Template attacks by -1 (to a minimum of 1). In addition, it treats Dangerous "
     "Terrain tests as automatically passed.", "prov industrial", ["It Will Not Die (X)"]),
    ("Ancestral Pattern Stabilizers", 20, "Survivors of the Dark Age only. Preserved intact from before Old Night with "
     "functioning gyro-balancers and refractory shielding. The model ignores the -1\" penalty to Run and Charge "
     "distance rolls from Clumsy Hydraulic Actuators, and gains a 6+ Invulnerable Save against shooting attacks (if "
     "upgraded with Dreadnought Extra Armour, its Invulnerable Save against shooting attacks improves to 5+).",
     "prov survivors", []),
    ("Forbidden Archaeo-Reactor", 20, "Armoury of Old Night only. Powered by an unshielded pre-Imperial singularity or "
     "rad-core. All Plasma, Volkite, Conversion, and Graviton weapons equipped by this model gain +1 Strength (to a "
     "maximum of 9) and Shred, but any To Hit roll of a natural 1 inflicts 1 automatic Wound on this model "
     "(Invulnerable Saves may be taken as normal).", "prov armoury", ["Shred"]),
    ("Tech-Priest Servo-Interface", 15, "Arms of the Omnissiah only. Directly linked to Mars-pattern cogitator-shrines "
     "and maintained by Enginseer Auxilia. The model improves its Ballistic Skill to 5 when firing at Vehicles, "
     "Dreadnoughts, Armigers, or Automata, and friendly models with the Battlesmith (X) special rule within 3\" add +1 "
     "to their Battlesmith rolls when repairing this model (to a maximum of 2+).", "prov omnissiah", []),
]
HEXAGRAMMATON = [(f"Hexagrammaton: {w}", 0, f"The model has the {w} Hexagrammaton Sub-type.", None, [])
                 for w in WINGS]


def imperial_upgrades(caedere):
    ups = [("High Techno-Arcana Chassis Upgrade", TECHNO_ARCANA, "mech"),
           ("Questoris Household Upgrade", QUESTORIS_UPGRADE, "mech or questoris"),
           ("XII Legion Chassis Upgrade", WORLD_EATERS_UPGRADES, "we"),
           ("IV Legion Chassis Upgrade", IRON_WARRIORS_UPGRADES, "iw"),
           ("X Legion Chassis Upgrade", IRON_HANDS_UPGRADES, "ih"),
           ("XVIII Legion Chassis Upgrade", SALAMANDERS_UPGRADES, "sal"),
           ("XIV Legion Chassis Upgrade", DEATH_GUARD_UPGRADES, "dg"),
           ("VII Legion Chassis Upgrade", IMPERIAL_FISTS_UPGRADES, "if"),
           ("VI Legion Chassis Upgrade", SPACE_WOLVES_UPGRADES, "sw"),
           ("Hexagrammaton Sub-type", HEXAGRAMMATON, "da"),
           ("I Legion Chassis Upgrade", DARK_ANGELS_UPGRADES, "da"),
           ("III Legion Chassis Upgrade", EMPERORS_CHILDREN_UPGRADES, "ec"),
           ("V Legion Chassis Upgrade", WHITE_SCARS_UPGRADES, "ws"),
           ("VIII Legion Chassis Upgrade", NIGHT_LORDS_UPGRADES, "nl"),
           ("IX Legion Chassis Upgrade", BLOOD_ANGELS_UPGRADES, "ba"),
           ("XIII Legion Chassis Upgrade", ULTRAMARINES_UPGRADES, "um"),
           ("XV Legion Chassis Upgrade", THOUSAND_SONS_UPGRADES, "ts"),
           ("XVI Legion Chassis Upgrade", SONS_OF_HORUS_UPGRADES, "soh"),
           ("XVII Legion Chassis Upgrade", WORD_BEARERS_UPGRADES, "wb traitor"),
           ("XIX Legion Chassis Upgrade", RAVEN_GUARD_UPGRADES, "rg"),
           ("XX Legion Chassis Upgrade", ALPHA_LEGION_UPGRADES, "al"),
           ("Blackshields Chassis Upgrade", BLACKSHIELDS_UPGRADES, "bs"),
           ("Imperialis Militia Chassis Upgrade", MILITIA_UPGRADES, "militia")]
    return ups, [CAEDERE] if caedere else []


COMMON = [("Relic (X)", "Relic (2)"), ("Support Squad", None)]


def imperial_specs():
    lucifer_ups, lucifer_opts = imperial_upgrades(True)
    carapace = [("Havoc Launcher", 10, "not dg"), ("Bile-Caster Mortar", 15, "dg"), ("Dreadnought Extra Armour", 15, None),
                ("Protodreadnought Helical Targeting Array", 15, None), ("Phosphex Discharger", 15, "iw")]
    return [
        {"name": "Lucifer-Pattern Protodreadnought", "model": "Lucifer-Pattern Protodreadnought", "slot": "Elites",
         "type": "Armiger", "stats": ["7", "4", "4", "7", "7", "5", "3", "3", "8", "3+"], "max": 3,
         "unit_pts": 5, "model_pts": 120, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Arc-Reactor", None), ("Clumsy Hydraulic Actuators", None)],
         "arms": [("Arm Weapon (1)", lucifer_arm()), ("Arm Weapon (2)", lucifer_arm())],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)],
         "model_options": [("Ravenspire Heavy Talons", 15, "rg")],
         "upgrades": lucifer_ups, "unit_options": lucifer_opts},
        {"name": "Furibundus-Pattern Protodreadnought", "model": "Furibundus-Pattern Protodreadnought",
         "slot": "Heavy Support", "type": "Armiger (Heavy)",
         "stats": ["6", "4", "4", "8", "8", "6", "2", "3", "8", "3+"], "max": 2, "unit_pts": 5, "model_pts": 175,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Dual-Core Reactor", None), ("Clumsy Hydraulic Actuators", None),
                            ("Siege-Breaker Chassis", None)],
         "arms": [("Arm Weapon (1)", furibundus_arm()), ("Arm Weapon (2)", furibundus_arm())],
         "carapace": [("Carapace Weapon", [("Phosphex Discharger", 15, "iw"), ("Havoc Launcher", 10, "not dg"),
                                           ("Bile-Caster Mortar", 15, "dg")], 1),
                      ("Carapace & Chassis Upgrades", [("Dreadnought Extra Armour", 15, None),
                                                       ("Protodreadnought Helical Targeting Array", 15, None)], None)],
         "upgrades": lucifer_ups, "unit_options": lucifer_opts},
        {"name": "Unification-Pattern Protodreadnought", "model": "Unification-Pattern Protodreadnought",
         "slot": "Heavy Support", "type": "Armiger (Heavy)",
         "stats": ["6", "3", "4", "7", "7", "6", "3", "2", "8", "3+"], "max": 2, "unit_pts": 5, "model_pts": 135,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": COMMON + [("Unstable Arc-Reactor", None), ("Clumsy Hydraulic Actuators", None),
                            ("Recoil-Braced Firing Stance", None)],
         "arms": [("Primary Gun Arm", unification_arm("primary")), ("Missile Pod Arm", unification_arm("missile"))],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)],
         "upgrades": imperial_upgrades(False)[0], "unit_options": []},
    ]


# ---- writing the Imperial units into the official files ------------------------------------------------------------

def catalogues():
    """(file, with Legiones Astartes (X), shows the Questoris upgrade's Troops slot)"""
    out = [(f, True, False) for f in sorted(glob.glob("2022 - LA - *.cat")) + ["Shattered Legions.cat"]]
    out += [("2022 - BG - Blackshields.cat", False, False), ("2022 - Mechanicum.cat", False, True),
            ("2022 - Questoris Household.cat", False, True), ("2022 - Imperialis Militia.cat", False, False)]
    return out


def root_link(f, unit, slot, legion, questoris):
    uid = unit.get("id")
    l = et.E("entryLink", id=mid(f, uid, "root"), name=unit.get("name"), hidden=False, collective=False, import_=False,
             targetId=uid, type="selectionEntry")
    if legion:
        el(el(l, "infoLinks"), "infoLink", id=mid(f, uid, "legion"), name=LEGIONES_ASTARTES[1], hidden=False,
           targetId=LEGIONES_ASTARTES[0], type="rule")
    if questoris:
        # the Bondsman-Rig moves the squadron to Troops and gives it the Line Sub-type
        rig = mid("imperial", "wargear", "Questoris Household Bondsman-Rig")
        troops = bc.SLOTS["Troops"][0]
        mods = el(l, "modifiers")
        for kind, value in (("remove", bc.SLOTS[slot][0][0]), ("add", troops[0]), ("set-primary", troops[0]),
                            ("add", LINE[0])):
            m = el(mods, "modifier", type=kind, field="category", value=value)
            el(el(m, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid, childId=rig,
               shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    cats = el(l, "categoryLinks")
    for cid, cname, primary in bc.SLOTS[slot][:1]:
        el(cats, "categoryLink", id=mid(f, uid, "slot"), name=cname, hidden=False, targetId=cid, primary=primary)
    el(cats, "categoryLink", id=mid(f, uid, "unit"), name=bc.UNIT_CATEGORY[1], hidden=False,
       targetId=bc.UNIT_CATEGORY[0], primary=False)
    return l


def insert_top(text, container, elements):
    """Elements at the end of the catalogue's own (top-level) container."""
    m = list(re.finditer(rf"{re.escape(text.nl)}  </{container}>", text.s))
    if len(m) != 1:
        sys.exit(f"{text.path}: {len(m)} top-level {container}")
    i = m[0].start()
    text.s = text.s[:i] + "".join(text.nl + et.xml(e, 2).replace("\n", text.nl) for e in elements) + text.s[i:]


RETIRED = ["Siege Claw", "Siege Drill", "Cyclone Missile System", "Twin-linked Gravis Bolt Cannon",
           "Twin-linked Gravis Autocannon", "Shrapnel Cannon", "Twin-linked Shrapnel Cannon", "Carapace Phosphex Discharger",
           "Heavy Dragon's Breath Flamer", "Iliastus Assault Cannon", "Twin-linked Iliastus Assault Cannon",
           "Twin-linked Plasma Repeater"]


def update():
    """Rebuild the Imperial units and their weapons and upgrades in the Mech Library from this script's data, in
    place: every entry keeps its id (saved rosters keep loading); entries new to the data are added."""
    lib = et.Text(LIBRARY)
    if "Lucifer-Pattern Protodreadnought" not in lib.s:
        sys.exit(f"{LIBRARY} has no Protodreadnoughts yet: run without --update")
    entries, rules = index([GST])
    root = ET.parse(LIBRARY).getroot()
    for e in root.findall(f"{NS}sharedSelectionEntries/{NS}selectionEntry"):   # the library's own first
        entries[norm(e.get("name"))] = e.get("id")
    for r in root.iter(f"{NS}rule"):
        rules.setdefault(norm(r.get("name")), r.get("id"))
    ctx = Ctx("imperial", entries, rules)
    imperial_weapons(ctx)
    units = [unit_entry(ctx, s) for s in imperial_specs()]
    added = replaced = 0
    fresh = []
    for name in RETIRED:                               # this script's own weapons, now the existing ones
        eid = mid("imperial", "weapon", name)
        if f'id="{eid}"' in lib.s:
            lib.remove(eid)
    for e in ctx.new + units:
        if f'id="{e.get("id")}"' in lib.s:
            start, end, indent, _ = lib.block(e.get("id"))
            lib.s = lib.s[:start] + et.xml(e, indent // 2).replace("\n", lib.nl).lstrip() + lib.s[end:]
            replaced += 1
        else:
            fresh.append(e)
            added += 1
    if fresh:
        insert_top(lib, "sharedSelectionEntries", fresh)
    lib.bump("catalogue")
    lib.save()
    print(f"{LIBRARY}: {replaced} entries rebuilt, {added} added")



def main():
    if "--update" in sys.argv:
        return update()
    lib = et.Text(LIBRARY)
    if "Lucifer-Pattern Protodreadnought" in lib.s:
        sys.exit(f"{LIBRARY} already has the Protodreadnoughts: run with --update to rebuild them")
    entries, rules = index([LIBRARY, GST])
    ctx = Ctx("imperial", entries, rules)
    imperial_weapons(ctx)
    specs = imperial_specs()
    units = [unit_entry(ctx, s) for s in specs]
    insert_top(lib, "sharedSelectionEntries", ctx.new + units)
    lib.bump("catalogue")
    lib.save()
    print(f"{LIBRARY}: {len(units)} units, {len(ctx.new)} weapons and upgrades")
    for f, legion, questoris in catalogues():
        t = et.Text(f)
        insert_top(t, "entryLinks", [root_link(f, u, s["slot"], legion, questoris) for u, s in zip(units, specs)])
        t.bump("catalogue")
        t.save()
    print(f"root entries in {len(catalogues())} catalogues")


# ---- the Leagues of Votann, at build time --------------------------------------------------------------------------

VOID_ARMOUR = EXTRA_ARMOUR
INBUILT_VOTANN = [("Magma-cutter", 5, "Magma-cutter"), ("EtaCarn plasma gun", 10, "EtaCarn plasma gun"),
                  ("Graviton Gun", 15, "Graviton Gun"), ("Volkanite disintegrator", 15, "Volkanite disintegrator")]
LEAGUE_UPGRADES = [
    ("Ancestor-Linked Cogitators", 15, "When resolving shooting attacks or close-combat attacks against an enemy unit "
     "that has at least 1 Judgement Token, this model treats that enemy unit as having +1 additional Judgement Token "
     "(to a maximum of 2). In addition, this model may re-roll failed Morale and Pinning tests.",
     "league Greater Thurian League", []),
    ("Overcharged Hydraulic Rams", 20, "This model ignores the -1\" penalty to Charge distance rolls from Heavy "
     "Hydraulic Pistons (it still suffers the -1\" penalty to Run moves), and gains Hammer of Wrath (2) and Furious "
     "Charge (1) on any turn in which it successfully completes a Charge.", "league Kronus Hegemony",
     ["Hammer of Wrath (X)", "Furious Charge (X)"]),
    ("Void-Drift Thruster Vanes", 15, "This model gains the Scout and Move Through Cover special rules, and "
     "automatically passes all Dangerous Terrain tests.", "league Trans-Hyperian Alliance",
     ["Scout", "Move Through Cover"]),
    ("Ablative Bastion-Plates", 20, "This model reduces the Strength of all incoming ranged attacks from Strength 8 or "
     "higher by -1 (to a minimum of 7) when resolving To Wound rolls, and gains Feel No Pain (6+) (or improves an "
     "existing Feel No Pain (X) roll by +1, to a maximum of 4+).", "league Urani-Surtr Regulates",
     ["Feel No Pain (X)"]),
    ("Master-Forged Weavefield Capacitors", 25, "This model gains a 5+ Invulnerable Save against shooting attacks (if "
     "upgraded with Void-Hardened Extra Armour, its Invulnerable Save against melee attacks remains 6+). In addition, "
     "all Beam, Conversion, Magma, Plasma, and Volkanite ranged weapons equipped by this model add +4\" to their "
     "maximum range.", "league Ymyr Conglomerate", []),
]


def votann_weapons(ctx):
    """The Votann weapons the rigs name that the catalogue does not have, profiled as their Imperial counterparts."""
    weapon(ctx, "Gravis concussion gauntlet", [(None, "-", "9", "2", "Melee, Brutal (2), Concussive (1)")])
    weapon(ctx, "Gravis plasma axe", [(None, "-", "10", "2", "Melee, Armourbane (Melee), Murderous Strike (5+)")])
    weapon(ctx, "Cthonian mining drill", [(None, "-", "12", "2", "Melee, Armourbane (Melee)")])
    weapon(ctx, "Heavy seismic drill", [(None, "-", "12", "2", "Melee, Armourbane (Melee)")])
    weapon(ctx, "Cthonian siege claw", [(None, "-", "10", "2", "Melee, Brutal (3)")])
    weapon(ctx, "Magma-cutter", [(None, "Template", "5", "4", "Assault 1")])
    weapon(ctx, "Heavy magma-cutter", [(None, "Template", "5", "4", "Assault 1")])
    weapon(ctx, "Heavy bolt cannon", [(None, '48"', "5", "4", "Heavy 6, Rupture (6+)")])
    weapon(ctx, "Twin-linked heavy bolt cannon", [(None, '48"', "5", "4", "Heavy 6, Rupture (6+), Twin-linked")])
    weapon(ctx, "Magna-rail cannon", [(None, '48"', "9", "2", "Heavy 2, Sunder")])
    weapon(ctx, "Twin-linked autoch-pattern bolter", [(None, '24"', "4", "5", "Rapid Fire, Rupture (6+), Twin-linked")])
    weapon(ctx, "Twin-linked L7 missile pod", [
        ("Twin-linked L7 missile pod - Frag", '48"', "4", "6", 'Heavy 1, Blast (3"), Pinning, Twin-linked'),
        ("Twin-linked L7 missile pod - Krak", '48"', "8", "3", "Heavy 1, Twin-linked")])
    weapon(ctx, "Heavy graviton bombard", [(None, '18"', "†", "4", 'Heavy 1, Large Blast (5"), Graviton Collapse, '
                                                                   "Torsion Crusher, Ignores Cover, Concussive (1), "
                                                                   "Haywire")])
    weapon(ctx, "Twin-linked volkanite disintegrator", [(None, '24"', "5", "4", "Assault 2, Breaching (6+), Shred, "
                                                                                "Twin-linked")])
    weapon(ctx, "Subterranean mole-mortar", [(None, '24"', "6", "4", 'Heavy 1, Barrage, Large Blast (5"), Pinning, '
                                                                     "One Shot")])
    wargear(ctx, "Void-Hardened Extra Armour", VOID_ARMOUR)
    wargear(ctx, "Pan Spectral Targeting Array", TARGETING, ["Skyfire", "Interceptor"])


def votann_specs():
    def gun(n, c):
        return (n, c, [n], None, None)

    ancestor = [("Gravis concussion gauntlet", 0, ["Gravis concussion gauntlet"],
                 inbuilt("Autoch-pattern combi-bolter", INBUILT_VOTANN), None),
                ("Gravis plasma axe", 10, ["Gravis plasma axe"], inbuilt("Autoch-pattern combi-bolter", INBUILT_VOTANN),
                 None),
                gun("HYLas rotary cannon", 5), gun("Heavy bolt cannon", 10), gun("L7 missile launcher", 15),
                gun("Magna-rail cannon", 15), gun("Graviton blast cannon", 15), gun("SP conversion beamer", 20),
                ("Cthonian mining drill with in-built heavy magma-cutter", 15,
                 ["Cthonian mining drill", "Heavy magma-cutter"], None, None)]
    strider = [("Cthonian siege claw", 0, ["Cthonian siege claw"],
                inbuilt("Twin-linked autoch-pattern bolter", INBUILT_VOTANN), None),
               ("Heavy seismic drill", 10, ["Heavy seismic drill"],
                inbuilt("Twin-linked autoch-pattern bolter", INBUILT_VOTANN), None),
               gun("Twin-linked HYLas rotary cannon", 10), gun("Twin-linked heavy bolt cannon", 15),
               gun("Twin-linked L7 missile pod", 25), gun("Twin-linked magna-rail cannon", 25),
               gun("Heavy graviton bombard", 25), gun("Heavy volkanite disintegrator", 25),
               gun("SP heavy conversion beamer", 20)]

    def ballistic(base):
        if base == "primary":
            costs = [("HYLas rotary cannon", 0), ("Heavy bolt cannon", 5), ("EtaCarn plasma beamer", 10),
                     ("Twin-linked volkanite disintegrator", 10), ("L7 missile launcher", 10), ("Magna-rail cannon", 15)]
        else:
            costs = [("L7 missile launcher", 0), ("HYLas rotary cannon", -10), ("Heavy bolt cannon", -5),
                     ("EtaCarn plasma beamer", 0), ("Twin-linked volkanite disintegrator", 0), ("Magna-rail cannon", 5)]
        return [gun(n, max(0, c)) for n, c in costs]        # no swap costs less than nothing

    carapace = [("MATR autocannon", 10, None), ("Void-Hardened Extra Armour", 15, None),
                ("Pan Spectral Targeting Array", 15, None)]
    common = [("Eye of the Ancestors", None), ("League (X)", None)] + COMMON
    leagues = [("League Upgrade", LEAGUE_UPGRADES, None)]
    return [
        {"name": "Ironkin Ancestor-Rig", "model": "Ironkin Ancestor-Rig", "slot": "Elites", "type": "Armiger",
         "stats": ["7", "4", "4", "7", "7", "5", "3", "3", "8", "3+"], "max": 3, "unit_pts": 5, "model_pts": 120,
         "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Darkstar-Core", None), ("Heavy Hydraulic Pistons", None)],
         "arms": [("Arm Weapon (1)", ancestor), ("Arm Weapon (2)", ancestor)],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)], "upgrades": leagues},
        {"name": "Cthonian Siege-Strider", "model": "Cthonian Siege-Strider", "slot": "Heavy Support",
         "type": "Armiger (Heavy)", "stats": ["6", "4", "4", "8", "8", "6", "2", "3", "8", "3+"], "max": 2,
         "unit_pts": 5, "model_pts": 175, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Dual-Core Reactor", None), ("Heavy Hydraulic Pistons", None),
                            ("Subterranean Siege-Chassis", None)],
         "arms": [("Arm Weapon (1)", strider), ("Arm Weapon (2)", strider)],
         "carapace": [("Carapace Weapon", [("Subterranean mole-mortar", 15, None), ("MATR autocannon", 10, None)], 1),
                      ("Carapace & Chassis Upgrades", carapace[1:], None)], "upgrades": leagues},
        {"name": "Brôkhyr Ballistic Strider", "model": "Brôkhyr Ballistic Strider", "slot": "Heavy Support",
         "type": "Armiger (Heavy)", "stats": ["6", "3", "4", "7", "7", "6", "3", "2", "8", "3+"], "max": 2,
         "unit_pts": 5, "model_pts": 135, "wargear": ["Searchlights", "Smoke Launchers"],
         "rules": common + [("Unstable Darkstar-Core", None), ("Heavy Hydraulic Pistons", None),
                            ("Recoil-Braced Firing Stance", None)],
         "arms": [("Primary Gun Arm", ballistic("primary")), ("Missile Pod Arm", ballistic("missile"))],
         "carapace": [("Carapace & Chassis Upgrades", carapace, None)], "upgrades": leagues},
    ]


def apply(b):
    """build_catalogue.py's hook for the Leagues of Votann: the rigs, their weapons and their root entries; and the
    Brôkhyr Void-Weave Projector's Reinforced Bulkhead Plating (Armour 13) on its profile."""
    from necron_fortifications import set_armour
    set_armour(b, {"Brôkhyr Void-Weave Projector": {"Reinforced Bulkhead Plating": 13}}, "Votann")
    entries = {norm(e.get("name")): e.get("id") for e in b.shared_entries.findall("selectionEntry")}
    rules = {norm(r.get("name")): r.get("id") for r in b.shared_rules.findall("rule")}
    gst_entries, gst_rules = index([GST])
    for k, v in gst_entries.items():
        entries.setdefault(k, v)
    for k, v in gst_rules.items():
        rules.setdefault(k, v)
    ctx = Ctx("votann", entries, rules)
    votann_weapons(ctx)
    specs = votann_specs()
    units = [unit_entry(ctx, s) for s in specs]
    b.shared_entries.extend(ctx.new + units)
    links = b.root.find("entryLinks")
    for u, s in zip(units, specs):
        l = el(links, "entryLink", import_=True, name=u.get("name"), hidden=False, id=mid("votann", u.get("id"), "root"),
               type="selectionEntry", targetId=u.get("id"))
        cats = el(l, "categoryLinks")
        cid, cname, _ = bc.SLOTS[s["slot"]][0]
        el(cats, "categoryLink", targetId=cid, id=mid("votann", u.get("id"), "slot"), primary=True, name=cname)
        el(cats, "categoryLink", targetId=bc.UNIT_CATEGORY[0], id=mid("votann", u.get("id"), "unit"), primary=False,
           name=bc.UNIT_CATEGORY[1])


if __name__ == "__main__":
    main()
