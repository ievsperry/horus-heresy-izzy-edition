#!/usr/bin/env python3
"""Give every twin-linked weapon the catalogues use its own entry.

usage: python3 homebrew/add_twin_linked.py [--dry-run]

Wherever a catalogue (or the game system) names a "Twin-linked <weapon>" and the master list has <weapon> but
not "Twin-linked <weapon>", a "Twin-linked <weapon>" row is added to homebrew/source/additional-weapons.md with
<weapon>'s profile plus the Twin-linked special rule, and add_gst_weapons.py then puts it in the game system.
Options that show a twin-linked weapon but link to the plain <weapon> (by their name, or by carrying a
Twin-linked rule link) are pointed at the new entry, and that extra rule link is dropped."""
import glob
import html
import re
import subprocess
import sys

SRC = "homebrew/source/additional-weapons.md"
GST = "2022 - Horus Heresy.gst"
DRY = "--dry-run" in sys.argv
HEADING = "## Twin-linked Weapons"
TL = re.compile(r"twin[- ]linked ", re.I)


def norm(name):
    return re.sub(r"\s+", " ", html.unescape(name).replace("’", "'")).strip().lower()


def md_rows(text):
    """{weapon: [(profile, range, str, ap, type)]} from the master list."""
    rows = {}
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith("| Weapon") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        parent = cells[0].split(" - ")[0]
        rows.setdefault(norm(parent), []).append(tuple(cells))
    return rows


def gst_weapons(gst):
    """{weapon: (entry id, [(profile, range, str, ap, type)])} for the game system's shared weapons."""
    a, b = gst.find("<sharedSelectionEntries>"), gst.find("</sharedSelectionEntries>")
    out = {}
    for m in re.finditer(r'\n    <selectionEntry ([^>]*)>(.*?)\n    </selectionEntry>', gst[a:b], re.S):
        name = html.unescape(re.search(r'name="([^"]+)"', m.group(1)).group(1))
        eid = re.search(r'\bid="([^"]+)"', m.group(1)).group(1)
        profs = []
        for p in re.finditer(r'<profile [^>]*name="([^"]+)"[^>]*typeName="Weapon"[^>]*>(.*?)</profile>', m.group(2), re.S):
            ch = dict(re.findall(r'<characteristic name="(\w+)"[^>]*>(.*?)</characteristic>', p.group(2), re.S))
            profs.append((html.unescape(p.group(1)), *(html.unescape(ch.get(k, "")) for k in ("Range", "Strength", "AP", "Type"))))
        if profs:
            out[norm(name)] = (eid, profs)
    return out


def with_tl(profile, weapon, single):
    """The twin-linked row; a weapon with several profiles keeps them together as "Twin-linked X - profile"."""
    name, rng, s, ap, typ = profile
    if "twin-linked" not in typ.lower():
        typ = typ + ", Twin-linked" if typ else "Twin-linked"
    if single or " - " in name:
        return ("Twin-linked " + name, rng, s, ap, typ)
    return (f"Twin-linked {weapon} - {name}", rng, s, ap, typ)


def files():
    return [GST] + sorted(f for f in glob.glob("*.cat") if not f.startswith("Homebrew - "))


def main():
    text = open(SRC, encoding="utf-8").read()
    md = md_rows(text)
    gst = open(GST, encoding="utf-8", newline="").read()
    gw = gst_weapons(gst)
    known = set(md) | set(gw)

    # every "Twin-linked X" the data names, whose X the master list has
    wanted, shown = {}, {}
    for f in files():
        for m in re.finditer(r'(?:name|value)="([^"]*)"', open(f, encoding="utf-8").read()):
            n = html.unescape(m.group(1))
            hit = TL.search(n)
            if not hit:
                continue
            rest = n[hit.end():].strip()
            for cand in (rest, rest[:-1], re.sub(r"es$", "", rest)):
                if norm(cand) in known:
                    base = norm(cand)
                    if "twin-linked " + base not in known:
                        wanted[base] = md.get(base) or gw[base][1]
                        shown[base] = cand.strip()
                    break

    lines = []
    for base, profiles in sorted(wanted.items()):
        for p in profiles:
            lines.append("| " + " | ".join(with_tl(p, shown[base], len(profiles) == 1)) + " |")
    if lines:
        print("adding:", ", ".join("Twin-linked " + shown[b] for b in sorted(wanted)))
        if HEADING not in text:
            block = (f"\n{HEADING}\n\nA twin-linked weapon is its weapon with the Twin-linked special rule.\n\n"
                     "| Weapon | Range | Str | AP | Type |\n|---|---|---|---|---|\n")
            i = text.find("\n# Melee Weapons")
            text = text[:i] + block + "\n".join(lines) + "\n" + text[i:] if i >= 0 else text + block + "\n".join(lines) + "\n"
        else:
            i = text.index(HEADING)
            j = text.find("\n## ", i + 1)
            j = j if j >= 0 else text.find("\n# ", i + 1)
            text = text[:j].rstrip("\n") + "\n" + "\n".join(lines) + "\n" + text[j:]
        if not DRY:
            open(SRC, "w", encoding="utf-8").write(text)
            subprocess.run([sys.executable, "homebrew/add_gst_weapons.py"], check=True, stdout=subprocess.DEVNULL)
    else:
        print("no new twin-linked weapons")
    if DRY:
        return

    # point twin-linked options at their own entry
    gst = open(GST, encoding="utf-8", newline="").read()
    gw = gst_weapons(gst)
    pairs = {gw[b][0]: gw["twin-linked " + b][0] for b in gw if "twin-linked " + b in gw}
    names = {gw[b][0]: b for b in gw}
    moved = 0
    for f in files():
        s = open(f, encoding="utf-8", newline="").read()
        out, pos = [], 0
        for m in re.finditer(r'<entryLink [^>]*targetId="([^"]+)"[^>]*?(/>|>)', s):
            if m.group(1) not in pairs or m.start() < pos:
                continue
            end = m.end() if m.group(2) == "/>" else s.index("</entryLink>", m.end()) + len("</entryLink>")
            blk = s[m.start():end]
            if blk.count("<entryLink ") > 1:
                continue
            shown = " ".join(re.findall(r'name="([^"]*)"', blk[:blk.find(">")]) +
                             re.findall(r'field="name" value="([^"]*)"', blk))
            tl_link = re.search(r'\s*<infoLink [^>]*name="Twin-linked"[^>]*/>', blk)
            if not (TL.search(html.unescape(shown)) and names[m.group(1)] in norm(shown)) and not tl_link:
                continue
            new = blk.replace(f'targetId="{m.group(1)}"', f'targetId="{pairs[m.group(1)]}"', 1)
            if tl_link:
                new = new.replace(tl_link.group(0), "", 1)
                new = re.sub(r"\s*<infoLinks>\s*</infoLinks>", "", new)
            out.append(s[pos:m.start()] + new)
            pos = end
            moved += 1
        if out:
            s = "".join(out) + s[pos:]
            open(f, "w", encoding="utf-8", newline="").write(s)
    print(f"pointed {moved} options at their twin-linked weapon")


if __name__ == "__main__":
    main()
