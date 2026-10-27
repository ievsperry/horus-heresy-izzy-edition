#!/usr/bin/env python3
"""Add the Imperatus Archaeotechnological Relics and bring the Imperatus Psychic Disciplines up to date.

usage: python3 homebrew/add_imperatus_wargear.py

The relics become shared upgrades of the game system, in an "Archaeotechnological Relics" group (one per model)
that the Solar Auxilia Legate Marshal can always take, and the Imperialis Militia Force Commander can take while
its Detachment has the Armoury of Old Night Provenance or its army has the Merchant Princeling or Connoisseur of
Alien Curios Warlord Trait. The Diabolism, Anathemata and Navis Astrologis disciplines already exist; their powers
and weapons are set to the Imperatus text. Running it again changes nothing."""
import html
import sys

sys.path.insert(0, "homebrew")
from faq_tools import GST, PTS, Ops, make_id, whole  # noqa: E402

WARGEAR = "2a1f-7837-f0ef-be44"
DESC = "347e-ee4a-764f-6be3"
GROUP = "Archaeotechnological Relics"
ARMOURY = "4bcd-7022-cefc-04da"
PRINCELING = "442f-6f93-eac9-f857"
CURIOS = "2266-94a7-36e3-dbe4"

RELICS = [
    ("Apex Digital Weapon", 15,
     "Once per game when making a Shooting Attack, a model with an Apex Digital Weapon can declare it will fire either "
     "a Disintegrator, Lascannon, Multi-Melta, Plasma Cannon or Volkite Culverin. When firing this weapon, treat the "
     "model as if it had the Relentless Special Rule."),
    ("Displacer Matrix", 30,
     "A Displacer Matrix provides a 3+ Invulnerable Save. This Invulnerable Save does not stack with other Invulnerable "
     "Saves, and cannot benefit from rules (like Cyber-Familiar wargear) that specifically increase existing saves. If a "
     "model has another Invulnerable Save then the Controlling Player must choose which one to use.\n\n"
     "In addition, the first time a roll of '1' is made for an Invulnerable Save for a model with a Displacer Matrix, "
     "the Wound is ignored, and the model is removed from the battlefield, entering the Controlling Player's Reserves "
     "assigned to a Deep Strike Assault (even if one had already been made earlier in the game). If the model was part "
     "of a unit, they count as having left the unit – even if they would not ordinarily be allowed to do so. No other "
     "units may be assigned to this Deep Strike Assault, and resolving this Deep Strike Assault does not prevent the "
     "Controlling Player from resolving another Deep Strike Assault later in the game if they have units still assigned "
     "to one. This Deep Strike Assault automatically arrives in the Controlling Player's next game turn. If the Deep "
     "Strike Assault is Disordered, or the game does not continue into the next turn (in which this model would "
     "arrive), then the model is counted as Destroyed."),
    ("Grav-Wave Generator", 10,
     "When an enemy unit declares a Charge targeting a unit which includes a model with a Grav-Wave Generator, the unit "
     "may make the Hold The Line Advanced Reaction (see the Horus Heresy: Age of Darkness rulebook, page 330) without "
     "expending a point of the Reactive Player's Reaction Allotment, and automatically passes the associated Morale "
     "Check. This does not allow the unit to make more than one Reaction per Phase, but does allow the Controlling "
     "Player to exceed the normal three Reactions limit in a given phase.\n\n"
     "In addition, a model receives no benefit from the Hammer of Wrath (X) Special Rule if they Charge a unit which "
     "makes a Hold The Line Advanced Reaction that includes a model with a Grav-Wave Generator."),
]

