#!/usr/bin/env python3
"""The Vigil-Seeker Marksman Squad (homebrew/source/legio-custodes.md, Fast Attack) in the Legio Custodes catalogue.

Three to five Vigil-Seekers (Infantry, Skirmish), 10 points for the squad and 70 per model. Each carries the
official Misericord, Auric Demi-plate, Frag and Krak Grenades and the new Refraction Cloak, and an Exterminus Sniper
Rifle it may exchange for an Arae-Shrike Las-Fusil, Pyrithite Lance-Rifle, Adrathic Sniper Rifle or Heavy Adrastus
Bolt Caliver (all new, with the doc's profiles). One Vigil-Seeker may take a Pan-Spectral Tracker (it carries the
official Nuncio-Vox and Augury Scanner) and the official Meltabombs. Its rules are the official ones, and Silent
Reposition is added as the catalogue's own rule.

Its root entry is a copy of the Custodian Venatari Squad's Fast Attack entry (its Tharanatoi "only one Fast Attack
choice" limit, the Moritoi Fast Attack or Heavy Support category and the Hykanatoi rule), pointed at this unit.

usage: python3 homebrew/add_vigil_seekers.py   (refuses to run twice)"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
import protodreadnoughts as pd  # noqa: E402
from build_catalogue import add_constraint, add_cost, child, el, norm  # noqa: E402

CAT = "2022 - LI - Custodes.cat"
LIBS = ["2022 - Mech Library.cat", "2022 - LI - Assassins.cat"]   # the libraries the catalogue imports
NAME, MODEL = "Vigil-Seeker Marksman Squad", "Vigil-Seeker"
KEY = "vigil-seekers"
VENATARI, VENATARI_FA_ROOT = "4c7e-42e0-1c1e-5ba9", "9fdd-741c-affb-289a"

CATEGORIES = [("ccca-a9de-0cd9-f8be", "Legio Custodes"), ("8b4f-bfe2-ce7b-f1b1", "Infantry Unit Type"),
              ("59a4-7b61-600a-c457", "Skirmish Sub-type")]
RULES = [("13d1-9270-6539-08ed", "Chosen Warriors", None), ("6998-b328-c080-5341", "Legio Custodes", None),
         ("d1de-a45d-2b9b-c878", "Loyalist", None), ("7adf-ac9a-5035-522d", "Relentless", None),
         ("7989-1f2c-a43d-82ae", "Stubborn", None), ("676c-7b75-4b6f-9405", "Bulky (X)", "Bulky (3)"),
         ("4f41-4c04-9cd8-c5a1", "Marked For Death", None), ("9cd8-e726-5dbe-b106", "Sniper", None),
         ("0e32-5b92-a95a-8464", "Infiltrate", None), ("aacf-9a7e-982d-b793", "Scout", None),
         ("2b6f-bfec-759e-1746", "Move Through Cover", None)]
WARGEAR = [("73cb-1501-d39e-4f24", "Misericord"), ("e22b-48fd-2586-75d4", "Auric Demi-plate"),
           ("cf9c-327b-3449-00d7", "Frag Grenades"), ("99df-2421-acf7-a5ad", "Krak Grenades")]
NUNCIO, AUGURY, MELTABOMBS = "005e-aae6-ddac-bb45", "67ee-7338-3b74-04b4", "b9dd-3b21-f3f8-78e3"
ONE_SHOT = "df0c-5423-b892-491e"                        # the game system's "One Use/One Shot"

SILENT_REPOSITION = ("Once per game, at the end of your opponent's Shooting phase, if this unit was targeted by a "
                     "shooting attack and is not locked in combat, it may immediately make a normal Move (up to its "
                     "full Movement characteristic of 8\") as if it were the Movement phase (it cannot move within 1\" "
                     "of enemy models).")
REFRACTION = ("Grants Shrouded (5+), and enemy units targeting this unit with shooting attacks treat the range as 6\" "
              "further away than the actual distance.")
TRACKER = "Counts as both a Nuncio-vox and an Augury Scanner."

WEAPONS = [  # name, cost to exchange the Exterminus Sniper Rifle for it, [(profile, range, S, AP, type)]
    ("Exterminus Sniper Rifle", 0, [
        ("Exterminus Sniper Rifle - (Standard Bolt)", '48"', "5", "4", "Heavy 1, Sniper, Rending (5+), Pinning, "
                                                                       "Shell Shock (1)"),
        ("Exterminus Sniper Rifle - (Banestrike)", '36"', "5", "3", "Heavy 1, Sniper, Breaching (5+), "
                                                                   "Murderous Strike (5+), Pinning"),
        ("Exterminus Sniper Rifle - (Hellfire)", '36"', "5", "4", 'Heavy 1, Blast (3"), Ignores Cover, Pinning')]),
    ("Arae-Shrike Las-Fusil", 10, [(None, '60"', "8", "2", "Heavy 1, Sunder")]),
    ("Pyrithite Lance-Rifle", 15, [(None, '24"', "8", "1", "Heavy 1, Armourbane (Melta), Lance")]),
    ("Adrathic Sniper Rifle", 15, [(None, '48"', "6", "2", "Heavy 1, Sniper, Armourbane (Ranged), Gets Hot, "
                                                           "Instant Death, Pinning")]),
    ("Heavy Adrastus Bolt Caliver", 15, [
        ("Heavy Adrastus Bolt Caliver - (Bolt Volley)", '48"', "5", "4", "Heavy 5, Pinning, Rupture (6+)"),
        ("Heavy Adrastus Bolt Caliver - (Disintegrator)", '36"', "5", "2", "Heavy 2, Instant Death, Gets Hot, One Shot, "
                                                                           "Rupture (6+)")]),
]


def mid(*k):
    return pd.mid(KEY, *k)


def link(parent, target, name, key, mn=1, mx=1, cost=None):
    l = el(child(parent, "entryLinks"), "entryLink", id=mid("link", *key), name=name, hidden=False, collective=False,
           import_=True, targetId=target, type="selectionEntry")
    if mn:
        add_constraint(l, "min", mn, mid(*key, "min"))
    if mx:
        add_constraint(l, "max", mx, mid(*key, "max"))
    if cost is not None:
        add_cost(l, cost)
    return l


def root_entry(cat, uid):
    """The Venatari's Fast Attack root entry, every id renewed, pointed at this unit."""
    i = cat.s.index(f'id="{VENATARI_FA_ROOT}"')
    start = cat.s.rfind("<entryLink", 0, i)
    end = cat.s.index("</entryLink>", start) + len("</entryLink>")
    block = cat.s[start:end]
    for old in set(re.findall(r'\bid="([^"]+)"', block)):
        block = block.replace(old, mid("root", old))
    block = block.replace(VENATARI, uid).replace('name="Custodian Venatari Squad"', f'name="{NAME}"')
    return block


