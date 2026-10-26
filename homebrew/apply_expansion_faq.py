#!/usr/bin/env python3
"""Apply the Liber Panoptica FAQ, Errata and Balance Changes for the army books, Legacies and Exemplary Battles
to the official game system and catalogues: points, characteristics, Unit Types, special rules, options and
rule text.

usage: python3 homebrew/apply_expansion_faq.py

Every change is written against the current data, so running it again changes nothing. Weapon profile
replacements are made by add_gst_weapons.py and core rule changes by apply_core_faq.py. Clarifications with
no data entry (how a rule is played, scenario notes) are not here."""
import re
import sys

sys.path.insert(0, "homebrew")
from faq_tools import Ops, append, make_id, sub, whole  # noqa: E402

o = Ops()
LA = "Legiones Astartes"


def every(op, unit, *path, **kw):
    """Run an operation on a unit in every catalogue that has it."""
    files = o.units(unit)
    if not files:
        o.failed.append(f"{unit}: no such unit")
    for f in files:
        getattr(o, op)(f, unit, *path, **kw)


# ======================================================================= Liber Astartes & Hereticus (p80)
o.cost_each(LA, "Contemptor Dreadnought Talon", "Contemptor Dreadnought", "Gravis Melta Cannon", v=15)
o.cost_each(LA, "Contemptor Dreadnought Talon", "Contemptor Dreadnought", "Kheres Assault Cannon", v=5)
o.price(LA, "Contemptor Dreadnought Talon", 200, 200, "Contemptor Dreadnought")
o.category(LA, "Tactical Support Squad", add="Line Sub-type")
o.retarget(LA, "Storm Eagle Gunship", "1) Hull (Front) Weapon Options", "Multi-Melta", to="Gravis Melta Cannon")
o.price(LA, "Xiphon Interceptor", 145)
o.rule(LA, "Dreadclaw Drop Pod", add="Assault Vehicle")
o.cost(LA, "Heavy Support Squad", "1) Squad Weaponry:", "Lascannon", v=15)
o.cost(LA, "Heavy Support Squad", "1) Squad Weaponry:", "Volkite Culverin", v=10)
o.category(LA, "Sicaran Venator Squadron", add="Bombard Sub-type")
o.drop(LA, "Sicaran Venator Squadron", "?? Bombard Sub-type ?? (Ambiguity)")
o.char(LA, "Sicaran Venator Squadron", "P:Sicaran Venator", UT="Vehicle (Bombard)")
o.raw(LA, "Sicaran Venator Squadron", "P:Sicaran Venator", what="Bombard always shown", fn=lambda x: re.sub(
    r'\s*<modifier type="append" field="e555-4aed-dfcc-c0b4" value="\(Bombard\)">.*?</modifier>', "", x, flags=re.S))
o.price(LA, "Scorpius Squadon", 175, 160, "Scorpius")
o.char(LA, "Arquitor Squadron", "P:Arquitor", Front="13", UT="Vehicle (Bombard, Reinforced)")
o.category(LA, "Arquitor Squadron", add="Reinforced Sub-type")
o.char(LA, "Deathstorm Drop Pod Squadron", "P:Legion Deathstorm Drop Pod", BS="4")
o.price(LA, "Glaive", 575)
o.price(LA, "Fellblade", 600)
o.price(LA, "Falchion", 625)
o.add_link(LA, "Mastodon", to="Magna-Melta Array", shown="Hull (Front) Mounted Magna-Melta Array")
o.rule(LA, "Mastodon", add="Reinforced Shell")

o.add_link(LA, "Heavy Support Squad", "1) Squad Weaponry:", "Multi-Melta", to="Suspensor Web")

# ======================================================================= Martian Civil War
NIGHT = ("If the Player with Strategic Advantage elects to not activate Night Fighting, the Opposing Player may still "
         "have the Night Fighting Rules in effect on a roll of a 4+.")
o.text("gst", "R:Night Fighting", fn=append(NIGHT))
o.text("LI - Solar Auxilia", "R:Iron Pattern Cohort", fn=lambda t: t if "Corrupted Engine" in t else t.replace(
    "\n\nLimitations", "\n• An army that uses the Cohort Doctrine: Iron Pattern Cohort may take a single unit with the "
    "Corrupted Engine Unit Sub-type. An army can only include a maximum of one unit with the Corrupted Engine Unit "
    "Sub-type chosen in this manner.\n\nLimitations", 1))
o.rule_x("Mech Library", "Blood Slaughterer", "Blood Slaughterer", rule="Malefic Aegis (X)", to="Malefic Aegis (5+)")
o.rule("Mech Library", "Blood Slaughterer", "Blood Slaughterer", add="Rage (2)")
o.text("Mech Library", "R:Animatus Malevolence (Cybertheurgic Rite)", fn=sub(
    "that is entirely composed of models with the Corrupted Engine Unit Sub-type and then",
    "that contains any models with the Corrupted Engine Unit Sub-type or models with both the Automata Unit Type and "
    "the Corrupted Unit Sub-type, and then"))
o.retarget(LA, "Kaedes Nex", "Power Armour", to="Artificer Armour")
o.rule(LA, "Kaedes Nex", add="Consul (Moritat)")

# ======================================================================= Beta-Garmon
o.text("gst", "R:Panoply of Old (X)", fn=append(
    "It should be noted that any Legion-specific upgrades which allow a unit or model to purchase a Special Rule, Unit "
    "Type or Sub-type, or so on are permitted to be selected by this Oath as though they were items of Wargear - unless "
    "this would be prevented by the inherent restrictions in this Oath."))
o.text("gst", "R:The Spoils of Victory", fn=sub(
    "Note that units that are not normally allowed to make a Sweeping Advance gain no benefit from this Oath.",
    "†Note that units that are not normally allowed to make a Sweeping Advance, such as models that have Legion "
    "Cataphractii Terminator Armour, gain no benefit from this Oath."))
o.text("gst", "R:Augmetic Transport Bay", fn=append(
    "A Legion Rhino Transport that gains this Special Rule may be selected as a Dedicated Transport for a Legion "
    "Tactical Squad or Legion Despoiler Squad composed of up to 15 models, rather than 10 models as is normally the case."))
o.rule(LA, "Overseer", add="Field Officer")
o.text("LI - Solar Auxilia", "R:Reconnaissance Pattern Cohorts", fn=lambda t: re.sub(
    r"\s*NOTE\s*\nThe 2nd bullet point.*$", "", t, flags=re.S).replace(
    "Solar Auxilia Veletaris Assault Squadrons", "Solar Auxilia Hermes Veletaris Squadrons"))
