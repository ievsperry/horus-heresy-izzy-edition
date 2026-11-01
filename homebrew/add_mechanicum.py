#!/usr/bin/env python3
"""Add the Liber Ingenium expansion to the official Mechanicum and Questoris Household catalogues.

usage: python3 homebrew/add_mechanicum.py

The doc (homebrew/source/mechanicum.md, from the Claude Doc "Liber Ingenium for The Horus Heresy 2.0 — Homebrew
Conversion") is read by build_catalogue.py's Builder; its units move into 2022 - Mechanicum.cat, and its Divisio
Tactica: Questoris Households units into 2022 - Questoris Household.cat, as text, linked to the official entries
wherever the catalogue, its libraries or the game system already have them (see expansion_tools.py). Its special
rules and Unit Sub-types are in additional-special-rules.md and the game system (add_gst_rules.py). On top of the
units this writes:

- the Orders of Lesser Techno-Arcana every Magos Prime picks from, and the Skitariiax-Primus Order in the official
  Archmagos Prime's Higher Orders;
- the Legiones Skitarii Warlord Traits beside the official ones, for a Skitarii Warlord (Accursed Scrapcode on
  Kelbor-Hal);
- the doc's "Additional Options for Existing ... Units" on the official Mechanicum, Questoris Household and Titan
  Legions units;
- the Questoris Crusader Host Force Organisation Chart in the game system.

It refuses to run on a catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, add_cost, add_rule, child, el, norm  # noqa: E402
from expansion_tools import E, Text, any_entry, deep, link_el, mid, model_entry  # noqa: E402

MECH = "2022 - Mechanicum.cat"
QUESTORIS = "2022 - Questoris Household.cat"
TITANS = "2022 - Titan Legions.cat"
DOC = "homebrew/source/mechanicum.md"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]
C = et.NS["cat"]
TRAITOR, LOYALIST = "f9c0-0c5a-3e24-58c7", "d0b6-712f-0b12-a308"
PRIMARCH_SLOT = [("e031-3c2-e3f8-d40a", "Primarch:", True)]

# What the Builder cannot place: the Questoris rule the official catalogue names otherwise
ALLOWED = [r"rule 'Armiger and Moirax Talons'"]

SUB_TYPES = {"Light": ("bff2-ae16-74a8-8712", "Light Sub-type"), "Automata": ("d8ab-8e21-e193-63ba", "Automata Unit Type"),
             "Hover": ("3a7a-8bb7-b0d3-e2e7", "Hover Sub-type"), "Reinforced": ("9b0d-738c-10e4-4ec1", "Reinforced Sub-type")}
SUB_TYPE_RULES = ("Crawler", "Servitor", "Skitarii")
SLOT_HEADS = ("HQ", "Elites", "Troops", "Fast Attack", "Heavy Support", "Lords of War")


# ---- the doc, as the Builder reads it


def base_text():
    """The doc with the wording the Builder reads: slots as ## sections, its special rules as the army-wide rules,
    its wargear one item to a heading (armour from its table), and a few datasheet lines made plain."""
    text = open(DOC, encoding="utf-8").read()
    text = re.sub(r"^### (" + "|".join(SLOT_HEADS) + r")$", r"## \1", text, flags=re.M)
    text = text.replace("\n## Units\n", "\n")
    text = text.replace("## Mechanicum Special Rules", "## Army-wide Special Rules")
    i = text.index("## Mechanicum Wargear")
    j = text.index("\n## ", i + 5)
    out = []
    for ln in text[i:j].split("\n"):
        m = re.match(r"\*\*(.+?)\.\*\*\s*(.*)$", ln)
        if m:
            out += [f"#### {m.group(1)}", "", m.group(2)]
            continue
        m = re.match(r"\| ([^|]+?) \| (\d\+|–|-) \| (\d\+|–|-) \|$", ln)
        if m and m.group(1) != "Armour":
            sv, inv = m.group(2), m.group(3)
            t = f"A model with {m.group(1)} has a {sv} Armour Save" + (
                f" and a {inv} Invulnerable Save." if inv not in "–-" else ".")
            out += [f"#### {m.group(1)}", "", t, ""]
            continue
        if ln.startswith("|"):
            continue
        out.append(ln)
    text = text[:i] + "\n".join(out) + text[j:]
    text = text.replace("exchange either their Laspistol and/or Power Weapon each for one of",
                        "exchange their Laspistol and/or Power Weapon, each for one of")
    for w in ("Mechadendrite Hive", "Machinator Array"):  # "... with in-built Prehensile Data-spike"
        text = text.replace(f"- {w} with in-built Prehensile Data-spike", f"- {w}\n- Prehensile Dataspike")
    text = text.replace("| **An Arvus Lighter may exchange its entire Transport Capacity for:** |  |",
                        "| **An Arvus Lighter may take (in place of its Transport Capacity):** |  |")
    # the Onager's wargear is a Phosphor Cannon Array; its option names it otherwise
    text = text.replace("may exchange their Hull (Front) Mounted Twin-Linked Phosphor Cannon for",
                        "may exchange their Hull (Front) Mounted Phosphor Cannon Array for")
    text = text.replace("- Four Module Slots\n", "")
    text = text.replace("Enhanced Data Tether", "Enhanced Data-Tether")
    text = text.replace(" & Fulgurite Electoo", " and Fulgurite Electoo").replace(" & Corpuscarii Electoo",
                                                                             " and Corpuscarii Electoo")
    text = text.replace("Magma Cannon\\*", "Magma Cannon")  # the Modular rule gives them
    text = text.replace("- Co-axial Mounted Autocannon", "- Co-axial Autocannon")
    text = text.replace("and Co-axial Mounted Autocannon for one of", "and Co-axial Autocannon for one of")
    # the official Prehensile Dataspike (the Mech Library has it), so the Builder knows its profile
    text = text.replace("| Mechadendrite Hive | - | User | 3 | Melee, Reach (1), Shred |",
                        "| Mechadendrite Hive | - | User | 3 | Melee, Reach (1), Shred |\n"
                        "| Prehensile Dataspike | - | 5 | 4 | Melee, Breaching (4+), Murderous Strike (6+), Reach (2) |")
    # "Warlord: Ever-Vigilant" on a datasheet: the trait it always has, from the doc (Accursed Scrapcode) or the
    # game system (the official Mechanicum traits)
    traits = {}
    m = re.search(r"\*\*Warlord Trait: Accursed Scrapcode\.\*\* \*Kelbor-Hal only\.\* (.+)", text)
    traits["Accursed Scrapcode"] = m.group(1).strip()
    gst = ET.parse(et.GST).getroot()
    for name in ("Ever-Vigilant", "The Logic of Victory", "The Science of Slaughter"):
        p = next(x for x in gst.iter(et.NS["gst"] + "profile") if norm(x.get("name")) == norm(name)
                 and x.get("typeName") == "Warlord Trait")
        traits[name] = " ".join((c.text or "").strip() for c in p.iter(et.NS["gst"] + "characteristic"))
    k = text.index("\n## ", text.index("## Warlord Traits") + 5)
    text = text[:k] + "".join(f"\n### Warlord: {n}\n\n{t}\n" for n, t in traits.items()) + text[k:]
    # a weapon given once per range band ("Eradication Beam Cannon | Up to 12\"", "| 12-24\"" ...): one profile each
    i = text.index("## Armoury of the Mechanicum")
    j = text.index("\n## ", i + 5)
    rows = text[i:j].split("\n")
    counts = {}
    for r in rows:
        m = re.match(r"\| ([^|]+?) \| ([^|]+?) \|", r)
        if m and m.group(1) not in ("Weapon", "---"):
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    for n, r in enumerate(rows):
        m = re.match(r"\| ([^|]+?) \| ([^|]+?) \|", r)
        if m and counts.get(m.group(1), 0) > 1:
            rows[n] = r.replace(f"| {m.group(1)} |", f"| {m.group(1)} – {m.group(2).strip()} |", 1)
    text = text[:i] + "\n".join(rows) + text[j:]
    return text


def split_texts():
    """(Mechanicum text, Questoris text): the Questoris Households units under their slots, apart from the rest."""
    text = base_text()
    i = text.index("## Divisio Tactica: Questoris Households")
    j = text.index("## Divisio Tactica: The Titan Legions")
    mech = text[:i] + text[j:]
    q = text[i:j]
    units = re.split(r"\n(?=### )", q)
    troops = [u for u in units if u.startswith("### 0-3 Questoris Knight Moirax Talon")]
    lords = [u for u in units if u.startswith(("### Knight Dominus", "### Knight Maeliviax"))]
    a = text.index("## HQ")
    b = text.index("## Divisio Tactica: Questoris Households")
    lords = [u.replace("\n- Moirax Talon\n", "\n- Armiger and Moirax Talons\n") for u in lords]
    troops = [u.replace("\n- Moirax Talon\n", "\n- Armiger and Moirax Talons\n") for u in troops]
    questoris = (text[:a] + "## Troops\n\n" + "\n".join(troops) + "\n\n## Lords of War\n\n" + "\n".join(lords) + "\n\n"
                 + text[j:])
    return mech, questoris


def build(text, faction):
    first = next(l for l in text.splitlines() if l.startswith("# "))[2:].strip()
    b = bc.Builder(first, faction, text)
    root = b.build()
    bad = [p for p in b.problems if not any(re.search(a, p) for a in ALLOWED)]
    if bad:
        sys.exit("the doc does not build cleanly:\n  " + "\n  ".join(bad))
    return b, root


# ---- helpers


def cond(parent, kind, value, child_id, scope="force"):
    el(child(parent, "conditions"), "condition", type=kind, value=value, field="selections", scope=scope,
       childId=child_id, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)


def hidden_unless(e, child_id, scope="force"):
    e.set("hidden", "true")
    mod = el(child(e, "modifiers"), "modifier", type="set", field="hidden", value="false")
    cond(mod, "atLeast", 1, child_id, scope)


def add_top(cat, container, elements):
    """At the catalogue's own container (an official file may have a nested closing tag at the top level's indent)."""
    body = "".join(et.xml(e, 2).replace("\n", cat.nl) + cat.nl for e in elements)
    if f"{cat.nl}  <{container}>" not in cat.s:
        # a new container, after the ones the schema puts before it
        order = ["entryLinks", "sharedSelectionEntries", "sharedSelectionEntryGroups", "sharedRules", "sharedProfiles"]
        k = max(cat.s.rindex(f"{cat.nl}  </{c}>") for c in order[:order.index(container)]
                if f"{cat.nl}  </{c}>" in cat.s)
        k = cat.s.index(cat.nl, k + len(cat.nl)) + len(cat.nl)
        cat.s = cat.s[:k] + f"  <{container}>{cat.nl}" + body + f"  </{container}>{cat.nl}" + cat.s[k:]
        return
    i = cat.s.index(f"{cat.nl}  <{container}>") + len(cat.nl)
    j = cat.s.index(f"{cat.nl}  </{container}>", i) + len(cat.nl)
    cat.s = cat.s[:j] + body + cat.s[j:]


def sub_type_rules():
    gst = bc.load_gst_rules()
    return {t: (gst[f"{t.lower()} sub-type"][0], f"{t} Sub-type") for t in SUB_TYPE_RULES}


def transplant_into(path, text, faction, key, extra=None):
    """Build the text's units and put them in the catalogue: (cat Text, builder, entries, units, root links)."""
    et.configure(path, LIBS, DOC, faction, key)
    cat = Text(path)
    idx = et.official_index()
    b, root = build(text, faction)
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    made = tidy(b, root, key)
    hook = extra(b, root, entries) if extra else None
    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx, extra_ids=made | (hook or set()))
    roots = []
    rules = sub_type_rules()
    for ds in b.datasheets:
        u = entries[b.units[ds["name"]]]
        et.drop_unit_category(u)
        et.add_types(u, SUB_TYPES, rules)
        types = " ".join(et.unit_types(u))
        primarch = re.search(r"\bPrimarch\b", types)
        if primarch:
            et.SLOTS["Primarch"] = PRIMARCH_SLOT
        r = et.root_link(u, ds, slot="Primarch" if primarch else None)
        if "Traitor" in ds["rules"]:
            hidden_unless(r, TRAITOR)
        elif "Loyalist" in ds["rules"]:
            hidden_unless(r, LOYALIST)
        roots.append(r)
    add_top(cat, "entryLinks", roots)
    add_top(cat, "sharedSelectionEntries", units + keep_entries)
    if keep_groups:
        add_top(cat, "sharedSelectionEntryGroups", keep_groups)
    if keep_rules:
        add_top(cat, "sharedRules", keep_rules)
    return cat, b, entries, units, roots, keep_entries


