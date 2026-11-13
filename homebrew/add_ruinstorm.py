#!/usr/bin/env python3
"""Add the Daemons of the Ruinstorm expansion to the official Daemons of the Ruinstorm catalogue.

usage: python3 homebrew/add_ruinstorm.py

The doc (homebrew/source/ruinstorm.md) is read by build_catalogue.py's Builder, and its units move into
2022 - Daemons - Daemons of the Ruinstorm.cat as text, linked to the official rules and entries wherever those exist.
It also writes:

- the eight Daemonic Assassins as HQ choices that are not Compulsory HQ and never the Warlord, each an error unless
  the Detachment's Ætheric Dominion is the assassin's own (any single one under Formless Distortion);
- the Ætheric Blessings: every Daemon unit (official and new) may buy one, priced per model (the datasheet's price,
  or +5 / +15 / +30 by Wounds), shown only with the matching Dominion (any under Formless Distortion);
- Master of the Ruinstorm on the Ruinstorm Daemon Sovereign and Harbinger, with the Master of the Legion rule and
  its limit of one such model per full 1,000 points of the army's points limit;
- the Rites of War: Warlord prerequisites, Dominions, extra Troops (and Line) and Elites choices, Compulsory Troops,
  bans, Troops minimums, unit sizes, the Swarming Horde discount, Soul-Forge squadrons, Dark Communion's discount and
  the Blessings each Dominion Rite requires. In-game effects are the Rite's text.

Daemons of the Ruinstorm were already Traitor only (the game system's faction entry). It refuses to run on a
catalogue that already has the expansion."""
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, "homebrew")
import build_catalogue as bc  # noqa: E402
import expansion_tools as et  # noqa: E402
from build_catalogue import add_constraint, child, el, norm  # noqa: E402
from expansion_tools import E, Text, mid  # noqa: E402

CAT = "2022 - Daemons - Daemons of the Ruinstorm.cat"
CAT_ID = "ac63-5340-2e9e-1eb6"
DOC = "homebrew/source/ruinstorm.md"
LIBS = ["Daemon Library.cat", "2022 - LI - Assassins.cat"]
et.configure(CAT, LIBS, DOC, "Daemons of the Ruinstorm", "ruinstorm expansion")

PTS = bc.PTS
WARLORD = "0176-56a3-d590-b103"
ALLIED = "d4f2-6da5-b6de-06ec"
DAEMON = ("e699-d9cd-e68e-46d9", "Daemon Unit Type")
CORRUPTED_ENGINE = ("a443-dbf4-cb6c-4da1", "Corrupted Engine Sub-type")
TRAITOR, SHATTERED_VEIL, FADING_ECHO, MOTL = ("eff2-8b0e-21da-2f0d", "6a21-fe63-1857-c12b", "df6e-3482-d5ed-0e42",
                                              "c772-87ea-d49c-c7ba")
RITE_CATEGORY = ("d494-e450-d4aa-579a", "Rite of War:")
CATS = {"HQ": "4f85-eb33-30c9-8f51", "Elites": "7aee-565f-b0ae-294e", "Troops": "9b5d-fac7-799b-d7e7",
        "Fast Attack": "20ef-cd01-a8da-376e", "Heavy Support": "7031-469a-1aeb-eab0",
        "Fortification": "a24f-12d8-36c1-f477", "Lords of War": "c658-dc6b-727b-c488",
        "Compulsory Troops": "8f42-a824-fb5f-8fea", "Line": "6399-5c65-7833-1025"}
# the Ætheric Dominions (Daemon Library): the army's pick, and the category each Dominion's entries carry
DOMINIONS = {"Heedless Slaughter": ("3d70-1d54-a791-ac60", "f074-f60a-9aa6-c52a"),
             "Putrid Corruption": ("b7db-bf16-47c5-dc05", "8cf6-d802-d054-6a86"),
             "Infernal Tempest": ("e4fb-66cd-e07d-609b", "6508-4f6a-0dc1-8f56"),
             "Rapturous Sensation": ("1214-3abe-c6d1-2038", "a1d4-4662-c944-19cc"),
             "Encroaching Ruin": ("ca6c-e8cf-7bc1-eaa0", "c42-1919-c37e-51f0"),
             "Malevolent Artifice": ("9508-8124-d34a-500a", "bcf6-8350-9099-1e91"),
             "Ravenous Dissolution": ("945c-b969-75eb-19d9", "2774-1a32-f196-be76"),
             "Formless Distortion": ("8ed0-3582-f536-c48e", "9556-82c1-c70a-126e")}
FORMLESS = DOMINIONS["Formless Distortion"][0]