POWERS = {
    "A Dark and Terrible Power":
        "When a Charge is declared for a model with this power, or for a unit that includes a model with this power, the "
        "Controlling Player may choose to make a Psychic check for the model before any dice are rolled to determine the "
        "Charge Distance of that Charge. If the Psychic check is successful then the model with this power gains the "
        "Hammer of Wrath (3) Special Rule and increases both their Strength and Toughness Characteristics by +1 for the "
        "duration of that Assault phase. If the Check is failed then the model suffers Perils of the Warp, and once that "
        "has been resolved gains +1 to both its Strength and Toughness Characteristics until the start of the "
        "Controlling Player's next turn.",
    "Seal the Veil":
        "Instead of making a Shooting Attack, a Psyker with this Psychic Power may select a single enemy unit composed "
        "entirely of models with the Daemon Unit Type or Corrupted Unit Sub-type that is within line of sight and has at "
        "least one model within 18\" of the Psyker. All models in the target unit must reduce their Strength and "
        "Toughness by 1 (to a minimum of Toughness or Strength 1) until the end of the target unit's Controlling Player's "
        "next turn – the Controlling Player of the Psyker using this Power may then choose to make a Psychic check for "
        "the Psyker. If the Check is passed the target unit also suffers Perils of the Warp, and if the Check is failed "
        "then both the target unit and the Psyker using this Psychic Power suffer Perils of the Warp.",
    "Breach the Veil":
        "Instead of making a Shooting Attack, a Psyker with this Psychic Power may select a point within 12\" and at "
        "least 3\" away from any enemy model or Impassable Terrain - place a Blast (3\") Marker to represent the Warp "
        "Rift until this power is resolved.\n\n"
        "The Controlling Player may then choose to make a Psychic check for the model casting this Psychic Power. If the "
        "Check is failed or not taken then the chosen point is scattered as per the normal rules for Scatter. If it "
        "scatters onto Impassable Terrain, within 3\" of an enemy model, or off of the edge of the battlefield then the "
        "model casting this Psychic Power suffers Perils of the Warp, and the chosen point is moved the minimum distance "
        "required in a direction of the Controlling Player's choice to place it clear of all Impassable Terrain, on the "
        "battlefield, and at least 3\" away from any enemy model. If the Check is passed then the Warp Rift does not "
        "scatter.\n\n"
        "Once the final location of the chosen point is determined, the model casting this Psychic Power's Controlling "
        "Player may choose to deploy up to one of the Ruinstorm Daemon units in Reserves onto the battlefield (that "
        "player may choose to place no units if they wish). That unit moves onto the battlefield from any point along "
        "the edge of the Blast marker placed to represent the Warp Rift as if it was entering play from Reserves, "
        "treating the Warp Rift marker as though it was the Controlling Player's battlefield edge.\n\n"
        "Once all models in the unit have moved onto the battlefield, the Warp Rift marker is removed from play. The "
        "Daemon unit brought into play by use of this power may be targeted by the Interceptor Reaction and may act as "
        "normal in the Shooting phase in which it arrives and may declare a Charge in the Assault phase of the turn in "
        "which it enters play.\n\n"
        "Note that to use this power, a player will need access to the Ruinstorm Daemons Army List.",
}


def relic_xml(nl):
    entries, links = [], []
    for name, pts, text in RELICS:
        full = "Archaeotechnological Relic: " + name
        eid = make_id("relic", name)
        desc = html.escape(text, quote=False).replace('"', "&quot;").replace("\n", nl)
        entries.append(
            f'    <selectionEntry id="{eid}" name="{html.escape(full, quote=False)}" hidden="false" collective="false" '
            f'import="true" type="upgrade">{nl}'
            f'      <profiles>{nl}'
            f'        <profile id="{make_id("relic profile", name)}" name="{html.escape(full, quote=False)}" hidden="false" '
            f'typeId="{WARGEAR}" typeName="Wargear Item">{nl}'
            f'          <characteristics>{nl}'
            f'            <characteristic name="Description" typeId="{DESC}">{desc}</characteristic>{nl}'
            f'          </characteristics>{nl}'
            f'        </profile>{nl}'
            f'      </profiles>{nl}'
            f'      <costs>{nl}'
            f'        <cost name="Pts" typeId="{PTS}" value="{pts}"/>{nl}'
            f'      </costs>{nl}'
            f'    </selectionEntry>{nl}')
        links.append(f'        <entryLink id="{make_id("relic link", name)}" name="{html.escape(full, quote=False)}" '
                     f'hidden="false" collective="false" import="true" targetId="{eid}" type="selectionEntry"/>{nl}')
    gid = make_id("relic group")
    group = (f'    <selectionEntryGroup id="{gid}" name="{GROUP}" hidden="false" collective="false" import="true">{nl}'
             f'      <constraints>{nl}'
             f'        <constraint field="selections" scope="parent" value="1" percentValue="false" shared="true" '
             f'includeChildSelections="false" includeChildForces="false" id="{make_id(gid, "max")}" type="max"/>{nl}'
             f'      </constraints>{nl}'
             f'      <entryLinks>{nl}' + "".join(links) + f'      </entryLinks>{nl}'
             f'    </selectionEntryGroup>{nl}')
    return "".join(entries), group, gid