o.drop("LI - Solar Auxilia", "Reconnaissance Pattern Cohorts", "R:Outflank (Ambiguous Recon Cohorts)")
o.cond_rule("LI - Solar Auxilia", "Hermes Veletaris Squadron", rule="Outflank", child="7e09-aae1-d5ff-d43e")
o.text("gst", "R:Mechanised Unit Sub-type", fn=sub(
    "• A model with the Mechanised Unit Sub-type is affected by the Haywire, Detonation and Battlesmith (X) special "
    "rules as if it had the Dreadnought Unit Type.",
    "• Any attacks made against a unit with the Mechanised Unit Sub-type are resolved as if the model had the "
    "Dreadnought Unit Type. Note that this affects any Wargear, Weapons, Special Rules, Psychic Powers, or any other "
    "abilities."))
AETHON = ("LI - Solar Auxilia", "Aethon Heavy Sentinel Squadron", "Aethon Heavy Sentinel")
o.cost(*AETHON, "Autocannon", v=0)
o.cost(*AETHON, "Volkite Culverin", v=5)
o.cost(*AETHON, "Lascannon", v=10)
o.cost(*AETHON, "Heavy Incinerator", v=5)
o.cost(*AETHON, "Melta lance", v=15)
o.cost(*AETHON, "Hunter-Killer Missile", v=10)
o.char("LI - Solar Auxilia", "Lifeward Section", "P:Auxilia Protector", WS="5")
o.rule("LI - Solar Auxilia", "Lifeward Section", add="Relentless")
o.rule("LA - Sons of Horus", "Tybalt Marr", add="Shattered Legionary")
o.char(LA, "Shadrak Meduson", "P:Shadrak Meduson", WS="6")
o.char(LA, "P:Legion Optae", A="3")
o.text(LA, "R:Souls of Iron", fn=lambda t: t if "Stubborn" in t else t.replace(
    "if there is an enemy unit within range,", "if there is an enemy unit within range that they are able to inflict "
    "Wounds or Hull Points of Damage upon with weapons the unit is equipped with,").replace(
    "any Pinning tests it is required to take.", "any Pinning tests it is required to take, and gains the Stubborn "
    "Special Rule."))
o.cond_rule(LA, "Despoiler Squad", "L:Inductii", rule="Rage (2)", child="296e-301e-3ce1-1c15")
o.text(LA, "R:Barbaran Resilience", fn=lambda t: t.replace(
    "ten or more models at the start of a given Phase, this rule", "ten or more models at the start of resolving the "
    "Wound Pool, then this rule").replace("at the start of a given Phase", "at the start of resolving the Wound Pool"))

# ======================================================================= Siege of Cthonia
# (the Night Fighting note is the same as the Martian Civil War's)
o.text("LA - Imperial Fists", "P:Warlord: Butcher of Larissan", char="Text", fn=lambda t: t if "Blood Feud" in t else t.replace(
    "(to a minimum of 0)", "(to a minimum of 1)").replace(
    "controlling player. In addition, an army", "controlling player. Note that this ability cannot be used for any "
    "Victory Points scored ‘at the end of the game’, such as those awarded by the Blood Feud mission. In addition, an army"))
o.text("LA - Imperial Fists", "P:The Tyrant’s Regalia", fn=append(
    "In addition, a unit that includes Lord-Castellan Evander Garrius may not make Sweeping Advances."))
o.rule("LA - Sons of Horus", "Vheren Ashurhaddon", add="Outflank")
o.text(LA, "P:Decurion Defensor", fn=append(
    "The Advanced Reactions provided by the Legiones Decurion Defensor allows all models in a unit to participate in the "
    "Advanced Reaction, so long as at least one model in the unit has the Legiones Decurion Defensor Upgrade."))
o.cost_if(LA, "Tactical Squad", "L:Inductii", v=25, child="b2b4-2198-0b90-dd9f")
o.text(LA, "Tactical Squad", "L:Inductii", "R:Dark Angels Legion Inductii Template",
       fn=sub("volkite charger at no additional cost", "volkite charger at a cost of +25 points for the unit"))

# ======================================================================= Liber Astartes (p86)
for f in o.units("Dawnbreaker Cohort"):
    o.cost(f, "Dawnbreaker Cohort", "Dawnbreaker w/ Falling-Star Power Spear", v=30)
    o.cost(f, "Dawnbreaker Cohort", "Dawnbreaker w/ Equinox Power Blade Case", v=35)
    o.cost(f, "Dawnbreaker Cohort", "Dawnbreaker Champion", v=65)
o.cost(LA, "Praetor, Cataphractii", "1) Armour Choice", "Gorgon Terminator Armour", v=10)
o.cost(LA, "Centurion, Cataphractii", "1) Armour Choice", "Gorgon Terminator Armour", v=10)
o.text(LA, "P:Gorgon Terminator Armour", fn=whole(
    "Gorgon Terminator armour confers a 2+ Armour Save, a 5+ Invulnerable Save, and the Augmetics (5+) Special Rule.\n"
    "At the end of any Phase in which a model with Gorgon Terminator armour has passed at least one Armour Save or "
    "Invulnerable Save, roll a D6. On the result of a 4+, all enemy units with at least one model within 6\" of the "
    "model with Gorgon Terminator armour must test as if they had been wounded by a weapon with the Blind special rule. "
    "Any unit that is composed entirely of models with Gorgon Terminator armour are immune to this effect."))
every("rule", "Gorgon Terminator Squad", remove="Feel No Pain (X)", add="Augmetics (5+)")
every("rule", "Medusan Immortal Squad", add="Relentless")
every("add_link", "Medusan Immortal Squad", "3) Dedicated Transport:", to="Termite Assault Drill", mn=None)
o.text(LA, "P:Argyrum Pattern Boarding Shield", fn=append(
    "An Argyrum Pattern Boarding Shield counts as a Boarding Shield for all intents and purposes, including Rites of War, "
    "Special Rules, and wargear limitations which either require their use or prevent it (such as a Master of Signals "
    "being prevented from taking a Boarding Shield), though it does not confer any of the benefits normally gained from "
    "a Boarding Shield from any such sources.\n\n"
    "In addition, a model armed with an Argyrum Pattern Boarding Shield cannot claim bonus attacks for having more than "
    "one melee weapon."))
