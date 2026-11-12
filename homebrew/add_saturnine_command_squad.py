"""Add the Saturnine Command Squad (homebrew/source/saturnine.md) to the Legiones Astartes library, with the Saturnine
concussion hammer and war axe (also for the Praetor and Centurion in Saturnine Terminator Armour), and link the unit
from every Legion catalogue the way the Praetor in Saturnine Terminator Armour is linked. Run once; it refuses to run
again on a library that already has the unit."""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402

LIBRARY = "2022 - Legiones Astartes.cat"
PUB = "ecd9-109b-245d-4083"  # the Saturnine entries' publication
PTS = 'typeId="d2ee-04cb-5f8a-2642"'
RULES = {  # game system and library rules, by name
    "Legiones Astartes (X)": "ffcb-13b4-9b4c-84da", "Bulky (X)": "676c-7b75-4b6f-9405",
    "Relentless": "7adf-ac9a-5035-522d", "Slow and Purposeful": "d69a-cfb3-db43-32c5",
    "Deep Strike": "f1e1-986f-c783-ca9e", "Retinue": "6b79-ac44-4d89-2124", "Chosen Warriors": "13d1-9270-6539-08ed",
    "Legends": "6bd6-620e-c9db-b8e5", "Thermal Diffraction Field": "261a-aaba-ab5f-13a7",
    "Unwieldy": "1570-c21a-881f-8b8a", "Brutal (X)": "5079-1fec-d32b-8b84", "Concussive (X)": "7ce5-1bfb-64e6-f826",
    "Concussion (X)": "019c-9f2c-548b-b0ff", "Murderous Strike (X)": "93b9-1454-0e7c-42ae",
    "Reaping Blow (X)": "bd8c-4f52-d682-1b40",
}
CATS = {"Legiones Astartes": "11f2-472f-c1d1-9ae9", "Terminators:": "bab3-f50d-3e5f-2f78",
        "Infantry Unit Type": "8b4f-bfe2-ce7b-f1b1", "Heavy Sub-type": "9231-183c-b97b-63f9",
        "Legends": "5292-382b-71f5-4b8f", "Character": "f75a-d5c1-59ba-5c5a"}
FIST = "3351-cc7e-9ba8-c881"
PRAETOR = "62c1-7532-c5b2-3f1d"
PRAETOR_MELEE = "1b0a-7132-54e6-04b3"
CENTURION_FIST_LINK = "5d9e-e550-89b3-ea54"
SYNCHRONISER_TEXT = ("A unit that includes a model with a Saturnine teleport synchroniser does not scatter when it arrives "
                     "by Deep Strike if it is set up within 6&quot; of a friendly unit whose name includes Saturnine "
                     "that was on the battlefield at the start of the turn.")
THERMAL_TEXT = ("Weapons with the Las, Plasma, Melta or Flame traits subtract 1 from their Strength when targeting a "
                "model with a thermal diffraction field. In addition, when such a model rolls for Gets Hot, it may "
                "re-roll the result.")


def mk(*key):
    return bc.make_id("saturnine command squad", *key)


def rule(key, name, shown=None):
    mod = (f'<modifiers><modifier type="set" field="name" value="{shown}"/></modifiers>' if shown else "")
    return (f'<infoLink id="{mk(key, "rule", name)}" name="{name}" hidden="false" targetId="{RULES[name]}" type="rule">'
            f'{mod}</infoLink>')


def cat(key, name, primary=False):
    return (f'<categoryLink id="{mk(key, "category", name)}" name="{name}" hidden="false" targetId="{CATS[name]}" '
            f'primary="{str(primary).lower()}"/>')


def cons(key, mn=None, mx=None, scope="parent"):
    out = ""
    for t, v in (("min", mn), ("max", mx)):
        if v is not None:
            out += (f'<constraint type="{t}" value="{v}" field="selections" scope="{scope}" shared="true" '
                    f'id="{mk(key, t)}" percentValue="false" includeChildSelections="false" includeChildForces="false"/>')
    return f"<constraints>{out}</constraints>"


