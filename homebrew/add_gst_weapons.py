#!/usr/bin/env python3
"""Apply homebrew/source/additional-weapons.md to the game system and every catalogue.

usage: python3 homebrew/add_gst_weapons.py [--dry-run]

Every weapon profile in the game system and the catalogues whose name matches a row (ignoring case and
punctuation) is updated to that row's Range, Strength, AP and Type; a melee row only updates melee
profiles and a ranged row only ranged ones. A weapon the game system has no entry for is added to its
shared selection entries, so every catalogue can link to it. The Extrinsica Melee Weapons also get their
points, a shared rule and a category that allows one per army."""
import glob
import hashlib
import re
import sys
from xml.sax.saxutils import escape, quoteattr

SRC = "homebrew/source/additional-weapons.md"
GST = "2022 - Horus Heresy.gst"
DRY = "--dry-run" in sys.argv
WEAPON_TYPE = "1a1a-e592-2849-a5c0"
CHARS = [("Range", "95ba-cda7-b831-6066"), ("Strength", "24d9-b8e1-a355-2458"), ("AP", "f7a6-e0d8-7973-cd8d"),
         ("Type", "2f86-c8b4-b3b4-3ff9")]
PTS = "d2ee-04cb-5f8a-2642"
ALIASES = {"fellblade accelerator cannon": "fellblade accelerator autocannon",
           "whirlwind missile launcher talonis he missile": "talonis he missile"}