for f in o.units("Invictarus Suzerain Squad"):
    U = (f, "Invictarus Suzerain Squad")
    o.cost(*U, "Suzerain w/Bolt Pistol & Legatine Axe", v=35)
    o.cost(*U, "Suzerain w/Bolt Pistol & Thunder Hammer", v=45)
    o.cost(*U, "Suzerain w/Plasma Pistol & Legatine Axe", v=45)
    o.cost(*U, "Suzerain w/Plasma Pistol & Thunder Hammer", v=55)
    o.chars_all(f, "Suzerain", UT="Infantry (Heavy)")
    o.rule(*U, add="Chosen Warriors")
    o.add_link(*U, "2) Dedicated Transport:", to="Termite Assault Drill", mn=None)
o.cat_strip("Invictarus Suzerain Squad", ("Line Sub-type", "Character"))
every("add_link", "Praetorian Breacher Squad", "3) Dedicated Transport:", to="Termite Assault Drill", mn=None)
o.text("gst", "R:The Covenant of Fire", fn=sub(
    "• Pyroclast Squads and Legion Tactical Support Squads that include any models with Dragon’s Breath flamers may be "
    "chosen as Troops choices in a Detachment using this Rite of War and gain the Line Unit Sub-type.",
    "• Pyroclast Squads may be chosen as Troops choices in a Detachment using this Rite of War gain the Line Unit "
    "Sub-type. Legion Tactical Support Squads that include any models with Dragon’s Breath Flamers gain the Heart of the "
    "Legion Special Rule."))
o.text("gst", "R:The Awakening Fire", fn=lambda t: t if "Adherents" in t else re.sub(
    r"Effects\n• [^\n]*", "Effects\n• Salamanders Adherents Squads chosen as Troops choices in a Detachment using this Rite "
    "of War lose the Support Squad Special Rule and gain the Line Unit Sub-type.", t, count=1))
o.text(LA, "R:Dragon's Breath", fn=append("All weapons with this Special Rule gain the Breaching (6+) Special Rule."))
o.cost_named("Mantle of the Elder Drake", 25)

# ======================================================================= Liber Astartes (p87)
o.text("gst", "R:Legiones Astartes (Raven Guard)", fn=whole(
    "Shadow and Fury: Models with the Legiones Astartes (Raven Guard) Special Rule gain one of the following Special "
    "Rules based on the Unit Type and Wargear of the model. Models that do not fulfil one of the listed criteria gain no "
    "additional benefit.\n"
    "• Models with the Legiones Astartes (Raven Guard) Special Rule that have the Infantry Unit Type, but are not "
    "equipped with Terminator Armour of any kind, a Legion Warhawk Jump Pack or a Corvid Pattern Jump Pack gain the "
    "Talons Special Rule.\n"
    "• Models with the Legiones Astartes (Raven Guard) Special Rule that have the Dreadnought or Primarch Unit Types; any "
    "models with the Legiones Astartes (Raven Guard) Special Rule that are equipped with Terminator Armour of any "
    "variety, a Legion Warhawk Jump Pack or a Corvid Pattern Jump Pack gain the Falcons Special Rule.\n"
    "• Models with the Legiones Astartes (Raven Guard) special rule that have the Cavalry Unit Type or the both the "
    "Vehicle Unit Type and the Fast or Flyer Unit Sub-Types gain the Hawks Special Rule.\n\n"
    "Talons: If a unit composed entirely of models with the Talons Special Rule is targeted by a Shooting Attack, all "
    "models in the unit gain the Shrouded (6+) special rule if the attacking unit is more than 8\" from any model in the "
    "target unit. In addition, all models with this Special Rule also gain the Infiltrate Special Rule.\n\n"
    "Falcons: Any models with this Special Rule may re-roll all failed To Hit rolls of 1 in any Assault phase in which "
    "they make a successful Charge - even if that Charge is considered Disordered.\n\n"
    "Hawks: Any models with this Special Rule gain the Shrouded (6+) Special Rule on any turn in which they Run, Move "
    "Flat Out or move as a Zooming Flyer, with this benefit lasting until the start of the Controlling Player’s next "
    "turn - or if that model would already gain the Shrouded (6+) Special Rule, it gains the Shrouded (5+) Special Rule "
    "(if a model already has Shrouded (5+) or better than it gains no additional benefit)."))
o.text("gst", "R:Decapitation Strike", fn=sub(
    "Shrouded (5+) special rule for the duration of the Game Turn in which they are deployed to the battlefield.",
    "Shrouded (5+) Special Rule until the start of the Controlling Player’s Next Turn when they enter play."))

# ======================================================================= Liber Astartes (p84)
o.text("gst", "R:The Eskaton Imperative", fn=sub(
    "gain +1 to all To Wound rolls made against models in any zone",
    "gain +1 to all To Wound rolls made against a unit which has half or more of its models in any zone"))
o.text("gst", "R:The Storm Of War", fn=sub(
    "and must have the Stormwing Unit Sub-type.",
    "and must have the Stormwing Unit Sub-type. Note that Legion Centurions selected in this manner do not prevent "
    "Legion Apothecaries or Legion Techmarines from joining the unit during list construction, contrary to the normal "
    "rules around Legion Apothecaries or Legion Techmarines joining units with the Independent Character Special Rule. "
    "Any Centurions selected in this manner may not also select a Legion Company Command Squad."))
o.text("gst", "R:The Unbroken Vow", fn=lambda t: t if "Compulsory Troops choices in a Detachment using this Rite of War gain the Line" in t else t.replace(
    "\nLimitations", "\n• Any Legion Terminator Cataphractii Squads and Legion Terminator Tartaros Squads taken as "
    "Compulsory Troops choices in a Detachment using this Rite of War gain the Line Sub-type.\nLimitations", 1))
o.text("gst", "R:Serpent's Bane", fn=sub(
    "the controlling player must select three enemy Primarch, HQ, Elites or Lords of War choices as Priority Targets "
    "and declare the chosen units to their opponent.",
    "the Controlling Player must select three enemy units which contain a model selected as a part of a Primarch, HQ, "
    "Elites, or Lord of War choice."))
for unit in ("Inner Circle Knights Cenobium", "Inner Circle Knights Cenobium - Order of the Broken Claws"):
    for f in o.units(unit):
        o.category(f, unit, "Order Cenobites", remove="Character")
        o.rule(f, unit, add="Chosen Warriors")
        o.cost_each(f, unit, "Thunder Hammer", v=5)
