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
# superseded: the Imperatus Special Rules (additional-special-rules.md) hold this rule's current text
# o.text("gst", "R:Independent Fire Control", fn=whole(
#     "A model with this Special Rule may remain stationary, move at Combat Speed, or Cruising Speed, and still fire all "
#     "of its weapons as though it had the Super-Heavy Sub-type. Note that this does not grant any of the other benefits "
#     "of the Super-Heavy Sub-type."))
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

# ======================================================================= Liber Mechanicum (pp96-98) and Legacies: Mechanicum
MECH, ML = "Mechanicum", "Mech Library"
o.cost(MECH, "Myrmidon Secutor Host", "Graviton Gun", v=10)
o.cost(MECH, "Myrmidon Secutor Host", "Phased Plasma-Fusil", v=15)
o.price(MECH, "Scyllax Guardian-Automata Maniple", 0)
o.rule(MECH, "Scyllax Guardian-Automata Maniple", "Scyllax", add="Feel No Pain (5+)")
o.char(MECH, "Ursarax Cohort", "P:Ursarax", S="5")
o.rule(ML, "Thanatar Siege-automata Maniple", "Thanatar", add="Hammer of Wrath (3)")
for f in (ML, MECH):
    for k in ("Styrix", "Magaera", "Atrapos"):
        unit = ("Questoris Knight " if f == ML else "Mechanicum Knight ") + k
        o.add_link(f, unit, to="Flare Shield")
o.add_link(MECH, "Ordinatus Ulator", to="Searchlights")
o.price(MECH, "Ordinatus Aktaeus", 700)
o.rule(MECH, "Ordinatus Aktaeus", add="Transport Bay")
o.rule(MECH, "Archmagos Anacharis Scoria", add="Stubborn")
o.rule(MECH, "E:Inar Satarael", add="Born of Steel")
o.chars_all(MECH, "Tech-thralls", Sv="5+")
o.char(MECH, "Macrocarid Explorator", "P:Macrocarid Explorator", M="12", HP="6")
o.category(MECH, "Macrocarid Explorator", add="Reinforced Sub-type")
# superseded: the Imperatus Special Rules (additional-special-rules.md) hold this rule's current text
# o.text_all("Destructor", whole(
#     "Any model which suffers an unsaved Wound or Hull Point loss from a weapon with this Special Rule does not suffer only "
#     "one Wound or Hull Point of damage, but instead suffers D6 Wounds or Hull Points of damage instead, with all of the "
#     "Wounds or Hull Points inflicted using the same AP and special rules as that of the initial Wound. Roll to save "
#     "against each Wound or Hull Point of damage inflicted separately, but note that Wounds or Hull Points of damage caused "
#     "in excess of a given model's remaining Wounds or Hull Points do not spill over to other models and are lost.\n\n"
#     "In addition, if the target of this attack is a model with the Knight, Titan, Gargantuan, Super-Heavy Vehicle, or "
#     "Building or Fortification Unit Type, or the Monstrous Unit Sub-type, increase the number of Wounds suffered or Hull "
#     "Points lost to 2D6."))
o.text_all("Disruption (X)", whole(
    "To Hit rolls of the value X indicated made by a weapon with this Special Rule cause an automatic Glancing Hit against "
    "models with the Vehicle Unit Type instead of rolling for Armour Penetration, and an automatic Wound against models "
    "with the Dreadnought, Automata, or Armiger Unit Types, instead of rolling To Wound.\n\n"
    "On weapons which do not roll to Hit, such as Template or Blast Weapons, a D6 should be rolled for every applicable "
    "target - a roll of X or higher causes an automatic Glancing Hit against models with the Vehicle Unit Type instead of "
    "rolling for Armour Penetration, and an automatic Wound against models with the Dreadnought, Automata, or Armiger "
    "Unit Types.\n\n"
    "Only Invulnerable Saves or Damage Mitigation rolls may be taken against Wounds or Hull Points of damage inflicted "
    "automatically by this Special Rule."))
o.text_all("Feudal Hierarchy", lambda t: t.replace(
    "A single Detachment may not include both an Archmagos Prime and an Archmagos Prime on Abeyant.",
    "A single Detachment may only ever include a single model with this Special Rule."))
o.text_all("God-Engine", append("In addition, all units wholly within 18\" of a model with this Special Rule and which "
                                "have a Kyropatris Field Generator gain the Line Sub-type."))
o.text_all("Paragon of Metal", append("A model which has this Special Rule changes their Armour Save to 2+."))
o.text_all("Pride of Place", append(
    "A model with this Special Rule may ignore the restrictions applied by it if the Unit with the Transport Sub-type they "
    "are attempting to Embark onto also has the Super-Heavy Sub-type. In addition, a model with this Special Rule gains "
    "the Bulky (X) Special Rule, where X is equal to the model's starting Wounds Characteristic."))
o.text_all("Thanatar Maniple", append(
    "Once a unit with this Special Rule has separated, each model counts as its own unit for the purposes of Victory "
    "Points, Units Destroyed, and similar rules."))
o.text_all("Ionic Deflector", lambda t: t.replace(
    "any model with an ionic deflector and a Wounds Characteristic gains the Eternal Warrior special rule.",
    "any model with an Ionic Deflector and a Wounds Characteristic that suffers an unsaved Wound with the Instant Death "
    "Special Rule is not immediately removed as a casualty, but instead loses D3 Wounds instead of one for each unsaved "
    "Wound with the Instant Death Special Rule inflicted on it."), tag="profile")
o.text_all("Ordinatus Dispersion Shield", append(
    "In subsequent Game Turns after the first, the Ordinatus Dispersion Shield counts as a Flare Shield."), tag="profile")
FREE_MOVE = (" may move over both friendly and enemy models or units without penalty - but must end its Movement at least "
             "1\" away from any model from another unit, and ignores the effects of any Difficult, Dangerous, or Impassable "
             "Terrain they move over as they make their move, though they must still take Dangerous Terrain Tests as "
             "normal should they start or end their move in terrain that would require them to do so.")
o.text_all("Incunabulan Jet Pack", lambda t: t if "own Shooting Phase" in t else (lambda parts: parts[0] +
    " This extra move can only be made in the Controlling Player's own Shooting Phase.\n" + parts[1])(t.split("\n", 1)) +
    "\nA model with an activated Incunabulan Jet Pack" + FREE_MOVE + " It should be noted that, for the purposes of "
    "Reactions, an Incunabulan Jet Pack is classed as having being activated for the purposes of moving over any models or "
    "terrain.", tag="profile")
