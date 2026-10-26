#!/usr/bin/env python3
"""Apply the Liber FAQ, Errata and Balance Changes for the Horus Heresy: Age of Darkness Core Rulebook to the
rules the game system holds (special rules, Unit Types and psychic powers).

usage: python3 homebrew/apply_core_faq.py

Each change is written against the current text, so running it again changes nothing. Changes to rulebook
procedures the data has no entry for (Sweeping Advances, Snap Shots, Deep Strike Assaults and so on) are not
here."""
import html
import re
import sys

GST = "2022 - Horus Heresy.gst"
with open(GST, encoding="utf-8", newline="") as f:
    src = f.read()
NL = "\r\n" if "\r\n" in src else "\n"
done, missing = [], []


def esc(text):
    return html.escape(text, quote=False).replace('"', "&quot;").replace("\n", NL)


def edit(kind, name, fn):
    """Change the description of every rule (or psychic power profile) with this name."""
    global src
    if kind == "rule":
        pat = re.compile(r'(<rule [^>]*?name="' + re.escape(esc(name)) + r'"[^>]*>\s*<description>)(.*?)(</description>)', re.S)
    else:
        pat = re.compile(r'(<profile [^>]*?name="' + re.escape(esc(name)) + r'"[^>]*>\s*<characteristics>\s*'
                         r'<characteristic name="Description"[^>]*>)(.*?)(</characteristic>)', re.S)
    hits = 0

    def sub(m):
        nonlocal hits
        hits += 1
        old = html.unescape(m.group(2)).replace("\r\n", "\n")
        new = fn(old)
        return m.group(1) + (esc(new) if new != old else m.group(2)) + m.group(3)
    src = pat.sub(sub, src)
    (done if hits else missing).append(name)


def append(extra):
    return lambda t: t if extra in t else t.rstrip() + "\n\n" + extra


def replace(old, new):
    def fn(t):
        if new in t:
            return t
        if old not in t:
            sys.exit(f"text not found: {old[:60]}")
        return t.replace(old, new)
    return fn


def whole(new):
    return lambda t: new


# ---- special rules
edit("rule", "Shock Pulse", append(
    "Models with the Super-Heavy, Lumbering, Knight, or Titan Sub-types are not forced to make Snap Shots as part "
    "of their next Shooting Attack, instead suffering a -2 penalty to their Ballistic Skill Characteristic when they "
    "make their next Shooting Attack, and in addition, any weapons they are equipped with that use a Scatter dice to "
    "roll to hit and which roll a result of 'Hit' on the Scatter die must re-roll it. This penalty can only be "
    "applied to a model once per turn."))
edit("rule", "Night Fighting", replace("roll a D6 before deployment: on a 2+,", "roll a D6 before deployment: on a 4+,"))
edit("rule", "Blind", whole(
    "If a non-Vehicle unit suffers one or more unsaved Wounds from a weapon with the Blind Special Rule, it must take "
    "a Initiative test once the firing unit has finished its Shooting Attacks for that Phase. This is called a Blind "
    "test. If the unit fails the Test, it is Blinded. If the test is passed, there is no further effect. If the "
    "Initiative test is failed, all models in the unit are reduced to Weapon Skill 1 and Ballistic Skill 1 until the "
    "end of their Controlling Player's next turn. Should the attacking unit hit themselves, they automatically pass "
    "the Initiative test. Any model that does not have an Initiative Characteristic (for example, Vehicles, "
    "Buildings, etc) are unaffected by this Special Rule."))
edit("rule", "Concussive (X)", whole(
    "Any unit hit by one or more models or weapons with this Special Rule must take a Leadership test once the attack "
    "is fully resolved. If the test is passed, there is no further effect. If the Leadership test is failed, all "
    "models in the unit suffer a penalty to their Weapon Skill equal to the value in brackets until the end of their "
    "Controlling Player's next turn. Should the attacking unit hit themselves, they automatically pass the Leadership "
    "test. Any model that does not have a Leadership Characteristic (for example, Vehicles, Buildings, etc) are "
    "unaffected by this Special Rule.\n\n"
    "If a single unit has been the target of several Concussive attacks with different values and fails the "
    "Leadership test, then it suffers the effects of the highest single modifier among those attacks – the effects "
    "do not stack or otherwise become cumulative."))
