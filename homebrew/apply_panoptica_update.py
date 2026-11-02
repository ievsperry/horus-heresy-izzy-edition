#!/usr/bin/env python3
"""Apply what the Liber Panoptica conversion doc (homebrew/source/panoptica.md, the Claude Doc "Liber Panoptica for
The Horus Heresy 2.0 — Homebrew Conversion") changes that apply_expansion_faq.py and apply_core_faq.py did not
already: characteristics, special rules and the rule text of the entries the doc changes.

usage: python3 homebrew/apply_panoptica_update.py

Every change is written against the current data, so running it again changes nothing. A rule whose text the doc
changes gets the doc's wording after it as a "Liber Panoptica:" note (once). Weapon profiles are not here: the
doc's Panoptica Weapon Profiles match additional-weapons.md, except where a later weapon update changed them on
purpose (Medusa Mortar, Thunderblast Cannon, Krak Grenades and the Unwieldy (X) values), which are kept."""
import re
import sys

sys.path.insert(0, "homebrew")
from faq_tools import Ops  # noqa: E402

o = Ops()
LA = "Legiones Astartes"
MARK = "Liber Panoptica:"


def note(f, *path, text, char="Description"):
    """The doc's wording after an entry's text, once."""
    o.text(f, *path, char=char, fn=lambda t: t if MARK in t else t.rstrip() + "\n" + MARK + " " + text)


# ---- characteristics and special rules
o.chars_all("LI - Custodes", "Orion Assault Dropship", Tr="36")
o.chars_all("LI - Solar Auxilia", "Stormhammer", Front="14")
o.rule("LA - World Eaters", "Shabran Darr", add="Shattered Legionary")
o.rule_x("Mech Library", "Warlord Battle Titan", "E:Warlord Battle Titan", rule="Void Shields", to="Void Shields (8)")
o.rule("gst", "Hammerfall Bunker", add=("Hardwired Defences", "Power of the Machine Spirit"))
o.rule("gst", "Vengeance Weapon Battery", add="Hardwired Defences")
o.add_link("LI - Assassins", "Davinite Lodge Priest", to="Psychic Discipline: Anathemata", mn=1, mx=1, pts=0)
o.add_link("LA - Emperor's Children", "Sun Killer Squad", "G:Sun Killer Weapon Choices:", "Multi-Melta", to="Suspensor Web")

# ---- rule text the doc changes
note("gst", "R:Recon Company", text="Legion Scout Squads gain the Line Sub-type. The re-roll for first turn also covers "
     "Strategic Advantage, as well as Seize the Initiative and First Strike attempts.")
note("gst", "R:Armoured Spearhead^", text="one single-model Legion Sicaran, Predator or Kratos Squadron must be taken "
     "as an HQ choice. It gains Master of the Legion and Legiones Astartes Command Tank, must be the Warlord (even "
     "though it is a Vehicle) and must use the Master of Armour Warlord Trait.")
note("gst", "R:Fury Of The Ancients", text="new Limitation: each Dreadnought with the Line Sub-type is worth +1 Victory "
     "Point to the opponent when destroyed.")
note("gst", "R:Auxiliary Vehicle Bay", text="Flyers and models with Movement 0 can never embark in it. A model normally "
     "forbidden in list building (for example by a Rite of War) may still be taken if it starts the game embarked in "
     "an Auxiliary Vehicle Bay.")
note("gst", "R:Rocket Barrage", text="a model that did not move gains Rending (5+), Shell Shock (1) and Pinning with the "
     "weapon until the start of its next turn.")
note("gst", "R:The Stage is Set", text="a model deployed by this rule counts as having arrived by Deep Strike Assault "
     "for Movement, Shooting Attacks and Charges.")
note("Mech Library", "R:Implacable", text="attacks against the model inflict 1 fewer Hull Point of damage (to a minimum "
     "of 1), and Vehicle Damage table rolls against it are reduced by 1.")
