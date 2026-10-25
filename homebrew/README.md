Homebrew catalogues
===================

The `Homebrew - <Faction>.cat` files in the repo root are generated from Isaac's
homebrew conversion docs for The Horus Heresy 2.0. The doc text is kept in
[source](source) as Markdown, and [build_catalogue.py](build_catalogue.py) turns it
into a catalogue.

To rebuild a catalogue after the doc changes, export the doc to Markdown again,
replace its file in `source/`, and run from the repo root:

```
python3 homebrew/build_catalogue.py homebrew/source/tyranids.md "Homebrew - Tyranids.cat"
python3 homebrew/build_catalogue.py homebrew/source/orks.md "Homebrew - Orks.cat"
python3 homebrew/build_catalogue.py homebrew/source/necrons.md "Homebrew - Necrons.cat"
python3 homebrew/build_catalogue.py homebrew/source/tau.md "Homebrew - T'au Empire.cat"
python3 homebrew/build_catalogue.py homebrew/source/astra-militarum.md "Homebrew - Astra Militarum.cat"
python3 homebrew/build_catalogue.py homebrew/source/drukhari.md "Homebrew - Drukhari.cat"
```

Each rebuild that changes the catalogue raises its `revision`, so BattleScribe and
NewRecruit offer the update. IDs come from entry names, so rebuilding keeps them stable and saved rosters keep
loading. The script prints anything in the doc it could not place.

## What the catalogue covers

- Every datasheet, with its profiles, wargear, special rules, Force Organisation
  slot and points. A unit's starting cost always matches the doc.
