"""Custom units (homebrew/source/custom-units.md) written into the official catalogues.

The Red Fangs: a World Eaters Heavy Support Squad. It is a copy of the library's Heavy Support Squad (same models,
options and transports, every id renewed) in `2022 - LA - World Eaters.cat`, linked from that catalogue the way the
Heavy Support Squad is, with its heavy weapon pick cut down to heavy bolters (default) or autocannons (+5 per model),
both with the Wrathful Souls profiles, and the Bitter Duty, Slow and Purposeful, Wrathful Souls and Dying Gift rules.
Each unit is added once; running again skips what is already there."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402

LIBRARY = "2022 - Legiones Astartes.cat"
WORLD_EATERS = "2022 - LA - World Eaters.cat"
HEAVY_SUPPORT_SQUAD = "bac9-5389-e2e7-0b1f"
HSS_ROOT_LINK_WE = "2354-d46f-49c8-4630"
SQUAD_WEAPONRY = "3ef1-3886-773d-1742"
GST_RULES = {"Bitter Duty": "d1b8-31da-c53c-4fe2", "Slow and Purposeful": "d69a-cfb3-db43-32c5",
             "Rupture (X)": "d530-0b40-4723-af90", "Rending (X)": "0ac9-fab7-aef3-de1d"}
PTS = 'name="Pts" typeId="d2ee-04cb-5f8a-2642"'

WRATHFUL_SOULS = (
    "A unit with this special rule armed with heavy bolters gives them Rupture (6+); when the unit makes Shooting "
    "Attacks as part of an Overwatch Reaction, this becomes Rupture (4+). Against a unit with the Legiones Astartes "
    "(World Eaters) special rule of a different Allegiance, the Rupture (X) becomes Breaching (X) of the same value "
    "instead. In addition, its autocannons fire one additional shot (Heavy 3 instead of Heavy 2).")
DYING_GIFT = (
    "Once per battle, at the start of the controlling player&apos;s Shooting phase, a unit with this special rule armed with heavy "
    "bolters or autocannons may elect to give those weapons the Gets Hot special rule for the phase and to improve "
    "their Rupture (X) or Rending (X) to Rupture (4+) or Rending (4+). A Wound suffered from Gets Hot while this is in "
    "effect is resolved at the improved AP: AP 3 for a weapon with Rupture and AP 2 for one with Rending.")


def mk(*key):
    return bc.make_id("custom units", *key)


def nl_of(s):
    return "\r\n" if "\r\n" in s[:2000] else "\n"


def element_span(s, start, tag):
    """(start, end) of the element with this tag that begins at `start`."""
    d = 0
    for m in re.finditer(r"<(/?)%s\b[^>]*?(/?)>" % tag, s[start:]):
        if m.group(1):
            d -= 1
        elif not m.group(2):
            d += 1
        if d == 0:
            return start, start + m.end()
    raise ValueError(tag)


def child_span(block, tag):
    """(start, end) of the direct child `tag` of the block's root element, or None."""
    depth = 0
    for m in re.finditer(r"<(/?)([A-Za-z]+)\b[^>]*?(/?)>", block):
        close, name, empty = m.groups()
        if close:
            depth -= 1
            continue
        if depth == 1 and name == tag:
            return element_span(block, m.start(), tag)
        if not empty:
            depth += 1
    return None


def renew_ids(block, key):
    """Every id defined in the block gets a new one, and every reference to it inside the block follows."""
    ids = set(re.findall(r'\sid="([^"]+)"', block))
    return re.sub(r'"([0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4})"',
                  lambda m: f'"{mk(key, m.group(1))}"' if m.group(1) in ids else m.group(0), block)


def weapon(key, name, profile, rng, s, ap, typ, rule, shown):
    return (f'<selectionEntry id="{mk(key)}" name="{name}" hidden="false" collective="false" import="true" '
            f'type="upgrade"><profiles><profile id="{mk(key, "profile")}" name="{profile}" hidden="false" '
            f'typeId="1a1a-e592-2849-a5c0" typeName="Weapon"><characteristics>'
            f'<characteristic name="Range" typeId="95ba-cda7-b831-6066">{rng}</characteristic>'
            f'<characteristic name="Strength" typeId="24d9-b8e1-a355-2458">{s}</characteristic>'
            f'<characteristic name="AP" typeId="f7a6-e0d8-7973-cd8d">{ap}</characteristic>'
            f'<characteristic name="Type" typeId="2f86-c8b4-b3b4-3ff9">{typ}</characteristic>'
            f'</characteristics></profile></profiles><infoLinks>'
            f'<infoLink id="{mk(key, "rule")}" name="{rule}" hidden="false" targetId="{GST_RULES[rule]}" type="rule">'
            f'<modifiers><modifier type="set" field="name" value="{shown}"/></modifiers></infoLink></infoLinks>'
            f'<costs><cost {PTS} value="0"/></costs></selectionEntry>')


