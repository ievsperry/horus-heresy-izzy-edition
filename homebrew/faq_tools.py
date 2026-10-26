"""Small text-level editing tools for the official game system and catalogues, used by the FAQ scripts.

Edits are made on the XML text with proper tag matching, so a file keeps its own formatting and only the
changed lines differ. Names are matched ignoring case, "&apos;" and curly apostrophes."""
import glob
import hashlib
import html
import re

GST = "2022 - Horus Heresy.gst"
PTS = "d2ee-04cb-5f8a-2642"
TAG = re.compile(r"<(/?)([A-Za-z]+)((?:[^>\"']|\"[^\"]*\"|'[^']*')*?)(/?)>")
ORDER = ["comment", "modifiers", "modifierGroups", "constraints", "profiles", "rules", "infoGroups", "infoLinks",
         "categoryLinks", "selectionEntries", "selectionEntryGroups", "entryLinks", "costs"]


def norm(name):
    return re.sub(r"\s+", " ", html.unescape(name).replace("’", "'").replace("‘", "'")).strip().lower()


def make_id(*parts):
    h = hashlib.md5(("faq|" + "|".join(parts)).encode("utf-8")).hexdigest()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


class Files:
    def __init__(self):
        self.paths = [GST] + sorted(f for f in glob.glob("*.cat") if not f.startswith("Homebrew - "))
        self.text = {p: open(p, encoding="utf-8", newline="").read() for p in self.paths}
        self.orig = dict(self.text)
        self.log = []
        self.rule_ids = {}
        for p in self.paths:
            for m in re.finditer(r'<rule id="([^"]+)" name="([^"]+)"', self.text[p]):
                self.rule_ids.setdefault(norm(m.group(2)), (p, m.group(1)))

    def short(self, path):
        return path.replace("2022 - ", "").replace(".cat", "").replace(".gst", "")

    def file(self, key):
        """A file by a short name ("Legiones Astartes", "LA - Salamanders", "gst")."""
        if key == "gst":
            return GST
        hits = [p for p in self.paths if self.short(p).lower() == key.lower()]
        if len(hits) != 1:
            raise KeyError(f"file {key}: {hits}")
        return hits[0]

    # ---- elements
    def span(self, path, start):
        """(start, end) of the element whose start tag begins at `start`."""
        s = self.text[path]
        depth = 0
        for m in TAG.finditer(s, start):
            if m.group(4):  # self-closing
                if depth == 0:
                    return start, m.end()
                continue
            depth += -1 if m.group(1) else 1
            if depth == 0:
                return start, m.end()
        raise ValueError("unclosed element")

    def find(self, path, name, tag=None, within=None, typ=None):
        """Start offsets of elements with this name (optionally a tag, inside a span, of a type)."""
        s = self.text[path]
        lo, hi = within or (0, len(s))
        out = []
        for m in TAG.finditer(s, lo, hi):
            if m.group(1) or (tag and m.group(2) != tag):
                continue
            a = re.search(r'\sname="([^"]*)"', m.group(3))
            if not a or norm(a.group(1)) != norm(name):
                continue
            if typ and not re.search(r'\stype="' + typ + '"', m.group(3)):
                continue
            out.append(m.start())
        return out

    def one(self, path, name, tag=None, within=None, typ=None, pick=None):
        hits = self.find(path, name, tag, within, typ)
        if pick is not None:
            return self.span(path, hits[pick])
        if len(hits) != 1:
            raise KeyError(f"{self.short(path)}: {len(hits)} x {tag or ''} '{name}'")
        return self.span(path, hits[0])

    def children(self, path, sp):
        """Direct children of an element: [(tag, start, end)]."""
        s = self.text[path]
        a, b = sp
        first = TAG.match(s, a)
        out, pos = [], first.end()
        while True:
            m = TAG.search(s, pos, b)
            if not m or m.group(1):
                break
            e = self.span(path, m.start())
            out.append((m.group(2), m.start(), e[1]))
            pos = e[1]
        return out

    def child(self, path, sp, tag):
        return next(((a, b) for t, a, b in self.children(path, sp) if t == tag), None)

    def attr(self, path, sp, name):
        m = re.search(r'\s' + name + r'="([^"]*)"', TAG.match(self.text[path], sp[0]).group(3))
        return m.group(1) if m else None

    # ---- writing
    def replace(self, path, a, b, new, what):
        s = self.text[path]
        if s[a:b] != new:
            self.text[path] = s[:a] + new + s[b:]
            self.log.append((self.short(path), what))

    def nl(self, path):
        return "\r\n" if "\r\n" in self.text[path] else "\n"

    def indent_of(self, path, pos):
        s = self.text[path]
        line = s.rfind("\n", 0, pos) + 1
        return s[line:pos] if s[line:pos].strip() == "" else ""

    def insert_child(self, path, sp, tag, xml_inner, what):
        """Add xml_inner (one or more elements) into the element's <tag> container, creating it in order."""
        s = self.text[path]
        nl = self.nl(path)
        ind = self.indent_of(path, sp[0])
        c = self.child(path, sp, tag)
        if c:
            close = s.rfind("</" + tag + ">", c[0], c[1])
            line = s.rfind("\n", 0, close) + 1
            if s[line:close].strip() == "":
                self.replace(path, line, line, "".join(ind + "    " + x + nl for x in xml_inner), what)
            else:
                self.replace(path, close, close, "".join(xml_inner), what)
            return
        kids = self.children(path, sp)
        after = [k for k in kids if k[0] in ORDER and ORDER.index(k[0]) > ORDER.index(tag)]
        block = (ind + "  <" + tag + ">" + nl + "".join(ind + "    " + x + nl for x in xml_inner) +
                 ind + "  </" + tag + ">" + nl)
        start_tag = TAG.match(s, sp[0])
        if start_tag.group(4):  # <x .../> becomes <x ...>...</x>
            head = s[sp[0]:start_tag.end() - 2].rstrip() + ">"
            self.replace(path, sp[0], sp[1], head + nl + block + ind + "</" + start_tag.group(2) + ">", what)
            return
        pos = (s.rfind("\n", 0, after[0][1]) + 1) if after else (s.rfind("\n", 0, s.rfind("</", sp[0], sp[1])) + 1)
        self.replace(path, pos, pos, block, what)

    # ---- edits
    def set_cost(self, path, sp, value, what):
        c = self.child(path, sp, "costs")
        if c:
            s = self.text[path]
            m = re.search(r'(<cost [^>]*typeId="' + PTS + r'"[^>]*value=")([^"]*)(")', s[c[0]:c[1]])
            if m:
                oldv = m.group(2)
                a = c[0] + m.start(2)
                self.replace(path, a, a + len(oldv), str(value), what)
                # a per-model option is priced again by an increment for each further model; keep it in step
                mods = self.child(path, sp, "modifiers")
                if mods:
                    s = self.text[path]
                    for t, x, y in self.children(path, mods):
                        mm = re.match(r'<modifier type="increment" field="' + PTS + r'" value="([^"]*)"', s[x:y])
                        if mm and float(mm.group(1)) == float(oldv):
                            self.replace(path, x + mm.start(1), x + mm.end(1), str(value), what)
                            break
                return
        self.insert_child(path, sp, "costs", [f'<cost name="Pts" typeId="{PTS}" value="{value}"/>'], what)

    def cost_of(self, path, sp):
        c = self.child(path, sp, "costs")
        if not c:
            return None
        m = re.search(r'typeId="' + PTS + r'"[^>]*value="([^"]*)"', self.text[path][c[0]:c[1]])
        return m.group(1) if m else None

    def set_char(self, path, profile_sp, char, value, what):
        s = self.text[path]
        a, b = profile_sp
        m = re.search(r'(<characteristic (?:[^>]*\s)?name="' + re.escape(char) + r'"[^>]*?)(?:/>|>(.*?)</characteristic>)', s[a:b], re.S)
        if not m:
            raise KeyError(f"no {char} in profile")
        new = m.group(1) + ">" + html.escape(str(value), quote=False).replace('"', "&quot;") + "</characteristic>"
        self.replace(path, a + m.start(), a + m.end(), new, what)

    def char_of(self, path, profile_sp, char):
        m = re.search(r'<characteristic (?:[^>]*\s)?name="' + re.escape(char) + r'"[^>]*?(?:/>|>(.*?)</characteristic>)',
                      self.text[path][profile_sp[0]:profile_sp[1]], re.S)
        return html.unescape(m.group(1) or "") if m else None

    def rule_link(self, name):
        """(id, real name) of a shared rule by name or by its '(X)' form."""
        n = norm(name)
        if n in self.rule_ids:
            return self.rule_ids[n][1], name
        base = re.sub(r"\s*\(.*\)$", "", n)
        for k, (p, rid) in self.rule_ids.items():
            if re.sub(r"\s*\(x\)$", "", k) == base:
                return rid, k
        raise KeyError(f"no rule {name}")

    def add_rule(self, path, sp, shown, what):
        """Give an entry a rule (as an infoLink), e.g. 'Hammer of Wrath (3)' links Hammer of Wrath (X)."""
        s = self.text[path]
        if re.search(r'<infoLink [^>]*name="' + re.escape(html.escape(shown, quote=False)) + '"', s[sp[0]:sp[1]]) or \
                re.search(r'value="' + re.escape(html.escape(shown, quote=False)) + '"', s[sp[0]:sp[1]]):
            return
        rid, real = self.rule_link(shown)
        lid = make_id(path, str(sp[0]), shown)
        real_name = next((m.group(1) for m in re.finditer(r'<rule id="' + rid + r'" name="([^"]+)"', "".join(self.text.values()))), shown)
        if norm(real_name) == norm(shown):
            x = f'<infoLink id="{lid}" name="{real_name}" hidden="false" targetId="{rid}" type="rule"/>'
        else:
            nl = self.nl(path)
            ind = self.indent_of(path, sp[0]) + "    "
            x = (f'<infoLink id="{lid}" name="{real_name}" hidden="false" targetId="{rid}" type="rule">{nl}'
                 f'{ind}  <modifiers>{nl}{ind}    <modifier type="set" field="name" value="{html.escape(shown, quote=False)}"/>{nl}'
                 f'{ind}  </modifiers>{nl}{ind}</infoLink>')
        self.insert_child(path, sp, "infoLinks", [x], what)

    def remove_rule(self, path, sp, name, what):
        """Drop an entry's infoLink to a rule (matched by link name or its shown name)."""
        s = self.text[path]
        il = self.child(path, sp, "infoLinks")
        if not il:
            raise KeyError("no infoLinks")
        for t, a, b in self.children(path, il):
            blk = s[a:b]
            nm = re.search(r'name="([^"]*)"', blk).group(1)
            shown = re.search(r'field="name" value="([^"]*)"', blk)
            if norm(nm) == norm(name) or (shown and norm(shown.group(1)) == norm(name)):
                line = s.rfind("\n", 0, a) + 1
                end = b + (len(self.nl(path)) if s[b:b + 2] in ("\r\n",) or s[b:b + 1] == "\n" else 0)
                self.replace(path, line if s[line:a].strip() == "" else a, end, "", what)
                return
        raise KeyError(f"no rule link {name}")

    def edit_text(self, path, sp, fn, what, char="Description"):
        """Change a rule's description, or a profile's text characteristic, with fn(old) -> new."""
        s = self.text[path]
        a, b = sp
        m = re.search(r"<description>(.*?)</description>", s[a:b], re.S) or \
            re.search(r'<characteristic (?:[^>]*\s)?name="' + char + r'"[^>]*>(.*?)</characteristic>', s[a:b], re.S)
        old = html.unescape(m.group(1)).replace("\r\n", "\n")
        new = fn(old)
        if new == old:
            return
        enc = html.escape(new, quote=False).replace('"', "&quot;").replace("\n", self.nl(path))
        self.replace(path, a + m.start(1), a + m.end(1), enc, what)

    def save(self):
        changed = [p for p in self.paths if self.text[p] != self.orig[p]]
        for p in changed:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(self.text[p])
        return changed


