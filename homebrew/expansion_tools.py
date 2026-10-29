"""Shared machinery for adding a homebrew expansion doc to an official catalogue (add_sisters_of_silence.py,
add_solar_auxilia.py).

build_catalogue.py's Builder reads the doc's datasheets into unit entries; transplant() takes those units and
everything of the Builder's they use, links them to the official entries wherever the catalogue, the libraries it
imports or the game system already have them, and Text writes them into the official file as text so it keeps its
own formatting. configure() names the catalogue, its libraries, the doc, the faction and the prefix new ids are made
from (ids stay the same from run to run)."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
from build_catalogue import add_constraint, add_cost, child, el, make_id, norm  # noqa: E402

GST = "2022 - Horus Heresy.gst"
NS = {"cat": "{http://www.battlescribe.net/schema/catalogueSchema}",
      "gst": "{http://www.battlescribe.net/schema/gameSystemSchema}"}
MORTALIS = "7b69-bf2f-4547-e83b"  # official units a Zone Mortalis force may not take are hidden by this
UNIT = ("36c3-e85e-97cc-c503", "Unit:")
SLOTS = {"HQ": [("4f85-eb33-30c9-8f51", "HQ:", True), ("f823-8c1d-6a87-26a1", "Compulsory HQ:", False)],
         "Elites": [("7aee-565f-b0ae-294e", "Elites:", True)],
         "Troops": [("9b5d-fac7-799b-d7e7", "Troops:", True), ("8f42-a824-fb5f-8fea", "Compulsory Troops:", False)],
         "Fast Attack": [("20ef-cd01-a8da-376e", "Fast Attack:", True)],
         "Heavy Support": [("7031-469a-1aeb-eab0", "Heavy Support:", True)],
         "Lords of War": [("c658-dc6b-727b-c488", "Lords of War:", True),
                          ("2eaf-32d6-9d1d-d906", "LoW & Primarchs (25% Limit)", False)]}
WARLORD_TRAIT = ("a0e6-a7b4-d55d-85b8", "Warlord Trait", "c68e-2cda-b67b-baca")


class Config:
    remap = {}  # the Builder's ids that transplant() linked to official entries instead
    cat = None
    libs = []
    doc = None
    faction = None
    prefix = None


cfg = Config()


def configure(cat, libs, doc, faction, prefix):
    cfg.cat, cfg.libs, cfg.doc, cfg.faction, cfg.prefix = cat, libs, doc, faction, prefix


def mid(*parts):
    return make_id(cfg.prefix, *parts)


def sources():
    return [cfg.cat] + cfg.libs + [GST]


def official_index():
    """{kind: {norm name: id}} for what the catalogue can link: its own entries and rules, its libraries', the game
    system's. Earlier sources win."""
    idx = {"entry": {}, "rule": {}}
    for f in sources():
        root = ET.parse(f).getroot()
        ns = NS["gst"] if f == GST else NS["cat"]
        for e in root.findall(f"{ns}sharedSelectionEntries/{ns}selectionEntry"):
            if e.find(f"{ns}profiles") is not None:
                idx["entry"].setdefault(norm(e.get("name")), e.get("id"))
        for r in root.iter(f"{ns}rule"):
            idx["rule"].setdefault(norm(r.get("name")), r.get("id"))
    return idx


def refs(e):
    """Ids an element points at."""
    out = set()
    for x in e.iter():
        for a in ("targetId", "childId"):
            if x.get(a):
                out.add(x.get(a))
    return out


def build(text=None):
    text = text or open(cfg.doc, encoding="utf-8").read()
    first = next(l for l in text.splitlines() if l.startswith("# "))[2:].strip()
    b = bc.Builder(first, cfg.faction, text)
    root = b.build()
    if b.problems:
        sys.exit("the doc does not build cleanly:\n  " + "\n  ".join(b.problems))
    return b, root


def rename(root, entry, name):
    """Rename an entry, its profiles and the links that show it."""
    old = entry.get("name")
    entry.set("name", name)
    for p in entry.iter("profile"):
        if p.get("name") == old:
            p.set("name", name)
    for l in root.iter("entryLink"):
        if l.get("targetId") == entry.get("id"):
            l.set("name", name)