COUNTS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Eight": 8}
MOUNT = r"^(?:Hull \(Front\)|Carapace|Turret|Centreline|Sponson|Pintle|Arm)(?: Mounted)? "
RULE_OPTIONS = {"master-crafted": None, "twin-linked": None, "void shield (1)": "Void Shields (1)"}


def official_profile(name):
    """A weapon profile any official catalogue has, by name (for weapons the doc names but its catalogue's
    libraries do not hold)."""
    import glob
    for f in ["2022 - Horus Heresy.gst"] + sorted(glob.glob("2022 - *.cat")):
        for p in ET.parse(f).getroot().iter():
            if p.tag.endswith("profile") and norm(p.get("name") or "") == norm(name) and p.get("typeName") == "Weapon":
                return p
    return None


def weapon_target(b, root, name, key):
    """An entry for a weapon by name: the catalogue's or its libraries' own, the doc's, or a copy of an official
    profile from elsewhere."""
    for n in (name, re.sub(r"s$", "", name)):
        e = any_entry(n, required=False)
        if e:
            return e
        wid = b.find_weapon(n)[0]
        if wid:
            return wid
        p = official_profile(n)
        if p is not None:
            e = el(root.find("sharedSelectionEntries"), "selectionEntry", type="upgrade", import_=True, name=n,
                   hidden=False, id=mid(key, "weapon", n))
            c = deep(p)
            for x in c.iter():
                x.tag = x.tag.split("}")[-1]
                x.attrib.pop("publicationId", None)
                x.attrib.pop("page", None)
                if x.get("id"):
                    x.set("id", mid(key, "weapon", n, x.get("id")))
            child(e, "profiles").append(c)
            add_cost(e, 0)
            return e.get("id")
    return None