edit("rule", "Force", append(
    "If multiple modifiers would affect the Strength of a model using a Force Weapon, these should be resolved as "
    "follows:\n"
    "• If a model has a weapon which would increase its S via a flat +X bonus (such as a force maul), this occurs first.\n"
    "• If a model uses the Force Psychic Power, the S multiplication from this is resolved next.\n"
    "• This means, assuming a base Strength of 4, a weapon strength of 6, and a successful cast of the Force Power "
    "for x2 strength on the attack, the model would resolve its attacks at Strength 12.\n"
    "The reasoning for this is that Force specifically applies its Strength multiplication bonus to the attack itself, "
    "not to the weapon or bearer's Strength."))
edit("rule", "Guided Fire", append(
    "Models wounded by a weapon with this Special Rule may never benefit from a Cover Save due to intervening terrain "
    "and models."))
edit("rule", "Hit & Run", lambda t: t.replace("add the unit’s Movement Characteristic to the result",
                                               "add the unit’s Initiative Characteristic to the result")
                                      .replace("add the unit's Movement Characteristic to the result",
                                               "add the unit's Initiative Characteristic to the result")
                                      .replace("equal to the 2D6 + Movement result", "equal to the 2D6 + Initiative Characteristic result"))
edit("rule", "Master-crafted", append(
    "Master-Crafted Blast or Template Weapons are treated as though they have the Twin-Linked Special Rule."))
edit("rule", "Monster Hunter", whole(
    "A unit that contains at least one model with this Special Rule re-rolls all failed To-Wound rolls against "
    "Dreadnoughts, Automata and Primarch models as well as any unit with the Monstrous Sub-type or Gargantuan Sub-type."))
edit("rule", "Night Vision", whole(
    "A unit that contains at least one model with this Special Rule ignores the effects of Night Fighting (see page "
    "308) and no model may make Shrouded rolls to negate Wounds or Hull Points inflicted by their attacks."))
PRECISION = ("If a model makes any attack, then they may only gain the benefit of the Precision Shots / Strikes (X) "
             "Special Rules on a successful Hit (provided the Hit Roll is equal to or better than the value X).")
edit("rule", "Precision Shots (X)", append(PRECISION))
edit("rule", "Precision Strikes (X)", append(
    "The Precision Strikes (X) Special Rule does not allow models to strike into - or out of - a Challenge. Outside "
    "forces must attack other Outside forces, and Challengers must strike each other, in line with the Challenge "
    "section on pages 198 and 199.\n\n" + PRECISION))
edit("rule", "Slow Vehicles", replace(
    "In addition, when a Slow Vehicle moves, other than to pivot in place, it is always considered to have moved at "
    "Cruising Speed regardless of how many inches it moves.",
    "In addition, when a Slow Vehicle moves at Cruising Speed, it may only fire Snap Shots, regardless of the normal "
    "rules for Vehicles and Shooting."))
edit("rule", "Detonation", append(
    "A weapon with the Detonation Special Rule is never counted when determining if a model has two melee Weapons."))
edit("rule", "Assault Vehicle", append(
    "Units that have Disembarked from a model with the Assault Vehicle Special Rule in Step 5 of the Flanking Assault "
    "process may Charge in the following Assault phase, as an exception to the Assault Vehicle Special Rule."))

# ---- Unit Types
COUNT = ("• For the purposes of any rules that consider number of models in a unit (such as Rampage), a {} model counts "
         "as a number of models equal to its starting Wounds Characteristic.")
REROLL = ("• Failed To Wound rolls made against a unit with the {} Unit Type by a weapon with the Ordnance type or the "
          "Sunder Special Rule may be re-rolled.")