# official units: entry id, root link id, Blessing price per model (by Wounds)
OFFICIAL = {"Ruinstorm Daemon Sovereign": ("2f3f-adc4-b19f-a5c7", "61db-a83f-c0b6-90fd", 30),
            "Ruinstorm Daemon Hierarch": ("ae8b-ee65-95b6-a8f9", "50a8-b11-67b1-26b5", 15),
            "Ruinstorm Daemon Harbinger": ("5a2e-abe2-3044-3c1c", "aaad-9ba0-9f12-f55", 15),
            "Ruinstorm Daemon Brutes": ("2219-cb60-b52-a36c", "24b7-aabd-c772-ff9", 15),
            "Ruinstorm Daemon Beasts": ("69ad-927-c71b-6b24", "6c10-5ca2-fe18-f7b2", 15),
            "Ruinstorm Lesser Daemons": ("157c-7592-a6b9-f96", "7a1e-4bc1-85cb-7569", 5),
            "Ruinstorm Daemon Swarms": ("bb35-e585-a226-28e", "d155-b3f4-5fca-6df2", 15),
            "Ruinstorm Daemon Cavalry": ("b7b5-c59a-768c-276c", "47f6-44fe-d2ec-819e", 15),
            "Ruinstorm Daemon Harriers": ("14c1-3063-c9b4-d99b", "af04-d38a-aa6e-8d43", 5),
            "Greater Ruinstorm Daemon Beast": ("41a0-6caa-af06-3684", "271c-cc74-3c17-d759", 30),
            "Ruinstorm Daemon Behemoth": ("240a-1822-9e4f-3080", "59ea-d83-a465-2697", 30),
            "Ruinstorm Arch-Daemon": ("1fbb-b82e-ae1e-5a12", "bde9-cbb2-1c62-da9a", 30),
            "Ka’bandha Unbound": ("baa5-baed-1a62-c820", "d606-d66-9d34-6fb4", 30),
            "Cor’bax Utterblight Unbound": ("ef9d-3ad6-1f39-b84b", "957e-2292-544d-8031", 30),
            "Samus Unbound": ("63f0-9b87-6482-87ee", "6f48-b881-40f3-5da", 30)}
OFFICIAL_SLOTS = {"Ruinstorm Daemon Brutes": "Elites", "Ruinstorm Daemon Beasts": "Elites",
                  "Ruinstorm Lesser Daemons": "Troops", "Ruinstorm Daemon Swarms": "Troops",
                  "Ruinstorm Daemon Cavalry": "Fast Attack", "Ruinstorm Daemon Harriers": "Fast Attack",
                  "Greater Ruinstorm Daemon Beast": "Heavy Support", "Ruinstorm Daemon Behemoth": "Heavy Support"}
# Warlord links in official units
WARLORD_LINKS = {"Ruinstorm Daemon Sovereign": "c7e9-b5ee-aac-92c0", "Ruinstorm Daemon Hierarch": "1655-8fed-b79a-24f6",
                 "Ruinstorm Daemon Harbinger": "4c82-36a0-e269-75c9", "Ka’bandha Unbound": "2109-c0df-c953-602c",
                 "Cor’bax Utterblight Unbound": "499-6206-31d0-28be", "Samus Unbound": "97a9-bc02-d06a-a63b"}
WINGS = ["fd64-626a-d3d4-9b8e", "7647-8112-eaf7-fbea"]  # Immaterial Wings, Ætheric Flight
CONDUIT = "9c2-edf8-c9bd-ec05"  # Ætheric Conduit: the Psyker Sub-type
MODELS = {"Ruinstorm Lesser Daemons": ("5da5-c15b-dfe5-d1b5", "82e-bbd5-df4b-dcd1", 0),
          "Ruinstorm Daemon Swarms": ("cb8c-b27a-ea4e-1c91", "3426-8409-ce4a-3c85", 0)}  # model, its max, other models
SUPPORT_SQUAD = "Support Squad"

# the new units' Blessing price per model (their datasheets)
NEW_BLESSING = {"Ruinstorm Herald Conclave": 15, "Ruinstorm Incinerator Swarm": 10, "Ruinstorm Warp-Spawn Pack": 5,
                "Ruinstorm Sky-Ray Pack": 10, "Ruinstorm Flesh-Reaper Cavalry": 15, "Ruinstorm Soul-Forge Engine": 25,
                "Ruinstorm Cataclysm Brute Pack": 15}
ASSASSIN_BLESSING = 15  # 3 Wounds
MUST_EXCHANGE = {"Ruinstorm Warp-Spawn Pack": "Warp-Fire Bolts", "Ruinstorm Cataclysm Brute Pack": "Empyric Rotary Torrent"}

LDS = ["Ruinstorm Lesser Daemons", "Ruinstorm Daemon Swarms"]  # "Lesser Daemon Swarms"
SOV, HARB, ARCH = "Ruinstorm Daemon Sovereign", "Ruinstorm Daemon Harbinger", "Ruinstorm Arch-Daemon"
WS, INC, SKY, FR, SFE, CBP, HER = ("Ruinstorm Warp-Spawn Pack", "Ruinstorm Incinerator Swarm", "Ruinstorm Sky-Ray Pack",
                                   "Ruinstorm Flesh-Reaper Cavalry", "Ruinstorm Soul-Forge Engine",
                                   "Ruinstorm Cataclysm Brute Pack", "Ruinstorm Herald Conclave")