o.char("LA - Dark Angels", "P:Order Cenobites", UT="Infantry (Heavy)")
o.price("LA - Dark Angels", "Dreadwing Interemptor Squad", 150, 25, "Interemptors", n=4)
o.text("LA - Dark Angels", "P:Regalia of the Shattered Sceptre", fn=append(
    "In addition, The Regalia of the Shattered Sceptre confers the Bulky (2) Special Rule, and a unit that includes "
    "Marduk Sedras may not make Sweeping Advances."))
o.text("gst", "R:Legiones Astartes (White Scars)", fn=sub(
    "to Seize the Initiative, the controlling player",
    "to Seize the Initiative (or otherwise has Strategic Advantage), the controlling player"))
o.text(LA, "P:Shamshir Jetbike", fn=append(
    "A model with the Infantry Unit Type that selects a Legion Shamshir Jetbike as an upgrade (or is otherwise equipped "
    "with one as part of its basic Wargear) must change its Unit Type to Cavalry (Antigrav), keeping any other Unit "
    "Sub-types it previously had, changes its Movement Characteristic to 19\", gains the Firing Protocols (2), "
    "Battle-Hardened (1), Skilled Rider, and Hammer of Wrath (1) Special Rules and improves its Armour Save to 2+ if it "
    "was worse. A model that is equipped with a Legion Shamshir Jetbike counts as having a Legion Scimitar Jetbike for "
    "rules and interactions that affect or require that wargear."))
o.rule(LA, "E:Shamshir Jetbike", add=("Battle-Hardened (1)", "Skilled Rider"))
o.rule("LA - White Scars", "Jaghatai Khan", add="Outflank")
o.text("LA - White Scars", "R:Sojutsu Pattern Voidbike", fn=append(
    "If Jaghatai Khan selected his Sojutsu Pattern Voidbike, he is counted as having a Legion Scimitar Jetbike for rules "
    "and interactions that affect or require that wargear.\n"
    "Note that even though Jaghatai Khan is counted as having the Cavalry Unit Type whilst upgraded to have a Sojutsu "
    "Pattern Voidbike for the purposes of any Rules, he cannot be affected by Narthecium Wargear."))

# ======================================================================= Liber Astartes (p82)
o.text("gst", "P:Geo-locator Beacon", fn=sub("As long as a model with this special rule", "As long as a model equipped with a Geo-Locator Beacon"))
for bike in ("Scimitar Jetbike", "Spatha Combat Bike"):
    o.text(LA, "P:" + bike, fn=append(
        "A model equipped with a Legion " + bike.replace("Jetbike", "Jetbike").replace("Combat Bike", "Combat Bike") +
        " gains the Battle-Hardened (1) and Skilled Rider Special Rules and sets its Wounds Characteristic to 2, unless it "
        "already has a higher starting Wounds Characteristic."))
    o.rule(LA, "E:" + bike, add=("Battle-Hardened (1)", "Skilled Rider"))
o.text("gst", "P:Scout Armour", fn=append("A model with Scout armour gains the Light Sub-type."))
o.raw(LA, "E:Teleport Strike", what="also Sons of Horus and Night Lords", fn=lambda x: x if "01b4-57c7-bf61-2abf" in x else x.replace(
    '<condition type="equalTo" value="0" field="selections" scope="force" childId="a0e1-f2c4-8bcd-0723" shared="true" percentValue="false" includeChildSelections="true" includeChildForces="false"/>',
    '<condition type="equalTo" value="0" field="selections" scope="force" childId="a0e1-f2c4-8bcd-0723" shared="true" percentValue="false" includeChildSelections="true" includeChildForces="false"/>\n'
    '                <condition type="equalTo" value="0" field="selections" scope="force" childId="01b4-57c7-bf61-2abf" shared="true" percentValue="false" includeChildSelections="true" includeChildForces="false"/>\n'
    '                <condition type="equalTo" value="0" field="selections" scope="force" childId="b28b-71f7-e4f4-8f9c" shared="true" percentValue="false" includeChildSelections="true" includeChildForces="false"/>'))
o.text(LA, "R:Teleport Strike", fn=whole(
    "All models with the Legiones Astartes (Imperial Fists), (Sons of Horus) or (Night Lords) Special Rule in a unit "
    "equipped with any form of Terminator Armour may be given the Deep Strike Special Rule for +25 points per unit.\n"
    "Any model with the Legiones Astartes (Imperial Fists), (Sons of Horus) or (Night Lords) Special Rule and the "
    "Independent Character Special Rule may be given the Deep Strike Special Rule for +20 points per model."))

# ======================================================================= Liber Astartes (p85)
o.cat_strip("Golden Keshig Squadron", ("Heavy Sub-type",))
o.char("LA - White Scars", "P:Golden Keshig Rider", UT="Cavalry (Antigrav)")
o.char("LA - White Scars", "P:Golden Keshig Champion", UT="Cavalry (Antigrav, Character)")
o.text("gst", "R:Ungainly", fn=sub("on a turn in which it makes a successful Charge,",
                                   "on a turn in which it makes a Charge (even if that Charge is Disordered),"))
for f in o.units("Ebon Keshig Cohort"):
    o.add_link(f, "Ebon Keshig Cohort", to="Land Raider Proteus Carrier", shown="Dedicated Transport: Land Raider Proteus Carrier (5 models or fewer)", mn=None)
    o.add_link(f, "Ebon Keshig Cohort", to="Land Raider Spartan", shown="Dedicated Transport: Land Raider Spartan", mn=None)
for w in ("Frost Axe", "Frost Claw", "Frost Sword"):
    o.cost(LA, "G:Power Weapon (all)", w, v=0)
    o.cost(LA, "Speaker Of The Dead", w, v=0)
o.cost(LA, "G:Power Weapon (all)", "Great Frost Blade", v=5)
o.cost(LA, "Speaker Of The Dead", "Great Frost Blade", v=5)
o.text(LA, "P:Stormwrought", fn=sub(
    "if the Check is failed the Shrouded (5+) special rule is applied to the target unit and the Psyker",
    "if the Check is failed the Psyker"))
