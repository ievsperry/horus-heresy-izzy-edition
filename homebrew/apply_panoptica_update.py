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

o.F.save()
o.report()