BRU, BEA, GB, BEH = ("Ruinstorm Daemon Brutes", "Ruinstorm Daemon Beasts", "Greater Ruinstorm Daemon Beast",
                     "Ruinstorm Daemon Behemoth")
LOW = [ARCH, "Ka’bandha Unbound", "Cor’bax Utterblight Unbound", "Samus Unbound"]

# Rites of War, by the doc's heading: what the app can check
RITES = {
    "Tide of the Empyrean": dict(
        warlord={SOV: [], HARB: []}, troops=[WS, BEA], compulsory_only=LDS + [WS], no_support_squad=[WS],
        sizes={n: 20 for n in LDS + [WS]}, bans_roster_slots=["Lords of War"], max_slots={"Heavy Support": 1},
        min_troops=3),
    "Phalanx of Abominations": dict(
        warlord={SOV: [], HARB: []}, troops=[BRU], compulsory_only=[BRU], elites=[CBP],
        bans=LDS + [WS, "Ruinstorm Daemon Harriers"], bans_slots=["Fortification"], no_allies=True),
    "Screaming Host of the Skies": dict(
        warlord={SOV: [("any", WINGS)]}, troops=[SKY, BEA], bans=[BRU, CBP, FR, SFE], bans_slots=["Fortification"]),
    "Swarming Horde of the Veil": dict(
        warlord={SOV: [], HARB: []}, compulsory_only=LDS, no_support_squad=[WS],
        sizes={n: 25 for n in LDS + [WS]}, discount=LDS + [WS], bans_roster_slots=["Lords of War"],
        bans_slots=["Heavy Support"], min_troops=4),
    "Legion of the Brass Throne (Heedless Slaughter)": dict(
        dominion="Heedless Slaughter", warlord="blessing", troops=[BEA, GB, FR], bans=[WS, INC, CBP], blessing=True),
    "The Plague-Swollen Host (Putrid Corruption)": dict(
        dominion="Putrid Corruption", warlord="blessing", troops=[BRU, BEA], line=LDS + [BRU],
        bans_slots=["Fast Attack"], blessing=True),
    "Conflagration of Change (Infernal Tempest)": dict(
        dominion="Infernal Tempest", warlord="blessing+psyker", troops=[SKY, INC], bans=[SFE], blessing=True),
    "Carnival of Excess (Rapturous Sensation)": dict(
        dominion="Rapturous Sensation", warlord="blessing", troops=[BEA, FR], bans=[CBP], blessing=True),
    "Host of Inevitable Decay (Encroaching Ruin)": dict(
        dominion="Encroaching Ruin", warlord="blessing", troops=[BRU, GB], bans=[SKY], blessing=True),
    "Soul-Forge Conclave (Malevolent Artifice)": dict(
        dominion="Malevolent Artifice", warlord={SOV: [("blessing",)], HARB: []}, troops=[CBP, BRU],
        bans_slots=["Fast Attack"], need=[[HER], [SFE, BEH]], squadron=True, communion=True, blessing=True),
    "Maw of Annihilation (Ravenous Dissolution)": dict(
        dominion="Ravenous Dissolution", warlord={SOV: [("blessing",)], ARCH: [("blessing",)]}, troops=[GB, INC],
        line=LDS + [GB], no_allies=True, blessing=True),
    "Reality-Shattering Flux (Formless Distortion)": dict(
        dominion="Formless Distortion", warlord="blessing", troops=[WS, INC, BRU], compulsory_only=LDS + [WS],
        bans=[SFE], blessing=True),
}


# ---- the doc's text


def doc_sections():
    """{'## title': {'### title': text}} of the doc."""
    out, top, sub = {}, None, None
    for line in open(DOC, encoding="utf-8").read().splitlines():
        if line.startswith("## "):
            top, sub = line[3:].strip(), None
            out[top] = {}
        elif line.startswith("### ") and top:
            sub = line[4:].strip()
            out[top][sub] = []
        elif top and sub:
            out[top][sub].append(line)
    return out