def tidy(b, root, key):
    """What the Builder leaves empty: options that give a special rule, weapons its libraries hold or another
    official catalogue has, weapons given in pairs or with an in-built one. Returns the ids it made, which travel
    with the expansion."""
    gst = bc.load_gst_rules()
    made = set()
    for e in list(root.find("sharedSelectionEntries")):
        if any(e.find(t) is not None for t in ("profiles", "entryLinks", "infoLinks", "rules", "selectionEntries")):
            continue
        name = e.get("name")
        k = norm(name)
        if k in RULE_OPTIONS:
            base = re.sub(r"\s*\(.*\)$", "", k).rstrip("s")
            rid, rname = next((v for kk, v in gst.items() if kk.rstrip("s") == base), (None, None))
            il = el(child(e, "infoLinks"), "infoLink", name=rname, id=mid(e.get("id"), "rule"), hidden=False,
                    targetId=rid, type="rule")
            if RULE_OPTIONS[k]:
                el(el(il, "modifiers"), "modifier", type="set", field="name", value=RULE_OPTIONS[k])
            continue
        parts = re.split(r" with in-built | and ", name, flags=re.I)
        for part in parts:
            n = 1
            m = re.match(r"(One|Two|Three|Four|Eight) (.+)$", part)
            if m:
                n, part = COUNTS[m.group(1)], m.group(2)
            part = re.sub(MOUNT, "", part)
            part = re.sub(r"^Hull \(Front\) ", "", part)
            target = weapon_target(b, root, part, key)
            if target is None:
                continue
            made.add(target)
            child(e, "entryLinks").append(link_el(part, target, e.get("id"), mn=n, mx=n))
    return made


# ---- Orders of Techno-Arcana and Warlord Traits


def doc_blocks(heading_re):
    """{name: text} for each '#### <heading_re>(name)' block of the doc: its paragraphs, flavour left out."""
    text = open(DOC, encoding="utf-8").read()
    out = {}
    heading_re = heading_re.replace("(.+)", "([^\n]+)")
    for m in re.finditer(r"^#### " + heading_re + r"\n(.*?)(?=^#{2,4} |\Z)", text, re.M | re.S):
        paras = [bc.strip_md(l.strip()).replace("*", "") for l in m.group(2).split("\n")
                 if l.strip() and not re.fullmatch(r"\*[^*].*\*", l.strip())]
        out[m.group(1).strip()] = "\n".join(paras)
    return out