def rule_link(key, name, target):
    return f'<infoLink id="{mk(key, name)}" name="{name}" hidden="false" targetId="{target}" type="rule"/>'


def red_fangs():
    lib = open(LIBRARY, encoding="utf-8").read()
    we = open(WORLD_EATERS, encoding="utf-8").read()
    if 'name="The Red Fangs"' in we:
        return "The Red Fangs: already there"
    nl = nl_of(we)
    # the unit, copied from the library's Heavy Support Squad
    a = lib.index(f'<selectionEntry id="{HEAVY_SUPPORT_SQUAD}"')
    a, b = element_span(lib, a, "selectionEntry")
    unit = lib[a:b]
    g = unit.index(f'id="{SQUAD_WEAPONRY}"')
    ga, gb = element_span(unit, unit.rfind("<selectionEntryGroup", 0, g), "selectionEntryGroup")
    group = unit[ga:gb]
    links = child_span(group, "entryLinks")
    keep = []
    for m in re.finditer(r"<entryLink\b", group[links[0]:links[1]]):
        la, lb = element_span(group, links[0] + m.start(), "entryLink")
        link = group[la:lb]
        name = re.search(r'name="([^"]+)"', link).group(1)
        if name == "Heavy Bolter":
            keep.append(link.replace('targetId="07fd-c24a-9235-4206"', f'targetId="{mk("heavy bolter")}"'))
        elif name == "Autocannon":
            keep.append(link.replace('targetId="56b3-de09-9fea-deb6"', f'targetId="{mk("autocannon")}"'))
    assert len(keep) == 2, keep
    group = group[:links[0]] + "<entryLinks>" + "".join(keep) + "</entryLinks>" + group[links[1]:]
    unit = unit[:ga] + group + unit[gb:]
    unit = unit.replace('name="Heavy Support Squad"', 'name="The Red Fangs"', 1)
    rules = (rule_link("red fangs", "Bitter Duty", GST_RULES["Bitter Duty"])
             + rule_link("red fangs", "Slow and Purposeful", GST_RULES["Slow and Purposeful"])
             + rule_link("red fangs", "Wrathful Souls", mk("wrathful souls"))
             + rule_link("red fangs", "Dying Gift", mk("dying gift")))
    il = child_span(unit, "infoLinks")
    unit = unit[:il[1] - len("</infoLinks>")] + rules + unit[il[1] - len("</infoLinks>"):]
    unit = renew_ids(unit, "red fangs")
    weapons = (weapon("heavy bolter", "Heavy Bolter (Wrathful Souls)", "Heavy Bolter (Wrathful Souls)", "36&quot;", "5", "4",
                      "Heavy 4, Rupture (6+)", "Rupture (X)", "Rupture (6+)")
               + weapon("autocannon", "Autocannon (Wrathful Souls)", "Autocannon (Wrathful Souls)", "48&quot;", "7", "4",
                        "Heavy 3, Rending (6+)", "Rending (X)", "Rending (6+)"))
    i = we.index("  </sharedSelectionEntries>")
    we = we[:i] + "    " + unit + nl + "    " + weapons + nl + we[i:]
    # the rules
    rules_xml = "".join(
        f'<rule id="{mk(k)}" name="{n}" hidden="false"><description>{t}</description></rule>'
        for k, n, t in (("wrathful souls", "Wrathful Souls", WRATHFUL_SOULS), ("dying gift", "Dying Gift", DYING_GIFT)))
    if "<sharedRules>" in we:
        i = we.index("  </sharedRules>")
        we = we[:i] + "    " + rules_xml + nl + we[i:]
    else:
        i = we.index("  </sharedSelectionEntryGroups>") + len("  </sharedSelectionEntryGroups>")
        we = we[:i] + nl + "  <sharedRules>" + nl + "    " + rules_xml + nl + "  </sharedRules>" + we[i:]
    # the root link, as the Heavy Support Squad's
    r = we.index(f'<entryLink id="{HSS_ROOT_LINK_WE}"')
    ra, rb = element_span(we, r, "entryLink")
    root = we[ra:rb].replace('name="Heavy Support Squad"', 'name="The Red Fangs"', 1)
    root = root.replace(f'targetId="{HEAVY_SUPPORT_SQUAD}"', f'targetId="{mk("red fangs", HEAVY_SUPPORT_SQUAD)}"', 1)
    root = renew_ids(root, "red fangs root")
    line = we.rfind(nl, 0, ra) + len(nl)
    we = we[:rb] + nl + we[line:ra] + root + we[rb:]
    open(WORLD_EATERS, "w", encoding="utf-8", newline="").write(we)
    return "The Red Fangs: added to " + WORLD_EATERS