def transplant(b, root, idx, units=None, extra_ids=()):
    """The units (the doc's, unless given) and everything of the Builder's they use, linked to the official entries
    where those exist: (units, entries, groups, rules) to add. extra_ids are Builder entries the official units will
    link to; cfg.remap says which of them are official entries now."""
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    shared_groups = root.find("sharedSelectionEntryGroups")
    groups = {g.get("id"): g for g in (shared_groups if shared_groups is not None else [])}
    rules = {r.get("id"): r for r in root.find("sharedRules")}
    units = units if units is not None else [entries[b.units[ds["name"]]] for ds in b.datasheets]
    todo, used = list(units), set(i for i in extra_ids if i in entries)
    todo += [entries[i] for i in used]
    while todo:
        for r in refs(todo.pop()):
            if r in used:
                continue
            target = next((m[r] for m in (entries, groups, rules) if r in m), None)
            if target is not None:
                used.add(r)
                todo.append(target)
    remap = {}
    for r in used:
        if r in entries and entries[r].find("profiles") is not None and entries[r].get("type") == "upgrade":
            name = norm(entries[r].get("name"))
            if name in idx["entry"]:
                remap[r] = idx["entry"][name]
        elif r in rules:
            name = norm(rules[r].get("name"))
            if name in idx["rule"]:
                remap[r] = idx["rule"][name]
    cfg.remap = remap
    keep_entries = [entries[r] for r in entries if r in used and r not in remap and entries[r] not in units]
    keep_groups = [groups[r] for r in groups if r in used]
    keep_rules = [rules[r] for r in rules if r in used and r not in remap]
    for e in units + keep_entries + keep_groups + keep_rules:
        for x in e.iter():
            x.attrib.pop("publicationId", None)
            for a in ("targetId", "childId"):
                if x.get(a) in remap:
                    x.set(a, remap[x.get(a)])
    return units, keep_entries, keep_groups, keep_rules


def unit_types(unit):
    """Every model's Unit Type text in a unit."""
    return [c.text or "" for c in unit.iter("characteristic") if c.get("name") == "Unit Type"]


def drop_unit_category(unit):
    """The root entry carries Unit:, as in the official catalogues."""
    cats = child(unit, "categoryLinks")
    for c in list(cats):
        if c.get("targetId") == UNIT[0]:
            cats.remove(c)
    return cats


def add_types(unit, sub_types, sub_type_rules=None):
    """Sub-type categories (and rules) the official units carry, from the models' Unit Types."""
    uid = unit.get("id")
    cats = child(unit, "categoryLinks")
    types = " ".join(unit_types(unit))
    for word, (cat, name) in sub_types.items():
        if re.search(r"\b" + word + r"\b", types) and not any(c.get("targetId") == cat for c in cats):
            el(cats, "categoryLink", targetId=cat, id=mid(uid, "type", word), primary=False, name=name)
    for word, (rid, name) in (sub_type_rules or {}).items():
        if re.search(r"\b" + word + r"\b", types) and not any(i.get("targetId") == rid for i in unit.iter("infoLink")):
            el(child(unit, "infoLinks"), "infoLink", name=name, id=mid(uid, "type rule", word), hidden=False,
               targetId=rid, type="rule")


def root_link(unit, ds, slot=None, name=None, key="root"):
    """The catalogue's entry for a unit: its slot, Unit:, and the official limits."""
    uid = unit.get("id")
    e = ET.Element("entryLink", {"id": mid(uid, key), "name": name or unit.get("name"), "hidden": "false",
                                 "collective": "false", "import": "false", "targetId": uid, "type": "selectionEntry"})
    types = " ".join(unit_types(unit))
    if re.search(r"\b(Vehicle|Dreadnought|Automata|Knight|Titan)\b", types):
        mod = el(el(e, "modifiers"), "modifier", type="set", field="hidden", value="true")
        el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope="force",
           childId=MORTALIS, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    if ds is not None and ("Unique" in types or ds.get("army_limit")):  # "0-1 per army"
        add_constraint(e, "max", ds.get("army_limit") or 1, mid(uid, "army") if key == "root" else mid(uid, key, "army"),
                       scope="roster", children=True)
    cats = el(e, "categoryLinks")
    el(cats, "categoryLink", id=mid(uid, key, "unit"), name=UNIT[1], hidden=False, targetId=UNIT[0], primary=False)
    for cat, cname, primary in SLOTS[slot or ds["slot"]]:
        el(cats, "categoryLink", id=mid(uid, key, cname), name=cname, hidden=False, targetId=cat, primary=primary)
    return e