note("Mech Library", "P:Ephemera Perfidiae (Cybertheurgic Rite)", text="may target an enemy unit made entirely of "
     "Vehicles, Dreadnoughts or Automata, but not one with any Super-Heavy, Lumbering, Titan or Knight models.")
note("Mech Library", "R:Lacyraemarta", text="Opus Viscera may not be used on a unit locked in combat, and only on units "
     "made entirely of Mechanicum models.")
note("Mechanicum", "P:Forbidden Protocols", char="Text", text="this Warlord Trait can affect a unit Scoria has joined, "
     "even though it no longer contains only Automata.")
note("Mechanicum", "R:Rites of the Beast", text="Scoria has the Artificia Machina, Artificia Cybernetica, Ephemera "
     "Incursus and Anima Malefica Arcana, with all their Rites and weapons.")

o.report()

# ---- the weapon and option changes (edited by element id, after the name-path changes above are saved)
import xml.etree.ElementTree as ET  # noqa: E402
import expansion_tools as et  # noqa: E402
import build_catalogue as bc  # noqa: E402

C = et.NS["cat"]
et.configure("2022 - Legiones Astartes.cat", [], None, "", "panoptica")
done = []


def profile_type(path, name, fn):
    """A weapon profile's Type line, in every profile of that name in a file."""
    t = et.Text(path)
    for m in list(re.finditer(r'<profile [^>]*name="' + re.escape(name) + r'"', t.s)):
        a = m.start()
        b = t.s.index("</profile>", a)
        body = t.s[a:b]
        k = re.search(r'(<characteristic name="Type"[^>]*>)([^<]*)(<)', body)
        new = fn(k.group(2))
        if new != k.group(2):
            t.s = t.s[:a + k.start(2)] + new + t.s[a + k.end(2):]
            done.append(f"{path}: {name}: Type {new}")
    t.save()


# Ephemera Exocluo: Blind is replaced by Sensor Flare
profile_type("2022 - Mech Library.cat", "Ephemera Exocluo (Cybertheurgic Weapon)", lambda x: x.replace("Blind", "Sensor Flare"))
# Talon of Perdition: a model with two gains +2 Attacks instead of +1
for f in ("2022 - Legiones Astartes.cat", "2022 - LA - Blood Angels.cat"):
    profile_type(f, "Talon of Perdition", lambda x: x if "+2 Attacks" in x else x + "; a model with two gains +2 Attacks")


def cost_of(e):
    c = e.find(f"{C}costs/{C}cost")
    return float(c.get("value")) if c is not None else 0.0


def fmt(v):
    return str(int(v)) if float(v).is_integer() else str(v)


ILIASTUS = "10aa-3c70-2bbe-9509"  # the shared entry, shown only to the Blood Angels and Imperial Fists