o.text_all("Stratos Thrusters", append(
    "On a Game Turn in which a model armed with Stratos Thrusters activates them, they may elect to gain the Skyfire "
    "Special Rule for all Ranged Weapons they are armed with. In addition, a model equipped with Stratos Thrusters also "
    "gains the Deep Strike Special Rule. A model with an activated set of Stratos Thrusters" + FREE_MOVE), tag="profile")
o.text_all("Utan Jump Booster", append("A model with an activated Utan Jump Booster" + FREE_MOVE), tag="profile")

TAR = "Mechanicum Tarantula Sentry Gun Battery"
o.rule(MECH, TAR, remove="Bulky (X)", add=("Fearless", "Immobile"))
o.chars_all(MECH, "Tarantula Sentry Gun", WS="-", BS="3", S="5", T="5", W="2", I="-", A="-", Ld="5", Sv="3+")
o.chars_under(MECH, "Ordo Reductor Artillery Tank Battery", "Vehicle", Front="13", UT="Vehicle (Bombard, Reinforced)")
o.category(MECH, "Ordo Reductor Artillery Tank Battery", add="Reinforced Sub-type")
o.category(MECH, "Ordo Reductor Artillery Tank Battery", add="Bombard Sub-type")
o.retarget(MECH, "Ordo Reductor Minotaur Battery", "Ordo Reductor Minotaur", "Twin-linked Earthshaker Cannon",
           to="Earthshaker Battery", shown="Centreline (Rear) Mounted Earthshaker Battery")
o.rename(MECH, "Ordo Reductor Minotaur Battery", "Ordo Reductor Minotaur", "L:Hunter-Killer Missile",
         to="Hull (Rear) Mounted Hunter-Killer Missile")

# ======================================================================= Liber Imperium
CUS, SOS = "LI - Custodes", "LI - Sisters Of Silence"
o.text(CUS, "P:Golden Exemplar", char="Text", fn=append(
    "Furthermore, the first Reaction made in each Game Turn by this Warlord and any unit he has joined does not use up a "
    "point of the Controlling Player's Reaction Allotment."))
for unit, grp in (("Custodes Tribune", "Tribune Weapon"), ("E:Custodian Shield Captain", "Shield Captain Weapon")):
    o.cost(CUS, unit, grp, "Paragon Blade", v=0)
    o.cost(CUS, unit, grp, "Meridian Swords", v=35)
    o.cost(CUS, unit, grp, "Paragon Glaive", v=10)
o.cost(CUS, "Hetaeron Guard Squad", "Hetaeron Guard", v=60)
o.cost(CUS, "Hetaeron Guard Squad", "Hetaeron Guard", "Weapon", "L:Paragon Blade", v=0)
o.cost(CUS, "Hetaeron Guard Squad", "Hetaeron Guard", "Weapon", "L:Meridian Swords", v=35)
o.char(CUS, "Custodian Guard Squad", "P:Custodian", A="3")
o.char(CUS, "Sentinel Guard Squad", "P:Sentinel", A="3")
o.char(CUS, "Agamatus Jetbike Squadron", "P:Agamatus", A="2")
o.cost(CUS, "Custodian Venatari Squad", "Venatari w/ Kinetic Destoyer and Tarsus Buckler", v=60)
o.cost(CUS, "Custodian Venatari Squad", "Venatari w/ Venatari Lance", v=70)
o.price(CUS, "Custodian Venatari Squad", 10)
o.char(CUS, "Custodian Venatari Squad", "P:Venatari", A="3")
o.rename(CUS, "E:Caladius Grav-Tank", "Turret Mounted Illastus Accelerator Cannon", to="Turret Mounted Iliastus Accelerator Cannon Arrays")
o.rule(SOS, "Silent Fury", add="Firing Protocols (2)")
o.category(SOS, "Silent Fury", "E:Silent Fury", add="Antigrav Sub-type")
o.char(SOS, "Questora Cadre", "P:Questora", WS="4", BS="5")
o.rename(SOS, "Questora Cadre", "The entire unit may exchange their Vratine bolters for:",
         to="Any model in the unit may exchange their Vratine Bolter for one of the following options:")
ART = o.shared_id("Artificer Armour")[0]
for unit in ("Questora Cadre", "Raptora Cadre"):
    o.raw(SOS, unit, what="Artificer Armour instead of Vratine Armour", fn=lambda x: re.sub(
        r'(<entryLink [^>]*)name="Vratine Armour"([^>]*)targetId="[^"]*"', r'\1name="Artificer Armour"\2targetId="' + ART + '"', x))
o.cost(SOS, "Eradicator Cadre", "Eradicator w/ Vratine Bolter", v=15)
o.cost(SOS, "Eradicator Cadre", "Eradicator w/ options", v=15)
o.price(SOS, "Eradicator Cadre", 20)
o.char(SOS, "Eradicator Cadre", "P:Eradicator", BS="5", Ld="8")
o.char(SOS, "Eradicator Cadre", "P:Eradicator Mistress", BS="5", Ld="9")
for m in ("Eradicator Mistress", "Eradicator w/ Vratine Bolter", "Eradicator w/ options"):
    o.add_link(SOS, "Eradicator Cadre", m, to="Voidsheen Cloak")
o.category(SOS, "Vigilator Cadre", remove="Silent Sisterhood (Chamber of Oblivion)")
o.category(SOS, "Vigilator Cadre", add="Silent Sisterhood (Chamber of Vigilance)")
o.retarget(SOS, "Kharon Pattern Acquistor", "1) Hull (Front) Mounted Weapon", "Multi-Melta", to="Gravis Melta Cannon")
o.price(SOS, "Pursuer Cadre", 15)
o.cost(SOS, "Pursuer Cadre", "Pursuer", "Execution Blade", v=5)
o.raw(SOS, "Pursuer Cadre", what="Rage (2)", fn=lambda x: x.replace('value="Rage (1)"', 'value="Rage (2)"'))
o.retarget(SOS, "Expurgator Cadre", "L:Adrathic Destructor", to="Adrathic Devastator",
           shown="Adrathic Devastator (with Suspensor Web)")

# ======================================================================= Liber Imperium and Legacies: Solar Auxilia
SA = "LI - Solar Auxilia"
o.rule(SA, "Legate Marshal", "Solar Auxilia Legate Marshal", add="Field Officer")
for unit, models in (("Tactical Command Section", ("Auxilia Companion", "Auxilia Captain")),
                     ("Companion Sections", ("Auxilia Companion",))):
    o.rule(SA, unit, add="Chosen Warriors")
    for m in models:
        o.add_link(SA, unit, m, to="Close Combat Weapon")
o.cost(SA, "Companion Sections", "Auxilia Companion", "Magna Combi-weapon", v=10)
for m in ("Power Sword", "Power Lance", "Power Maul", "Power Axe"):
    o.cost(SA, "Veletaris Command Section", "Veletarii w/ " + m, v=13)