def make_id(*parts):
    h = hashlib.md5(("gst weapon|" + "|".join(parts)).encode("utf-8")).hexdigest()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def norm(name):
    n = name.replace("&apos;", "'").replace("’", "'").lower()
    n = re.sub(r"[()\-–]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    for a, b in ALIASES.items():
        if n.startswith(a):
            n = b + n[len(a):]
    return n


def parse(text):
    """[(weapon, [(profile, range, str, ap, type)], cost, extrinsica)] in source order."""
    weapons, cost, extrinsica = [], None, False
    for line in text.split("\n"):
        if line.startswith("## "):
            extrinsica = line.startswith("## Extrinsica")
            cost = None
        m = re.match(r"\*\*Cost:\*\* \+(\d+) points", line)
        if m:
            cost = int(m.group(1))
        if not line.startswith("| ") or line.startswith("| Weapon"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        name, rng, s, ap, typ = cells
        parent = name.split(" - ")[0] if " - " in name else name
        if weapons and weapons[-1][0] == parent and " - " in name:
            weapons[-1][1].append((name, rng, s, ap, typ))
        else:
            weapons.append((parent, [(name, rng, s, ap, typ)], cost, extrinsica))
    return weapons


def files():
    # the homebrew catalogues are built from homebrew/source/*.md, so their weapons are changed there
    return [GST] + sorted(f for f in glob.glob("*.cat") if not f.startswith("Homebrew - "))


PROFILE = re.compile(r'(<profile [^>]*?name="([^"]+)"[^>]*?typeId="' + WEAPON_TYPE + r'"[^>]*>)(.*?)(</profile>)', re.S)


def is_melee(rng):
    return rng.strip() in ("-", "")


def char(body, cname):
    m = re.search(r'<characteristic name="' + cname + r'"[^>]*>(.*?)</characteristic>|<characteristic name="' + cname + r'"[^>]*/>', body, re.S)
    return (m.group(1) or "") if m else None


def set_char(body, cname, value):
    v = escape(value)
    new, n = re.subn(r'(<characteristic name="' + cname + r'"[^>]*?)(?:/>|>.*?</characteristic>)',
                     lambda m: m.group(1).rstrip("/") + ">" + v + "</characteristic>", body, count=1, flags=re.S)
    return new


def main():
    weapons = parse(open(SRC, encoding="utf-8").read())
    rows = {norm(p[0]): p for w in weapons for p in w[1]}
    texts = {f: open(f, encoding="utf-8", newline="").read() for f in files()}
    updated, seen, seen_gst = [], set(), set()
    for f, s in texts.items():
        def fix(m):
            head, pname, body, tail = m.groups()
            row = rows.get(norm(pname))
            if not row:
                return m.group(0)
            cur_range = char(body, "Range")
            if cur_range is None or is_melee(cur_range) != is_melee(row[1]):
                return m.group(0)
            seen.add(norm(pname))
            if f == GST:
                seen_gst.add(norm(pname))
            new = body
            for (cname, _), v in zip(CHARS, row[1:]):
                new = set_char(new, cname, v)
            if new != body:
                updated.append((f, pname))
            return head + new + tail
        texts[f] = PROFILE.sub(fix, s)

    # the game system's own weapons, by entry name
    gst = texts[GST]
    gst_names = {norm(m.group(1)) for m in re.finditer(r'<selectionEntry [^>]*?name="([^"]+)"', gst)}
    nl = "\r\n" if "\r\n" in gst else "\n"
    added = []
    blocks = []
    extrinsica_cat = make_id("category", "Extrinsica Melee Weapon")
    extrinsica_rule = make_id("rule", "Extrinsica Melee Weapons")
    for name, profiles, cost, extr in weapons:
        if norm(name) in gst_names or make_id("entry", name) in gst or any(norm(p[0]) in seen_gst for p in profiles):
            continue
        eid = make_id("entry", name)
        shown = re.sub(r" \(Melee\)$", "", name)  # "Shock Lance (Melee)": the entry is the Shock Lance
        b = [f'    <selectionEntry id="{eid}" name={quoteattr(shown)} hidden="false" collective="false" import="true" type="upgrade">']
        if extr:
            b += ["      <constraints>",
                  f'        <constraint field="selections" scope="parent" value="1" percentValue="false" shared="true" includeChildSelections="false" includeChildForces="false" id="{make_id("max", name)}" type="max"/>',
                  "      </constraints>"]
        b.append("      <profiles>")
        for pname, rng, st, ap, typ in profiles:
            b.append(f'        <profile id="{make_id("profile", pname)}" name={quoteattr(pname)} hidden="false" typeId="{WEAPON_TYPE}" typeName="Weapon">')
            b.append("          <characteristics>")
            for (cname, cid), v in zip(CHARS, (rng, st, ap, typ)):
                b.append(f'            <characteristic name="{cname}" typeId="{cid}">{escape(v)}</characteristic>')
            b.append("          </characteristics>")
            b.append("        </profile>")
        b.append("      </profiles>")
        if extr:
            b += ["      <infoLinks>",
                  f'        <infoLink id="{make_id("rule link", name)}" name="Extrinsica Melee Weapons" hidden="false" targetId="{extrinsica_rule}" type="rule"/>',
                  "      </infoLinks>",
                  "      <categoryLinks>",
                  f'        <categoryLink id="{make_id("cat link", name)}" name="Extrinsica Melee Weapon" hidden="false" targetId="{extrinsica_cat}" primary="false"/>',
                  "      </categoryLinks>"]
        if cost:
            b += ["      <costs>", f'        <cost name="Pts" typeId="{PTS}" value="{cost}"/>', "      </costs>"]
        b.append("    </selectionEntry>")
        blocks.append(nl.join(b) + nl)
        added.append(name)
    if blocks:
        i = gst.index("  </sharedSelectionEntries>")
        gst = gst[:i] + "".join(blocks) + gst[i:]
    # the Extrinsica rule and its one-per-army category
    if f'<categoryEntry id="{extrinsica_cat}"' not in gst:
        text = open(SRC, encoding="utf-8").read()
        sec = text.split("## Extrinsica Melee Weapons", 1)[1].split("### ", 1)[0].strip()
        desc = escape("\n".join(p.strip() for p in sec.split("\n\n") if p.strip())).replace("\n", nl)
        cat = (f'    <categoryEntry id="{extrinsica_cat}" name="Extrinsica Melee Weapon" hidden="false">{nl}'
               f"      <constraints>{nl}"
               f'        <constraint field="selections" scope="roster" value="1" percentValue="false" shared="true" includeChildSelections="true" includeChildForces="true" id="{make_id("one per army")}" type="max"/>{nl}'
               f"      </constraints>{nl}"
               f"    </categoryEntry>{nl}")
        i = gst.index("  </categoryEntries>")
        gst = gst[:i] + cat + gst[i:]
        rule = (f'    <rule id="{extrinsica_rule}" name="Extrinsica Melee Weapons" hidden="false">{nl}'
                f"      <description>{desc}</description>{nl}    </rule>{nl}")
        i = gst.index("  </sharedRules>")
        gst = gst[:i] + rule + gst[i:]
    texts[GST] = gst

    # a melee row for an entry that has only other profiles (Krak Grenades, Ripper Gun): its melee profile is added
    missing = []
    for name, profiles, cost, extr in weapons:
        if name in added or any(norm(p[0]) in seen for p in profiles):
            continue
        pname, rng, st, ap, typ = profiles[0]
        if not is_melee(rng):
            missing.append(name)
            continue
        label = pname + " (Melee)"
        for f, s in texts.items():
            nl2 = "\r\n" if "\r\n" in s else "\n"
            out, pos, n = [], 0, 0
            for m in re.finditer(r'<selectionEntry [^>]*?name="' + re.escape(name) + r'"[^>]*>', s, re.I):
                end = s.find("</selectionEntry>", m.end())
                close = s.find("</profiles>", m.end())
                if close < 0 or close > end or label in s[m.end():end]:
                    continue
                line = s.rfind(nl2, 0, close) + len(nl2)
                ind = s[line:close]
                prof = (f'{ind}  <profile id="{make_id("melee profile", f, str(m.start()), label)}" name={quoteattr(label)} hidden="false" typeId="{WEAPON_TYPE}" typeName="Weapon">{nl2}'
                        f"{ind}    <characteristics>{nl2}" +
                        "".join(f'{ind}      <characteristic name="{cn}" typeId="{cid}">{escape(v)}</characteristic>{nl2}'
                                for (cn, cid), v in zip(CHARS, (rng, st, ap, typ))) +
                        f"{ind}    </characteristics>{nl2}{ind}  </profile>{nl2}")
                out.append(s[pos:line] + prof)
                pos = line
                n += 1
                updated.append((f, label + " (added)"))
            if n:
                texts[f] = "".join(out) + s[pos:]
        if not any(lbl == label + " (added)" for _, lbl in updated):
            missing.append(name)
    print(f"updated {len(updated)} profiles in {len({f for f, _ in updated})} files; added {len(added)} weapons to the game system")
    for f, p in updated:
        print("  updated", f, "|", p)
    print("  added:", ", ".join(added))
    if missing:
        print("  not found anywhere:", ", ".join(missing))
    if not DRY:
        for f, s in texts.items():
            with open(f, "w", encoding="utf-8", newline="") as fh:
                fh.write(s)


if __name__ == "__main__":
    main()