def iliastus():
    """'Blood Angels or Imperial Fists Infantry or Cavalry, and Dreadnoughts or Vehicles, may exchange a Heavy Flamer
    or Twin-Linked Heavy Flamer for one at +10 points each': in every pick beside a Heavy Flamer it costs the Heavy
    Flamer's points +10 for each weapon (a pair of sponsons +20); picks with a Twin-Linked Heavy Flamer, and the
    Cavalry units' picks with a Heavy Flamer, gain it."""
    for f in ("2022 - Legiones Astartes.cat", "2022 - LA - Blood Angels.cat", "2022 - LA - Imperial Fists.cat"):
        t = et.Text(f)
        root = ET.fromstring(t.s.encode("utf-8"))
        cavalry = {g for u in root.find(C + "sharedSelectionEntries") if u.get("type") == "unit"
                   and any("Cavalry" in (c.get("name") or "") for c in u.iter(C + "categoryLink"))
                   for g in u.iter(C + "selectionEntryGroup")}
        sets, adds = [], []
        for g in root.iter(C + "selectionEntryGroup"):
            items = list(g.findall(f"{C}entryLinks/{C}entryLink")) + list(g.findall(f"{C}selectionEntries/{C}selectionEntry"))
            by = {(x.get("name") or "").lower(): x for x in items}
            n = 2 if "sponson" in (g.get("name") or "").lower() else 1
            il = by.get("iliastus assault cannon")
            hf = by.get("heavy flamer")
            tl = by.get("twin-linked heavy flamer")
            if il is not None and hf is not None and il.find(f"{C}costs/{C}cost") is not None:
                want = cost_of(hf) + 10 * n
                if cost_of(il) != want:
                    sets.append((il.get("id"), want))
            elif il is None and (tl is not None or (hf is not None and g in cavalry)):
                base = tl if tl is not None else hf
                lid = bc.make_id("panoptica iliastus", g.get("id"))
                if lid not in t.s:
                    l = et.link_el("Iliastus Assault Cannon", ILIASTUS, lid, pts=cost_of(base) + 10 * n)
                    l.set("id", lid)
                    mx = base.find(f"{C}constraints/{C}constraint[@type='max']")
                    if mx is not None:
                        bc.el(bc.child(l, "constraints"), "constraint", type="max", value=mx.get("value"),
                              field="selections", scope="parent", shared=True, id=bc.make_id(lid, "max"),
                              percentValue=False, includeChildSelections=False, includeChildForces=False)
                    adds.append((g.get("id"), l))
        for eid, v in sets:
            a, b, _, _ = t.block(eid)
            blk = t.s[a:b]
            blk = re.sub(r'(<cost [^>]*?value=")[^"]*(")', lambda m: m.group(1) + fmt(v) + m.group(2), blk, count=1)
            t.s = t.s[:a] + blk + t.s[b:]
            done.append(f"{f}: Iliastus Assault Cannon {eid}: {fmt(v)} points")
        for gid, l in adds:
            a, b, indent, _ = t.block(gid)
            body = t.s[a:b]
            if "<entryLinks>" in body and not re.search(re.escape(t.nl) + " " * (indent + 2) + "<entryLinks>", body):
                continue
            t.add(gid, "entryLinks", [l])
            done.append(f"{f}: + Iliastus Assault Cannon in {gid}")
        t.save()


iliastus()

# Hammerfall Bunker: may land by Drop Pod or Deep Strike Assault instead of deploying as a Fortification
HAMMERFALL = ("Instead of deploying it as a Fortification, the Hammerfall Bunker may be assigned to a Drop Pod Assault or "
              "Deep Strike Assault. It then gains Orbital Assault Vehicle, Inertial Guidance System and Deep Strike, so it "
              "can land outside your Deployment Zone, and may be taken in a Drop Pod Assault.")
gst = et.Text(et.GST)
groot = ET.fromstring(gst.s.encode("utf-8"))
G = et.NS["gst"]
hb = next(e for e in groot.iter(G + "selectionEntry") if e.get("name") == "Hammerfall Bunker")
oid = bc.make_id("panoptica hammerfall orbital")
if oid not in gst.s:
    e = et.E("selectionEntry", id=oid, name="Orbital Deployment (Drop Pod or Deep Strike Assault)", hidden=False,
             collective=False, import_=True, type="upgrade")
    bc.add_constraint(e, "max", 1, bc.make_id(oid, "max"))
    r = bc.el(bc.el(e, "rules"), "rule", id=bc.make_id(oid, "rule"), name="Orbital Deployment", hidden=False)
    bc.el(r, "description").text = HAMMERFALL
    for rid, rname in (("7fc9-7bcd-b44c-6719", "Orbital Assault Vehicle"), ("d222-fde9-51b8-8739", "Inertial Guidance System"),
                       ("f1e1-986f-c783-ca9e", "Deep Strike")):
        bc.el(bc.child(e, "infoLinks"), "infoLink", id=bc.make_id(oid, rname), name=rname, hidden=False, targetId=rid,
              type="rule")
    bc.add_cost(e, 0)
    gst.add(hb.get("id"), "selectionEntries", [e])
    gst.save()
    done.append("gst: Hammerfall Bunker: + Orbital Deployment")

print(f"{len(done)} weapon and option changes")
for d in done:
    print("  " + d)
