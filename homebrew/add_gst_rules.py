#!/usr/bin/env python3
"""Add (or update) the special rules in homebrew/source/additional-special-rules.md as shared rules in
2022 - Horus Heresy.gst, so that every catalogue can link to them.

usage: python3 homebrew/add_gst_rules.py [source.md] [game system] [--keep-existing]

Each "## Name" section is one rule; its italic flavour line stays in the source and the paragraphs after
it become the rule's description. A rule is given a fixed id from its name, so running this again updates
the rules it added instead of adding them twice. A rule whose name the game system already has under
another id has its text updated to the source's (wherever the game system holds it, such as a Unit Sub-type's
rule), unless --keep-existing is given."""
import hashlib
import re
import sys
from xml.sax.saxutils import escape, quoteattr

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
KEEP = "--keep-existing" in sys.argv
SRC = ARGS[0] if len(ARGS) > 0 else "homebrew/source/additional-special-rules.md"
GST = ARGS[1] if len(ARGS) > 1 else "2022 - Horus Heresy.gst"


def make_id(name):
    h = hashlib.md5(("gst rule|" + name).encode("utf-8")).hexdigest()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def rules(text):
    out = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        name, _, body = block.partition("\n")
        paras = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
        paras = [p for p in paras if not (p.startswith("_") and p.endswith("_"))]  # the flavour line
        out.append((name.strip(), "\n".join(paras)))
    return out


def main():
    with open(GST, encoding="utf-8", newline="") as f:
        gst = f.read()
    nl = "\r\n" if "\r\n" in gst else "\n"
    start = gst.index("<sharedRules>")
    end = gst.index("</sharedRules>")
    existing = {m.group(2): m.group(1) for m in
                re.finditer(r'<rule id="([^"]+)" name="([^"]+)"', gst[start:end])}
    added = updated = 0
    for name, desc in rules(open(SRC, encoding="utf-8").read()):
        rid = make_id(name)
        xml_name = escape(name, {'"': "&quot;"})
        body = escape(desc).replace("\n", nl)
        block = (f'    <rule id="{rid}" name={quoteattr(name)} hidden="false">{nl}'
                 f"      <description>{body}</description>{nl}"
                 f"    </rule>{nl}")
        # only the game system's shared rules and Unit Sub-type rules count; a rule of the same name inside an
        # option (Eye of the Storm, the White Scars Legiones Auxilia trait) is a different rule
        areas = [(gst.index(f"<{t}>"), gst.index(f"</{t}>")) for t in ("sharedRules", "categoryEntries") if f"<{t}>" in gst]
        own = [m for m in re.finditer(r'<rule [^>]*name="' + re.escape(xml_name) + r'"[^>]*>', gst)
               if f'id="{rid}"' not in m.group(0) and any(a < m.start() < b for a, b in areas)]
        if own:
            if KEEP:
                print(f"kept the game system's own {name}")
                continue
            for m in reversed(own):
                end = gst.index("</rule>", m.end())
                inner = gst[m.end():end]
                d = re.search(r"<description>.*?</description>|<description/>", inner, re.S)
                new_d = f"<description>{body}</description>"
                if d:
                    inner2 = inner[:d.start()] + new_d + inner[d.end():]
                else:
                    ind = re.search(r"\n(\s*)<", inner)
                    pad = ind.group(1) if ind else "      "
                    inner2 = inner.rstrip() + nl + pad + new_d + nl + pad[:-2] if inner.strip() else nl + "      " + new_d + nl + "    "
                if inner2 != inner:
                    gst = gst[:m.end()] + inner2 + gst[end:]
                    updated += 1
            continue
        m = re.search(r'    <rule id="' + rid + r'".*?</rule>' + re.escape(nl), gst, flags=re.S)
        if m:
            if m.group(0) != block:
                gst = gst[:m.start()] + block + gst[m.end():]
                updated += 1
            continue
        i = gst.index("  </sharedRules>")
        gst = gst[:i] + block + gst[i:]
        added += 1
    with open(GST, "w", encoding="utf-8", newline="") as f:
        f.write(gst)
    print(f"added {added}, updated {updated}")


if __name__ == "__main__":
    main()