o.price(SA, "Veletaris Command Section", 50 - 4 * 8)
o.maxsel(SA, "Veletaris Command Section", "G:Veletarii", v=19)
for m in ("Lasrifle", "Autorifle", "Lascarbine", "Lasgun", "Shotgun", "Stubcarbine"):
    o.cost(SA, "Line Command Section", "Auxilia Veteran w/ " + m, v=6)
o.cost(SA, "Line Command Section", "Auxilia Veteran w/ Lasrifle and Bayonet", v=7)
o.price(SA, "Line Command Section", 40 - 4 * 6)
o.maxsel(SA, "Line Command Section", "Auxilia Veterans", v=19)
o.char(SA, "Line Command Section", "P:Auxilia Troop Master", Ld="8")
LR = (SA, "Leman Russ Strike Squadron", "1) All models may exchange their Turret Mounted Battlecannon for one of the following:")
o.rename(*LR, "Two Turret Mounted Gravis Autocannons", to="Turret Mounted Exterminator Autocannon")
o.retarget(*LR, "Turret Mounted Exterminator Autocannon", "Gravis Autocannon", to="Exterminator Autocannon")
o.rename(*LR, "Turret Mounted Gravis Lascannons", to="Turret Mounted Gravis Heavy Lascannon")
o.retarget(*LR, "Turret Mounted Gravis Heavy Lascannon", "Gravis Lascannon", to="Gravis Heavy Lascannon")
o.cost(SA, "Leman Russ Assault Squadron", "Leman Russ Battle Tank", v=145)
o.char(SA, "Leman Russ Assault Squadron", "P:Leman Russ Battle Tank", Rear="11")
o.rule(SA, "Artillery Command Section", add="Artillery Spotters")
o.rule(SA, "Tarantula Sentry Battery", remove="Bulky (X)", add="Immobile")
o.char(SA, "Tarantula Sentry Battery", "P:Tarantula Sentry Gun", WS="-", BS="3", S="5", T="5", W="2", I="-", A="-", Ld="5", Sv="3+")
o.char(SA, "Rapier Battery", "P:Auxilia Gunner", Sv="4+")
MH = (SA, "Malcador Heavy Tank Squadron", "Malcador Heavy Tank")
o.retarget(*MH, "1) May exchange its Hull (Front) Mounted battlecannon for one of the following:", "Gravis Lascannon",
           to="Gravis Heavy Lascannon", shown="Hull (Front) Mounted Twin-linked Gravis Heavy Lascannon")
o.cost(*MH, "3) May exchange its Hull (Left) & Hull (Right) Mounted heavy bolters for:", "Lascannon", v=15)
o.cost(*MH, "2) May exchange its Hull (Front) Mounted heavy bolter for one of the following:", "Demolisher Cannon", v=35)
o.rule(SA, "Valdor Tank Destroyer Squadron", add="Independent Fire Control")
o.rule(SA, "Malcador Infernus Squadron", add="Independent Fire Control")
o.price(SA, "E:Dracosan Armoured Transport", 135)
o.cost(SA, "E:Dracosan Armoured Transport", "Demolisher Cannon", v=20)
o.char(SA, "P:Aurox Transport", Tr="12")
o.add_link(SA, "E:Arvus Transport", to="Heavy Stubber", shown="Hull (Front) Mounted Heavy Stubber")
o.text(SA, "R:Solar Auxilia Command Tank", fn=lambda t: t if "Armoured Legate may nominate" in t else re.sub(
    r"A Leman Russ Command Tank must be assigned to a Leman Russ Strike Squadron or a Leman Russ Assault Squadron\.?",
    "A model with this Special Rule must be assigned to another unit made up entirely of models with the Vehicle Unit "
    "Type purchased as part of the same Tercio.\n\nAn Armoured Legate may nominate a single Auxilia Armoured Tercio in "
    "the same Detachment, and may use their Solar Auxilia Command Tank Special Rule to join squads within that Tercio as "
    "if they were purchased as part of it.\n\nIn addition, a model with this Special Rule may still make Shooting Attacks "
    "as normal in a turn in which they use their Cognis-Signum to provide +1 Ballistic Skill to all other models in their "
    "unit, even though this would normally be prevented by using this Wargear.", t))
o.text(SA, "R:Reborn Cohorts", fn=lambda t: re.sub(r"Effects\n• [^\n]*", "Effects\n• All models with the Infantry Unit "
    "Type in a Detachment using this Cohort Doctrine gain a bonus of +1 to their Leadership Characteristic, to a maximum of "
    "Leadership 10, and the Stubborn Special Rule.", t, count=1))
o.text(SA, "R:Armoured Fist Pattern Cohorts", fn=lambda t: t if "Mechanised Unit Sub-type" in t else re.sub(
    r"Effects\n• [^\n]*", "Effects\n• A Detachment using this Cohort Doctrine may select Auxilia Armoured Tercios as Troops "
    "choices. An Auxilia Armoured Tercio selected as a Troops choice may only consist of a single unit. Auxilia Armoured "
    "Tercios selected as Compulsory Troop Choices in a Primary Detachment using this Cohort Doctrine gain the Line Unit "
    "Sub-type.", t, count=1).replace(
    "\n\nWarlord Trait: Armoured Legate", "\n• The first time in a game that any models with the Infantry Unit Type "
    "Disembark from their own Dedicated Transport, they gain the Relentless Special Rule until the end of that turn.\n\n"
    "Warlord Trait: Armoured Legate", 1).replace(
    "or in Reserves. (THIS MUST BE MANUALLY CHECKED)", "or in Reserves, unless the unit has the Mechanised Unit Sub-type. "
    "(THIS MUST BE MANUALLY CHECKED)\n• A Detachment using this Cohort Doctrine may not include any models with a "
    "Movement Characteristic of 0 or '-'.\n• An army which includes at least one Detachment using this Cohort Doctrine "
    "may not select any Fortification choices."))


