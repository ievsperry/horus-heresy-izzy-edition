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
    "At the start of the controlling player&apos;s Shooting phase, a unit with this special rule armed with heavy "
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
    weapons = (weapon("heavy bolter", "Heavy Bolter", "Heavy Bolter (Wrathful Souls)", "36&quot;", "5", "4",
                      "Heavy 4, Rupture (6+)", "Rupture (X)", "Rupture (6+)")
               + weapon("autocannon", "Autocannon", "Autocannon (Wrathful Souls)", "48&quot;", "7", "4",
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


if __name__ == "__main__":
    print(red_fangs())