def cost(v):
    return f'<costs><cost name="Pts" {PTS} value="{v}"/></costs>'


def link(key, name, target, mn=None, mx=None, pts=None):
    c = cons(key, mn, mx) if (mn is not None or mx is not None) else ""
    return (f'<entryLink id="{mk(key)}" name="{name}" hidden="false" collective="false" import="true" '
            f'targetId="{target}" type="selectionEntry">{c}{cost(pts) if pts is not None else ""}</entryLink>')


def weapon(key, name, s, ap, typ, rules):
    chars = (f'<characteristic name="Range" typeId="95ba-cda7-b831-6066">-</characteristic>'
             f'<characteristic name="Strength" typeId="24d9-b8e1-a355-2458">{s}</characteristic>'
             f'<characteristic name="AP" typeId="f7a6-e0d8-7973-cd8d">{ap}</characteristic>'
             f'<characteristic name="Type" typeId="2f86-c8b4-b3b4-3ff9">{typ}</characteristic>')
    return (f'<selectionEntry id="{mk(key)}" name="{name}" publicationId="{PUB}" hidden="false" collective="false" '
            f'import="true" type="upgrade"><profiles><profile id="{mk(key, "profile")}" name="{name}" '
            f'publicationId="{PUB}" hidden="false" typeId="1a1a-e592-2849-a5c0" typeName="Weapon">'
            f'<characteristics>{chars}</characteristics></profile></profiles>'
            f'<infoLinks>{"".join(rule(key, n, v) for n, v in rules)}</infoLinks>{cost("0.0")}</selectionEntry>')


def wargear(key, name, text=None, rules=()):
    prof = (f'<profiles><profile id="{mk(key, "profile")}" name="{name}" publicationId="{PUB}" hidden="false" '
            f'typeId="2a1f-7837-f0ef-be44" typeName="Wargear Item"><characteristics>'
            f'<characteristic name="Description" typeId="347e-ee4a-764f-6be3">{text}</characteristic>'
            f'</characteristics></profile></profiles>') if text else ""
    links = f'<infoLinks>{"".join(rule(key, n) for n in rules)}</infoLinks>' if rules else ""
    return (f'<selectionEntry id="{mk(key)}" name="{name}" publicationId="{PUB}" hidden="false" collective="false" '
            f'import="true" type="upgrade">{prof}{links}{cost("0.0")}</selectionEntry>')


def model(key, name, unit_type, stats, mn, mx, pts, cats, kit):
    names = ["Move", "WS", "BS", "S", "T", "W", "I", "A", "Ld", "Save"]
    ids = ["893e-2d76-8f04-44e5", "cc42-7ed5-7092-5c84", "74ae-c840-0036-d244", "e478-41d4-a092-48a8",
           "c32b-5fdd-3fbe-9b1f", "57ee-1126-32a9-5672", "62d3-22d7-2d49-52dc", "f111-2ce5-dd12-d6b0",
           "e8a6-1da9-d384-8727", "e593-6b3c-f169-04f0"]
    chars = (f'<characteristic name="Unit Type" typeId="ddd7-6f5c-a939-b69e">{unit_type}</characteristic>'
             + "".join(f'<characteristic name="{n}" typeId="{i}">{v}</characteristic>'
                       for n, i, v in zip(names, ids, stats)))
    return (f'<selectionEntry id="{mk(key)}" name="{name}" publicationId="{PUB}" hidden="false" collective="false" '
            f'import="true" type="model">{cons(key, mn, mx)}'
            f'<profiles><profile id="{mk(key, "profile")}" name="{name}" publicationId="{PUB}" hidden="false" '
            f'typeId="4bb2-cb95-e6c8-5a21" typeName="Unit"><characteristics>{chars}</characteristics></profile>'
            f'</profiles><categoryLinks>{"".join(cat(key, c) for c in cats)}</categoryLinks>'
            f'{kit(key)}{cost(pts)}</selectionEntry>')


