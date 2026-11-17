#!/usr/bin/env python3
"""Give the homebrew Fortifications already in the game system and the Ruinstorm catalogue the Fortification Unit Type.

usage: python3 homebrew/fortification_unit_types.py

The game system's own Fortifications carry the Fortification Unit Type category, and their Building, Emplacement or
Barricade Sub-type, on their root link. add_imperial_fortifications.py, add_chaos_fortifications.py and
add_ruinstorm_fortifications.py now give their Fortifications the same (expansion_tools.fortification_categories);
this adds them to the twelve those scripts added before (and to the official Hammerfall Bunker, which lacked
the Fortification Unit Type), in 2022 - Horus Heresy.gst and
2022 - Daemons - Daemons of the Ruinstorm.cat. The catalogues build_catalogue.py writes get them from the builder.
Running it again changes nothing."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import expansion_tools as et  # noqa: E402
from build_catalogue import TYPE_CATEGORIES, make_id  # noqa: E402

FILES = {
    "2022 - Horus Heresy.gst": ("gameSystem", [
        "Strategic Listening Post", "Automated Sentry Turret Battery", "Thermo-Plasma Conduit Tower",
        "Orbital Uplink Bunker", "Sacrificial Circle", "Daemon Pit", "Desecrated Stronghold",
        "Warp-Flayer Turret Battery", "Hammerfall Bunker"]),
    "2022 - Daemons - Daemons of the Ruinstorm.cat": ("catalogue", [
        "Warp-Breach Monolith", "Altar of Brass & Skulls", "Feculent Gnarlmaw", "Warp-Lightning Spire"]),
}


def main():
    for path, (tag, names) in FILES.items():
        root = ET.parse(path).getroot()
        ns = root.tag.split("}")[0] + "}"
        byid = {e.get("id"): e for e in root.iter() if e.get("id")}
        text = et.Text(path)
        added = 0
        for link in root.find(ns + "entryLinks"):
            if link.get("name") not in names:
                continue
            unit = byid[link.get("targetId")]
            types = " ".join(c.text or "" for c in unit.iter(ns + "characteristic") if c.get("name") == "Unit Type")
            have = {c.get("targetId") for c in link.iter(ns + "categoryLink")}
            new = []
            for word in et.FORTIFICATION_TYPES:
                cat, cname = TYPE_CATEGORIES[word]
                if re.search(r"\b" + word + r"\b", types) and cat not in have:
                    new.append(f'<categoryLink id="{make_id(link.get("id"), "type", cat)}" name="{cname}" '
                               f'hidden="false" targetId="{cat}" primary="false"/>')
            if not new:
                continue
            start = text.s.index(f'<entryLink id="{link.get("id")}"')
            end = text.s.index("</entryLink>", start)
            m = re.compile(r'([ \t]*)<categoryLink [^>]*targetId="a24f-12d8-36c1-f477"[^>]*/>(\r?\n)').search(
                text.s, start, end)
            indent, nl = m.group(1), m.group(2)
            text.s = text.s[:m.end()] + "".join(indent + c + nl for c in new) + text.s[m.end():]
            added += len(new)
            print(f"  {path}: {link.get('name')}: +{len(new)}")
        if added:
            text.bump(tag)
            text.save()
        print(f"{path}: {added} categories added")


if __name__ == "__main__":
    main()