def armoured_fist_troops(x):
    """The Troops choice is any single unit of an Auxilia Armoured Tercio, with Line when it is Compulsory."""
    if "Auxilia Armoured Tercio" in x:
        return x
    x = x.replace('name="Armoured Fist - Leman Russ Strike Squadron"', 'name="Armoured Fist - Auxilia Armoured Tercio"')
    m = re.search(r"\n(\s*)<entryLinks>\s*<entryLink [^>]*name=\"Leman Russ Strike Squadron\".*?</entryLinks>", x, re.S)
    ind = m.group(1)
    con = lambda kind, gid: (f'<constraint field="selections" scope="parent" value="1" percentValue="false" shared="true" '
                             f'includeChildSelections="false" includeChildForces="false" id="{make_id(gid, kind)}" type="{kind}"/>')
    gid = make_id("armoured fist tercio unit")
    links = "".join(f'{ind}      <entryLink id="{make_id(gid, n)}" name="{n}" hidden="false" collective="false" import="true" '
                    f'targetId="{tid}" type="selectionEntry"/>\n'
                    for n, tid in (("Leman Russ Strike Squadron", "3fce-bf1a-6369-a386"),
                                   ("Leman Russ Assault Squadron", "813c-fa93-375d-5f3e")))
    group = (f"\n{ind}<selectionEntryGroups>\n{ind}  <selectionEntryGroup id=\"{gid}\" name=\"Auxilia Armoured Tercio unit\" "
             f"hidden=\"false\" collective=\"false\" import=\"true\">\n{ind}    <constraints>\n{ind}      {con('min', gid)}\n"
             f"{ind}      {con('max', gid)}\n{ind}    </constraints>\n{ind}    <entryLinks>\n{links}{ind}    </entryLinks>\n"
             f"{ind}  </selectionEntryGroup>\n{ind}</selectionEntryGroups>")
    x = x[:m.start()] + group + x[m.end():]
    line = (f'\n{ind}  <modifier type="add" field="category" value="6399-5c65-7833-1025">\n{ind}    <conditions>\n'
            f'{ind}      <condition type="instanceOf" value="1" field="selections" scope="ancestor" childId="8f42-a824-fb5f-8fea" '
            f'shared="true" percentValue="false" includeChildSelections="false" includeChildForces="false"/>\n'
            f'{ind}    </conditions>\n{ind}  </modifier>')
    return x.replace("<modifiers>", "<modifiers>" + line, 1)


o.raw(SA, "E:Armoured Fist - " + ("Auxilia Armoured Tercio" if "Armoured Fist - Auxilia Armoured Tercio" in
                                  o.F.text[o.F.file(SA)] else "Leman Russ Strike Squadron"),
      fn=armoured_fist_troops, what="Troops choice: any single unit of an Auxilia Armoured Tercio")
o.text(SA, "R:Penal Pattern Cohorts", fn=lambda t: t if "Chainsword for +1" in t else t.replace(
    "Lascarbine, Lasgun, Stubcarbine, Autorifle, or Shotgun", "Lascarbine, Lasgun, Stubcarbine, Autorifle, Laspistol and "
    "Close Combat Weapon, or Shotgun").replace("\nLimitations", "\n• Any model in a Detachment using this Cohort Doctrine "
    "may replace a Close Combat Weapon with a Chainsword for +1 point per model.\nLimitations", 1))
o.text(SA, "R:Feral Pattern Cohorts", fn=lambda t: t if "Chain Axe for +2" in t else t.replace("\nLimitations",
    "\n• All models with the Infantry Unit Type from a Detachment using this Cohort Doctrine gain a bonus of +1 to their "
    "Weapon Skill, to a maximum of 5, for the duration of any player turn in which they make a Successful Charge.\n"
    "• Any model in a Detachment using this Cohort Doctrine may replace a Bayonet with a Chain Bayonet for +1 point per "
    "model.\n• Any model with the Character Unit Sub-type in a Detachment using this Cohort Doctrine may exchange a Close "
    "Combat Weapon for a Chain Axe for +2 points per model.\nLimitations", 1))
o.text(SA, "R:Siege Pattern Cohorts", fn=lambda t: t if "Defence Line" in t else t.replace(
    "as both Elites and Heavy Support choices.", "as both Elites and Heavy Support choices. In addition, they may select "
    "Solar Auxilia Artillery Battery squads as both Heavy Support and Fortification choices.").replace("\nLimitations",
    "\n• Any unit eligible to purchase a Dedicated Transport may instead elect to purchase a Defence Line without "
    "occupying a Fortification Force Organisation slot, but the cost in points must be counted towards the army total as "
    "usual. A unit which has selected a Defence Line in this way counts as having purchased a Dedicated Transport.\n"
    "Limitations", 1) + "\n• A Detachment using this Cohort Doctrine may only be selected for an army's Primary Detachment.")
# Legacies: Solar Auxilia
o.cost(SA, "Thunderer Siege Tank Squadron", "Thunderer Siege Tank", v=135)
o.cost(SA, "Destroyer Tank Hunter Squadron", "Destroyer Tank Hunter", v=135)
o.raw(SA, "Trojan Support Vehicle", what="Field Repair (3+)", fn=lambda x: re.sub(r'value="Field Repair \(\d\+\)"',
      'value="Field Repair (3+)"', x))
o.retarget(SA, "Minotaur Battery", "Minotaur", "Earthshaker cannon", to="Earthshaker Battery",
           shown="Centreline (Rear) Mounted Earthshaker Battery")
o.rename(SA, "Minotaur Battery", "Minotaur", "L:Hunter-Killer Missile", to="Hull (Rear) Mounted Hunter-Killer Missile")
o.move_slot("Macharius Heavy Tank Squadron", "Lords of War:", "Heavy Support:")
o.cat_strip("Macharius Heavy Tank Squadron", ("LoW & Primarchs (25% Limit)",))
o.cost(SA, "Macharius Heavy Tank Squadron", "Macharius Heavy Tank", v=330)
o.maxsel(SA, "Macharius Heavy Tank Squadron", "Macharius Heavy Tank", v=3)
for unit, pts, extra in (("Stormblade", 475, {}), ("Baneblade", 450, {}), ("Banehammer", 475, {"Tr": "22"}),
                         ("Stormlord", 450, {"Tr": "32"}), ("Shadowsword", 525, {}), ("Stormsword", 475, {})):
    o.price(SA, unit, pts)
    o.char(SA, unit, "P:" + unit, Front="14", **extra)
o.add_link(SA, "Stormblade", to="Heavy Bolter", shown="Hull (Front) Mounted Heavy Bolter")
o.rule(SA, "Banehammer", add="Tank Desant (10)")
o.rule(SA, "Stormlord", add=("Tank Desant (10)", "Assault Vehicle"))
o.char(SA, "Stormlord", "P:Stormlord", **{"Access Points": "A Solar Auxilia Stormlord has one Access Point at the rear of the hull."})
o.price(SA, "Praetor Armoured Assault Launcher", 450)
o.rename(SA, "Praetor Armoured Assault Launcher", "E:Praetor Launcher", to="Centreline Mounted Praetor Launcher")
o.char(SA, "Crassus Armoured Assault Transport", "P:Crassus Armoured Assault Transport", Tr="48")
o.rule(SA, "Crassus Armoured Assault Transport", add="Transport Bay")
o.price(SA, "Artillery Battery", 0)
for g in ("Earthshaker Artillery Platforms", "Medusa Artillery Platforms"):
    o.rule(SA, "Artillery Battery", g, "E:" + g, add=("Immobile", "Bulky (5)"))
