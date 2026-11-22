#!/usr/bin/env python3
"""Show the value of every (X) rule a wargear item links, as the official links do ("Fear (1)", not "Fear (X)").

A wargear item that grants a rule with a value (its text says, say, "gains Fear (1)") links the shared "Fear (X)"
rule; the official files give such a link a name modifier with the value, so the roster shows "Fear (1)". Some
entries made by the homebrew scripts (and two official ones) link the (X) rule bare. For each such link this finds
the value in the item's own wargear text and adds the name modifier; a link whose text gives no value is left as it is
and listed. Each changed file's revision goes up by one. Run from the repository root.
"""
import glob
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import expansion_tools as et


def tree(text):
    return ET.fromstring(re.sub(r' xmlns="[^"]+"', "", text, count=1))


def value_in(text, base):
    """The value given for rule `base` in text: 'Fear (1)' -> '1', 'Hatred (Psykers & Daemons)' -> that."""
    m = re.search(rf"\b{re.escape(base)}\s*\(([^()]+)\)", text, re.I)
    return m.group(1).strip() if m else None


def main():
    skipped = []
    for path in sorted(glob.glob("*.cat")):
        doc = et.Text(path)
        root = tree(doc.s)
        fixes = []
        for e in root.iter("selectionEntry"):
            texts = [c.text or "" for p in e.findall("profiles/profile") if p.get("typeName") == "Wargear Item"
                     for c in p.iter("characteristic")]
            text = " ".join(texts)
            if not text:
                continue
            for link in e.findall("infoLinks/infoLink"):
                name = link.get("name") or ""
                if link.get("type") != "rule" or not name.endswith("(X)") or link.find("modifiers") is not None:
                    continue
                base = name[:-3].strip()
                v = value_in(text, base)
                if v and v.upper() != "X":
                    fixes.append((link.get("id"), f"{base} ({v})", e.get("name")))
                else:
                    skipped.append((path, e.get("name"), name))
        if not fixes:
            continue
        nl = doc.nl
        for lid, shown, entry in fixes:
            m = re.search(rf'([ \t]*)<infoLink [^>]*?id="{re.escape(lid)}"[^>]*?(/?)>', doc.s)
            if not m:
                skipped.append((path, entry, f"link {lid} not found"))
                continue
            pad = m.group(1)
            mods = (f"{pad}  <modifiers>{nl}{pad}    <modifier type=\"set\" field=\"name\" value=\"{escape(shown, {chr(34): '&quot;'})}\"/>{nl}"
                    f"{pad}  </modifiers>{nl}")
            if m.group(2):                                   # <infoLink .../>: open it up
                new = m.group(0)[:-2].rstrip() + ">" + nl + mods + f"{pad}</infoLink>"
                doc.s = doc.s[:m.start()] + new + doc.s[m.end():]
            else:                                            # it has children already: put the modifiers first
                doc.s = doc.s[:m.end()] + nl + mods.rstrip(nl) + doc.s[m.end():]
            print(f"{path}: {entry}: {shown}")
        doc.bump("catalogue")
        doc.save()
    for s in skipped:
        print("left as it is (no value in the text):", " | ".join(s))


if __name__ == "__main__":
    main()