def lesser_orders(b, root, entries):
    """'Every Magos Prime and Magos Prime on Abeyant ... must select one Lesser Order'; 'A Magos Prime on Abeyant
    may only take Lachrimallion, Macroteknia or Ruinor'; 'each must take a different Lesser Order'."""
    orders = doc_blocks(r"Order of Lesser Techno-Arcana: (.+)")
    shared = root.find("sharedSelectionEntries")
    ids = {}
    for name, text in orders.items():
        full = f"Order of Lesser Techno-Arcana: {name}"
        e = el(shared, "selectionEntry", type="upgrade", import_=True, name=full, hidden=False, id=mid("lesser order", name))
        add_rule(e, full, text, e.get("id"))
        add_constraint(e, "max", 1, mid("lesser order", name, "army"), scope="roster", children=True)
        add_cost(e, 0)
        ids[name] = e.get("id")
    for unit, model, allowed in (("Magos Prime", "Magos Prime", list(orders)),
                                 ("Magos Prime on Abeyant", None, ["Lachrimallion", "Macroteknia", "Ruinor"])):
        u = entries[b.units[unit]]
        m = model_entry(u, model) if model else next(x for x in u.iter("selectionEntry") if x.get("type") == "model")
        g = el(child(m, "selectionEntryGroups"), "selectionEntryGroup", name="Order of Lesser Techno-Arcana", hidden=False,
               id=mid(m.get("id"), "lesser order"))
        add_constraint(g, "min", 1, mid(m.get("id"), "lesser order min"))
        add_constraint(g, "max", 1, mid(m.get("id"), "lesser order max"))
        for n in allowed:
            child(g, "entryLinks").append(link_el(f"Order of Lesser Techno-Arcana: {n}", ids[n], m.get("id"), mx=1))
    return set(ids.values())


WARLORD = "0176-56a3-d590-b103"
MECH_TRAITS = "1ebb-8e01-7d58-9d99"