o.chars_all(SA, "Artillery Platform", WS="-", BS="4", S="7", T="7", W="4", I="-", A="-", Ld="5", Sv="3+")
o.chars_all(SA, "Auxilia Gunner", Sv="4+")

# ======================================================================= Legacies: Assassins and Liber Imperium wargear
ASN = "LI - Assassins"
o.char(ASN, "Clade Vindicare Assassin", "P:Clade Vindicare Assassin", W="3")
o.char(ASN, "Clade Culexus Assassin", "P:Clade Culexus Assassin", WS="5", W="3")
o.char(ASN, "Clade Callidus Assassin", "P:Clade Callidus Assassin", W="3")
o.text(ASN, "P:Polymorphine", fn=append("In addition, whilst the effects of Polymorphine are active, the model equipped with it "
                                        "does not count as a Scoring or Denial Unit."))
o.rule(ASN, "Clade Eversor Assassin", add="No Witnesses")
o.rule(ASN, "Clade Adamus Assassin", add="Preferred Enemy (Characters)")
o.rule(ASN, "Clade Venenum Assassin", add="Fleet (2)")
o.add_link(ASN, "Clade Vanus Infocyte Assassin", to="Panoply Of The Assassin")
o.text(ASN, "P:Autotomic Servo-limbs", fn=whole(
    "Once per battle, at the start of any turn, the Controlling Player of a model with Autotomic Servo-Limbs may choose to "
    "grant that model the Counter-Attack (2) Special Rule until the start of their next turn."))
o.text(ASN, "P:Auspectre", fn=append(
    "Note that weapons selected to fire in this manner must still follow the rules and restrictions placed upon them by "
    "their mountings, Unit Types, or Unit Sub-types, such as allowed targets for reactions in the case of Knights and "
    "Titans only being allowed to react to other Knights and Titans, Super-heavy Vehicles, Lumbering Flyers or any model "
    "with 8 or more Wounds."))
o.text(ASN, "P:Panoply Of The Assassin", fn=append(
    "A model equipped with the Panoply of the Assassin also gains Frag Grenades, and the Hit & Run and Shrouded (5+) "
    "Special Rules."))
o.text("gst", "R:Assassin Sub-type", fn=append(
    "• Models with the Assassin Sub-type gain the Precision Shots (2+), Precision Strikes (2+), and Predator's Gaze "
    "Special Rules."))
o.text("gst", "R:Anathema Sub-type", fn=sub(
    "caused by a Force Weapon gain no benefit from the Force special rules,",
    "caused by a Force Weapon gain no benefit from the Force, Achean Force, or Soul Tear Special Rules,"))
o.text(SA, "R:Demolition Vehicle", fn=sub(
    "When a model with this special rule is called upon to make attacks during an Assault, instead of rolling To Hit as "
    "normal it instead", "At Initiative step 10, instead of rolling To Hit as normal, a model with this Special Rule instead"))
o.text(CUS, "P:Praesidium Shield", fn=sub(
    "A Praesidium shield confers a 5+ Invulnerable Save – this does not stack with existing Invulnerable Saves and if a "
    "model has more than one such save, the controlling player must select one to use against any Wounds inflicted on "
    "that model.", "A model with a Praesidium Shield adds +1 to its Invulnerable Save (to a maximum of 3+) or an "
    "Invulnerable Save of 6+ if they do not already possess one."))
o.text(SA, "E:Command Vox", "P:Command Vox", fn=append(
    "While at least one model with a Command Vox is present on the battlefield and not Embarked in a Vehicle or Building, "
    "the Controlling Player may re-roll any Scatter rolls made (whether as part of a weapon attack or the deployment of a "
    "model or unit), as long as the model with the Command Vox has line of sight to the unit targeted by the attack or the "
    "point chosen as the target of the deployment."))
o.rule(CUS, "E:Gyrfalcon Jetbike", add="Skilled Rider")
o.text(SOS, "P:Erinyes Jetbike", fn=append(
    "In addition, any model equipped with an Erinyes Jetbike sets its Movement Characteristic to 18\", and gains the "
    "Skilled Rider and Battle-Hardened (1) Special Rules."))
o.rule(SOS, "E:Erinyes Jetbike", add=("Skilled Rider", "Battle-Hardened (1)"))

# ======================================================================= Legacies: Imperialis Militia (and Constanix II)
IM = "Imperialis Militia"
o.text("gst", "R:Third-line Unit Sub-type", fn=lambda t: t if t.startswith("The following rules apply") else
       "The following rules apply to all models with the Third-Line Sub-type:\n" + t)
o.text(IM, "P:Merchant Princeling", char="Text", fn=append(
    "If the Warlord has a Retinue unit of any kind, this unit is instead automatically designated as the Warlord's "
    "Lifeguard unit. A Warlord with this Trait also gains the Heavy Unit Sub-Type."))
o.text("gst", "R:Legacy of the Great Crusade", fn=sub(
    "Imperialis Militia Command Cadres, and Discipline Masters in a Detachment",
    "Imperialis Militia Command Cadres, and units that contain a Discipline Master or Mounted Discipline Master in a Detachment"))
o.text("gst", "R:Clanfolk Levy", fn=whole(
    "A Detachment with this Provenance may choose to fill Compulsory Troops choices only with Imperialis Militia Cavalry "
    "Squads. Units selected in this manner gain the Line Sub-type. In addition, all models in Imperialis Militia Cavalry "
    "Squads gain a bonus of +1 to their Leadership Characteristic. In addition, a Detachment with this Provenance may "
    "include four additional Fast Attack choices – but these additional choices may only be used to select Imperialis "
    "Militia Cavalry Squads."))
o.text("gst", "R:Cyber-Augmetics", fn=whole(
    "All eligible units and models gain the Feel No Pain (6+) Special Rule, and any eligible unit may be given the Slow "
    "and Purposeful Special Rule at no additional points cost. In addition, any unit which includes a Militia Medicae "
    "improves the Feel No Pain (6+) Special Rule provided by their Auto-Medicus to a (5+).\n\n"
    "This Provenance may not be chosen in conjunction with the Gene-crafted Provenance and any Detachment with this "
    "Provenance is treated as Sworn Brothers by any Detachment with the Mechanicum Faction in the same army."))
o.text("gst", "R:Kinfolk Helots", fn=sub(
    "receive an increase of +1 to their Toughness Characteristic but also lower their Initiative and Movement "
    "Characteristics by -1 (to a minimum of 1, models with a Movement of 0 or - are not affected and remain Movement 0 or -).",
    "change their Toughness Characteristic to be one higher than its starting value (a Toughness characteristic of 3 being "
    "changed to 4 on their statline, for example), but also change their Initiative and Movement Characteristics to be one "
    "lower than its starting value (in the same way as above)."))