RED_FANGS_COST, RED_FANGS_WOUNDS = 130, 2  # always the sergeant and four Legionaries


def red_fangs_changes():
    """Always five models (the sergeant and four Legionaries, no more), 130 points, 2 Wounds on both profiles and the
    Legionary's Toughness filled in."""
    we = open(WORLD_EATERS, encoding="utf-8").read()
    a = re.search(r'<selectionEntry [^>]*name="The Red Fangs"', we).start()
    a, b = element_span(we, a, "selectionEntry")
    unit = we[a:b]

    def set_cost(block, value):
        cs = child_span(block, "costs")
        costs = re.sub(r'(<cost name="Pts"[^>]*value=")[^"]*', lambda m: m.group(1) + str(value), block[cs[0]:cs[1]])
        return block[:cs[0]] + costs + block[cs[1]:]

    def named(name):  # before or after red_fangs_models renames the models
        return name if f'name="{name}"' in unit else RED_FANGS_NAMES[name]

    for name in ("Legionaries (collective)", "Legionary w/ Options"):
        j = unit.index(f'name="{named(name)}"')
        ea, eb = element_span(unit, unit.rfind("<selectionEntry", 0, j), "selectionEntry")
        unit = unit[:ea] + set_cost(unit[ea:eb], 0) + unit[eb:]
    unit = set_cost(unit, RED_FANGS_COST)
    j = unit.index(f'name="{named("0) Legionaries")}"')
    ga, gb = element_span(unit, unit.rfind("<selectionEntryGroup", 0, j), "selectionEntryGroup")
    group = re.sub(r'(<constraint [^>]*value=")\d+("[^>]*type="max")', r"\g<1>4\2", unit[ga:gb], count=1)
    unit = unit[:ga] + group + unit[gb:]
    unit = re.sub(r'(<characteristic name="W" typeId="57ee-1126-32a9-5672">)[^<]*', rf"\g<1>{RED_FANGS_WOUNDS}", unit)
    # the official Legionary profile leaves Toughness blank: the Legionary is T4, as the sergeant
    unit = unit.replace('<characteristic name="T" typeId="c32b-5fdd-3fbe-9b1f"/>',
                        '<characteristic name="T" typeId="c32b-5fdd-3fbe-9b1f">4</characteristic>')
    if unit != we[a:b]:
        open(WORLD_EATERS, "w", encoding="utf-8", newline="").write(we[:a] + unit + we[b:])
        return "The Red Fangs: five models, 130 points, W2"
    return "The Red Fangs: already five models, 130 points, W2"

def red_fangs_sync():
    """Keep an existing catalogue in step: the rules' text, and the Wrathful Souls weapons named apart from the
    official heavy bolter and autocannon (only The Red Fangs link them)."""
    we = open(WORLD_EATERS, encoding="utf-8").read()
    before = we
    for key, text in (("wrathful souls", WRATHFUL_SOULS), ("dying gift", DYING_GIFT)):
        we = re.sub(r'(<rule id="%s"[^>]*>\s*<description>).*?(</description>)' % mk(key),
                    lambda m: m.group(1) + text + m.group(2), we, count=1, flags=re.S)
    for key, name in (("heavy bolter", "Heavy Bolter"), ("autocannon", "Autocannon")):
        new = f"{name} (Wrathful Souls)"
        we = re.sub(r'(<selectionEntry id="%s" name=")[^"]*' % mk(key), lambda m: m.group(1) + new, we, count=1)
        we = re.sub(r'(<entryLink [^>]*name=")%s("[^>]*targetId="%s")' % (re.escape(name), mk(key)),
                    lambda m: m.group(1) + new + m.group(2), we)
    if we != before:
        open(WORLD_EATERS, "w", encoding="utf-8", newline="").write(we)
        return "The Red Fangs: rules and weapon names brought up to date"
    return "The Red Fangs: rules and weapon names up to date"