o.text("gst", "R:The Stone Gauntlet", fn=lambda t: t.replace(
    "may reroll all failed Invulnerable Saves made against", "may re-roll all failed Invulnerable Saves of 1 made against").replace(
    "must select Phalanx Warder Squads to fill all Compulsory", "must select Phalanx Warder Squads or Legion Breacher "
    "Squads to fill all Compulsory"))
VIGIL = ("Any model with both the Independent Character and Legiones Astartes (Imperial Fists) Special Rule that does not "
         "also have the Unique Unit Sub-type may take a Vigil Storm Shield for +15 points. Any model with the Legiones "
         "Astartes (Imperial Fists) Special Rule and Legion Cataphractii or Legion Tartaros Terminator Armour may exchange "
         "a Combi-Bolter for a Vigil Storm Shield for +10 points each.\n\n")
SHIELD = ("A Vigil Storm Shield provides a 5+ Invulnerable Save or increases an Invulnerable Save the model already has "
          "by one step (for example, from 5+ to 4+, to a maximum of 3+). A model with a Vigil Storm Shield may not claim "
          "an additional attack for a second weapon in close combat or make attacks with any weapon that has the "
          "Two-handed Special Rule.")
o.text("LA - Imperial Fists", "P:Vigil Storm Shield", fn=whole(VIGIL + SHIELD))
o.text(LA, "P:Vigil Storm Shield", fn=whole(SHIELD))
o.rule("LA - Imperial Fists", "Sigismund", remove="Eternal Warrior", add="Emperor's Chosen")
o.text("gst", "P:Blood Angels Advanced Reaction", fn=sub(
    "composed entirely of models with the Infantry Unit Type and the Legiones Astartes (Blood Angels)",
    "composed entirely of models with the Infantry or Cavalry Unit Type and the Legiones Astartes (Blood Angels)"))

# ======================================================================= Liber Hereticus (p88)
EC, IW, NL, WE, TS, SOH, WB, AL = ("LA - Emperor's Children", "LA - Iron Warriors", "LA - Night Lords", "LA - World Eaters",
                                   "LA - Thousand Sons", "LA - Sons of Horus", "LA - Word Bearers", "LA - Alpha Legion")
o.category(EC, "Phoenix Terminator Squad", "Phoenix Terminators", remove="Character")
o.category(EC, "Phoenix Terminator Squad", "Phoenix Terminator Standard Bearer", remove="Character")
o.char(EC, "P:Phoenix Terminator", UT="Infantry")
o.char(EC, "P:Phoenix Champion", UT="Infantry (Character)")
o.rule(EC, "Phoenix Terminator Squad", add="Chosen Warriors")
o.rule(EC, "Captain Saul Tarvitz", add="Shattered Legionary")
o.category(IW, "Perturabo", "E:Perturabo", add="Heavy Sub-type")
o.char(IW, "P:Perturabo", UT="Primarch (Heavy, Unique)")
o.add_link(IW, "Perturabo", "E:Perturabo", to="Nuncio-Vox")
o.add_link(IW, "Perturabo", "E:Perturabo", to="Cognis-Signum")
o.text(IW, "P:Omni-scope", fn=sub("ignores all the effects of Night Fighting,", "has the Night Vision Special Rule. In addition,"))
o.text("gst", "R:Terror Assault", fn=lambda t: t.replace(
    "\n• An army whose Primary Detachment has this Rite of War may not include any Lords of War choices or models with "
    "the Super-heavy Sub-type.", "").replace(
    "\nLimitations", "\n• Terror Squads taken as Compulsory Troops in a Detachment using this Rite of War gain the Line "
    "Sub-type.\nLimitations", 1) if "Terror Squads taken as Compulsory" not in t else t)
o.cost(LA, "G:Power Weapon (all)", "Chainblade", v=0)
o.cost(LA, "G:Power Weapon (all)", "Chainglaive", v=0)
for m, v in (("Executioner w/Chainsword", 22), ("Executioner w/Chainglaive", 32), ("Executioner w/Chainblade", 32),
             ("Executioner w/Chainaxe", 27)):
    o.cost(NL, "Terror Squad", m, v=v)
o.price(NL, "Terror Squad", 135 - 18 - 4 * 22)
o.char(NL, "P:Executioner", W="2")
o.char(NL, "P:Headsman", W="2")
o.price(NL, "Night Raptor Squad", 150 - 25 - 4 * 25)
o.cost(NL, "Contekar Terminator Squad", "Contekars", v=45)
o.price(NL, "Contekar Terminator Squad", 250 - 65 - 4 * 45)
o.text("gst", "R:Legiones Astartes (World Eaters)", fn=sub(
    "On any turn in which a unit with this special rule makes a successful Charge",
    "On any turn in which a model with this special rule makes a successful Charge"))
o.text("gst", "P:World Eaters Advanced Reaction", fn=sub(
    "targeting a friendly unit with the Infantry Unit Type under", "targeting a friendly unit with the Infantry or Cavalry "
    "Unit Type under"))

# ======================================================================= Liber Hereticus (p89)
o.text("gst", "R:Berserker Assault", fn=sub(" This Charge may not initiate a Multiple Combat.", ""))
o.text(LA, "R:Ravening Madmen", fn=sub("(this does not affect the attacking unit's Strength",
                                       "(this does affect the attacking unit's Strength"))
for f in (WE, LA):
    o.text(f, "R:Red Sands", fn=lambda t: t.replace("enemy models with the Character sub-type",
                                                    "enemy models with the Chosen Warrior Special Rule, Character Sub-type").replace(
        "enemy Characters or Primarchs", "enemy models with the Chosen Warrior Special Rule, Characters or Primarchs"))
o.text(LA, "R:Achean Force", fn=append(
    "A model with the Dreadnought Unit Type and a weapon with the Achean Force Special Rule may activate it despite "
    "normally being prevented from doing so because they do not have the Psyker Sub-type."))
o.rule(TS, "Magnus the Red", "E:Magnus the Red", add="Psychic Mastery (3)")
o.rule(TS, "Ahzek Ahriman", "E:Ahzek Ahriman", add="Psychic Mastery (2)")
o.text(TS, "P:Sire of the Thousand Sons", char="Text", fn=sub("All models with the Infantry Unit Type", "All models with the Infantry or Cavalry Unit Type"))
o.text(LA, "P:Warlord: Sire of the Thousand Sons", char="Text", fn=lambda t: t.replace(
    "Infantry Unit Type", "Infantry or Cavalry Unit Type", 1) if "Infantry or Cavalry" not in t else t)