PLASMA_BOMBARD, TWIN_HEAVY_DISINTEGRATOR = "7112-6c13-99a7-1ba7", "d4ef-1a5c-49cd-e684"
PARTICLE_SHREDDER, PLASMA_BLASTER, LEGION_STANDARD = "d9cd-6782-6a72-fc3a", "cd52-e9e8-3ab1-995c", "7e13-cc1f-6bd7-7ac6"
FIST_SWAPS = [  # (name, the other weapon, cost per model)
    ("Plasma Bombard and one Saturnine Disruption Fist", "Plasma Bombard", PLASMA_BOMBARD, "10.0"),
    ("Twin Heavy Disintegrator and one Saturnine Disruption Fist", "Twin Heavy Disintegrator",
     TWIN_HEAVY_DISINTEGRATOR, "20.0"),
    ("Saturnine War Axe and one Saturnine Disruption Fist", "Saturnine War Axe", None, "10.0"),
    ("Saturnine Concussion Hammer and one Saturnine Disruption Fist", "Saturnine Concussion Hammer", None, "20.0"),
]


def weapon_pair(key, name, other_name, other_id):
    return (f'<selectionEntry id="{mk(key)}" name="{name}" publicationId="{PUB}" hidden="false" collective="false" '
            f'import="true" type="upgrade"><entryLinks>'
            + link(key + " other", other_name, other_id, 1, 1)
            + link(key + " fist", "Saturnine Disruption Fist", FIST, 1, 1)
            + f'</entryLinks>{cost("0.0")}</selectionEntry>')


def group(key, name, body, mn, mx, default=None):
    d = f' defaultSelectionEntryId="{default}"' if default else ""
    return (f'<selectionEntryGroup id="{mk(key)}" name="{name}" hidden="false" collective="false" import="true"{d}>'
            + cons(key, mn, mx) + f"<entryLinks>{body}</entryLinks></selectionEntryGroup>")


def kit(key, standard=False):
    fists = group(key + " fists", "Exchange paired Saturnine disruption fists",
                  link(key + " fists paired", "Paired Saturnine Disruption Fists", mk("paired fists"), pts="0.0")
                  + "".join(link(f"{key} fists {i}", n, mk(f"pair {i}"), pts=c) for i, (n, _, _, c) in enumerate(FIST_SWAPS)),
                  1, 1, mk(key + " fists paired"))
    extra = group(key + " extra", "Options",
                  link(key + " shredder", "Particle Shredder", PARTICLE_SHREDDER, pts="5.0")
                  + link(key + " blaster", "Plasma Blaster", PLASMA_BLASTER, pts="10.0"), None, 1)
    groups = f"<selectionEntryGroups>{fists}{extra}</selectionEntryGroups>"
    links = (link(key + " field", "Thermal Diffraction Field", mk("thermal field"), 1, 1)
             + link(key + " sync", "Saturnine Teleport Synchroniser", mk("synchroniser"), 1, 1))
    if standard:  # one Saturnine Chosen in the unit
        links += (f'<entryLink id="{mk(key, "standard")}" name="Legion Standard" hidden="false" collective="false" '
                  f'import="true" targetId="{LEGION_STANDARD}" type="selectionEntry">'
                  + cons(key + " standard", None, 1, scope=mk("unit")).replace(
                      'includeChildSelections="false"', 'includeChildSelections="true"')
                  + cost("20.0") + "</entryLink>")
    return groups + f"<entryLinks>{links}</entryLinks>"