RED_FANGS_NAMES = {"Legion Support Sergeant": "Alpha Fang", "Legionary": "Fang Legionary",
                   "Legionaries (collective)": "Fang Legionaries", "Legionary w/ Options": "Fang Legionary w/ Options",
                   "0) Legionaries": "0) Fang Legionaries"}


def red_fangs_models():
    """The Alpha Fang and Fang Legionaries: the models and profiles renamed, Initiative 3, and a combat blade with the
    bolt pistol every model already has."""
    we = open(WORLD_EATERS, encoding="utf-8").read()
    if 'name="Alpha Fang"' in we:
        return "The Red Fangs: models already the Alpha Fang and Fang Legionaries"
    nl = nl_of(we)
    blade = (f'<selectionEntry id="{mk("combat blade")}" name="Combat Blade" hidden="false" collective="false" '
             f'import="true" type="upgrade"><profiles><profile id="{mk("combat blade", "profile")}" name="Combat Blade" '
             f'hidden="false" typeId="1a1a-e592-2849-a5c0" typeName="Weapon"><characteristics>'
             f'<characteristic name="Range" typeId="95ba-cda7-b831-6066">-</characteristic>'
             f'<characteristic name="Strength" typeId="24d9-b8e1-a355-2458">User</characteristic>'
             f'<characteristic name="AP" typeId="f7a6-e0d8-7973-cd8d">-</characteristic>'
             f'<characteristic name="Type" typeId="2f86-c8b4-b3b4-3ff9">Melee</characteristic>'
             f'</characteristics></profile></profiles><costs><cost {PTS} value="0"/></costs></selectionEntry>')
    a = re.search(r'<selectionEntry [^>]*name="The Red Fangs"', we).start()
    a, b = element_span(we, a, "selectionEntry")
    unit = we[a:b]
    # Initiative 3 on both profiles
    unit = re.sub(r'(<characteristic name="I" typeId="62d3-22d7-2d49-52dc">)[^<]*', r"\g<1>3", unit)
    # the combat blade on every model, beside its bolt pistol
    for name in ("Legion Support Sergeant", "Legionaries (collective)", "Legionary w/ Options"):
        j = re.search(r'<selectionEntry [^>]*name="%s"[^>]*type="model"' % re.escape(name), unit).start()
        ma, mb = element_span(unit, j, "selectionEntry")
        model = unit[ma:mb]
        link = (f'<entryLink id="{mk("combat blade link", name)}" name="Combat Blade" hidden="false" collective="false" '
                f'import="true" targetId="{mk("combat blade")}" type="selectionEntry"><constraints>'
                f'<constraint type="min" value="1" field="selections" scope="parent" shared="true" '
                f'id="{mk("combat blade link", name, "min")}" percentValue="false" includeChildSelections="false" '
                f'includeChildForces="false"/><constraint type="max" value="1" field="selections" scope="parent" '
                f'shared="true" id="{mk("combat blade link", name, "max")}" percentValue="false" '
                f'includeChildSelections="false" includeChildForces="false"/></constraints></entryLink>')
        links = child_span(model, "entryLinks")
        if links:
            end = links[1] - len("</entryLinks>")
            model = model[:end] + link + model[end:]
        else:
            after = child_span(model, "selectionEntryGroups") or child_span(model, "categoryLinks") \
                or child_span(model, "profiles")
            model = model[:after[1]] + f"<entryLinks>{link}</entryLinks>" + model[after[1]:]
        unit = unit[:ma] + model + unit[mb:]
    # the names
    for old, new in RED_FANGS_NAMES.items():
        unit = re.sub(r'(<(?:selectionEntry|selectionEntryGroup|profile|infoLink) [^>]*name=")%s"' % re.escape(old),
                      lambda m: m.group(1) + new + '"', unit)
    we = we[:a] + unit + we[b:]
    i = we.index("  </sharedSelectionEntries>")
    we = we[:i] + "    " + blade + nl + we[i:]
    open(WORLD_EATERS, "w", encoding="utf-8", newline="").write(we)
    return "The Red Fangs: the Alpha Fang and Fang Legionaries, I3, combat blades"


if __name__ == "__main__":
    print(red_fangs())
    print(red_fangs_changes())
    print(red_fangs_sync())
    print(red_fangs_models())
