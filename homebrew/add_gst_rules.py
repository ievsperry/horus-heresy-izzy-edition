#!/usr/bin/env python3
"""Add (or update) the special rules in homebrew/source/additional-special-rules.md as shared rules in
2022 - Horus Heresy.gst, so that every catalogue can link to them.

usage: python3 homebrew/add_gst_rules.py [source.md] [game system]

Each "## Name" section is one rule; its italic flavour line stays in the source and the paragraphs after
it become the rule's description. A rule is given a fixed id from its name, so running this again updates
the rules it added instead of adding them twice. A rule whose name the game system already has under
another id is left alone and reported."""
import hashlib
import re
import sys
from xml.sax.saxutils import escape, quoteattr

SRC = sys.argv[1] if len(sys.argv) > 1 else "homebrew/source/additional-special-rules.md"
GST = sys.argv[2] if len(sys.argv) > 2 else "2022 - Horus Heresy.gst"


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
        if xml_name in existing and existing[xml_name] != rid:
            print(f"kept the game system's own {name}")
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