- Weapon exchanges sit on each model: the weapon a model starts with is its default, and
  picking a swap replaces it (a Tyranid Warrior that takes a venom cannon loses its devourer).
  In a unit of several models, models with different weapons are split into separate
  selections. Unit-wide limits still hold: "one in every three" and "up to two may" share
  one limit across the unit, and "One Guardsman may..." allows one in the unit. Only a
  loadout the whole unit picks together (Ork Boyz' slugga or shoota) keeps a unit-level pool.
- Options that add something rather than replace it are bought per model at unit level: a
  unit of 10 can buy any number from 0 to 10 of each.
- Biomorphs (everything in the doc's Biomorphs section) are taken by every model
  in the unit, and cost their points for each model. Tails are weapon options:
  bought per model, added to the model's other weapons.
- Biomorphs with a **Cost:** line in the doc (adrenal glands, toxin sacs, flesh hooks,
  Dynamic Camouflage, Hardened Carapace) are offered to every unit whose models can all
  use them ("Character, Monstrous or Gargantuan models only" or "Genestealers, Hormagaunts,
  Termagants and Ripper Swarms only" limits who), priced by model: a named list of small models, every other model, Monstrous
  and Gargantuan ("Gargantuan models may not take them" leaves them out). A datasheet that
  prices a biomorph itself keeps its own cost, and units the Biomorphs section says "may
  not take biomorphs" (spores and transports) get none.
- Options: extra models, weapon exchanges (including "one in every three"),
  per-model and whole-unit upgrades, and model upgrades such as the Neurothrope.
  "Each type only once" limits are enforced.
- Dedicated Transports: units that fit in a Mycetic Spore or Tyrannocyte (20
  Infantry models or one Monstrous model) may take one, offered only while they fit. Units the
  Dedicated Transports section says "may not take" one (spores, winged units) never get it.
- The army selection: hive fleet (with its rules and advanced reaction), Rite of War,
  and the army-wide advanced reaction.
- Warlords: every Character model in an HQ unit (or, in an HQ with no Character, its own model, such
  as the Trygon Prime) may be the Warlord, using the game system's
  Warlord entry, so an army must have exactly one. A model whose datasheet says it "must be
  your Warlord" (Ghazghkull, Imotekh, Vect...) is offered it in any slot and must take it.
  A bodyguard unit with the Retinue rule (the Warboss Retinue) is never the Warlord.
  The Warlord must pick one Warlord Trait: a generic trait, or its sub-faction's own, which
  shows only when the army has that sub-faction. Da Finkin' Kap lets its bearer take a second, generic trait;
  no trait can be taken twice.
- Weapons and psychic powers from the doc's armoury, linked to the core rules
  in `2022 - Horus Heresy.gst` wherever a rule of the same name exists.

- Xenos factions (Tyranids, Orks, Necrons, T'au Empire, Drukhari, Leagues of
  Votann) take the Xenos allegiance added to `2022 - Horus Heresy.gst`: their army
  selection makes Xenos required for the force, and every unit has the Xenos rule.

- Vehicles, Dreadnoughts, Knights and Titans get the game system's Vehicle or Knights
  and Titans profile, and their sub-types (Fast, Flyer, Transport...) as categories.
- Models bought as options (ammo runts, grot oilers, Spanners) are their own model
  entries, with the kit and unit type their wargear entry gives them. Linked counts
  are kept: each Mek Gun brings 2 Gretchin crew, and Gretchin get a Runtherd per 10.
- Datasheets that name their Dedicated Transports get exactly those, each offered
  only while the unit fits inside it (a Trukk holds 12).
- Kombi-weapons, artefacts (one of each per army) and wargear that confers an Armour
  Save ('eavy armour, mega armour) are handled; the Save shows on the profile.

- Named abilities in a "Power | Effect" table (the Powers of the C'tan) are given to
  the datasheets that list them, or offered as a pick when a datasheet says "of your
  choice". Rites of War may be headings or bold paragraphs.

- Drones (T'au) are models with the profiles and kit from the doc's Drones section. Fixed
  drones come with their unit; drones a unit may buy sit in a Drones group with its limit
  ("up to two", "two per battlesuit", "one each of"). A vehicle that exchanges its Gun
  Drones for a weapon loses them, and the Droneport swaps drones at the difference in cost.
- Battlesuit Armoury weapons and support systems are a pick list on the units that use it
  (four for a Commander, three per Crisis battlesuit). Rows of a "Unit | Option | Cost" table
  are added to the datasheets they name.
- Kill Teams: "9 models chosen from..." is a group of exactly that many, each specialist at
  most once. A model whose wargear reads "X or Y" chooses one.
- Weapons that keep their official 2.0 profile (the flamer) link to the game system's entry.
  A T'au weapon that shares its name with an official weapon keeps the doc's profile and is
  named "Tau X" (Tau Close combat weapon, Tau Neutron blaster).

- Astra Militarum is not Xenos: the army may be Loyalist or Traitor. Weapons that keep their
  official 2.0 profile link to the game system under its 2.0 name (a storm bolter is the combi-bolter,
  a boltgun the bolter, a force stave the force staff), and a weapon's mount is not part of its name
  ("Hull (Front) Mounted heavy bolter" is the official heavy bolter). Wargear marked "(Sergeant only)"
  replaces that model's weapons, and "Flamer, grenade launcher or sniper rifle" is one pick of three.
- Wargear grouped under a heading ("### Armour" holding "#### Kabalite Armour") is read item by item.
  "Scourge wings (count as a jump pack)" is the official jump pack under the doc's name. "May exchange
  any dark lance" lets each of the three be swapped; "one macro-scalpel" only one of the two.
- A unit that includes another datasheet's character ("Asdrubael Vect (use his HQ profile and
  wargear)") gets that model, with its kit and its rules.

- Rites of War work in the app, read from their own wording: units a Rite lets take another
  slot ("may be taken as Troops") are listed there while it is chosen (a Rite that grants Line, or
  says Compulsory, lets them fill compulsory Troops); "gain the Line sub-type", "may contain up to
  N models", and special rules a Rite gives or takes away apply while it is chosen. "Must have a
  Big Mek as its Warlord" leaves only those models able to be the Warlord, and a named Warlord
  that is not an HQ (a Trygon Prime) is offered the Warlord option under that Rite.
- Rite of War limitations are checked too: units a Rite bars ("no Lords of War", "any Flyers",
  "Heavy Support choices other than Broadsides", "Destroyers of any kind") are hidden while it is
  chosen and are an error on the Rite if already taken; "no more than two Heavy Support choices"
  and "must include at least two Genestealer units" are errors on the Rite when broken; and a Rite
  that "may not be used by an Allied Detachment" is hidden in one.

- A psychic discipline whose rule says to "roll one D3 on the ... Psychic Powers table" (the
  Weirdboy Discipline) gives each psyker that has it a pick of one power and one psychic weapon
  from the tables under its "####" headings, standing in for the rolls. Powers and weapons before
  any heading are the ones every psyker of the discipline knows (Power of da Waaagh!).
- A "## ... Doctrine" section with one "###" per doctrine is a pick of one on the army entry; when
  its text says a "model with the X special rule may select" one, it shows only while the army has
  such a model.
- Bold weapon rules written beside the armoury tables ("**Mishap.**") are rules weapons link to.

- A biomorph granted by a sub-faction ("Deep Burrowers: Infantry units gain the Burrower biomorph")
  or a Warlord Trait ("The Warlord and any unit it joins gain the Burrower biomorph") shows its
  rules on those units while that sub-faction or trait is chosen, and the paid option is hidden.

- A "## Primarch" section puts its units in the game system's Primarch slot (Ghazghkull Thraka),
  counting toward the Lords of War and Primarchs points limit. "If you take this entry, you may not
  also take X" makes the two entries exclusive (only one Vect).

## Not enforced

- Rite of War limitations that compare unit counts ("may not include more Infantry units than
  Dreadnought units") or are in-game only ("must start the game embarked", "no Reserves"), and Rite
  effects that are in-game only (Deep Strike from turn one), are text only.
- Instinctive Behaviour, Synapse and other in-game rules are text only.
- Lords of War use the game system's existing 25% points category; nothing
  Tyranid-specific is added to it.