def main():
    o = Ops()
    gst = o.F.text[GST]
    nl = o.F.nl(GST)
    entries, group, gid = relic_xml(nl)

    def add_relics():
        s = o.F.text[GST]
        if gid in s:
            return
        i = s.index("  </sharedSelectionEntries>")
        s = s[:i] + entries + s[i:]
        i = s.index("  </sharedSelectionEntryGroups>")
        s = s[:i] + group + s[i:]
        o.F.replace(GST, 0, len(o.F.text[GST]), s, "Archaeotechnological Relics added")
    o.run("relics", add_relics)

    def link(f, *path, hidden_unless=None):
        def go():
            p, sp = o.at(f, *path)
            s = o.F.text[p]
            if gid in s[sp[0]:sp[1]]:
                return
            ind = o.F.indent_of(p, sp[0]) + "    "
            lid = make_id("relic group link", f)
            if hidden_unless:
                conds = "".join(
                    f'{ind}          <condition field="selections" scope="{scope}" value="1" percentValue="false" shared="true" '
                    f'includeChildSelections="true" includeChildForces="false" childId="{cid}" type="atLeast"/>{nl}'
                    for scope, cid in hidden_unless)
                x = (f'<entryLink id="{lid}" name="{GROUP}" hidden="true" collective="false" import="true" targetId="{gid}" '
                     f'type="selectionEntryGroup">{nl}{ind}  <modifiers>{nl}{ind}    <modifier type="set" field="hidden" '
                     f'value="false">{nl}{ind}      <conditionGroups>{nl}{ind}        <conditionGroup type="or">{nl}'
                     f'{ind}          <conditions>{nl}' + conds.replace(f"{ind}          <condition", f"{ind}            <condition") +
                     f'{ind}          </conditions>{nl}{ind}        </conditionGroup>{nl}{ind}      </conditionGroups>{nl}'
                     f'{ind}    </modifier>{nl}{ind}  </modifiers>{nl}{ind}</entryLink>')
            else:
                x = (f'<entryLink id="{lid}" name="{GROUP}" hidden="false" collective="false" import="true" targetId="{gid}" '
                     f'type="selectionEntryGroup"/>')
            o.F.insert_child(p, sp, "entryLinks", [x], f"{' > '.join(path)}: + {GROUP}")
        o.run(f"{f} relic link", go)

    link("LI - Solar Auxilia", "Legate Marshal", "Solar Auxilia Legate Marshal")
    link("Imperialis Militia", "IM - Force Commander", "1) Force Commander",
         hidden_unless=[("force", ARMOURY), ("roster", PRINCELING), ("roster", CURIOS)])

    for name, text in POWERS.items():
        o.text("gst", "P:" + name, fn=whole(text))
    o.raw("LI - Assassins", "P:Lidless Stare (Psychic Weapon)", what="Assault 1, Pinning, Force, Instant Death",
          fn=lambda x: x.replace(">Pinning, Force</characteristic>", ">Assault 1, Pinning, Force, Instant Death</characteristic>"))
    o.report()


if __name__ == "__main__":
    main()