edit("rule", "Automata Unit-type", lambda t: t if "Rampage" in t else t.rstrip() + "\n" + COUNT.format("Automata") + "\n" + REROLL.format("Automata"))
edit("rule", "Dreadnought Unit-type", lambda t: t if "Rampage" in t else t.rstrip() + "\n" + COUNT.format("Dreadnought") + "\n" + REROLL.format("Dreadnought"))
edit("rule", "Cavalry Sub-type", lambda t: t if "Rampage" in t else t.rstrip() + "\n" + COUNT.format("Cavalry"))
edit("rule", "Daemon Unit-type", replace(
    "• No model that is not also of the Daemon Unit Type may join a unit that includes a Daemon model.",
    "• No unit that does not also have the Daemon Unit Type or the Corrupted Unit Sub-type may join a unit that "
    "includes one or more models with the Daemon Unit Type."))
edit("rule", "Primarch Unit-type", lambda t: t if "Heroic Stand" in t else replace(
    "• Any Hits inflicted by a Primarch, as part of either Shooting Attacks or in close combat, are allocated by the "
    "Primarch’s controlling player and not the controlling player of the target unit. These Hits should form a "
    "separate Wound Pool.",
    "• Primarchs have the Precision Strikes (2+) and Precision Shots (2+) Special Rules, and may choose to use these "
    "rules when attacking even when ordinarily they would be prevented from doing so, including when making Snap "
    "Shots.")(t).rstrip() + "\n• Any unit entirely composed of models with the Primarch Unit Type may choose to "
    "ignore the Heroic Stand Special Rule, ignoring any penalties normally applied for declining a Challenge, unless "
    "the Challenge was issued by a model with the Knight, Gargantuan, Titan, Primarch, or Daemon Primarch Unit Types.")
edit("rule", "Antigrav Sub-type", lambda t: re.sub(
    r"^• A unit that includes only models with the Antigrav sub-type.*$",
    "• Models with the Antigrav Sub-type may move over friendly and enemy models, but cannot end their move on top "
    "of either. They may also move over all terrain, ignoring all penalties for Difficult Terrain and Dangerous "
    "Terrain. However, if a moving model with the Antigrav Sub-type starts or ends its move in Difficult Terrain or "
    "Dangerous Terrain, it must take a Dangerous Terrain test. An Antigrav model can even end its move over "
    "Impassable Terrain if it is possible to actually place the model on top of it, but if it does so it must take a "
    "Dangerous Terrain test. If an Antigrav model is forced to end its move over friendly or enemy models, move the "
    "model the minimum distance so that no models are left underneath it.", t, count=1, flags=re.M))
edit("rule", "Knights and Titans", append(
    "Any model with either the Knight or Titan Unit Type gain the Hammer of Wrath (3) Special Rule.\n"
    "A Knight or Titan may make a Charge move against a model in area terrain, ignoring vertical distances - treat the "
    "model being charged as though it is on the ground floor for the purposes of charges. A Knight or Titan may make "
    "a melee attack against a model whose base is within 1\" horizontally of their own, regardless of vertical "
    "distance.\n"
    "In addition, a Knight or Titan gains +2 Attacks for being equipped with two Melee weapons, instead of the normal "
    "+1 it would gain for having Two Weapons (page 184)."))

# ---- psychic powers
edit("rule", "Hallucinations", whole(
    "A unit that suffers one or more Hits from a Weapon with this Special Rule must make an immediate Pinning test, "
    "suffering a -1 modifier to their Leadership Characteristic for each successful Hit scored by this attack before "
    "the result is decided. For example, if a Psyker attacks an enemy unit that has a Leadership of 8, scoring 3 Hits "
    "with Telepathic Hallucinations, then that unit must make an immediate Pinning test with a -3 modifier to their "
    "Leadership Characteristic. Note that models with Special Rules that ignore Leadership modifiers, such as "
    "Stubborn, do not suffer this negative modifier."))
edit("profile", "Telekine Dome", lambda t: re.sub(r"(?<!wholly )within 8\"", "wholly within 8\"", t))
edit("profile", "Thamaturgic Succour", replace(
    "all non-Vehicle models in the target unit may roll a D6. On a roll of a 5+, that model regains a single lost Wound.",
    "all non-Vehicle models in the target unit regain a single lost Wound."))

with open(GST, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("changed:", ", ".join(done))
if missing:
    print("not found:", ", ".join(missing))
