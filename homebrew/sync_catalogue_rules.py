#!/usr/bin/env python3
"""Give a catalogue's own copy of a rule the text the shared rules source has for it.

usage: python3 homebrew/sync_catalogue_rules.py

Some official catalogues define their own copy of a rule instead of linking to the game system's. Each copy
listed in SYNC has its description set to the rule's text in homebrew/source/additional-special-rules.md (the
paragraphs after its italic flavour line). Running it again changes nothing."""
import re
import sys

sys.path.insert(0, "homebrew")
from faq_tools import Ops, whole  # noqa: E402

SRC = "homebrew/source/additional-special-rules.md"
SYNC = [
    ("LI - Custodes", ["Auramite Talon", "Gravitic Repulsion", "Master of the Shield-Hosts", "Slayer of Kings"]),
    ("LI - Solar Auxilia", ["Solar Auxilia Command Tank"]),
    ("LI - Sisters Of Silence", ["Vigilant Covenant"]),
]


def source_rules():
    out = {}
    for block in re.split(r"^## ", open(SRC, encoding="utf-8").read(), flags=re.M)[1:]:
        name, _, body = block.partition("\n")
        paras = [p.strip() for p in body.strip().split("\n\n") if p.strip()]
        out[name.strip()] = "\n".join(p for p in paras if not (p.startswith("_") and p.endswith("_")))
    return out


def main():
    rules = source_rules()
    o = Ops()
    for f, names in SYNC:
        for name in names:
            o.text(f, "R:" + name, fn=whole(rules[name]))
    o.report()


if __name__ == "__main__":
    main()