o.text("gst", "R:Abhuman Muster", fn=whole(
    "All eligible units and models change their Strength and Movement Characteristic to be one higher than its starting "
    "value (a Strength characteristic of 3 being changed to 4 on their statline, for example), but also change their "
    "Ballistic Skill Characteristic to be one lower than its starting value (in the same way as above) and, if they do not "
    "already possess any variant of the Bulky (X) Special Rule, gain the Bulky (2) Special Rule. All eligible models in a "
    "Detachment with this Provenance gain the Hammer of Wrath (1) Special Rule. If a model also has the Character Unit "
    "Sub-type or the Monstrous Unit Sub-type, they gain the Hammer of Wrath (2) Special Rule instead, or +1 to an existing "
    "Hammer of Wrath (X) Special Rule if they already have the Hammer of Wrath (2) Special Rule. This Provenance may not be "
    "chosen in conjunction with the Ogryn Conscripts Provenance."))
o.text(IM, "R:Among the Ranks", fn=sub(
    "Discipline Masters may only be assigned to units composed entirely of models with the Infantry Unit Type and Militia "
    "Unit Sub-type, unless upgraded to a Mounted Discipline Master, in which case that model must be assigned to an "
    "Imperialis Militia Cavalry Squad.",
    "Discipline Masters may only be assigned to units composed entirely of models with the Infantry Unit Type, and either "
    "the Militia or Artillery Unit Sub-types, unless upgraded to a Mounted Discipline Master, in which case that model must "
    "be assigned to a Unit with the Cavalry Unit Type and the Militia Unit Sub-type."))
o.text("gst", "R:Strength in Numbers", fn=sub("using the Among the Ranks and Militia Medicae Support special rules",
                                              "using any Special Rules"))
o.text(IM, "R:Emplaced", fn=append(
    "If taken as part of a Mortalis Assault Force Organisation Chart, a unit that includes any models with this Special "
    "Rule may only make the Suppress Reaction."))
o.text(IM, "P:Militia Standard", fn=append(
    "A unit that includes at least one model with a Militia Standard gains the Line Sub-type for as long as that model is "
    "part of the unit."))
o.text("gst", "R:Arms of the Omnissiah", fn=lambda t: t.replace(
    "may upgrade lasguns to laslocks and may upgrade sniper rifles to arc rifles at a cost of +45 points per unit",
    "may upgrade Lasguns to Las-locks at no additional points cost, and may upgrade Sniper Rifles to Arc Rifles at a cost "
    "of +25 points per unit") + ("" if "Sworn Brothers" in t else "\n\nAny Detachment with this Provenance is treated as "
    "Sworn Brothers by any Detachment with the Mechanicum Faction in the same army."))
o.text("gst", "R:Augmented Levy", fn=append(
    "Any Detachment with this Provenance is treated as Sworn Brothers by any Detachment with the Mechanicum Faction in "
    "the same army."))
for e in ("Mounted Force Commander*", "Mounted Discipline Master*"):
    o.category(IM, "E:" + e, add="Skirmish Sub-type")
    o.category(IM, "E:" + e, add="Light Sub-type")
o.cost(IM, "IM - Command Cadre", "2) Militia Bodyguard", v=5)
o.rename(IM, "IM - Command Cadre", "2) Militia Bodyguard", "1.4) One Militia bodyguard Special Weapon:",
         to="1.4) For every five models in the unit, one Militia Bodyguard in the squad may exchange their Lasgun for one of the following:")
o.cost(IM, "IM - Command Cadre", "2) Militia Bodyguard", "1.4) For every five models in the unit, one Militia Bodyguard in the "
       "squad may exchange their Lasgun for one of the following:", "Plasma Gun", v=10)
o.rename(IM, "IM - Grenadier Squad", "2) Grenadier", "1.4) Two Grenadiers may exchange their Lasgun for:",
         to="1.4) For every ten models in the unit, up to two Grenadiers in the squad may exchange their Lasgun for one of the following:")
for m in ("Lascannon", "Autocannon", "Heavy Stubber", "Missile Launcher Frag/Krak", "Mortar", "Multilaser", "Heavy Bolter"):
    o.cost(IM, "IM - Fire Support Squad", "Militia Fire Team w/ " + m, v=10)
o.price(IM, "IM - Fire Support Squad", 5)
o.category(IM, "IM - Fire Support Squad", add="Skirmish Sub-type")
o.rule(IM, "IM - Fire Support Squad", add="Crew-Served Weapon")
o.rename(IM, "IM - Fire Support Squad", "Missile Launcher w/Frag & Krak Missiles", to="Missile Launcher (with Frag, Krak, and Flak Missiles)")
o.price(IM, "IM - Reconnaissance Squad", 15)
o.category(IM, "IM - Reconnaissance Squad", add="Skirmish Sub-type")
o.rename(IM, "IM - Reconnaissance Squad", "3) All models in the unit may exchange their shotguns for one of the following",
         to="3) Any model in the unit may exchange their Shotguns, Lascarbines, or Stubcarbines for one of the following:")
o.cost(IM, "IM - Field Gun Battery", "Militia Field Gun w/ Heavy Lascannon", "Heavy Lascannon", v=10)
o.cost(IM, "IM - Field Gun Battery", "Militia Field Gun w/ Kalliope Mortar", "Kalliope Mortar", v=10)
o.category(IM, "IM - Field Gun Battery", add="Skirmish Sub-type")
o.add_link(IM, "IM - Arvus Transport", to="Heavy Stubber", shown="Hull (Front) Mounted Heavy Stubber")
o.add_link(IM, "IM - Arvus Transport", to="Searchlights")
o.chars_all(IM, "Outrider", W="2")
o.char(IM, "IM - Cavalry Squad", "P:Outrider Sergeant", W="2", UT="Cavalry (Light, Militia, Skirmish, Character)")
o.char(IM, "IM - Cavalry Squad", "P:Outrider", UT="Cavalry (Light, Militia, Skirmish)")
o.category(IM, "IM - Cavalry Squad", add="Skirmish Sub-type")
o.rename(IM, "IM - Cavalry Squad", "2) One Militia Outrider in the unit may take one of the following:",
         to="2) For every five models in the unit, one Militia Outrider in the unit may take one of the following:")