def models_over(group_or_link, uid, n, key=None):
    """Hidden while the unit has more than n models."""
    mod = el(child(group_or_link, "modifiers"), "modifier", type="set", field="hidden", value="true")
    el(el(mod, "conditions"), "condition", type="greaterThan", value=n, field="selections", scope=uid, childId="model",
       shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)


def transport_group(unit, choices, key, name="Dedicated Transport"):
    """'Dedicated Transport: ...': one of the given transports, each hidden past the size it allows, and none while
    the unit has the wargear that rules it out: [(name, target, most models or None, barred by entry id or None)]."""
    uid = unit.get("id")
    gs = child(unit, "selectionEntryGroups")
    for g in list(gs):
        if g.get("name") == "Dedicated Transport":
            gs.remove(g)  # the Builder's, which knew only the doc's own transports
    g = el(gs, "selectionEntryGroup", name=name, hidden=False, id=mid(uid, key))
    add_constraint(g, "max", 1, mid(uid, key, "max"))
    for tname, target, most, barred in choices:
        link = el(child(g, "entryLinks"), "entryLink", import_=True, name=tname, hidden=False, id=mid(uid, key, tname),
                  type="selectionEntry", targetId=target)
        add_constraint(link, "max", 1, mid(uid, key, tname, "max"))
        if most:
            models_over(link, uid, most, key)
        if barred:
            mod = el(child(link, "modifiers"), "modifier", type="set", field="hidden", value="true")
            el(el(mod, "conditions"), "condition", type="atLeast", value=1, field="selections", scope=uid,
               childId=barred, shared=True, includeChildSelections=True, includeChildForces=False, percentValue=False)
    return g


def model_entry(unit, name):
    return next(m for m in unit.iter("selectionEntry") if m.get("type") == "model" and m.get("name") == name)


def link_named(group, name):
    return next((l for l in group.findall("entryLinks/entryLink") if l.get("name") == name), None)


def clear_when_any(group, targets, scope):
    """The group needs (and allows) nothing once one of these is taken."""
    for c in group.findall("constraints/constraint"):
        mod = el(child(group, "modifiers"), "modifier", type="set", field=c.get("id"), value=0)
        conds = el(el(el(mod, "conditionGroups"), "conditionGroup", type="or"), "conditions")
        for t in targets:
            el(conds, "condition", type="atLeast", value=1, field="selections", scope=scope, childId=t, shared=True,
               includeChildSelections=True, includeChildForces=False, percentValue=False)


def warlord_trait(entry, name, text, key):
    p = el(child(entry, "profiles"), "profile", name=name, typeId=WARLORD_TRAIT[0], typeName=WARLORD_TRAIT[1],
           hidden=False, id=mid(key, "trait", name))
    el(el(p, "characteristics"), "characteristic", name="Text", typeId=WARLORD_TRAIT[2]).text = text
    return p


# ---- writing into the official files as text


ORDER = bc.ENTRY_ORDER + ["description", "repeats", "conditions", "conditionGroups"]


def sort_kids(e):
    kids = list(e)
    order = bc.MODIFIER_ORDER if e.tag in ("modifier", "conditionGroup") else ORDER
    if kids and all(k.tag in order for k in kids):
        kids.sort(key=lambda k: order.index(k.tag))
        for k in list(e):
            e.remove(k)
        e.extend(kids)
    for k in kids:
        sort_kids(k)


def xml(e, level):
    sort_kids(e)
    ET.indent(e, space="  ", level=level)
    return " " * (2 * level) + ET.tostring(e, encoding="unicode").replace(" />", "/>")