o.cost(TS, "E:Castellax-Achea Automata", "Castellax-Achea", v=95)
o.cost(TS, "E:Castellax-Achea Automata", v=5)
o.text(TS, "R:Psy -automata", fn=lambda t: t if "Rapid-Fire" in t else (lambda i: t[:i] + t[i:].replace(
    "• Models with the Psy -automata Sub-type may fire Heavy and Ordnance weapons and count as Stationary even if they "
    "moved in the preceding Movement phase, and may declare charges as normal regardless of any Shooting Attacks made in "
    "the same turn.", "• Models with the Psy-Automata Unit Sub-type may declare a charge in the same turn in which they "
    "shoot a Rapid-Fire Weapon.", 1))(0))
o.text("gst", "R:The Achaean Configuration", fn=sub("must include at least one Legion Techmarine Covenant.",
                                                    "must include at least one Legion Techmarine Covenant or Thousand Sons Numerologist Cabal."))

# ======================================================================= Liber Hereticus (p90)
o.text("gst", "R:The Black Reaving", fn=lambda t: t if "conferred by this Rite of War is also" in t else t.replace(
    "\nLimitations", "\n• The Deep Strike Special Rule conferred by this Rite of War is also conferred to any models with "
    "the Character Sub-type that join a unit given it by the Rite of War.\n• The Outflank Special Rule conferred by any "
    "source is also conferred to any models with the Character Sub-type that join a unit which possesses it in a "
    "Detachment using this Rite of War.\nLimitations", 1))
o.add_link(SOH, "Justaerin Terminator Squad", "2) Dedicated Transport", to="Land Raider Spartan", mn=None)
o.cost_all(SOH, "Reaver Attack Squad", ("Power Maul", "Power Sword", "Power Lance", "Power Axe", "Carsoran Power Axe",
                                        "Carsoran Power Tabar", "Charnabal Glaive", "Charnabal Sabre", "Charnabal Tabar"), 5)
o.rule(SOH, "Reaver Attack Squad", add="Outflank")
o.rule(SOH, "Maloghurst the Twisted", add="Broken Soul")
o.rule(SOH, "Garviel Loken", add="Shattered Legionary")
o.text(SOH, "R:Born Survivor", fn=lambda t: t.replace("then the Warlord is not removed", "then the model is not removed"))
for f in ("gst", WB):
    o.text(f, "P:Unswerving Devotion", char="Text", fn=sub("Any units that include at least one model with the Legiones Astartes (Word Bearers)",
                                                           "Any friendly units that include at least one model with the Legiones Astartes (Word Bearers)"))
DARK = ("Any unit with the Traitor Allegiance, and the Infantry, Dreadnought, or Cavalry Unit Type as well as the Legiones "
        "Astartes (Word Bearers) special rule may be upgraded with Dark Channelling for +25 points per unit. All models in "
        "a unit with this upgrade gain the Corrupted Unit Sub-type.")
o.text(LA, "P:Dark Channelling", fn=whole(DARK))
o.text(LA, "P:Dark Channeling", fn=whole(DARK))
o.cost_named("Dark Channeling", 25)
o.cost_named("Dark Channelling", 25)
o.cost(WB, "Tainted Weapon", v=5)
for w in ("Tainted Axe", "Tainted Blade", "Tainted Maul"):
    o.cost(LA, "G:Power Weapon (all)", w, v=5)
o.text("gst", "R:Corrupted Sub-type", fn=sub(
    "• No model that does not also have the Corrupted Unit Sub-type or the Daemon Unit Type may join",
    "• No unit that does not also have the Corrupted Unit Sub-type or the Daemon Unit Type may join"))
o.raw(LA, "E:Diabolist", what="needs the Traitor Allegiance", fn=lambda x: x if "f9c0-0c5a-3e24-58c7" in x else re.sub(
    r'(\n(\s*)<condition [^>]*childId="9dbf-0760-d7ae-f125"[^>]*/>)',
    lambda m: m.group(1) + "\n" + m.group(2) + '<condition field="selections" scope="roster" value="1" percentValue="false" '
    'shared="true" includeChildSelections="true" includeChildForces="false" childId="f9c0-0c5a-3e24-58c7" type="atLeast"/>',
    x, count=1))

# ======================================================================= Liber Hereticus (p91)
for f in (WB, LA):
    o.text(f, "R:The Power of the Word", fn=lambda t: re.sub(
        r"^Any (Legion )?Command Squad, (Legion )?Cataphractii Command Squad or (Legion )?Tartaros Command Squad",
        "Any unit with the Retinue Special Rule", t))
o.text("gst", "R:The Coils Of The Hydra", fn=append(
    "You may select up to three different units via the Rewards of Treachery Special Rule, but these must all have the "
    "same variant of the Legiones Astartes Special Rule (for example, Legiones Astartes (Iron Warriors)) on their unit "
    "profile. Any units selected via the Rewards of Treachery Special Rule change their allegiance to match that of the "
    "Detachment they are taken in."))
o.category(AL, "E:Alpharius", "E:Alpharius", add="Skirmish Sub-type")
o.char(AL, "E:Alpharius", "P:Alpharius", UT="Primarch (Skirmish, Unique)")
o.add_link(AL, "E:Alpharius", "E:Alpharius", to="Nuncio-Vox")
o.cost(AL, "Lernaean Terminator Squad", "Lernaean w/Power Fist", v=50)
o.cost(AL, "Lernaean Terminator Squad", "Lernaean w/Chainfist", v=55)
o.cost_all(AL, "Lernaean Terminator Squad", ("Power Fist",), 5)
o.cost_all(AL, "Lernaean Terminator Squad", ("Chainfist",), 10)
o.category(AL, "Exodus", "E:Exodus", add="Skirmish Sub-type")
o.char(AL, "P:Exodus", UT="Infantry (Character, Light, Skirmish)")

# ======================================================================= Legacies: Legiones Astartes (p92)
o.text(LA, "R:Primus Nullificator", fn=lambda t: t.replace(
    "must exchange their power weapon for an Aethershock maul*", "may exchange their power weapon for an Aethershock maul*").replace(
    "A Legion Cataphractii Centurion may take the Legion Primus Nullificator Consul type.",
    "A Legion Cataphractii Centurion may take the Legion Primus Nullificator Consul type. A model with this Legiones "
    "Consularis upgrade increases his Leadership Characteristic to 10.") if "Leadership Characteristic to 10" not in t else t)