o.cost(IM, "IM - Cavalry Squad", "3) Squad Weapon - All models in the unit may take one of the following:", "Militia Lance", v=2)
o.price(IM, "IM - Beastmasters", 30 - 3 * 8)
o.rule(IM, "IM - Beastmasters", "1.1) Handlers", add="Fleet (1)")
o.category(IM, "IM - Beastmasters", "1.1) Handlers", add="Light Sub-type")
o.raw(IM, "IM - Beastmasters", what="War Beasts Rage (2)", fn=lambda x: x.replace('value="Rage (1)"', 'value="Rage (2)"'))
o.cost(IM, "IM - Sentinel Squadron", "Sentinel", v=40)
o.rename(IM, "IM - Sentinel Squadron", "L:Missile Launcher w/Frag & Krak Missiles", to="Missile Launcher (with Frag, Krak, and Flak Missiles)")
def air_superiority(x):
    if "Divisio Aeronautica Air Superiority" in x:
        return x
    sa = o.F.text[o.F.file(SA)]
    rule = re.search(r'<rule [^>]*name="Divisio Aeronautica Air Superiority".*?</rule>', sa, re.S).group(0)
    rule = re.sub(r'\sid="[^"]*"', ' id="' + make_id("im air superiority") + '"', rule, count=1)
    i = x.find("<infoLinks>") if "<infoLinks>" in x else x.find("<categoryLinks>")
    return x[:i] + "<rules>" + rule + "</rules>" + x[i:]


# the Solar Auxilia rule is not visible from the Militia catalogue, so the unit carries its own copy
o.raw(IM, "IM - Thunderbolt Fighter", fn=air_superiority, what="+ Divisio Aeronautica Air Superiority")
IMM = (IM, "IM - Malcador Heavy Tank")
o.rule(*IMM, add="Independent Fire Control")
o.retarget(*IMM, "1) May exchange its Hull (Front) Mounted battlecannon for one of the following:", "Gravis Lascannon",
           to="Gravis Heavy Lascannon", shown="Hull (Front) Mounted Twin-linked Gravis Heavy Lascannon")
o.cost(*IMM, "3) May exchange its Hull (Left) & Hull (Right) Mounted heavy bolters for:", "Lascannon", v=15)
o.cost(*IMM, "2) May exchange its Hull (Front) Mounted heavy bolter for one of the following:", "Demolisher Cannon", v=35)
ILR = (IM, "IM - Leman Russ", "1) All models may exchange their Turret Mounted Battlecannon for one of the following:")
o.rename(*ILR, "Turret Mounted Gravis Autocannons", to="Turret Mounted Exterminator Autocannon")
o.retarget(*ILR, "Turret Mounted Exterminator Autocannon", "Gravis Autocannon", to="Exterminator Autocannon")
o.rename(*ILR, "Turret Mounted Gravis Lascannons", to="Turret Mounted Gravis Heavy Lascannon")
o.retarget(*ILR, "Turret Mounted Gravis Heavy Lascannon", "Gravis Lascannon", to="Gravis Heavy Lascannon")
o.cost(IM, "IM - Leman Russ", "2) May exchange their Hull (Front) Mounted Heavy Bolter for one of the following:", "Lascannon", v=10)
for c in ("Earthshaker Gun Carriage", "Medusa Gun Carriage"):
    o.char(IM, "IM - Heavy Ordnance Battery", "P:" + c, UT="Infantry (Static Artillery*, Heavy)", WS="-", BS="3", S="7", T="7",
           W="4", I="-", A="-", Ld="5", Sv="3+")
    o.rule(IM, "IM - Heavy Ordnance Battery", "E:" + c, add=("Immobile", "Bulky (5)"))
o.rule(IM, "IM - Gorgon Heavy Transporter", add="Assault Vehicle")
o.char(IM, "IM - Baneblade Super-heavy Battle Tank", "P:Militia Baneblade", HP="12")

# ======================================================================= Exemplary Battles
SW, IF_, WS_ = "LA - Space Wolves", "LA - Imperial Fists", "LA - White Scars"
o.category(SW, "Jorlund Hunter Pack", add="Skirmish Sub-type")
o.rule(SW, "Jorlund Hunter Pack", add="Hit & Run")
o.cost(WB, "Procurators", "Procurator", "Heavy Chainsword", v=2)
o.text(WB, "R:Grim Purpose", fn=lambda t: t if "Retinue Squad" in t else t.rstrip().rstrip(".").rstrip(")") +
       "), unless that model has the Independent Character Special Rule and one of the following Psychic Disciplines: "
       "Harbinger of Chaos, Diabolism, or Anathemata.\n\nA Word Bearers Procurator Squad may be selected as a Retinue Squad "
       "in a Detachment that includes at least one model with both the Independent Character and Legiones Astartes (Word "
       "Bearers) Special Rules and one of the following Psychic Disciplines: Harbinger of Chaos, Diabolism, or Anathemata, "
       "instead of as an Elites choice. A unit selected as a 'Retinue Squad' must have one model with both the Independent "
       "Character and Legiones Astartes (Word Bearers) Special Rules and one of the following Psychic Disciplines: Harbinger "
       "of Chaos, Diabolism, or Anathemata from the same Detachment selected by the controlling player as the Word Bearers "
       "Procurator Squad's Leader for the purposes of this Special Rule. A Word Bearers Procurator Squad selected as a "
       "Retinue Squad does not use up a Force Organisation slot and is considered part of the same unit as the model "
       "selected as its Leader. A Word Bearers Procurator Squad selected as a Retinue Squad must be deployed with the model "
       "selected as its Leader deployed as part of the unit and the Leader may not voluntarily leave the Retinue Squad "
       "during play.")
o.char(NL, "Atramentar Squad", "P:Atramentar", WS="5", Ld="8")
o.char(NL, "Atramentar Squad", "P:Atramentar Trucidor", WS="5", Ld="9")
o.rule(NL, "Atramentar Squad", add="Stubborn")
o.cost_all(IW, "Dominator Cohort", ("Dominator", "Dominator w/Heavy Weapon"), 45)
o.add_link(IW, "Dominator Cohort", "2) Dedicated Transport", to="Dreadclaw Drop Pod", mn=None)
o.add_link(IW, "Dominator Cohort", "2) Dedicated Transport", to="Land Raider Spartan", mn=None)
RH = (WE, "Red Hand Destroyer Assault Squad")
for w, v in (("Meteor Hammer", 10), ("Excoriator Chainaxe", 10), ("Two Falax Blades", 5), ("Barb-Hook Lash", 5)):
    o.cost(*RH, "Blood Bonded", "Melee Options:", w, v=v)
    o.cost(*RH, "1) Ravagers", "Ravager w/" + w, v=15 + v)
o.add_link(SAL, "Sanctifier Squad", "4) Dedicated Transport", to="Rhino Transport", mn=None)
o.add_link(SAL, "Sanctifier Squad", "4) Dedicated Transport", to="Termite Assault Drill", mn=None)
o.rename(SAL, "Sanctifier Squad", "2) Sanctifiers", "Sanctifier w/ Options", "One Sanctifier May Take",
         to="Any model in the unit may exchange their Bolter for the following option:")