class Text:
    """A catalogue file edited as text."""

    def __init__(self, path):
        self.path = path
        self.s = open(path, encoding="utf-8", newline="").read()
        self.nl = "\r\n" if "\r\n" in self.s else "\n"

    def block(self, eid):
        """(start, end, indent, tag) of the element with this id."""
        i = self.s.index(f'id="{eid}"')
        start = self.s.rfind("<", 0, i)
        line = self.s.rfind("\n", 0, start) + 1
        tag = re.match(r"<(\w+)", self.s[start:]).group(1)
        head_end = self.s.index(">", start)
        if self.s[head_end - 1] == "/":
            return start, head_end + 1, start - line, tag
        end = self.s.index(f"</{tag}>", head_end)
        depth = self.s.count(f"<{tag} ", head_end, end) - len(re.findall(f"<{tag} [^>]*/>", self.s[head_end:end]))
        while depth:
            nxt = self.s.index(f"</{tag}>", end + 1)
            depth += self.s.count(f"<{tag} ", end, nxt) - len(re.findall(f"<{tag} [^>]*/>", self.s[end:nxt])) - 1
            end = nxt
        return start, end + len(f"</{tag}>"), start - line, tag

    def add(self, eid, container, elements):
        """Put elements at the end of the element's direct `container` child, making it if needed."""
        start, end, indent, tag = self.block(eid)
        body = self.s[start:end]
        if body.endswith("/>"):
            body = body[:-2] + f">{self.nl}{' ' * indent}</{tag}>"
            self.s = self.s[:start] + body + self.s[end:]
            start, end, indent, tag = self.block(eid)
            body = self.s[start:end]
        pad = " " * (indent + 2)
        close = f"{self.nl}{pad}</{container}>"
        open_tag = re.search(rf"{re.escape(self.nl)}{pad}<{container}>", body)
        text = "".join(self.nl + xml(e, indent // 2 + 2) for e in elements).replace("\n", self.nl)
        if open_tag:
            j = body.index(close, open_tag.start())
            body = body[:j] + text + body[j:]
        else:
            # a new container goes where the schema puts it
            k = ORDER.index(container)
            pos = None
            for c in ORDER[k + 1:]:
                m = re.search(rf"{re.escape(self.nl)}{pad}<{c}[ >]", body)
                if m:
                    pos = m.start()
                    break
            if pos is None:
                pos = body.rindex(f"{self.nl}{' ' * indent}</{tag}>")
            body = body[:pos] + f"{self.nl}{pad}<{container}>" + text + close + body[pos:]
        self.s = self.s[:start] + body + self.s[end:]

    def remove(self, eid):
        """Take out the element with this id, and its line."""
        start, end, _, _ = self.block(eid)
        line = self.s.rfind("\n", 0, start) + 1
        self.s = self.s[:line] + self.s[self.s.index("\n", end) + 1:]

    def add_top(self, container, elements, level=2):
        i = self.s.index(f"  </{container}>")
        self.s = self.s[:i] + "".join(xml(e, level).replace("\n", self.nl) + self.nl for e in elements) + self.s[i:]

    def bump(self, tag):
        m = re.search(rf'<{tag} [^>]*?revision="(\d+)"', self.s)
        self.s = self.s[:m.start(1)] + str(int(m.group(1)) + 1) + self.s[m.end(1):]

    def save(self):
        open(self.path, "w", encoding="utf-8", newline="").write(self.s)


def E(tag, **a):
    return ET.Element(tag, {k.rstrip("_"): ("true" if v is True else "false" if v is False else str(v)) for k, v in a.items()})


def link_el(name, target, key, mx=None, mn=None, pts=None, per_model_of=None):
    l = E("entryLink", id=mid(key, name), name=name, hidden=False, collective=False, import_=True, targetId=target,
          type="selectionEntry")
    if mn:
        add_constraint(l, "min", mn, mid(key, name, "min"))
    if mx:
        add_constraint(l, "max", mx, mid(key, name, "max"))
    if pts is not None and per_model_of:
        # a whole-unit pick priced per model
        add_cost(l, 0)
        mod = el(el(l, "modifiers"), "modifier", type="increment", field=bc.PTS, value=pts)
        el(el(mod, "repeats"), "repeat", field="selections", scope=per_model_of, value=1, percentValue=False,
           shared=True, includeChildSelections=False, includeChildForces=False, childId="model", repeats=1,
           roundUp=False)
    elif pts is not None:
        add_cost(l, pts)
    return l


def any_entry(name, required=True):
    """An entry of any kind the catalogue can link, by name: its own, its libraries', the game system's."""
    for f in sources():
        root = ET.parse(f).getroot()
        ns = NS["gst"] if f == GST else NS["cat"]
        for e in root.findall(f"{ns}sharedSelectionEntries/{ns}selectionEntry"):
            if norm(e.get("name")) == norm(name):
                return e.get("id")
    if required:
        sys.exit(f"no entry {name}")
    return None


def official_units():
    root = ET.parse(cfg.cat).getroot()
    return {e.get("name"): e for e in root.find(NS["cat"] + "sharedSelectionEntries") if e.get("type") == "unit"}


def find_in(unit, pred):
    return next(x for x in unit.iter() if pred(x))


def deep(e):
    return ET.fromstring(ET.tostring(e))