def skitarii_traits(b, root, entries):
    """'If your Warlord has the Skitarii Sub-type, it may choose one of the Legiones Skitarii Warlord Traits below
    instead of a Common Trait ... or a Mechanicum Warlord Trait': a pick beside the official one on every Skitarii
    character, shown once it is the Warlord."""
    text = open(DOC, encoding="utf-8").read()
    traits = re.findall(r"\*\*Legiones Skitarii Warlord Trait: (.+?)\.\*\* \*.+?\* (.+)", text)
    groups = root.find("sharedSelectionEntryGroups")
    if groups is None:
        groups = el(root, "sharedSelectionEntryGroups")
    gid = mid("skitarii traits")
    g = el(groups, "selectionEntryGroup", name="Warlord Traits (Legiones Skitarii)", hidden=True, id=gid)
    cmax = add_constraint(g, "max", 1, mid(gid, "max"))
    mod = el(el(g, "modifiers"), "modifier", type="set", field="hidden", value="false")
    el(el(mod, "conditions"), "condition", type="greaterThan", value=0, field="selections", scope="parent",
       childId=WARLORD, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    mod = el(g.find("modifiers"), "modifier", type="set", field=cmax, value=0)
    el(el(mod, "conditions"), "condition", type="greaterThan", value=0, field="selections", scope="parent",
       childId=MECH_TRAITS, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    for name, t in traits:
        e = el(child(g, "selectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name, hidden=False,
               id=mid(gid, name))
        et.warlord_trait(e, name, t.strip(), e.get("id"))
        add_cost(e, 0)
    for ds in b.datasheets:
        u = entries[b.units[ds["name"]]]
        for m in [x for x in u.iter("selectionEntry") if x.get("type") == "model"]:
            types = " ".join(c.text or "" for c in m.iter("characteristic") if c.get("name") == "Unit Type")
            links = m.find("entryLinks")
            if "Skitarii" in types and links is not None and any(l.get("name") == "Warlord Traits" for l in links):
                el(links, "entryLink", import_=True, name=g.get("name"), hidden=False, id=mid(m.get("id"), "skitarii traits"),
                   type="selectionEntryGroup", targetId=gid)
    return set()


def skitariiax_primus(cat):
    """'Order of Higher Techno-Arcana: Skitariiax-Primus. Only an Archmagos Prime may select this Order': a pick
    beside the official Higher Orders on the Archmagos Prime (not on Abeyant), the one or the other."""
    text = doc_blocks(r"Order of Higher Techno-Arcana: (.+)")["Skitariiax-Primus"]
    name = "Order of Higher Techno-Arcana: Skitariiax-Primus"
    root = ET.fromstring(cat.s.encode("utf-8"))
    ap = next(x for x in root.find(C + "sharedSelectionEntries") if x.get("name") == "Archmagos Prime")
    owner = next(x for x in ap.iter() if x.find(C + "entryLinks") is not None
                 and any(l.get("targetId") == HIGHER_ORDERS for l in x.find(C + "entryLinks")))
    link = next(l for l in owner.find(C + "entryLinks") if l.get("targetId") == HIGHER_ORDERS)
    g = E("selectionEntryGroup", id=mid("skitariiax"), name="Order of Higher Techno-Arcana (Liber Ingenium)",
          hidden=False, collective=False, import_=True)
    cmax = add_constraint(g, "max", 1, mid("skitariiax", "max"))
    mod = el(el(g, "modifiers"), "modifier", type="set", field="hidden", value="true")
    cond(mod, "atLeast", 1, HIGHER_ORDERS, scope=owner.get("id"))
    e = el(el(g, "selectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name, hidden=False,
           id=mid("skitariiax", "order"))
    add_rule(e, name, text, e.get("id"))
    add_cost(e, 0)
    cat.add(owner.get("id"), "selectionEntryGroups", [g])
    # and the official pick hidden once this one is taken
    hide = E("modifier", type="set", field="hidden", value="true")
    cond(hide, "atLeast", 1, e.get("id"), scope=owner.get("id"))
    cat.add(link.get("id"), "modifiers", [hide])
    return cmax


HIGHER_ORDERS = "c36b-a6a2-9cb2-b090"


# ---- "Additional Options for Existing ... Units"


def option_rows(heading):
    """(unit, option, cost) rows of the first table after a heading of the doc."""
    text = open(DOC, encoding="utf-8").read()
    i = text.index(heading)
    lines = text[i:].split("\n")
    k = next(n for n, l in enumerate(lines) if l.startswith("| Unit |"))
    rows = []
    for l in lines[k + 2:]:
        if not l.startswith("|"):
            break
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        rows.append((re.sub(r"^0-\d+ ", "", cells[0]), cells[1], cells[2]))
    return rows


OPTION_TABLES = {
    MECH: ["#### Additional Options for Existing HQ Units", "#### Additional Options for Existing Elites Units",
           "#### Additional Options for Existing Fast Attack Units",
           "#### Additional Options for Existing Heavy Support Units"],
    QUESTORIS: ["### Additional Options for Existing Questoris Households Units"],
    TITANS: ["## Divisio Tactica: The Titan Legions"],
}


ARTICLE = r"^(?:one or both|either|both|any|two|the|one|an?) "


def bare(name):
    """A weapon name without its mount, article or count: 'Arm Mounted Reaper Chainsword' -> 'reaper chainsword'."""
    n = name.strip()
    for _ in range(3):
        n = re.sub(ARTICLE, "", n, flags=re.I)
        n = re.sub(MOUNT, "", n, flags=re.I)
    return bc.singular_name(norm(n).replace("-", " "))


def option_items(option):
    """(replaced, [items]) for a row: replaced is None for an option that adds."""
    o = re.sub(r"\s*\(\*.*?\*.*?\)", "", option).strip()
    m = re.match(r"(?:Exchange|Replace) (.+?) (?:for|with) (.+)$", o, re.I)
    if m:
        items = [re.sub(ARTICLE, "", x.strip(), flags=re.I) for x in re.split(r", | or ", re.sub(r"^an? ", "", m.group(2)))]
        if len(items) > 1 and re.match(MOUNT, m.group(2).split(" ", 2)[0] + " Mounted "):
            mount = re.match(r"((?:\w+ )?(?:\w+) Mounted )", m.group(2))
            items = [items[0]] + [(mount.group(1) if mount else "") + x for x in items[1:]]
        return m.group(1), items
    o = re.sub(r"^(?:The \w+|Any \w+|The squadron|Any model) may (?:instead )?take ", "", o, flags=re.I)
    o = re.sub(r"^Deployment option: |, if .+$", "", o)
    m = re.match(r"If .+?, upgrade one to an? (.+)$", o)
    if m:
        o = m.group(1)
    return None, [re.sub(ARTICLE, "", o, flags=re.I)]


def cost_of(text):
    m = re.search(r"\+(\d+) points?", text)
    return (int(m.group(1)) if m else 0), "per model" in text


def resolve(name, sources):
    """A shared entry by name in these files: as written, without its mount, singular."""
    tries = {norm(name), norm(re.sub(MOUNT, "", name)), bare(name)}
    for f in sources:
        if f not in _SHARED:
            ns = et.NS["gst"] if f.endswith(".gst") else C
            _SHARED[f] = [(norm(e.get("name")), bare(e.get("name")), e.get("id")) for e in
                          ET.parse(f).getroot().findall(f"{ns}sharedSelectionEntries/{ns}selectionEntry")]
        for n, b_, i in _SHARED[f]:
            if n in tries or b_ in tries:
                return i
    return None


_SHARED = {}


_ANYWHERE = {}


def anywhere(name, doc_entries):
    """An entry with profiles or rules by name: the doc's (as the Builder made it), then any official one, nested or
    not (for weapons a catalogue holds inline)."""
    import glob
    k = bare(name)
    if k.startswith("twin linked ") and not anywhere_has(k, doc_entries):
        k = k[len("twin linked "):]
    for e in doc_entries:
        if bare(e.get("name")) == k and (e.find("profiles") is not None or e.find("rules") is not None):
            return e
    if not _ANYWHERE:
        for f in ["2022 - Horus Heresy.gst"] + sorted(glob.glob("2022 - *.cat")):
            for e in ET.parse(f).getroot().iter():
                if e.tag.endswith("}selectionEntry") and any(c.tag.endswith(("}profiles", "}rules")) for c in e):
                    _ANYWHERE.setdefault(bare(e.get("name")), e)
    return _ANYWHERE.get(k)


def anywhere_has(k, doc_entries):
    anywhere("", doc_entries)
    return k in _ANYWHERE or any(bare(e.get("name")) == k for e in doc_entries)


def plain(e, key):
    """A copy of an official element without its namespace, with new ids."""
    c = deep(e)
    for x in c.iter():
        x.tag = x.tag.split("}")[-1]
        for a in ("publicationId", "page"):
            x.attrib.pop(a, None)
    return c


def clone(e, name, key):
    """A copy of an entry's profiles and rules as a new upgrade entry (its rule links to the game system's rules)."""
    gst = bc.load_gst_rules()
    out = E("selectionEntry", id=mid(key, name), name=name, hidden=False, collective=False, import_=True,
            type="upgrade")
    for part in ("profiles", "rules"):
        src = next((c for c in e if c.tag.split("}")[-1] == part), None)
        if src is None:
            continue
        c = deep(src)
        for x in c.iter():
            x.tag = x.tag.split("}")[-1]
            for a in ("publicationId", "page"):
                x.attrib.pop(a, None)
            if x.get("id"):
                x.set("id", mid(key, name, x.get("id")))
        out.append(c)
    if re.match(r"twin-linked ", norm(name)) and not re.match(r"twin-linked ", norm(e.get("name") or "")):
        rid, rname = gst["twin-linked"]
        el(child(out, "infoLinks"), "infoLink", name=rname, id=mid(key, name, "twin"), hidden=False, targetId=rid,
           type="rule")
    links = next((c for c in e if c.tag.split("}")[-1] == "infoLinks"), None)
    for il in (links if links is not None else []):
        rid = gst.get(norm(il.get("name") or ""), (None,))[0]
        if rid:
            el(child(out, "infoLinks"), "infoLink", name=il.get("name"), id=mid(key, name, "rule", il.get("name")),
               hidden=False, targetId=rid, type="rule")
    return out


def option_element(item, label, sources, doc_entries, key, pts, per, mx, text):
    """The element an option gives: a link to a shared entry, a copy of the doc's or an official inline entry, a
    pair or set of them, or (where nothing defines it) an entry with the option's text."""
    parts = re.split(r" and (?![^(]*\))", item)
    shells = re.match(r"(.+) \(with (\w+) and (\w+) Shells\)$", item)
    if shells:
        parts = [f"{shells.group(1)} - {shells.group(2)}", f"{shells.group(1)} - {shells.group(3)}"]
    m = re.match(r"(Two|Both) (.+)$", item, re.I)
    if len(parts) == 1 and not m:
        target = resolve(item, sources)
        if target:
            return link_el(label, target, key, mx=mx, pts=pts, per_model_of=per)
        src = anywhere(item, doc_entries)
        if src is not None:
            e = clone(src, label, key)
        else:
            e = E("selectionEntry", id=mid(key, label), name=label, hidden=False, collective=False, import_=True,
                  type="upgrade")
            add_rule(e, label, text, e.get("id"))
            e.set("text", "1")
    else:
        e = E("selectionEntry", id=mid(key, label), name=label, hidden=False, collective=False, import_=True,
              type="upgrade")
        n = 2 if m else 1
        for part in ([m.group(2)] if m else parts):
            part = bc.singular_name(part) if n > 1 else part
            target = resolve(part, sources)
            if target:
                child(e, "entryLinks").append(link_el(part, target, mid(key, label), mn=n, mx=n))
                continue
            src = anywhere(part, doc_entries)
            if src is None:
                return None
            c = clone(src, part, mid(key, label))
            add_constraint(c, "min", n, mid(key, label, part, "min"))
            add_constraint(c, "max", n, mid(key, label, part, "max"))
            add_cost(c, 0)
            child(e, "selectionEntries").append(c)
    if mx:
        add_constraint(e, "max", mx, mid(key, label, "max"))
    if per:
        add_cost(e, 0)
        mod = el(el(e, "modifiers"), "modifier", type="increment", field=bc.PTS, value=pts)
        el(el(mod, "repeats"), "repeat", field="selections", scope=per, value=1, percentValue=False, shared=True,
           includeChildSelections=False, includeChildForces=False, childId="model", repeats=1, roundUp=False)
    else:
        add_cost(e, pts)
    return e


def exchange_groups(unit, what):
    """The unit's picks (selectionEntryGroups) that hold the replaced weapon: each of them for 'either' or 'one or
    both' of a pair on two arms, the first otherwise."""
    want = [bare(w) for w in re.split(r" and ", what)]
    out = []
    for g in unit.iter(C + "selectionEntryGroup"):
        names = [bare(x.get("name")) for x in list(g.findall(C + "selectionEntries/" + C + "selectionEntry"))
                 + list(g.findall(C + "entryLinks/" + C + "entryLink"))]
        if all(any(w == n or w in n for n in names) for w in want):
            out.append(g)
    return out if re.match(r"(either|one or both) ", what, re.I) else out[:1]


def fixed_weapon(unit, what):
    """(holder, entry): a weapon the unit always has, not in a pick, that the option replaces."""
    k = bare(what)
    for holder in [unit] + [m for m in unit.iter(C + "selectionEntry") if m.get("type") == "model"]:
        for e in holder.findall(C + "selectionEntries/" + C + "selectionEntry"):
            if e.get("type") == "upgrade" and bare(e.get("name")) == k:
                return holder, e
    return None, None


def wrap_fixed(holder, e, ops, f):
    """The fixed weapon as the default of a new pick of its own, so options can replace it."""
    n = next((int(c.get("value")) for c in e.iter(C + "constraint") if c.get("type") == "min"), 1)
    g = E("selectionEntryGroup", id=mid(e.get("id"), "exchange"), name=e.get("name"), hidden=False, collective=False,
          import_=True, defaultSelectionEntryId=e.get("id"))
    add_constraint(g, "min", n, mid(e.get("id"), "exchange min"))
    add_constraint(g, "max", n, mid(e.get("id"), "exchange max"))
    w = plain(e, None)
    cons = w.find("constraints")
    if cons is not None:
        for c in list(cons):
            if c.get("type") == "min":
                cons.remove(c)
    child(g, "selectionEntries").append(w)
    ops.setdefault(f, []).append((e.get("id"), "REMOVE", None))
    ops.setdefault(f, []).append((holder.get("id"), "selectionEntryGroups", [g]))
    return g


def unit_def(name, files):
    for f in files:
        r = ET.parse(f).getroot()
        for e in r.find(C + "sharedSelectionEntries"):
            if norm(e.get("name")) == norm(name) and e.get("type") in ("unit", "model"):
                return f, e
    return None, None


def plan_options(rows, files, doc_entries, notes, special=None):
    """{file: [(element id, container, [elements])]} for the rows, on the official units in files. Exchanges join
    the pick that holds the weapon they replace; other options go in a 'Liber Ingenium options' pick."""
    ops = {}
    groups = {}
    wrapped = {}

    def liber(gk, u, ops):
        if gk not in groups:
            groups[gk] = E("selectionEntryGroup", id=mid(u.get("id"), "liber ingenium"), name="Liber Ingenium options",
                           hidden=False, collective=False, import_=True)
            ops.setdefault(gk[0], []).append((u.get("id"), "selectionEntryGroups", [groups[gk]]))
        return groups[gk]

    for unit, option, cost in rows:
        f, u = unit_def(unit, files)
        if u is None:
            notes.append(f"no official unit '{unit}' for '{option}'")
            continue
        gk = (f, u.get("id"))
        if special and (unit, option) in special:
            for eid, cont, els in special[(unit, option)](u):
                if eid == "LIBER":
                    child(liber(gk, u, ops), cont).extend(els)
                else:
                    ops.setdefault(f, []).append((eid, cont, els))
            continue
        sources = [f, et.GST] if "Library" in f else [f] + LIBS + [et.GST]
        pts, each = cost_of(cost)
        replaced, items = option_items(option)
        gs = exchange_groups(u, replaced) if replaced else []
        if replaced and not gs:
            holder, fx = fixed_weapon(u, replaced)
            if fx is not None:
                if fx.get("id") not in wrapped:
                    wrapped[fx.get("id")] = wrap_fixed(holder, fx, ops, f)
                gs = [wrapped[fx.get("id")]]
        per = u.get("id") if each else None
        for item in items:
            text = f"{option} ({cost})."
            if gs:
                for g in gs:
                    key = mid(u.get("id"), "li option", option, item, g.get("id"))
                    e = option_element(item, item, sources, doc_entries, key, pts, per, None, text)
                    if e is None:
                        notes.append(f"{unit}: '{item}' ({option}) could not be made")
                        continue
                    if e.get("text"):
                        e.attrib.pop("text")
                        notes.append(f"{unit}: '{item}' is defined nowhere; added with the option's text")
                    cont = "entryLinks" if e.tag == "entryLink" else "selectionEntries"
                    if g.get("id") in {w.get("id") for w in wrapped.values()}:
                        child(g, cont).append(e)
                    else:
                        ops.setdefault(f, []).append((g.get("id"), cont, [e]))
                continue
            key = mid(u.get("id"), "li option", option, item)
            label = f"{item} (in place of {re.sub(ARTICLE, '', replaced, flags=re.I)})" if replaced else item
            e = option_element(item, label, sources, doc_entries, key, pts, per, 1, text)
            if e is None:
                notes.append(f"{unit}: '{item}' ({option}) could not be made")
                continue
            child(liber(gk, u, ops), "entryLinks" if e.tag == "entryLink" else "selectionEntries").append(e)
            if e.get("text"):
                e.attrib.pop("text")
                notes.append(f"{unit}: '{item}' is defined nowhere; added with the option's text")
            if replaced:
                notes.append(f"{unit}: no pick holds '{replaced}'; '{item}' is an extra pick marked 'in place of'")
    return ops


DUAL_BLADES = ("Knight Questoris", "Exchange an Arm Mounted Reaper Chainsword and Arm Mounted Rapid Fire Battle "
               "Cannon for Arm Mounted Dual Vulcanis Blades")


def special_rows(doc_entries=()):
    """Rows that are not a weapon or wargear pick."""
    def transports(u):
        g = next(x for x in u.iter(C + "selectionEntryGroup") if x.get("name") == "Dedicated Transport")
        ids = {e.get("name"): e.get("id") for e in ET.parse(MECH).getroot().find(C + "sharedSelectionEntries")}
        p = link_el("Porphetian Armoured Carrier", ids["Porphetian Armoured Carrier"], mid(u.get("id"), "li transport"),
                    mx=1)
        et.models_over(p, u.get("id"), 8)
        s_ = link_el("Skorpius Dunerider", ids["Skorpius Dunerider"], mid(u.get("id"), "li transport"), mx=1)
        return [(g.get("id"), "entryLinks", [p, s_])]

    def combi(u):
        g = E("x")
        l = el(child(g, "entryLinks"), "entryLink", import_=True, name="Pintle Mounted Combi-Weapon", hidden=False,
               id=mid(u.get("id"), "li combi link"), type="selectionEntryGroup", targetId="9b4b-07a4-31bc-fc16")
        add_constraint(l, "max", 1, mid(u.get("id"), "li combi max"))
        add_cost(l, 10)
        return [("LIBER", "entryLinks", [l])]

    def dual_blades(u):
        """'Exchange an Arm Mounted Reaper Chainsword and Arm Mounted Rapid Fire Battle Cannon for Arm Mounted Dual
        Vulcanis Blades': the blades take the battle cannon's arm, and the chainsword's arm pick then holds nothing."""
        groups = list(u.iter(C + "selectionEntryGroup"))
        cannon = next(g for g in groups if "Rapid-Fire Battle Cannon" in g.get("name"))
        sword = next(g for g in groups if "Reaper Chainsword" in g.get("name"))
        name = "Arm Mounted Dual Vulcanis Blades"
        e = option_element(name, name, [LIBRARY, et.GST], doc_entries, mid(u.get("id"), "li option", DUAL_BLADES[1]),
                           15, None, None, f"{DUAL_BLADES[1]} (+15 points).")
        mods = []
        for c in sword.findall(C + "constraints/" + C + "constraint"):
            m = E("modifier", type="set", field=c.get("id"), value=0)
            cond(m, "atLeast", 1, e.get("id"), scope=u.get("id"))
            mods.append(m)
        m = E("modifier", type="set", field="hidden", value="true")
        cond(m, "atLeast", 1, e.get("id"), scope=u.get("id"))
        mods.append(m)
        return [(cannon.get("id"), "selectionEntries" if e.tag == "selectionEntry" else "entryLinks", [e]),
                (sword.get("id"), "modifiers", mods)]

    return {
        DUAL_BLADES: dual_blades,
        ("Tech-Priest Auxilia", next(o for u, o, c in option_rows("#### Additional Options for Existing Elites Units")
                                     if u == "Tech-Priest Auxilia")): transports,
        ("Ordo Reductor Minotaur Battery", "Any Minotaur may take one Pintle Mounted Combi-Weapon (any type)"): combi,
    }


def crusader_host():
    """'Questoris Crusader Host': 1-10 Lords of War and up to two Troops for every Lord of War, as the Primary
    Detachment; its Lords of War do not count towards the 25% limit (so it has no 25% category)."""
    fid = "c1a5-7e2b-4d0f-9a61"
    f = E("forceEntry", id=fid, name="1. Questoris Crusader Host Force Organisation Chart", hidden=False)
    cats = el(f, "categoryLinks")
    a = el(cats, "categoryLink", id=bc.make_id(fid, "allegiance"), name="Allegiance:", hidden=False,
           targetId="e90d-e5a8-f42d-da84", primary=False)
    add_constraint(a, "min", 2, bc.make_id(fid, "allegiance min"), children=True)
    add_constraint(a, "max", 2, bc.make_id(fid, "allegiance max"), children=True)
    low = el(cats, "categoryLink", id=bc.make_id(fid, "low"), name="Lords of War:", hidden=False,
             targetId="c658-dc6b-727b-c488", primary=False)
    add_constraint(low, "min", 1, bc.make_id(fid, "low min"), scope="force", children=True)
    add_constraint(low, "max", 10, bc.make_id(fid, "low max"), scope="force", children=True)
    tr = el(cats, "categoryLink", id=bc.make_id(fid, "troops"), name="Troops:", hidden=False,
            targetId="9b5d-fac7-799b-d7e7", primary=False)
    tmax = add_constraint(tr, "max", 0, bc.make_id(fid, "troops max"), scope="force", children=True)
    mod = el(el(tr, "modifiers"), "modifier", type="increment", field=tmax, value=2)
    el(el(mod, "repeats"), "repeat", field="selections", scope="force", value=1, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="c658-dc6b-727b-c488", repeats=1, roundUp=False)
    el(cats, "categoryLink", id=bc.make_id(fid, "unit"), name="Unit:", hidden=False, targetId="36c3-e85e-97cc-c503",
       primary=False)
    el(el(f, "constraints"), "constraint", type="max", value=1, field="forces", scope="roster", shared=True,
       id=bc.make_id(fid, "one"), percentValue=False, includeChildSelections=True, includeChildForces=False)
    return f


def add_force(gst, f, after="58a7-8821-3cd9-c73"):
    """The force chart after another in the game system."""
    if f.get("id") in gst.s:
        return
    _, end, indent, _ = gst.block(after)
    k = gst.s.index("\n", end) + 1
    gst.s = gst.s[:k] + et.xml(f, indent // 2).replace("\n", gst.nl) + gst.nl + gst.s[k:]


def limit(cat, name, n, key):
    """'0-N': at most N of the unit in a Detachment."""
    root = ET.fromstring(cat.s.encode("utf-8"))
    for l in root.find(C + "entryLinks"):
        if l.get("name") == name:
            c = E("constraint", type="max", value=n, field="selections", scope="force", shared=True,
                  id=mid(key, name, "0-n"), percentValue=False, includeChildSelections=True, includeChildForces=False)
            cat.add(l.get("id"), "constraints", [c])


def apply_ops(ops):
    for f, items in ops.items():
        t = Text(f)
        for eid, cont, els in items:
            if cont == "REMOVE":
                t.remove(eid)
            else:
                t.add(eid, cont, els)
        t.save()


def main():
    for path, marker in ((MECH, "Magos Prime"), (QUESTORIS, "Knight Dominus")):
        if f'name="{marker}"' in open(path, encoding="utf-8").read():
            sys.exit(f"{path} already has the Liber Ingenium expansion")
    mech_text, questoris_text = split_texts()
    doc_entries = []

    def orders_and_traits(b, root, entries):
        doc_entries.extend(root.find("sharedSelectionEntries"))
        return lesser_orders(b, root, entries) | skitarii_traits(b, root, entries)

    cat, b, entries, units, roots, keep = transplant_into(MECH, mech_text, "Mechanicum", "liber ingenium",
                                                          orders_and_traits)
    skitariiax_primus(cat)
    limit(cat, "Cydonian Sisterhood Clade", 1, "liber ingenium")
    cat.save()
    print(f"{MECH}: {len(units)} units, {len(keep)} entries")

    def keep_docs(b, root, entries):
        doc_entries.extend(root.find("sharedSelectionEntries"))
        return set()

    cat, b, entries, units, roots, keep = transplant_into(QUESTORIS, questoris_text, "Questoris Household",
                                                          "liber ingenium questoris", keep_docs)
    limit(cat, "Questoris Knight Moirax Talon", 3, "liber ingenium questoris")
    cat.save()
    print(f"{QUESTORIS}: {len(units)} units, {len(keep)} entries")

    # the doc's "Additional Options for Existing ... Units", on the official units (some in the Mech Library)
    notes = []
    for path, heads in OPTION_TABLES.items():
        et.configure(path, LIBS, DOC, "", "liber ingenium options")
        rows = [r for h in heads for r in option_rows(h)]
        apply_ops(plan_options(rows, [path, LIBRARY], doc_entries, notes, special_rows(doc_entries)))
    for n in notes:
        print("  note:", n)

    gst = Text(et.GST)
    add_force(gst, crusader_host())
    gst.save()
    for path in (MECH, QUESTORIS, LIBRARY):
        t = Text(path)
        t.s = t.s.replace("\\*", "*")  # the doc's escaped asterisks ("Gravitic Implosion\*")
        t.s = re.sub(r"<description>\*[^*<]+\* ", "<description>", t.s)  # a doc rule's flavour line
        t.save()


LIBRARY = "2022 - Mech Library.cat"


if __name__ == "__main__":
    main()