def sub(old, new):
    """fn(text): replace old with new once; already-new text is left alone."""
    def fn(t):
        if new in t:
            return t
        if old not in t:
            raise KeyError(f"text not found: {old[:70]}")
        return t.replace(old, new, 1)
    return fn


def append(extra):
    return lambda t: t if extra.strip() in t else t.rstrip() + "\n\n" + extra


def whole(new):
    return lambda t: new


ENTRY_TAGS = ("selectionEntry", "selectionEntryGroup", "entryLink")


class Ops:
    """FAQ operations by name path. Each call finds its element again, so earlier edits never leave a stale
    offset. A failed lookup is recorded and reported instead of stopping the run."""

    def __init__(self):
        self.F = Files()
        self.failed = []
        self.cats = {norm(m.group(2)): m.group(1) for m in re.finditer(
            r'<categoryEntry id="([^"]+)" name="([^"]+)"', self.F.text[GST])}

    def run(self, label, fn):
        try:
            fn()
        except Exception as e:  # noqa: BLE001 - every failure is listed at the end
            self.failed.append(f"{label}: {e}")

    # ---- lookup
    def at(self, f, *path):
        """Span of an element: the first name is a unit (or any entry, rule or profile of that name), each
        further name a descendant. A name may be prefixed P: (profile), R: (rule), G: (group), L: (link),
        or end in #n to take the n-th match."""
        F = self.F
        p = F.file(f)
        sp = None
        for i, raw in enumerate(path):
            name, pick = raw, None
            m = re.match(r"(.*)#(\d+)$", name)
            if m:
                name, pick = m.group(1), int(m.group(2))
            tag = None
            if name[:2] in ("P:", "R:", "G:", "L:", "E:"):
                tag = {"P:": "profile", "R:": "rule", "G:": "selectionEntryGroup", "L:": "entryLink",
                       "E:": "selectionEntry"}[name[:2]]
                name = name[2:]
            if tag:
                hits = F.find(p, name, tag, sp)
            elif i == 0:
                hits = F.find(p, name, "selectionEntry", sp, "unit") or \
                    [h for t in ENTRY_TAGS for h in F.find(p, name, t, sp)] or F.find(p, name, None, sp)
            else:
                hits = sorted(h for t in ENTRY_TAGS + ("profile",) for h in F.find(p, name, t, sp))
            if sp:
                hits = [h for h in hits if h != sp[0]]
            if not hits:
                raise KeyError(f"{f}: no '{name}' in {' > '.join(path[:i]) or 'file'}")
            if pick is None and i == 0 and len(hits) > 1 and not tag:
                raise KeyError(f"{f}: {len(hits)} x '{name}'")
            sp = F.span(p, sorted(hits)[pick or 0])
        return p, sp

    def all(self, f, name, tag):
        p = self.F.file(f)
        return p, self.F.find(p, name, tag)

    # ---- operations
    def cost(self, f, *path, v):
        def go():
            p, sp = self.at(f, *path)
            self.F.set_cost(p, sp, v, f"{' > '.join(path)}: {v} points")
        self.run(" > ".join(path), go)

    def price(self, f, unit, base, per=None, model=None, n=1):
        """A unit's points: `base` for its smallest size (n models of `model`), `per` each additional model."""
        def go():
            p, usp = self.at(f, unit)
            if model:
                p, msp = self.at(f, unit, model)
                per_ = per if per is not None else base
                self.F.set_cost(p, msp, per_, f"{unit} > {model}: {per_} points per model")
                p, usp = self.at(f, unit)
                self.F.set_cost(p, usp, base - n * per_, f"{unit}: {base} points")
            else:
                self.F.set_cost(p, usp, base, f"{unit}: {base} points")
        self.run(f"{unit} price", go)

    def char(self, f, *path, **chars):
        def go():
            p, sp = self.at(f, *path)
            for k, v in chars.items():
                k = {"Type": "Unit Type", "UT": "Unit Type", "Sv": "Save", "M": "Move", "Tr": "Transport Capacity"}.get(k, k)
                self.F.set_char(p, sp, k, v, f"{' > '.join(path)}: {k} {v}")
        self.run(" > ".join(path) + " chars", go)

    def chars_all(self, f, profile, **chars):
        """Every profile of this name in a file."""
        def go():
            p = self.F.file(f)
            n = len(self.F.find(p, profile, "profile"))
            if not n:
                raise KeyError(f"no profile {profile}")
            for i in range(n):
                sp = self.F.span(p, self.F.find(p, profile, "profile")[i])
                for k, v in chars.items():
                    k = {"UT": "Unit Type", "Sv": "Save", "M": "Move", "Tr": "Transport Capacity"}.get(k, k)
                    self.F.set_char(p, sp, k, v, f"{profile}: {k} {v}")
        self.run(profile + " chars", go)

    def category(self, f, *path, add=None, remove=None):
        def go():
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            for name in ([add] if add else []):
                cid = self.cats[norm(name)]
                if re.search(r'<categoryLink [^>]*targetId="' + cid + '"', s[sp[0]:sp[1]]):
                    continue
                cl = self.F.child(p, sp, "categoryLinks")
                if cl and re.search(r'targetId="' + cid + '"', s[cl[0]:cl[1]]):
                    continue
                x = (f'<categoryLink id="{make_id(p, " > ".join(path), name)}" name="{html.escape(name, quote=False)}" '
                     f'hidden="false" targetId="{cid}" primary="false"/>')
                self.F.insert_child(p, sp, "categoryLinks", [x], f"{' > '.join(path)}: + {name}")
            for name in ([remove] if remove else []):
                cid = self.cats[norm(name)]
                cl = self.F.child(p, sp, "categoryLinks")
                for t, a, b in (self.F.children(p, cl) if cl else []):
                    if f'targetId="{cid}"' in s[a:b]:
                        line = s.rfind("\n", 0, a) + 1
                        end = s.find("\n", b) + 1
                        self.F.replace(p, line, end, "", f"{' > '.join(path)}: - {name}")
                        break
        self.run(" > ".join(path) + " category", go)

    def rule(self, f, *path, add=(), remove=()):
        def go():
            for r in ([add] if isinstance(add, str) else add):
                p, sp = self.at(f, *path)
                self.F.add_rule(p, sp, r, f"{' > '.join(path)}: + {r}")
            for r in ([remove] if isinstance(remove, str) else remove):
                p, sp = self.at(f, *path)
                self.F.remove_rule(p, sp, r, f"{' > '.join(path)}: - {r}")
        self.run(" > ".join(path) + " rules", go)

    def text(self, f, *path, fn, char="Description"):
        def go():
            p, sp = self.at(f, *path)
            self.F.edit_text(p, sp, fn, f"{' > '.join(path)}: text", char)
        self.run(" > ".join(path) + " text", go)

    def rename(self, f, *path, to):
        def go():
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            m = TAG.match(s, sp[0])
            a = re.search(r'\sname="([^"]*)"', m.group(0))
            st = sp[0] + a.start(1)
            self.F.replace(p, st, st + len(a.group(1)), html.escape(to, quote=False), f"{' > '.join(path)}: renamed {to}")
        self.run(" > ".join(path) + " rename", go)

    def report(self):
        changed = self.F.save()
        print(f"{len(self.F.log)} changes in {len(changed)} files")
        for path, what in self.F.log:
            print(f"  {path}: {what}")
        if self.failed:
            print(f"\n{len(self.failed)} NOT APPLIED:")
            for x in self.failed:
                print("  " + x)
        return changed

    def shared_id(self, name, prefer=None):
        """Id of a shared selection entry by name: the given file first, then the game system, then any file."""
        order = ([self.F.file(prefer)] if prefer else []) + [GST] + self.F.paths
        for p in order:
            m = re.search(r'\n\s{4}<selectionEntry id="([^"]+)" name="' + re.escape(html.escape(name, quote=False)) + '"',
                          self.F.text[p], re.I)
            if m:
                return m.group(1), p
        raise KeyError(f"no shared entry {name}")

    def retarget(self, f, *path, to, shown=None):
        """Point an entry link at another shared entry (and rename it)."""
        def go():
            p, sp = self.at(f, *path)
            tid, _ = self.shared_id(to, f)
            s = self.F.text[p]
            head = TAG.match(s, sp[0]).group(0)
            new = re.sub(r'targetId="[^"]*"', f'targetId="{tid}"', head)
            new = re.sub(r'\sname="[^"]*"', f' name="{html.escape(shown or to, quote=False)}"', new, count=1)
            self.F.replace(p, sp[0], sp[0] + len(head), new, f"{' > '.join(path)}: now {shown or to}")
            # a link renamed by a modifier keeps showing the old weapon's name; drop that name modifier
            p, sp = self.at(f, *path[:-1], shown or to) if len(path) > 1 else self.at(f, shown or to)
            s = self.F.text[p]
            m = re.search(r'\s*<modifier type="set" field="name" value="[^"]*"/>', s[sp[0]:sp[1]])
            if m:
                self.F.replace(p, sp[0] + m.start(), sp[0] + m.end(), "", f"{shown or to}: name modifier dropped")
        self.run(" > ".join(path) + " retarget", go)

    def add_link(self, f, *path, to, shown=None, mn=1, mx=1, pts=None):
        """Give an entry a link to a shared entry (a weapon or wargear), with min/max and an optional cost."""
        def go():
            p, sp = self.at(f, *path)
            tid, _ = self.shared_id(to, f)
            s = self.F.text[p]
            if re.search(r'<entryLink [^>]*targetId="' + tid + '"', s[sp[0]:sp[1]]) and not shown:
                return
            if shown and re.search(r'<entryLink [^>]*name="' + re.escape(html.escape(shown, quote=False)) + '"', s[sp[0]:sp[1]]):
                return
            nl = self.F.nl(p)
            ind = self.F.indent_of(p, sp[0]) + "    "
            lid = make_id(p, " > ".join(path), to, shown or "")
            body = []
            if mn is not None or mx is not None:
                body.append(f"{ind}  <constraints>")
                for kind, v in (("min", mn), ("max", mx)):
                    if v is not None:
                        body.append(f'{ind}    <constraint field="selections" scope="parent" value="{v}" percentValue="false" '
                                    f'shared="true" includeChildSelections="false" includeChildForces="false" '
                                    f'id="{make_id(lid, kind)}" type="{kind}"/>')
                body.append(f"{ind}  </constraints>")
            if pts is not None:
                body += [f"{ind}  <costs>", f'{ind}    <cost name="Pts" typeId="{PTS}" value="{pts}"/>', f"{ind}  </costs>"]
            x = (f'<entryLink id="{lid}" name="{html.escape(shown or to, quote=False)}" hidden="false" collective="false" '
                 f'import="true" targetId="{tid}" type="selectionEntry">{nl}' + nl.join(body) + f"{nl}{ind}</entryLink>")
            self.F.insert_child(p, sp, "entryLinks", [x], f"{' > '.join(path)}: + {shown or to}")
        self.run(" > ".join(path) + " add " + to, go)

    def drop(self, f, *path):
        """Remove an element (an option, a link) entirely."""
        def go():
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            line = s.rfind("\n", 0, sp[0]) + 1
            end = s.find("\n", sp[1]) + 1
            self.F.replace(p, line if s[line:sp[0]].strip() == "" else sp[0], end, "", f"{' > '.join(path)}: removed")
        self.run(" > ".join(path) + " drop", go)

    def maxsel(self, f, *path, v, kind="max"):
        """Change an entry's min or max selections constraint."""
        def go():
            p, sp = self.at(f, *path)
            c = self.F.child(p, sp, "constraints")
            s = self.F.text[p]
            m = re.search(r'<constraint [^>]*type="' + kind + '"[^>]*>', s[c[0]:c[1]]) if c else None
            if not m:
                raise KeyError(f"no {kind} constraint")
            vm = re.search(r'value="([^"]*)"', m.group(0))
            a = c[0] + m.start() + vm.start(1)
            self.F.replace(p, a, a + len(vm.group(1)), str(v), f"{' > '.join(path)}: {kind} {v}")
        self.run(" > ".join(path) + " " + kind, go)

    def each(self, f, *path):
        """Spans of every descendant named path[-1] under path[:-1] (re-found by index, so call one at a time)."""
        p, sp = self.at(f, *path[:-1])
        name = path[-1]
        hits = sorted(h for t in ENTRY_TAGS + ("profile",) for h in self.F.find(p, name, t, sp))
        return p, len(hits)

    def cost_each(self, f, *path, v):
        def go():
            p, n = self.each(f, *path)
            if not n:
                raise KeyError(f"none found")
            for i in range(n):
                p, sp = self.at(f, *path[:-1], f"{path[-1]}#{i}")
                self.F.set_cost(p, sp, v, f"{' > '.join(path)} [{i + 1}]: {v} points")
        self.run(" > ".join(path) + " (each)", go)

    def rule_x(self, f, *path, rule, to):
        """Change the value a linked '(X)' rule shows, e.g. Malefic Aegis (6+) to Malefic Aegis (5+)."""
        def go():
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            il = self.F.child(p, sp, "infoLinks")
            base = norm(re.sub(r"\s*\(.*\)$", "", rule))
            for t, a, b in (self.F.children(p, il) if il else []):
                blk = s[a:b]
                nm = norm(re.search(r'name="([^"]*)"', blk).group(1))
                if re.sub(r"\s*\(.*\)$", "", nm) != base:
                    continue
                m = re.search(r'(<modifier type="set" field="name" value="|<modifier type="set" value=")([^"]*)("(?: field="name")?/>)', blk)
                if m:
                    self.F.replace(p, a + m.start(2), a + m.end(2), html.escape(to, quote=False), f"{' > '.join(path)}: {to}")
                    return
                # an unmodified link to the plain rule: add the shown name
                self.F.remove_rule(p, sp, nm, f"{' > '.join(path)}: {to}")
                p, sp = self.at(f, *path)
                self.F.add_rule(p, sp, to, f"{' > '.join(path)}: {to}")
                return
            raise KeyError(f"no {rule} link")
        self.run(" > ".join(path) + " " + rule, go)

    def cond_rule(self, f, *path, rule, child, scope="force"):
        """Give an entry a rule that only shows while `child` (an entry id or shared entry name) is selected in
        the force (or roster), e.g. a rule granted by a Cohort Doctrine or a Legion."""
        def go():
            cid = child if re.match(r"^[0-9a-f]{4}-", child) else self.shared_id(child)[0]
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            if re.search(r'<infoLink [^>]*name="' + re.escape(html.escape(rule, quote=False)) + '"', s[sp[0]:sp[1]]):
                return
            rid, _ = self.F.rule_link(rule)
            real = re.search(r'<rule id="' + rid + r'" name="([^"]+)"', "".join(self.F.text.values())).group(1)
            nl = self.F.nl(p)
            ind = self.F.indent_of(p, sp[0]) + "    "
            lid = make_id(p, " > ".join(path), rule, cid)
            mods = [f'{ind}  <modifiers>',
                    f'{ind}    <modifier type="set" field="hidden" value="true">',
                    f'{ind}      <conditions>',
                    f'{ind}        <condition field="selections" scope="{scope}" value="0" percentValue="false" shared="true" '
                    f'includeChildSelections="true" includeChildForces="false" childId="{cid}" type="equalTo"/>',
                    f'{ind}      </conditions>',
                    f'{ind}    </modifier>']
            if norm(real) != norm(rule):
                mods.append(f'{ind}    <modifier type="set" field="name" value="{html.escape(rule, quote=False)}"/>')
            mods.append(f'{ind}  </modifiers>')
            x = (f'<infoLink id="{lid}" name="{html.escape(real, quote=False)}" hidden="false" targetId="{rid}" type="rule">{nl}'
                 + nl.join(mods) + f"{nl}{ind}</infoLink>")
            self.F.insert_child(p, sp, "infoLinks", [x], f"{' > '.join(path)}: + {rule} (while {child} is taken)")
        self.run(" > ".join(path) + " cond " + rule, go)

    def cost_if(self, f, *path, v, child, scope="force"):
        """Add `v` points to an entry while `child` (an entry id) is selected in the force."""
        def go():
            p, sp = self.at(f, *path)
            s = self.F.text[p]
            tag = f'<modifier type="increment" field="{PTS}" value="{v}">'
            mods = self.F.child(p, sp, "modifiers")
            if mods and child in s[mods[0]:mods[1]] and tag in s[mods[0]:mods[1]]:
                return
            nl = self.F.nl(p)
            ind = self.F.indent_of(p, sp[0]) + "    "
            x = (f"{tag}{nl}{ind}  <conditions>{nl}"
                 f'{ind}    <condition field="selections" scope="{scope}" value="1" percentValue="false" shared="true" '
                 f'includeChildSelections="true" includeChildForces="false" childId="{child}" type="atLeast"/>{nl}'
                 f"{ind}  </conditions>{nl}{ind}</modifier>")
            self.F.insert_child(p, sp, "modifiers", [x], f"{' > '.join(path)}: +{v} points while {child} is taken")
        self.run(" > ".join(path) + " cost_if", go)

    def cost_named(self, name, v, files=None):
        """Set the points of every entry and link with this name that carries a cost (in every file, or the
        given ones), e.g. an upgrade bought from several units."""
        def go():
            n = 0
            for p in ([self.F.file(x) for x in files] if files else self.F.paths):
                for tag in ("selectionEntry", "entryLink"):
                    i = 0
                    while True:
                        hits = self.F.find(p, name, tag)
                        if i >= len(hits):
                            break
                        sp = self.F.span(p, hits[i])
                        i += 1
                        if self.F.cost_of(p, sp) is not None:
                            self.F.set_cost(p, sp, v, f"{name}: {v} points")
                            n += 1
            if not n:
                raise KeyError("nothing priced")
        self.run(f"{name} cost", go)

    def units(self, name):
        """Every file with a unit of this name (the Legion catalogues repeat many units)."""
        return [self.F.short(p) for p in self.F.paths if self.F.find(p, name, "selectionEntry", None, "unit")]

    def cat_strip(self, unit, names):
        """Remove category links (Unit Sub-types) from a unit and everything in it, in every file with the unit."""
        def go():
            for f in self.units(unit):
                p, sp = self.at(f, unit)
                for name in names:
                    cid = self.cats[norm(name)]
                    while True:
                        p, sp = self.at(f, unit)
                        s = self.F.text[p]
                        m = re.search(r'\n[ \t]*<categoryLink [^>]*targetId="' + cid + r'"[^>]*/>', s[sp[0]:sp[1]])
                        if not m:
                            break
                        self.F.replace(p, sp[0] + m.start(), sp[0] + m.end(), "", f"{unit}: - {name}")
        self.run(unit + " strip", go)

    def raw(self, f, *path, fn, what="edited"):
        """Rewrite an element's XML with fn(xml) -> xml (for edits no other operation covers)."""
        def go():
            p, sp = self.at(f, *path)
            old = self.F.text[p][sp[0]:sp[1]]
            new = fn(old)
            if new != old:
                self.F.replace(p, sp[0], sp[1], new, f"{' > '.join(path)}: {what}")
        self.run(" > ".join(path) + " raw", go)

    def cost_all(self, f, unit, names, v):
        """Set the points of every option with one of these names anywhere inside a unit (that has a cost)."""
        def go():
            n = 0
            for name in names:
                p, cnt = self.each(f, unit, name)
                for i in range(cnt):
                    p, sp = self.at(f, unit, f"{name}#{i}")
                    if self.F.cost_of(p, sp) is not None:
                        self.F.set_cost(p, sp, v, f"{unit} > {name}: {v} points")
                        n += 1
            if not n:
                raise KeyError("nothing priced")
        self.run(f"{unit} {names[0]}.. cost", go)