o.text(LA, "R:Hexagrammatic Wards", fn=whole(
    "When a model with this Special Rule suffers a wound from a Psychic Weapon or a Psychic Power, or from any attack made "
    "by a model with the Daemon or Corrupted Unit Type or Sub-type, the model may re-roll any failed Invulnerable Saves it "
    "makes."))
o.add_link(LA, "Nullificator Squad", "Dedicated Transport", to="Land Raider Spartan", mn=None)
for g in ("1) Weapon Option 1", "2) Weapon Option 2"):
    o.retarget(LA, "Castra Ferrum Dreadnought Talon", "Castra Ferrum Dreadnought", g, "Multi-Melta", to="Gravis Melta Cannon")
    o.cost(LA, "Castra Ferrum Dreadnought Talon", "Castra Ferrum Dreadnought", g, "Gravis Melta Cannon", v=15)
o.price(LA, "Castra Ferrum Dreadnought Talon", 150, 150, "Castra Ferrum Dreadnought")
o.rule(LA, "Spatha Attack Bike Squadron", add=("Support Squad", "Hit & Run", "Outflank"))
o.char(LA, "Spatha Attack Bike Squadron", "P:Legion Spatha Attack Bike", W="3")
o.cost(LA, "Spatha Attack Bike Squadron", "1) Spatha Combat Bike Weaponry.", "Multi-Melta", v=15)
o.text(LA, "Spatha Attack Bike Squadron", "P:Spatha Attack Bike", fn=append(
    "A model equipped with a Legion Spatha Attack Bike must change its Unit Type to Cavalry, keeping any Unit Sub-types "
    "it previously had, and may choose to gain the Skirmish Unit Sub-type. In addition, the model must change its Movement "
    "Characteristic to 14 and gains the Firing Protocols (2), Battle-Hardened (1), Skilled Rider, and Hammer of Wrath (1) "
    "Special Rules."))
o.rule(LA, "Spatha Attack Bike Squadron", add=("Battle-Hardened (1)", "Skilled Rider"))
o.price(LA, "Tarantula Sentry Gun Battery", 20)
o.rule(LA, "Tarantula Sentry Gun Battery", remove="Bulky (X)", add=("Immobile", "Sentry Protocols"))
o.char(LA, "Tarantula Sentry Gun Battery", "P:Tarantula Sentry Gun", WS="-", BS="3", S="5", T="5", W="2", I="-", A="-", Ld="5", Sv="3+")
SENTRY = ("A model with this Special Rule must target the closest enemy model as per the following limitations and "
          "restrictions:\n"
          "- Any model armed with a weapon of Strength 7 or more must target the nearest enemy model with the Vehicle, "
          "Automata, or Dreadnought Sub-types.\n"
          "- Any model armed with a weapon of Strength 6 or below must target the nearest enemy model without the Vehicle, "
          "Automata, or Dreadnought Sub-types.\n"
          "- Any model armed with a weapon with the Skyfire Special Rule must target the nearest enemy model with the Flyer "
          "Sub-type.\n"
          "If no such target is in range, then the Controlling Player may select a target as normal.")
o.text("gst", "R:Sentry Protocols", fn=whole(SENTRY))
o.add_link(LA, "Terminator Indomitus Squad", "Dedicated Transport:", to="Land Raider Spartan", mn=None)


def phobos():
    nid = o.F and o.clone_entry(LA, "Land Raider Phobos Squadron", "Land Raider Phobos", name="Land Raider Phobos",
                                salt="phobos transport")
    for f in o.F.paths:
        if "targetId=\"c123-bdc6-a6ba-79a2\"" in o.F.text[f]:
            o.link_beside(o.F.short(f), "c123-bdc6-a6ba-79a2", nid, "Land Raider Phobos", cost=None)


o.run("Land Raider Phobos as a Proteus Carrier", phobos)


def achilles(x):
    if "Quad Launcher - Frag" in x:
        return x
    links = []
    for shell in ("Frag", "Shatter", "Splinter", "Incendiary"):
        tid, _ = o.shared_id("Quad Launcher - " + shell)
        lid = make_id("achilles quad", shell)
        links.append(f'<entryLink id="{lid}" name="Quad Launcher - {shell}" hidden="false" collective="false" import="true" '
                     f'targetId="{tid}" type="selectionEntry"><constraints><constraint field="selections" scope="parent" '
                     f'value="1" percentValue="false" shared="true" includeChildSelections="false" includeChildForces="false" '
                     f'id="{make_id(lid, "min")}" type="min"/><constraint field="selections" scope="parent" value="1" '
                     f'percentValue="false" shared="true" includeChildSelections="false" includeChildForces="false" '
                     f'id="{make_id(lid, "max")}" type="max"/></constraints></entryLink>')
    x = re.sub(r"\s*<profiles>.*?</profiles>", "", x, count=1, flags=re.S)
    x = re.sub(r"\s*<infoLinks>.*?</infoLinks>", "", x, count=1, flags=re.S)
    x = x.replace('name="1) Hull (Front) Mounted Achillus Quad Launcher"', 'name="1) Hull (Front) Mounted Quad Launcher"')
    i = x.rfind("<costs>") if "<costs>" in x else x.rfind("</selectionEntry>")
    return x[:i] + "<entryLinks>" + "".join(links) + "</entryLinks>" + x[i:]


o.raw(LA, "Land Raider Achilles Squadron", "Land Raider Achilles",
      "1) Hull (Front) Mounted " + ("Quad Launcher" if "Mounted Quad Launcher\"" in o.F.text[o.F.file(LA)] else "Achillus Quad Launcher"),
      fn=achilles, what="Quad Launcher (Frag, Shatter, Splinter, Incendiary)")

# ======================================================================= Legacies: Legiones Astartes (pp93-95)
# The wording of the rewritten rules on these pages (Avatar, Keeper of the Keys, Beacon of Hope, Ferrum Occularis,
# Void Shield Envelope, Hammerfall Strike) is not reproduced here; only points, characteristics and options are.
o.category(LA, "Whirlwind", add="Bombard Sub-type")
o.char(LA, "Whirlwind", "P:Whirlwind", UT="Vehicle (Bombard)")
o.char(LA, "Caestus Assault Ram", "P:Caestus Assault Ram", M="18\"", Tr="12")
o.rule(LA, "Caestus Assault Ram", add=("Afterburner", "Caestus Prow", "Inertia Suppression Clamps"))
MAL = (LA, "Legion Malcador Assault Tank Squadron", "Malcador Assault Tank")
o.rename(*MAL, "3) Side Mounted Weapons", to="3) Hull (Left and Right) Mounted Weapons")
o.cost(*MAL, "3) Hull (Left and Right) Mounted Weapons", "Lascannon", v=15)
o.cost(*MAL, "2) Hull Mounted Weapon", "Demolisher Cannon", v=35)
o.retarget(*MAL, "1) Main Hull Weapon", "Gravis Lascannon", to="Gravis Heavy Lascannon",
           shown="Hull (Front) Mounted Twin-linked Gravis Heavy Lascannon")
