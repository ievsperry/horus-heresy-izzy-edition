#!/usr/bin/env python3
"""Give the Sisters of Silence expansion units the official weapons and wargear they name.

usage: python3 homebrew/fix_sisters_of_silence_links.py

add_sisters_of_silence.py moved the doc's units into 2022 - LI - Sisters Of Silence.cat, linking the official
entries for what the doc profiles itself. What the doc only names (it leaves the profile to the official books:
Execution Blade, Vratine Bolter, Corvae Las-Pulser, ...) stayed behind as empty entries with no profile. This
points each of those at the official entry, or, where that entry is in a catalogue the Sisters of Silence one
does not import (Legio Custodes), copies its profile in:

- linked to the official entry: Execution Blade, Proteus Neuro-lash, Voidscale Cloak, Vratine Bolter, Compression
  Tanks, Hellion Heavy Cannon Array, Vratine Missile Launcher, Charnabal Weapon (game system), Melta Bombs (the
  game system's Meltabombs) and Pintle Mounted Snare Cannon (the Snare Cannon);
- given the Legio Custodes profile: Corvae Las-Pulser, Solarite Power Lance, Spiculus Bolt Launcher and the
  Venatari Jump Harness (which also gives Bulky (2), as the doc says);
- Twin-Linked Vratine Bolter, Twin-Linked and Centreline Mounted Twin-Linked Corvae Las-Pulser: the weapon's
  profile and Twin-linked;
- Two Power Weapons: two of the game system's Power Weapon picks; Deep Strike: the game system's rule.

It does nothing on a catalogue that has no such empty entries left."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
from build_catalogue import make_id  # noqa: E402

CAT = "2022 - LI - Sisters Of Silence.cat"
CUSTODES = "2022 - LI - Custodes.cat"
NS = "{http://www.battlescribe.net/schema/catalogueSchema}"
PTS = "d2ee-04cb-5f8a-2642"
TWIN_LINKED = "8542-ee9d-e2fa-52fe"
BULKY = "676c-7b75-4b6f-9405"
DEEP_STRIKE = "f1e1-986f-c783-ca9e"
POWER_WEAPON = "d2db-7598-f55f-86fe"  # the game system's Power Weapon pick

LINKED = {"Execution Blade": "adc6-3519-204d-2921", "Proteus Neuro-Lash": "4d36-dac5-86a1-46cc",
          "Voidscale Cloak": "bd74-a0c5-cee0-bb03", "Vratine Bolter": "b48a-f5cb-983d-3832",
          "Compression Tanks": "3ac3-045d-bc0e-d7fe", "Hellion Heavy Cannon Array": "a17e-c567-c602-892e",
          "Vratine Missile Launcher": "0ee4-7a2e-804a-a934", "Charnabal Weapon": "e749-ba9b-bb76-a7d9",
          "Melta Bombs": "b9dd-3b21-f3f8-78e3", "Pintle Mounted Snare Cannon": "d267-639b-ec89-95e2"}
COPIED = {"Corvae Las-Pulser": "94ed-c2ef-d612-1ef9", "Solarite Power Lance": "50a3-987d-8087-4708",
          "Spiculus Bolt Launcher": "7346-97b2-65e8-f3b4", "Venatari Jump Harnesses": "7cf8-3f52-2876-60e9"}
TWINS = {"Twin-Linked Vratine Bolter": "Vratine Bolter", "Twin-Linked Corvae Las-Pulser": "Corvae Las-Pulser",
         "Centreline Mounted Twin-Linked Corvae Las-Pulser": "Corvae Las-Pulser"}
VRATINE_BOLTER_PROFILE = "a2be-5af6-49b2-8ec5"


def xml(tag, attrs, kids=(), text=None):
    a = "".join(f' {k}="{v}"' for k, v in attrs.items())
    if text is not None:
        return f"<{tag}{a}>{text}</{tag}>"
    if not kids:
        return f"<{tag}{a}/>"
    return [f"<{tag}{a}>", *kids, f"</{tag}>"]


def lines(node, depth, nl):
    if isinstance(node, str):
        return [" " * depth + node]
    out = [" " * depth + node[0]]
    for k in node[1:-1]:
        out += lines(k, depth + 2, nl)
    return out + [" " * depth + node[-1]]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def custodes_entry(eid):
    root = ET.parse(CUSTODES).getroot()
    return next(e for e in root.iter(NS + "selectionEntry") if e.get("id") == eid)


def profile_xml(p, key):
    chars = [xml("characteristic", {"name": c.get("name"), "typeId": c.get("typeId")}, text=esc(c.text or ""))
             for c in p.iter(NS + "characteristic")]
    return xml("profile", {"name": p.get("name"), "typeId": p.get("typeId"), "typeName": p.get("typeName"),
                           "hidden": "false", "id": make_id(key, "profile", p.get("name"))},
               [xml("characteristics", {}, chars)])


def info(key, name, target, kind="rule", value=None):
    attrs = {"name": name, "hidden": "false", "id": make_id(key, "info", name, value or ""), "targetId": target,
             "type": kind}
    if value:
        return xml("infoLink", attrs, [xml("modifiers", {}, [xml("modifier", {"type": "set", "field": "name",
                                                                             "value": value})])])
    return xml("infoLink", attrs)


def main():
    s = open(CAT, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    empties = dict((m.group(2), m.group(3)) for m in re.finditer(
        r'( *)<selectionEntry type="upgrade" import="true" name="([^"]+)" hidden="false" id="([^"]+)"/>', s))
    if not empties:
        sys.exit(f"{CAT} has no empty entries left")
    corvae_profile = None
    for name, eid in empties.items():
        key = eid
        pat = re.compile(r'( *)<selectionEntry type="upgrade" import="true" name="' + re.escape(name) +
                         r'" hidden="false" id="' + eid + r'"/>' + re.escape(nl))
        if name in LINKED:
            s = pat.sub("", s)
            for attr in ("targetId", "childId", "defaultSelectionEntryId"):
                s = s.replace(f'{attr}="{eid}"', f'{attr}="{LINKED[name]}"')
            continue
        profiles, infos, links = [], [], []
        if name in COPIED:
            src = custodes_entry(COPIED[name])
            for p in src.findall(f"{NS}profiles/{NS}profile"):
                profiles.append(profile_xml(p, key))
                if name == "Corvae Las-Pulser":
                    corvae_profile = make_id(key, "profile", p.get("name"))
            for i in src.findall(f"{NS}infoLinks/{NS}infoLink"):
                infos.append(info(key, i.get("name"), i.get("targetId")))
            if name == "Venatari Jump Harnesses":
                infos.append(info(key, "Bulky (X)", BULKY, value="Bulky (2)"))
        elif name in TWINS:
            continue  # after the Corvae Las-Pulser has its profile
        elif name == "Two Power Weapons":
            links.append(xml("entryLink", {"import": "true", "name": "Power Weapon", "hidden": "false",
                                           "id": make_id(key, "power weapon"), "type": "selectionEntry",
                                           "targetId": POWER_WEAPON},
                             [xml("constraints", {}, [
                                 xml("constraint", {"type": "min", "value": "2", "field": "selections",
                                                    "scope": "parent", "shared": "true", "id": make_id(key, "min"),
                                                    "percentValue": "false", "includeChildSelections": "false",
                                                    "includeChildForces": "false"}),
                                 xml("constraint", {"type": "max", "value": "2", "field": "selections",
                                                    "scope": "parent", "shared": "true", "id": make_id(key, "max"),
                                                    "percentValue": "false", "includeChildSelections": "false",
                                                    "includeChildForces": "false"})])]))
        elif name == "Deep Strike":
            infos.append(info(key, "Deep Strike", DEEP_STRIKE))
        else:
            sys.exit(f"no fix for the empty entry {name}")
        s = fill(s, pat, name, eid, profiles, infos, links, nl)
    for name, base in TWINS.items():
        if name not in empties:
            continue
        eid = empties[name]
        pat = re.compile(r'( *)<selectionEntry type="upgrade" import="true" name="' + re.escape(name) +
                         r'" hidden="false" id="' + eid + r'"/>' + re.escape(nl))
        prof = VRATINE_BOLTER_PROFILE if base == "Vratine Bolter" else corvae_profile
        infos = [info(eid, base, prof, kind="profile"), info(eid, "Twin-linked", TWIN_LINKED)]
        s = fill(s, pat, name, eid, [], infos, [], nl)
    open(CAT, "w", encoding="utf-8", newline="").write(s)


def fill(s, pat, name, eid, profiles, infos, links, nl):
    kids = []
    if profiles:
        kids.append(xml("profiles", {}, profiles))
    if infos:
        kids.append(xml("infoLinks", {}, infos))
    if links:
        kids.append(xml("entryLinks", {}, links))
    kids.append(xml("costs", {}, [xml("cost", {"name": "Pts", "typeId": PTS, "value": "0"})]))
    m = pat.search(s)
    if not m:
        sys.exit(f"{name} not found")
    node = xml("selectionEntry", {"type": "upgrade", "import": "true", "name": name, "hidden": "false", "id": eid},
               kids)
    text = nl.join(lines(node, len(m.group(1)), nl)) + nl
    return s[:m.start()] + text + s[m.end():]


if __name__ == "__main__":
    main()