DP = ("• A model with this Unit Type may join units with the Infantry Unit Type as if it had the Primarch Unit Type, or "
      "units with the Daemon Unit Type as if it had the Daemon Unit Type.\n")
o.text("gst", "R:Daemon Primarch Unit Type", fn=lambda t: t if "Heroic Stand" in t else re.sub(
    r"• Any Hits inflicted by a model with the Daemon Primarch Unit Type[^\n]*", "• Daemon Primarchs have the Precision "
    "Strikes (2+) and Precision Shots (2+) Special Rules, and may choose to use these rules when attacking even when "
    "ordinarily they would be prevented from doing so, including when making Snap Shots.", t).rstrip() + "\n" + DP +
    "• Any unit entirely composed of models with the Daemon Primarch Unit Type may choose to ignore the Heroic Stand "
    "Special Rule, ignoring any penalties normally applied for declining a Challenge, unless the Challenge was issued by "
    "a model with the Knight, Gargantuan, Titan, Primarch, or Daemon Primarch Unit Types.")
o.char(EC, "Fulgrim Transfigured", "P:Fulgrim", WS="9")
for t in ("Land Raider Proteus Carrier", "Dreadclaw Drop Pod", "Land Raider Spartan"):
    o.add_link(IF_, "E:Huscarl Squad", to=t, shown="Dedicated Transport: " + t, mn=None)
o.chars_all(DG, "Mortus Poisoner", W="2")
o.chars_all(DG, "Poison-master", W="2")
o.rule(DG, "E:Mortus Poisoner Squad", add="Battle-Hardened (1)")
o.cost_all(DG, "E:Mortus Poisoner Squad", ("Heavy Alchem Flamer",), 5)
o.cost_all(DG, "E:Mortus Poisoner Squad", ("Power Scythe",), 10)
o.char(WS_, "Dark Sons of Death", "P:Dark Son", A="2")
o.char(WS_, "Dark Sons of Death", "P:Death's Champion", A="3")
o.text(RG, "R:Corax's Shame", fn=lambda t: t.replace(
    "gain the Battle-hardened (1) special rule. If", "gain the Battle-hardened (1) and Hatred (Horus Lupercal) Special "
    "Rules. If").replace("gain the Hatred (Corvus Corax) special rule.", "gain the Battle-hardened (1) and Hatred (Corvus "
    "Corax) Special Rules.") if "Horus Lupercal" not in t else t)
o.text("gst", "R:Gargantuan Unit Sub-type", fn=append(
    "• Any unit entirely composed of models with the Gargantuan Unit Type may choose to ignore the Heroic Stand Special "
    "Rule, ignoring any penalties normally applied for declining a Challenge, unless the Challenge was issued by a model "
    "with the Knight, Gargantuan, Titan, Primarch, or Daemon Primarch Unit Types.").__class__ and (lambda t: t if "Heroic Stand" in t else t.rstrip() +
    "\n• Any unit entirely composed of models with the Gargantuan Unit Type may choose to ignore the Heroic Stand Special "
    "Rule, ignoring any penalties normally applied for declining a Challenge, unless the Challenge was issued by a model "
    "with the Knight, Gargantuan, Titan, Primarch, or Daemon Primarch Unit Types."))

# ======================================================================= Legacies: Daemons of the Ruinstorm
RS = "Daemons - Daemons of the Ruinstorm"
o.text_all("The Ætheric Dominion (X)", lambda t: re.sub(r"^2 - Lashing Pseudopods: Reach \(1\)\s*$",
                                                        "2 - Lashing Pseudopods: Reach (1), Rending (6+)", t, flags=re.M))
o.rule(RS, "Ruinstorm Daemon Sovereign", add="Lords of the Ruinstorm")
o.cost(RS, "Ruinstorm Daemon Sovereign", "Weapon", "Sovereign Greatblade", v=40)
o.cost(RS, "Ruinstorm Daemon Sovereign", "Immaterial Wings", v=50)
o.char(RS, "Ruinstorm Daemon Hierarch", "P:Hierarch", WS="6")
o.rule(RS, "Ruinstorm Daemon Hierarch", add="Independent Character")
o.chars_all(RS, "Harbinger", Sv="3+")
o.chars_all(RS, "Daemon Attendant", Sv="3+")
o.add_link(RS, "Ruinstorm Daemon Harbinger", "Harbinger", "Weapons", to="Infernal Armaments", mn=None)
for m in ("Daemon Beast w/ Daemon Armaments", "Daemon Beast w/ Immaterial Flame"):
    o.cost(RS, "Ruinstorm Daemon Beasts", m, v=20)
o.price(RS, "Ruinstorm Daemon Beasts", 70 - 3 * 20)
o.chars_all(RS, "Daemon Beast", A="4")
o.rule(RS, "Ruinstorm Daemon Beasts", add=("Furious Charge (1)", "Scout"))
o.price(RS, "Ruinstorm Lesser Daemons", 0)
o.rule(RS, "Ruinstorm Daemon Swarms", remove="Swarm", add="Daemonic Hordes")
o.char(RS, "Ruinstorm Daemon Cavalry", "P:Daemon Cavalry", Ld="7")
o.rule(RS, "Ruinstorm Daemon Cavalry", add=("Hit & Run", "Bulky (2)"))
o.rule_x(RS, "Ruinstorm Daemon Cavalry", rule="Hammer of Wrath (X)", to="Hammer of Wrath (1)")
o.price(RS, "Ruinstorm Daemon Harriers", 100)
o.char(RS, "Ruinstorm Daemon Harriers", "P:Daemon Harriers", A="2")
o.rule(RS, "Ruinstorm Daemon Harriers", add="Deep Strike")
o.char(RS, "Greater Ruinstorm Daemon Beast", "P:Greater Beast", Ld="8", S="6", T="6")
o.rule(RS, "Greater Ruinstorm Daemon Beast", add=("Bulky (5)", "Feeding Frenzy"))
o.char(RS, "Ruinstorm Daemon Behemoth", "P:Ruinstorm Behemoth", WS="5", Ld="8")
o.add_link(RS, "Ruinstorm Daemon Behemoth", "May take up to two of the following options:", to="The Unmaking", mn=None, pts=25)
o.cost(RS, "Ruinstorm Arch-Daemon", "Immaterial Wings", v=50)
o.rule(RS, "Ruinstorm Arch-Daemon", add="Warp Resplendent")
o.rule(RS, "Cor’bax Utterblight Unbound", add="Bulky (6)")


# last, so that every Proteus Carrier option added above also offers the Phobos
o.run("Land Raider Phobos as a Proteus Carrier", phobos)
o.report()