def shared_entries():
    hammer = weapon("hammer", "Saturnine Concussion Hammer", "x2", "2",
                    "Melee, Unwieldy (4), Brutal (2), Concussive (2), Concussion (2)",
                    [("Unwieldy", None), ("Brutal (X)", "Brutal (2)"), ("Concussive (X)", "Concussive (2)"),
                     ("Concussion (X)", "Concussion (2)")])
    axe = weapon("axe", "Saturnine War Axe", "+1", "2",
                 "Melee, Murderous Strike (6+), Reaping Blow (2), Unwieldy (2)",
                 [("Murderous Strike (X)", "Murderous Strike (6+)"), ("Reaping Blow (X)", "Reaping Blow (2)"),
                  ("Unwieldy", None)])
    fists = (f'<selectionEntry id="{mk("paired fists")}" name="Paired Saturnine Disruption Fists" publicationId="{PUB}" '
             f'hidden="false" collective="false" import="true" type="upgrade"><entryLinks>'
             + link("paired fists link", "Saturnine Disruption Fist", FIST, 2, 2) + f'</entryLinks>{cost("0.0")}'
             '</selectionEntry>')
    field = wargear("thermal field", "Thermal Diffraction Field", rules=["Thermal Diffraction Field"])
    sync = wargear("synchroniser", "Saturnine Teleport Synchroniser", SYNCHRONISER_TEXT)
    champion = model("champion", "Saturnine Chosen Champion", "Infantry (Character, Heavy)",
                     ["5", "5", "4", "5", "5", "3", "4", "3", "10", "2+"], 1, 1, "100.0",
                     ["Infantry Unit Type", "Heavy Sub-type", "Character"], lambda k: kit(k))
    chosen = model("chosen", "Saturnine Chosen", "Infantry (Heavy)",
                   ["5", "5", "4", "5", "5", "3", "4", "2", "9", "2+"], 1, 5, "60.0",
                   ["Infantry Unit Type", "Heavy Sub-type"], lambda k: kit(k, standard=True))
    unit_rules = [("Legiones Astartes (X)", None), ("Bulky (X)", "Bulky (3)"), ("Relentless", None),
                  ("Slow and Purposeful", None), ("Deep Strike", None), ("Retinue", None),
                  ("Chosen Warriors", None), ("Legends", None)]
    unit = (f'<selectionEntry id="{mk("unit")}" name="Saturnine Command Squad" publicationId="{PUB}" hidden="false" '
            f'collective="false" import="true" type="unit">'
            f'<infoLinks>{"".join(rule("unit", n, v) for n, v in unit_rules)}</infoLinks>'
            f'<categoryLinks>{"".join(cat("unit", c) for c in ["Legiones Astartes", "Terminators:", "Infantry Unit Type", "Heavy Sub-type", "Legends"])}'
            f'</categoryLinks><selectionEntries>{champion}{chosen}</selectionEntries>{cost("0.0")}</selectionEntry>')
    pairs = [weapon_pair(f"pair {i}", n, o, oid or mk("axe" if "Axe" in o else "hammer"))
             for i, (n, o, oid, _) in enumerate(FIST_SWAPS)]
    return [hammer, axe, fists, *pairs, field, sync, unit]


