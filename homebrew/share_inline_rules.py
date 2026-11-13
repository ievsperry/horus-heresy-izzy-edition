"""Make the official catalogues' rule links resolve.

Some official files link (infoLink, type rule) to a rule that is defined inside an entry or category, not as a
shared rule, and a rule link only reaches shared rules. For each such rule this adds a shared copy, with a new id,
to the sharedRules of the file that defines it, and points the links at the copy; where a shared rule of the same
name is already reachable it links that instead. The original rules stay where they are. Each changed file's
revision goes up by one. Run from the repository root.
"""
import glob
import hashlib
import re
import xml.etree.ElementTree as ET


def new_id(key):
    h = hashlib.md5(("shared rule " + key).encode()).hexdigest()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def tree(text):
    return ET.fromstring(re.sub(r' xmlns="[^"]+"', "", text, count=1))


def main():
    files = sorted(glob.glob("*.cat") + glob.glob("*.gst"))
    text = {f: open(f, encoding="utf-8").read() for f in files}
    roots = {f: tree(t) for f, t in text.items()}
    shared, by_name, defined = {}, {}, {}
    for f, r in roots.items():
        sr = r.find("sharedRules")
        for x in (sr if sr is not None else []):
            shared[x.get("id")] = f
            by_name.setdefault(x.get("name"), []).append((f, x.get("id")))
    for f, r in roots.items():
        for x in r.iter("rule"):
            if x.get("id") not in shared:
                defined.setdefault(x.get("id"), (f, x.get("name")))
    ids = {r.get("id"): f for f, r in roots.items()}
    gst = next(f for f in files if f.endswith(".gst"))

    def reach(f):
        return {f, gst} | {ids.get(c.get("targetId")) for c in roots[f].findall("catalogueLinks/catalogueLink")}

    retarget = {}  # (linking file, old id) -> new id
    copies = {}  # old id -> new id (a shared copy in its defining file)
    for f, r in roots.items():
        if f.startswith("Homebrew"):
            continue
        for il in r.iter("infoLink"):
            t = il.get("targetId")
            if il.get("type") != "rule" or t in shared or t not in defined:
                continue
            deff, name = defined[t]
            alt = [i for g, i in by_name.get(name, []) if g in reach(f)]
            if alt:
                retarget[(f, t)] = alt[0]
            elif deff in reach(f):
                copies.setdefault(t, new_id(t))
                retarget[(f, t)] = copies[t]
    changed = set()
    for t, nid in copies.items():
        deff, name = defined[t]
        s = text[deff]
        block = re.search(r'([ \t]*)(<rule\b[^>]*\sid="%s"[^>]*?(?:/>|>.*?</rule>))' % re.escape(t), s, re.S)
        rule = block.group(2).replace(f'id="{t}"', f'id="{nid}"', 1)
        rule = re.sub(r"\n[ \t]*", "\n    ", rule)  # re-indent under sharedRules
        rule = re.sub(r"\n    (?=</rule>)", "\n    ", rule)
        if "<sharedRules>" in s:
            s = s.replace("</sharedRules>", f"  {rule}\n  </sharedRules>", 1)
        else:
            s = s.replace("</sharedSelectionEntryGroups>", f"</sharedSelectionEntryGroups>\n  <sharedRules>\n    {rule}\n  </sharedRules>", 1)
        text[deff] = s
        changed.add(deff)
    for (f, t), nid in retarget.items():
        s = text[f]
        s2 = re.sub(r'(<infoLink\b[^>]*type="rule"[^>]*)targetId="%s"' % re.escape(t), r'\1targetId="%s"' % nid, s)
        s2 = re.sub(r'(<infoLink\b[^>]*)targetId="%s"([^>]*type="rule")' % re.escape(t), r'\1targetId="%s"\2' % nid, s2)
        if s2 != s:
            text[f] = s2
            changed.add(f)
    for f in sorted(changed):
        s = text[f]
        s = re.sub(r'(<(?:catalogue|gameSystem) [^>]*revision=")(\d+)"', lambda m: f'{m.group(1)}{int(m.group(2)) + 1}"', s, count=1)
        open(f, "w", encoding="utf-8", newline="\n").write(s)
        print(f)
    print(len(copies), "shared copies,", len(retarget), "links retargeted")


if __name__ == "__main__":
    main()