def paragraph_text(lines):
    paras, cur = [], []
    for l in lines + [""]:
        if l.strip():
            cur.append(l.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    return "\n\n".join(p for p in paras if not (p.startswith("*") and p.endswith("*") and not p.startswith("**")))


def rite_parts(lines):
    parts, cur = {}, None
    for l in lines:
        m = re.match(r"\*\*(Prerequisites|Effects|Limitations)\*\*", l)
        if m:
            cur = m.group(1)
            parts[cur] = []
        elif cur and l.startswith("- "):
            parts[cur].append(l[2:].strip())
    return {k: "\n".join("• " + x for x in v) for k, v in parts.items()}


# ---- XML helpers


def cond(parent, childId, kind="atLeast", value=1, scope="force", field="selections", forces=False):
    el(child(parent, "conditions"), "condition", type=kind, value=value, field=field, scope=scope, childId=childId,
       shared=True, includeChildSelections=True, includeChildForces=forces, percentValue=False)


def group(parent, kind):
    return el(child(parent, "conditionGroups"), "conditionGroup", type=kind)


def modifier(parent, field, value, kind="set"):
    return el(child(parent, "modifiers"), "modifier", type=kind, field=field, value=value)


def per_model_repeat(mod, uid, every=1):
    el(child(mod, "repeats"), "repeat", field="selections", scope=uid, value=every, percentValue=False, shared=True,
       includeChildSelections=True, includeChildForces=False, childId="model", repeats=1, roundUp=False)


def rite_any(parent, rite_ids):
    """Conditions true while any of these Rites is chosen in the Detachment."""
    if len(rite_ids) == 1:
        cond(parent, rite_ids[0])
    else:
        g = group(parent, "or")
        for r in rite_ids:
            cond(g, r)


def rule_el(name, text, key):
    r = E("rule", id=mid(key, "rule", name), name=name, hidden=False)
    el(r, "description").text = text
    return r


def info_link(name, target, key):
    return E("infoLink", id=mid(key, "info", name), name=name, hidden=False, targetId=target, type="rule")


def category_link(cat, name, key, primary=False):
    return E("categoryLink", id=mid(key, "cat", name), name=name, hidden=False, targetId=cat, primary=primary)


def allied_hidden(e, comment="The Shattered Veil: not in a Ruinstorm Allied Detachment"):
    m = modifier(e, "hidden", "true")
    el(m, "comment").text = comment
    el(child(m, "conditions"), "condition", type="instanceOf", value=0, field="selections", scope="ancestor",
       childId=ALLIED, shared=True, percentValue=False, includeChildSelections=False, includeChildForces=False)


def veil_links(uid):
    out = []
    for name, target in (("The Shattered Veil", SHATTERED_VEIL), ("The Fading Echo", FADING_ECHO)):
        i = info_link(name, target, uid)
        m = modifier(i, "hidden", "true")
        el(m, "comment").text = "The Shattered Veil: only in a Ruinstorm Allied Detachment"
        el(child(m, "conditions"), "condition", type="notInstanceOf", value=0, field="selections", scope="ancestor",
           childId=ALLIED, shared=True, percentValue=False, includeChildSelections=False, includeChildForces=False)
        out.append(i)
    return out


# ---- building the expansion


def main():
    cat = Text(CAT)
    if mid("blessing", "Heedless Slaughter") in cat.s:
        sys.exit(f"{CAT} already has the Daemons of the Ruinstorm expansion")
    doc = doc_sections()
    idx = et.official_index()
    b, root = et.build()
    entries = {e.get("id"): e for e in root.find("sharedSelectionEntries")}
    unit = lambda n: entries[b.units[n]]
    ds_by = {d["name"]: d for d in b.datasheets}
    assassins = [d["name"] for d in b.datasheets if d["slot"] == "HQ"]
    new_units = [d["name"] for d in b.datasheets if d["slot"] != "HQ"]

    # the doc's own fixes, before the units move
    for n in assassins:
        for parent in list(unit(n).iter()):
            for l in list(parent):
                if l.tag == "entryLink" and (l.get("targetId") == WARLORD or l.get("name") == "Warlord Traits"):
                    parent.remove(l)  # Harbinger of Execution: never the Warlord, so no Warlord Trait either
    for n, weapon in MUST_EXCHANGE.items():
        for g in unit(n).iter("selectionEntryGroup"):
            for l in list(g.findall("entryLinks/entryLink")):
                if l.get("name") == weapon:
                    g.find("entryLinks").remove(l)  # "must exchange": the default is not kept
                    g.attrib.pop("defaultSelectionEntryId", None)

    units, keep_entries, keep_groups, keep_rules = et.transplant(b, root, idx)
    uid_of = {u.get("name"): u.get("id") for u in units}
    all_uid = {**uid_of, **{n: v[0] for n, v in OFFICIAL.items()}}

    # ---- new units: categories, rules, root links
    roots = []
    root_of = {}
    for u in units:
        n, uid = u.get("name"), u.get("id")
        ds = ds_by[n]
        cats = et.drop_unit_category(u)
        if n == SFE:
            cats.append(category_link(*CORRUPTED_ENGINE, uid))
        else:
            cats.append(category_link(*DAEMON, uid))
        info = child(u, "infoLinks")
        info.append(info_link("Traitor", TRAITOR, uid))
        if ds["slot"] in ("Elites", "Troops", "Fast Attack"):
            info.extend(veil_links(uid))
        if n in assassins:
            dom = n.split(":")[0]
            cats.append(category_link(DOMINIONS[dom][1], dom, uid))
            link = et.root_link(u, ds, slot="HQ")
            for c in list(link.find("categoryLinks")):
                if c.get("name") == "Compulsory HQ:":  # Harbinger of Execution
                    link.find("categoryLinks").remove(c)
        else:
            link = et.root_link(u, ds)
        if ds["slot"] == "Heavy Support":
            allied_hidden(link)
        roots.append(link)
        root_of[n] = link

    # assassins: the Detachment's Dominion, or any single one under Formless Distortion
    for n in assassins:
        link, dom = root_of[n], n.split(":")[0]
        cid = add_constraint(link, "max", 0, mid(n, "dominion max"), scope="force", children=True)
        el(modifier(link, cid, -1), "comment").text = f"Harbinger of Execution: {dom} Detachments only"
        cond(link.find("modifiers")[-1], DOMINIONS[dom][0])
        if dom != "Formless Distortion":
            m = modifier(link, cid, 1)
            cond(m, FORMLESS)
            m = modifier(link, cid, 0)
            g = group(m, "and")
            cond(g, FORMLESS)
            og = group(g, "or")
            for other in assassins:
                if other != n:
                    cond(og, uid_of[other])

    # Soul-Forge Engine squadrons (Soul-Forge Conclave): later, once the Rite ids exist

    # ---- Ætheric Blessings
    blessing_text = doc["Ætheric Blessings of the Ruinstorm"]
    blessings = {}
    blessing_entries = []
    for dom, (dom_entry, dom_cat) in DOMINIONS.items():
        bid = mid("blessing", dom)
        blessings[dom] = bid
        e = E("selectionEntry", type="upgrade", import_=True, name=f"{dom} (Ætheric Blessing)", hidden=False, id=bid)
        cid = add_constraint(e, "max", 1, mid(bid, "max"))
        for field, value in (("hidden", "true"), (cid, 0)):
            m = modifier(e, field, value)
            g = group(m, "and")
            cond(g, dom_entry, "lessThan")
            cond(g, FORMLESS, "lessThan")
        el(child(e, "rules"), "rule", id=mid(bid, "rule"), name=f"Ætheric Blessing: {dom}",
           hidden=False).append(E("description"))
        e.find("rules/rule/description").text = paragraph_text(blessing_text[dom])
        e.append(E("categoryLinks"))
        e.find("categoryLinks").append(category_link(dom_cat, dom, bid))
        bc.add_cost(e, 0)
        blessing_entries.append(e)

    def blessing_group(uid, pts):
        g = E("selectionEntryGroup", id=mid(uid, "blessing group"), name="Ætheric Blessing", hidden=False,
              collective=False, import_=True)
        add_constraint(g, "max", 1, mid(uid, "blessing group max"))
        links = {}
        for dom, bid in blessings.items():
            l = el(child(g, "entryLinks"), "entryLink", id=mid(uid, "blessing", dom), name=f"{dom} (Ætheric Blessing)",
                   hidden=False, collective=False, import_=True, targetId=bid, type="selectionEntry")
            add_constraint(l, "max", 1, mid(uid, "blessing", dom, "max"))
            bc.add_cost(l, 0)
            per_model_repeat(modifier(l, PTS, pts, "increment"), uid)
            links[dom] = l
        return g, links

    blessing_links = {}  # unit name -> {dom: link element}
    blessing_price = {}
    new_groups = {}
    for n in new_units + assassins:
        pts = NEW_BLESSING.get(n, ASSASSIN_BLESSING)
        g, links = blessing_group(uid_of[n], pts)
        child(unit_by_name(units, n), "selectionEntryGroups").append(g)
        blessing_links[n], blessing_price[n] = links, pts
    for n, (uid, _, pts) in OFFICIAL.items():
        g, links = blessing_group(uid, pts)
        new_groups[n] = g
        blessing_links[n], blessing_price[n] = links, pts

    # ---- Master of the Ruinstorm (Sovereign and Harbinger)
    special = doc["Special Rules"]
    motr = rule_el("Master of the Ruinstorm", paragraph_text(special["Master of the Ruinstorm"]), "master")
    official_adds = {n: {"infoLinks": [], "constraints": [], "modifiers": [], "selectionEntryGroups": [new_groups[n]],
                         "entryLinks": []} for n in OFFICIAL}
    for n, other in ((SOV, HARB), (HARB, SOV)):
        uid = OFFICIAL[n][0]
        official_adds[n]["infoLinks"] += [info_link("Master of the Ruinstorm", motr.get("id"), uid),
                                          info_link("Master of the Legion", MOTL, uid)]
        holder = E("x")
        cid = add_constraint(holder, "max", 0, mid(uid, "few and proud"), scope="roster", children=True)
        holder.find("constraints/constraint").set("includeChildForces", "true")
        m = modifier(holder, cid, 1, "increment")
        el(child(m, "repeats"), "repeat", value=1000, percentValue=False, repeats=1, roundUp=False,
           field="limit::" + PTS, scope="roster", childId="any", shared=True, includeChildSelections=True,
           includeChildForces=False)
        el(m, "comment").text = "Master of the Ruinstorm: one Sovereign or Harbinger per full 1,000 points"
        m = modifier(holder, cid, 1, "decrement")
        el(child(m, "repeats"), "repeat", value=1, percentValue=False, repeats=1, roundUp=False, field="selections",
           scope="roster", childId=OFFICIAL[other][0], shared=True, includeChildSelections=True, includeChildForces=True)
        official_adds[n]["constraints"] += list(holder.find("constraints"))
        official_adds[n]["modifiers"] += list(holder.find("modifiers"))

    # ---- Rites of War
    rite_text = doc["Rites of War"]
    rite_group = E("selectionEntryGroup", id=mid("rites"), name="Rites of War", hidden=False, collective=False,
                   import_=True)
    add_constraint(rite_group, "max", 1, mid("rites", "max"))
    rite_ids = {}
    rite_entries = {}
    for name, spec in RITES.items():
        rid = mid("rite", name)
        rite_ids[name] = rid
        e = el(child(rite_group, "selectionEntries"), "selectionEntry", type="upgrade", import_=True, name=name,
               hidden=False, id=rid)
        rite_entries[name] = e
        for part, text in rite_parts(rite_text[name]).items():
            el(el(child(e, "rules"), "rule", id=mid(rid, part), name=part, hidden=False), "description").text = text
        bc.add_cost(e, 0)
        lim = add_constraint(e, "max", 1, mid(rid, "limits"))

        def invalid_when(kind="or"):
            m = modifier(e, lim, 0)
            return group(m, kind)
        if spec.get("dominion"):
            dom_entry = DOMINIONS[spec["dominion"]][0]
            m = modifier(e, "hidden", "true")
            cond(m, dom_entry, "lessThan")
            cond(invalid_when(), dom_entry, "lessThan")
        # the Warlord's units must be in the Detachment
        wl = spec["warlord"]
        allowed = [SOV, HARB] if isinstance(wl, str) else list(wl)
        g = invalid_when("and")
        for n in allowed:
            cond(g, all_uid[n], "lessThan", **({"scope": "roster", "forces": True} if n in LOW else {}))
        bans = [all_uid[n] for n in spec.get("bans", [])]
        if bans:
            g = invalid_when()
            for b_id in bans:
                cond(g, b_id)
        for slot in spec.get("bans_slots", []):
            cond(invalid_when(), CATS[slot])
        for slot in spec.get("bans_roster_slots", []):
            g = invalid_when()
            cond(g, CATS[slot], scope="roster", forces=True)
        for slot, most in spec.get("max_slots", {}).items():
            cond(invalid_when(), CATS[slot], "greaterThan", most)
        if spec.get("min_troops"):
            cond(invalid_when(), CATS["Troops"], "lessThan", spec["min_troops"])
        for needed in spec.get("need", []):
            g = invalid_when("and")
            for n in needed:
                cond(g, all_uid[n], "lessThan")
        if spec.get("no_allies"):
            cond(invalid_when(), ALLIED, field="forces", scope="roster", forces=True)

    rite_root = E("selectionEntry", type="upgrade", import_=True, name="Rite of War", hidden=False,
                  id=mid("rite of war"))
    add_constraint(rite_root, "max", 1, mid("rite of war", "max"), scope="force", children=True)
    allied_hidden(rite_root, "Rites of War: Primary Detachment only")
    child(rite_root, "categoryLinks").append(category_link(*RITE_CATEGORY, mid("rite of war"), primary=True))
    child(rite_root, "selectionEntryGroups").append(rite_group)
    bc.add_cost(rite_root, 0)

    def rites_where(key, n):
        return [rite_ids[r] for r, s in RITES.items() if n in s.get(key, [])]

    # Warlord: only the Rite's Warlord (with the Blessing, wings or Psyker it names) may be chosen
    def warlord_rules(n):
        """[(rite id, [requirement])] for unit n: None means barred."""
        out = []
        for r, s in RITES.items():
            wl = s["warlord"]
            if isinstance(wl, str):
                reqs = {SOV: [("blessing",)], HARB: [("blessing",)]}
                if wl == "blessing+psyker":
                    reqs = {k: [("blessing",), ("any", [CONDUIT])] for k in reqs}
            else:
                reqs = wl
            out.append((rite_ids[r], s.get("dominion"), reqs.get(n)))
        return out

    def warlord_mods(link_holder, n, uid, cid):
        for rid, dom, reqs in warlord_rules(n):
            # the Warlord may be in any Detachment (a Lord of War in the Lord of War Detachment): the whole army
            if reqs is not None and not reqs:
                continue
            m = modifier(link_holder, cid, 0)
            if reqs is None:
                cond(m, rid, scope="roster", forces=True)
                continue
            g = group(m, "and")
            cond(g, rid, scope="roster", forces=True)
            og = group(g, "or")
            for req in reqs:
                if req[0] == "blessing":
                    cond(og, blessings[dom], "lessThan", scope=uid)
                else:  # any of these
                    ag = group(og, "and")
                    for t in req[1]:
                        cond(ag, t, "lessThan", scope=uid)
            # an empty or-group would never be true
    warlord_adds = {}
    for n, lid in WARLORD_LINKS.items():
        holder = E("x")
        cid = add_constraint(holder, "max", 1, mid(lid, "rite warlord"))
        warlord_mods(holder, n, OFFICIAL[n][0], cid)
        warlord_adds[lid] = holder
    # the Arch-Daemon may be the Warlord only for the Maw of Annihilation
    arch_uid = OFFICIAL[ARCH][0]
    arch_wl = E("entryLink", id=mid(arch_uid, "warlord"), name="Warlord", hidden=True, collective=False, import_=True,
                targetId=WARLORD, type="selectionEntry")
    maw = rite_ids["Maw of Annihilation (Ravenous Dissolution)"]
    cond(modifier(arch_wl, "hidden", "false"), maw, scope="roster", forces=True)
    cid = add_constraint(arch_wl, "max", 1, mid(arch_uid, "warlord max"))
    m = modifier(arch_wl, cid, 0)
    g = group(m, "or")
    cond(g, maw, "lessThan", scope="roster", forces=True)
    cond(g, blessings["Ravenous Dissolution"], "lessThan", scope=arch_uid)
    official_adds[ARCH]["entryLinks"].append(arch_wl)

    # every eligible unit must buy the Rite's Blessing; Dark Communion: Malevolent Artifice 5 points cheaper
    communion = rite_ids["Soul-Forge Conclave (Malevolent Artifice)"]
    for n, links in blessing_links.items():
        uid = all_uid[n]
        for r, s in RITES.items():
            if not s.get("blessing"):
                continue
            l = links[s["dominion"]]
            cid = add_constraint(l, "min", 0, mid(uid, "blessing", r, "min"))
            cond(modifier(l, cid, 1), rite_ids[r])
        if blessing_price[n] > 5:
            m = modifier(links["Malevolent Artifice"], PTS, 5, "decrement")
            per_model_repeat(m, uid)
            cond(m, communion)

    # extra Troops and Elites choices; Line and Compulsory Troops
    def troops_rites(n):
        return [(rite_ids[r], (not s.get("compulsory_only")) or n in s["compulsory_only"])
                for r, s in RITES.items() if n in s.get("troops", [])]
    official_root_adds = {}
    for n in sorted({x for s in RITES.values() for x in s.get("troops", [])}):
        rs = troops_rites(n)
        slot = OFFICIAL_SLOTS.get(n) or ds_by.get(n, {}).get("slot")
        uid = all_uid[n]
        if slot == "Troops":  # the Warp-Spawn Pack: a Support Squad, Compulsory under these Rites
            target = root_of[n]
            comp = [r for r, c in rs if c]
            if comp:
                rite_any(modifier(target, "category", CATS["Compulsory Troops"], "add"), comp)
            continue
        e = E("entryLink", import_=True, name=n, hidden=True, id=mid("rite troops", n), type="selectionEntry",
              targetId=uid)
        rite_any(modifier(e, "hidden", "false"), [r for r, _ in rs])
        cats = child(e, "categoryLinks")
        cats.append(category_link(et.UNIT[0], et.UNIT[1], e.get("id")))
        cats.append(category_link(CATS["Troops"], "Troops:", e.get("id"), primary=True))
        comp = [r for r, c in rs if c]
        if comp:
            rite_any(modifier(e, "category", CATS["Compulsory Troops"], "add"), comp)
        roots.append(e)
    for n in sorted({x for s in RITES.values() for x in s.get("elites", [])}):
        e = E("entryLink", import_=True, name=n, hidden=True, id=mid("rite elites", n), type="selectionEntry",
              targetId=all_uid[n])
        rite_any(modifier(e, "hidden", "false"), rites_where("elites", n))
        cats = child(e, "categoryLinks")
        cats.append(category_link(et.UNIT[0], et.UNIT[1], e.get("id")))
        cats.append(category_link(CATS["Elites"], "Elites:", e.get("id"), primary=True))
        allied_hidden(e)
        roots.append(e)
    # Line: the units a Rite lets fill a Compulsory Troops slot, and those it names
    line_rites = {}
    for r, s in RITES.items():
        for n in s.get("troops", []):
            if (not s.get("compulsory_only")) or n in s["compulsory_only"]:
                line_rites.setdefault(n, []).append(rite_ids[r])
        for n in s.get("line", []):
            line_rites.setdefault(n, []).append(rite_ids[r])
    for n, rs in line_rites.items():
        if n in OFFICIAL:
            m = E("modifier", type="add", field="category", value=CATS["Line"])
            rite_any(m, rs)
            official_adds[n]["modifiers"].append(m)
        else:
            rite_any(modifier(unit_by_name(units, n), "category", CATS["Line"], "add"), rs)
    # Compulsory Troops only from the Rite's list
    for r, s in RITES.items():
        only = s.get("compulsory_only")
        if not only:
            continue
        for n in ("Ruinstorm Lesser Daemons",):
            if n not in only:
                m = E("modifier", type="remove", field="category", value=CATS["Compulsory Troops"])
                cond(m, rite_ids[r])
                official_root_adds.setdefault(OFFICIAL[n][1], []).append(m)
        # the Rite's own Troops links carry Compulsory Troops only where it allows
    # Support Squad: not under these Rites
    for n in {x for s in RITES.values() for x in s.get("no_support_squad", [])}:
        u = unit_by_name(units, n)
        for il in u.findall("infoLinks/infoLink"):
            if norm(il.get("name")) == norm(SUPPORT_SQUAD):
                rite_any(modifier(il, "hidden", "true"), rites_where("no_support_squad", n))
    # bigger units
    for r, s in RITES.items():
        for n, total in s.get("sizes", {}).items():
            if n in MODELS:
                model, max_id, others = MODELS[n]
                m = E("modifier", type="set", field=max_id, value=total - others)
                cond(m, rite_ids[r])
                official_adds.setdefault(("model", n), []).append((model, m))
            else:
                u = unit_by_name(units, n)
                models = [me for me in u.findall("selectionEntries/selectionEntry") if me.get("type") == "model"]
                main_model = max(models, key=lambda me: float(me.find("constraints/constraint[@type='max']").get("value")))
                others = sum(int(float(me.find("constraints/constraint[@type='min']").get("value")))
                             for me in models if me is not main_model)
                cmax = main_model.find("constraints/constraint[@type='max']").get("id")
                cond(modifier(main_model, cmax, total - others), rite_ids[r])
        # Swarming Horde: -1 point per model beyond the first 10
        for n in s.get("discount", []):
            uid = all_uid[n]
            mods = []
            for k in range(11, 26):
                m = E("modifier", type="decrement", field=PTS, value=1)
                g = el(el(m, "conditionGroups"), "conditionGroup", type="and")
                cond(g, rite_ids[r])
                el(child(g, "conditions"), "condition", type="atLeast", value=k, field="selections", scope=uid,
                   childId="model", shared=True, includeChildSelections=True, includeChildForces=False,
                   percentValue=False)
                mods.append(m)
            if n in OFFICIAL:
                official_adds[n]["modifiers"] += mods
            else:
                child(unit_by_name(units, n), "modifiers").extend(mods)
    # Soul-Forge Conclave: Soul-Forge Engines in squadrons of 1 to 3
    sfe = unit_by_name(units, SFE)
    model = next(me for me in sfe.findall("selectionEntries/selectionEntry") if me.get("type") == "model")
    cmax = model.find("constraints/constraint[@type='max']").get("id")
    unit_cost = float(sfe.find("costs/cost").get("value"))
    cond(modifier(model, cmax, 3), communion)
    cond(modifier(model, PTS, unit_cost), communion)
    cond(modifier(sfe, PTS, 0), communion)

    # ---- write
    for n, adds in official_adds.items():
        if isinstance(n, tuple):
            for model_id, m in adds:
                cat.add(model_id, "modifiers", [m])
            continue
        uid = OFFICIAL[n][0]
        for container in ("infoLinks", "constraints", "modifiers", "selectionEntryGroups", "entryLinks"):
            if adds[container]:
                cat.add(uid, container, adds[container])
    for lid, holder in warlord_adds.items():
        cat.add(lid, "constraints", list(holder.find("constraints")))
        if holder.find("modifiers") is not None:
            cat.add(lid, "modifiers", list(holder.find("modifiers")))
    for lid, mods in official_root_adds.items():
        cat.add(lid, "modifiers", mods)
    cat.add(CAT_ID, "entryLinks", roots)
    cat.add(CAT_ID, "sharedSelectionEntries", units + keep_entries + blessing_entries)
    if keep_groups:
        cat.add(CAT_ID, "sharedSelectionEntryGroups", keep_groups)
    cat.add(CAT_ID, "sharedRules", keep_rules + [motr])
    cat.add(CAT_ID, "selectionEntries", [rite_root])
    cat.bump("catalogue")
    cat.save()
    print(f"{CAT}: {len(units)} units, {len(keep_entries)} entries, {len(blessing_entries)} Blessings, "
          f"{len(RITES)} Rites of War, {len(keep_rules) + 1} rules added")


def unit_by_name(units, n):
    return next(u for u in units if u.get("name") == n)


if __name__ == "__main__":
    main()