o.text("gst", "R:Independent Fire Control", fn=whole(
    "A model with this Special Rule may remain stationary, move at Combat Speed, or Cruising Speed, and still fire all "
    "of its weapons as though it had the Super-Heavy Sub-type. Note that this does not grant any of the other benefits "
    "of the Super-Heavy Sub-type."))
o.retarget(LA, "Legion Minotaur Battery", "Minotaur", "Earthshaker cannon", to="Earthshaker Battery",
           shown="Centreline (Rear) Mounted Earthshaker Battery")
for unit, prof, pts, extra in (("Legion Stormblade", "Stormblade", 500, {}), ("Legion Baneblade", "Baneblade", 475, {}),
                               ("Legion Banehammer", "Banehammer", 500, {"Tr": "22"}),
                               ("Legion Stormlord", "Stormlord", 475, {"Tr": "32"}),
                               ("Legion Shadowsword", "Shadowsword", 550, {}), ("Legion Stormsword", "Stormsword", 525, {})):
    o.price(LA, unit, pts)
    o.char(LA, unit, "P:" + prof, Front="14", **extra)
o.add_link(LA, "Legion Stormblade", to="Heavy Bolter", shown="Hull (Front) Mounted Heavy Bolter")
o.rule(LA, "Legion Banehammer", add="Tank Desant (10)")
o.rule(LA, "Legion Stormlord", add=("Tank Desant (10)", "Assault Vehicle"))
# p94
o.move_slot("Legion Macharius Heavy Tank Squadron", "Lords of War:", "Heavy Support:")
o.move_slot("Legion Macharius Omega Heavy Tank", "Lords of War:", "Heavy Support:")
o.cat_strip("Legion Macharius Heavy Tank Squadron", ("LoW & Primarchs (25% Limit)",))
o.cat_strip("Legion Macharius Omega Heavy Tank", ("LoW & Primarchs (25% Limit)",))
o.cost(LA, "Legion Macharius Heavy Tank Squadron", "Macharius Heavy Tank", v=330)
o.cost(LA, "Legion Macharius Heavy Tank Squadron", "Additional Macharius Heavy Tank", v=335)
o.maxsel(LA, "Legion Macharius Heavy Tank Squadron", "Additional Macharius Heavy Tank", v=2)
o.rule(LA, "Legion Macharius Omega Heavy Tank", add="Exposed Compartment")
o.char(LA, "Legion Crassus Armoured Assault Transport", "P:Crassus Armoured Assault Transport", Tr="48")
o.rule(LA, "Legion Crassus Armoured Assault Transport", add="Transport Bay")
o.price(LA, "Legion Praetor Armoured Assault Launcher", 475)
o.rename(LA, "Legion Praetor Armoured Assault Launcher", "E:Praetor Launcher", to="Centreline Mounted Praetor Launcher")
DA, UM, SAL, RG, DG = "LA - Dark Angels", "LA - Ultramarines", "LA - Salamanders", "LA - Raven Guard", "LA - Death Guard"
o.rule(DA, "Farith Redloss", "E:Farith Redloss", add="Consul (Siege Breaker)")
o.price(DA, "Excindio Battle-automata", 300)
o.char(UM, "Honoured Telemechrus", "P:Honoured Telemechrus", UT="Dreadnought (Character, Unique)")
o.category(UM, "Honoured Telemechrus", "E:Honoured Telemechrus", add="Character")
o.add_link(UM, "Honoured Telemechrus", "E:Honoured Telemechrus", to="Legion Vexilla")
o.cost(UM, "Locutarus Storm Squad", "Locutarus", v=30)
o.add_link(LA, "E:Cassian Dracos Reborn", to="Iron Halo")
o.add_link(LA, "E:Cassian Dracos Reborn", to="Nuncio-Vox")
o.category(LA, "E:Cassian Dracos Reborn", add="Character")
o.char(LA, "E:Cassian Dracos Reborn", "P:Cassian Dracos Reborn", M="6", WS="6", BS="5", S="6", T="7", W="6", I="4", A="4",
       Ld="10", Sv="2+")
o.char(SAL, "Lord Chaplain Nomus Rhy'Tan", "P:Lord Chaplain Nomus Rhy'Tan", WS="6")
o.rule(SAL, "Lord Chaplain Nomus Rhy'Tan", add="It Will Not Die (5+)")
# p95
o.rule(LA, "Xiaphas Jurr", add="It Will Not Die (5+)")
o.add_link(RG, "Strike Captain Alvarex Maun", "E:Strike Captain Alvarex Maun", to="Refractor Field")
o.rule(EC, "E:Rylanor the Unyielding", add=("It Will Not Die (5+)", "Hatred (Traitors)", "Shattered Legionary"))
o.category(EC, "E:Rylanor the Unyielding", add="Character")
o.add_link(EC, "E:Rylanor the Unyielding", to="Legion Vexilla")
o.cost(IW, "E:The Tormentor", v=750)
o.char(IW, "E:The Tormentor", "P:The Tormentor", Front="14")
o.rule(IW, "E:Erasmus Golg", add="Traitor")
o.add_link("LA - Night Lords", "Kheron Ophion of the Kyroptera", "E:Kheron Ophion of the Kyroptera", to="Artificer Armour")
o.rule(DG, "Crysos Morturg", add="The Black Shield")
o.char(DG, "Marshal Durak Rask", "P:Marshal Durak Rask", W="3")
o.cost_all(SOH, "Reaver Aggressor Squad", ("Power Maul", "Power Sword", "Power Lance", "Power Axe", "Carsoran Power Axe",
                                           "Carsoran Power Tabar", "Charnabal Glaive", "Charnabal Sabre", "Charnabal Tabar"), 5)
o.rule(AL, "Autilon Skorr", remove="Traitor")

o.report()