def main():
    cat = et.Text(CAT)
    if f'name="{NAME}"' in cat.s:
        sys.exit(f"{CAT} already has the {NAME}")
    entries, rules = pd.index([pd.GST] + LIBS + [CAT])
    rules[norm("One Shot")] = ONE_SHOT
    ctx = pd.Ctx(KEY, entries, rules)
    rule = ET.Element("rule", {"id": mid("rule", "Silent Reposition"), "name": "Silent Reposition", "hidden": "false"})
    el(rule, "description").text = SILENT_REPOSITION
    weapons = {name: pd.weapon(ctx, name, profiles) for name, _, profiles in WEAPONS}
    cloak = pd.wargear(ctx, "Refraction Cloak", REFRACTION, ["Shrouded (X)"])
    tracker = pd.wargear(ctx, "Pan-Spectral Tracker", TRACKER)
    link(tracker, NUNCIO, "Nuncio-Vox", ("tracker", "nuncio"))
    link(tracker, AUGURY, "Augury Scanner", ("tracker", "augury"))

    uid = mid("unit")
    u = ET.Element("selectionEntry", {"id": uid, "name": NAME, "hidden": "false", "collective": "false",
                                      "import": "true", "type": "unit"})
    for cid, cname in CATEGORIES:
        el(child(u, "categoryLinks"), "categoryLink", id=mid("cat", cname), name=cname, hidden=False, targetId=cid,
           primary=False)
    m = el(child(u, "selectionEntries"), "selectionEntry", id=mid("model"), name=MODEL, hidden=False, collective=False,
           import_=True, type="model")
    add_constraint(m, "min", 3, mid("model", "min"))
    add_constraint(m, "max", 5, mid("model", "max"))
    p = el(child(m, "profiles"), "profile", id=mid("profile"), name=MODEL, hidden=False, typeId=pd.UNIT_PROFILE[0],
           typeName=pd.UNIT_PROFILE[1])
    cs = el(p, "characteristics")
    for (cname, cid), v in zip(bc.UNIT_CHARS, ["Infantry (Skirmish)", "8", "5", "5", "5", "5", "2", "5", "3", "10", "3+"]):
        el(cs, "characteristic", name=cname, typeId=cid).text = v
    for rid, rname, shown in RULES + [(rule.get("id"), "Silent Reposition", None)]:
        il = el(child(m, "infoLinks"), "infoLink", id=mid("info", rname), name=rname, hidden=False, targetId=rid,
                type="rule")
        if shown:
            el(el(il, "modifiers"), "modifier", type="set", field="name", value=shown)
    for wid, wname in WARGEAR + [(cloak.get("id"), "Refraction Cloak")]:
        link(m, wid, wname, ("wargear", wname))
    g = pd.group(m, "Sniper Rifle", (KEY, "rifle"), 1, 1)
    first = None
    for name, cost, _ in WEAPONS:
        l = link(g, weapons[name].get("id"), name, ("rifle", name), mn=None, mx=1, cost=cost)
        first = first if first is not None else l
    g.set("defaultSelectionEntryId", first.get("id"))
    for tid, tname, cost in ((tracker.get("id"), "Pan-Spectral Tracker", 20), (MELTABOMBS, "Meltabombs", 10)):
        l = link(m, tid, tname, ("upgrade", tname), mn=None, mx=1, cost=cost)       # one Vigil-Seeker in the unit
        add_constraint(l, "max", 1, mid("upgrade", tname, "unit"), scope=uid, children=True)
    add_cost(m, 70)
    add_cost(u, 10)

    cat.add_top("sharedSelectionEntries", ctx.new + [u])
    cat.add_top("sharedRules", [rule])
    i = cat.s.index(cat.nl + "  </entryLinks>") + len(cat.nl)          # the end of the catalogue's root entries
    cat.s = cat.s[:i] + "    " + root_entry(cat, uid) + cat.nl + cat.s[i:]
    cat.bump("catalogue")
    cat.save()
    print(f"{CAT}: {NAME}, {len(ctx.new)} weapons and wargear, 1 rule")


if __name__ == "__main__":
    main()