def hero_options(s):
    """The Praetor's Melee Weapon pick gains the hammer and axe; the Centurion's fixed fist becomes a pick."""
    i = s.index(f'id="{PRAETOR_MELEE}"')
    end = s.index("</entryLinks>", i)
    s = s[:end] + link("praetor hammer", "Saturnine Concussion Hammer", mk("hammer"), pts="10.0") \
        + link("praetor axe", "Saturnine War Axe", mk("axe"), pts="10.0") + s[end:]
    i = s.index(f'id="{CENTURION_FIST_LINK}"')
    a = s.rfind("<entryLink", 0, i)
    b = s.index("</entryLink>", a) + len("</entryLink>")
    group = (f'<selectionEntryGroup id="{mk("centurion melee")}" name="Exchange Saturnine disruption fist" '
             f'hidden="false" collective="false" import="true" defaultSelectionEntryId="{mk("centurion fist")}">'
             + cons("centurion melee", 1, 1) + "<entryLinks>"
             + link("centurion fist", "Saturnine disruption fist", FIST, pts="0")
             + link("centurion hammer", "Saturnine Concussion Hammer", mk("hammer"), pts="10")
             + link("centurion axe", "Saturnine War Axe", mk("axe"), pts="10")
             + "</entryLinks></selectionEntryGroup>")
    s = s[:a] + s[b:]
    # the Centurion's model: the pick goes in the model's own selectionEntryGroups (making them if needed)
    ms = s.rfind("<selectionEntry ", 0, s.rfind('name="Saturnine Centurion"', 0, a))
    depth, groups_at, links_at = 0, None, None
    for m in re.finditer(r"<(/?)([A-Za-z]+)\b[^>]*?(/?)>", s[ms:]):
        close, tag, empty = m.group(1), m.group(2), m.group(3)
        if empty:
            continue
        if close:
            depth -= 1
            if depth == 1 and tag == "selectionEntryGroups":
                groups_at = ms + m.start()
            if depth == 0:
                break
        else:
            if depth == 1 and tag == "entryLinks" and links_at is None:
                links_at = ms + m.start()
            depth += 1
    if groups_at is not None:
        s = s[:groups_at] + group + s[groups_at:]
    else:
        s = s[:links_at] + f"<selectionEntryGroups>{group}</selectionEntryGroups>" + s[links_at:]
    return s


def root_links():
    n = 0
    for f in sorted(glob.glob("2022 - LA - *.cat")) + ["Shattered Legions.cat"]:
        t = open(f, encoding="utf-8").read()
        i = t.index('name="Praetor in Saturnine Terminator Armour"')
        a = t.rfind("<entryLink", 0, i)
        d = 0
        for m in re.finditer(r"<(/?)entryLink\b[^>]*?(/?)>", t[a:]):
            if m.group(1):
                d -= 1
            elif not m.group(2):
                d += 1
            if d == 0:
                e = a + m.end()
                break
        blk = t[a:e]
        blk = re.sub(r"\s*<entryLinks>.*?</entryLinks>", "", blk, flags=re.S)  # no Warlord Traits for a squad
        blk = re.sub(r'\s*<categoryLink [^>]*name="Compulsory HQ:".*?</categoryLink>', "", blk, flags=re.S)
        blk = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{mk(f, m.group(1))}"', blk)
        blk = blk.replace('name="Praetor in Saturnine Terminator Armour"', 'name="Saturnine Command Squad"', 1)
        blk = blk.replace(f'targetId="{PRAETOR}"', f'targetId="{mk("unit")}"', 1)
        nl = "\r\n" if "\r\n" in t[a:e] else "\n"
        t = t[:e] + nl + t[t.rfind(nl, 0, a) + len(nl):a] + blk + t[e:]
        open(f, "w", encoding="utf-8", newline="").write(t)
        n += 1
    return n


def main():
    s = open(LIBRARY, encoding="utf-8").read()
    if 'name="Saturnine Command Squad"' in s:
        sys.exit(f"{LIBRARY} already has the Saturnine Command Squad")
    # Thermal Diffraction Field: worded for any model that has one, not only the Dreadnought
    s = re.sub(r'(<rule id="261a-aaba-ab5f-13a7"[^>]*>\s*<description>).*?(</description>)',
               lambda m: m.group(1) + THERMAL_TEXT + m.group(2), s, count=1, flags=re.S)
    i = s.index("</sharedSelectionEntries>")
    s = s[:i] + "".join(shared_entries()) + s[i:]
    s = hero_options(s)
    open(LIBRARY, "w", encoding="utf-8", newline="").write(s)
    print(f"{LIBRARY}: Saturnine Command Squad, concussion hammer and war axe added")
    print(f"Legion catalogues linked: {root_links()}")


if __name__ == "__main__":
    main()
