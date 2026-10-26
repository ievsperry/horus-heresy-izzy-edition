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
python3 homebrew/build_catalogue.py homebrew/source/drukhari.md "Homebrew - Aeldari (Drukhari).cat"
python3 homebrew/build_catalogue.py homebrew/source/asuryani.md "Homebrew - Aeldari (Asuryani).cat"
python3 homebrew/build_catalogue.py homebrew/source/anhrathe.md "Homebrew - Aeldari (Anhrathe).cat"
python3 homebrew/build_catalogue.py homebrew/source/rillietann.md "Homebrew - Aeldari (Rillietann).cat"
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
  A bodyguard unit with the Retinue rule (the Warboss Retinue, or "Retinue (Archon)" naming an HQ) is
  never the Warlord; a leader whose "Retinue (Incubi)" names the unit it leads still may be.
  The Warlord must pick one Warlord Trait: a generic trait, or its sub-faction's own, which
  shows only when the army has that sub-faction. Da Finkin' Kap lets its bearer take a second, generic trait;
  no trait can be taken twice.
- Weapons and psychic powers from the doc's armoury, linked to the core rules
  in `2022 - Horus Heresy.gst` wherever a rule of the same name exists.

- Xenos factions (Tyranids, Orks, Necrons, T'au Empire, Drukhari, Asuryani, Anhrathe, Rillietann,
  Leagues of Votann) take the Xenos allegiance added to `2022 - Horus Heresy.gst`: their army
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
- Several "## Psychic Discipline: X" sections (Runes of Battle, Runes of Fate, Voidsong) are each an entry
  holding their powers and weapons. "Psychic Discipline (Voidsong or Runes of Battle)" on a datasheet is a
  pick of one; "(Voidsong and one other)" a pick of two that must include Voidsong. "Must select either
  Protect or Jinx" is a pick of one power inside the discipline.
- Grenades listed both as wargear (with its own rules) and in the armoury (plasma grenades) are taken
  as the wargear, which carries the grenade's profile.
- A Bio-Construct (Talos, Cronos) also has the game system's Dreadnought category.
- A second sub-faction section whose entries say "**Sub-faction:** Wych Cults" (Drukhari Obsessions) is a
  second pick on the army entry: each Obsession shows only while its sub-faction is chosen, and its rules,
  advanced reaction and Warlord Trait come with it.
- "The Corsair Prince must select one of the following" is a required pick of one. An option named exactly
  like one of the doc's rules (Master of the Void) carries that rule's text.
- "0-1 Autarch" is at most one per detachment. "### World-Rune: ..." headings are Rites of War under their
  Asuryani name, and "## Grand Performances" is a pick of one like a Doctrine. A sub-faction rule that says
  an "army may choose" one (Anhrathe Fleet) is optional. "Centreline Mounted" and "Arm Mounted" are mounts,
  not part of a weapon's name.
- Each Aeldari civilization has its own catalogue, named "Homebrew - Aeldari (X)" so they sort together:
  `asuryani.md`, `anhrathe.md`, `rillietann.md` and `drukhari.md`. Their ids still come from the civilization
  name, so saved rosters keep loading. Each carries the shared Aeldari rules and detachments, and only the
  rules, wargear, weapons and psychic disciplines its own units use. The Asuryani and Rillietann (Saedath)
  lists come from the Liber Antiquia doc; where it and Liber Aelphari share a weapon, wargear or psychic
  discipline, the Liber Aelphari version is kept. The Anhrathe Void Dreamer picks from the Liber Aelphari
  disciplines (Runes of Battle, Runes of Fate, Voidsong).
- A list whose only "## Psychic Discipline: X" is named on a datasheet ("Psychic Discipline
  (Phantasmancy)") builds it as a discipline entry, as with several.
- With no datasheet naming its transports, a list's Dedicated Transports are offered to Infantry units
  of up to 20 models. When the list has only one, smaller transport, its Transport Capacity is the limit
  (a Corsair Venom holds 6).
- "## Aspect Shrines" holds one "### Aspect Shrine: X" per Path. A datasheet option table headed "... Aspect
  Shrine upgrade" becomes a required pick of one on each model. The chosen shrine applies its Special Rules,
  Unit Sub-types and Characteristic changes, and its wargear: "exchanges Aspect Armour for Heavy Aspect
  Armour" swaps the armour and save, "gains ... at no cost" adds the items, and its option table becomes the
  shrine's weapon swaps. A Skyrunner Jetbike sets Move 18 and makes the model Cavalry (Antigrav). "May be
  selected by up to N Exarchs in a Detachment" limits that shrine per detachment for Exarchs only.
- "## Grand Performances" is only shown when the detachment has a Saedath (Rillietann) unit, and is then
  required.
- "If the army includes any Phoenix Lord models, one of them must be the Warlord" (on a "### X (type)")
  locks every other model's Warlord option while the army has a model of that type. A type whose models
  can never be the Warlord (the Avatar of Khaine, a Daemon Primarch) changes nothing.
- The World-Rune pick works like a Craftworld: it only shows (and may only be taken) in a detachment
  with an Asuryani unit.
- A "### Infantry Platoon" whose lines hold a "**Platoon Composition**" list ("2-5 Infantry Squads") is one
  choice in its slot, holding the squads from the "## Infantry Platoon" section between those numbers.
  The squads cannot be taken on their own.
- "Two other Guardsmen may form a Heavy Weapons Team, who must select one of the following" makes the
  team's profile a model that takes the place of two Guardsmen and must take one of the items. "Each
  Heavy Weapons Team must select one of the following" is one pick per team.
- Several swaps of the same weapon keep their own limits: "Any Veteran ... shotgun", "One other Veteran
  ... heavy flamer" and "Up to three remaining Veterans ... special weapons" are one lasgun swap with a
  cap on each pick. "Three Guardsmen must exchange their lasgun" means exactly three.
- "One other Guardsman ..." and "Any remaining Guardsman ..." make those picks exclusive on each model:
  a Guardsman with a vox-caster, platoon standard or medi-pack may not also swap his lasgun for a heavy
  flamer or special weapon, and each item stays within its number across the squad. "(up to two if a
  heavy flamer is taken)" lowers the special weapon cap while the squad has one.
- "A Heavy Weapons Team with a missile launcher may take: Flakk missiles" allows one per missile launcher
  in the squad.
- "Power weapon", when the doc gives it no profile of its own, is the game system's Power Weapon: a
  choice of power axe, power lance, power maul or power sword.
- "For every 10 models, up to two Shock Troopers may exchange ... (no weapon may be taken more than once
  per 10 models)" allows two picks, and each weapon once, per 10 models in the unit (the sergeant
  counts). "For every 10 models, one Shock Trooper with a lasgun may take" also counts every model.
- A swap of two weapons ("his laspistol and chainsword for a Sergeant's autogun and close combat
  weapon") beside a swap of one of them is one choice of what replaces the first; taking it gives up
  the second as well.
- "Lasgun (Jungle Fighters only)" and "Laspistol (Jungle Fighter Sergeant only)": when every model has
  its own weapons listed, the unmarked wargear ("Close combat weapon") is everyone's.
- An heirloom that is also a weapon in the Armoury (The Blade of Conquest) keeps its profile and its
  text, and may be taken once per army.
- A Rite of War or regiment saying "Infantry units of 12 or fewer models may take a Valkyrie or Vendetta
  as a Dedicated Transport" adds those transports to the units' Dedicated Transport choice while it is
  chosen (not to lone characters), and only while the unit fits. A barred transport is hidden inside
  units too, and a listed ban ("Leman Russ") covers every datasheet whose name starts with it.
- A regiment's "Infantry units and Sentinels have Deep Strike" or "Infantry units of 10 or more models
  have Feel No Pain (6+)" shows that rule on those units while the regiment is chosen, and "may not
  include Leman Russ or Rogal Dorn tanks" hides them. Rules that depend on the moment ("while in area
  terrain", "or increase an existing") stay as text.
- House rule: smoke launchers (in `2022 - Horus Heresy.gst`, so every list) and Ork smoke bombz grant
  Shrouded (5+) instead of their 6+ Cover Save. Both entries keep the original rule and say which is the
  house rule.
- A "## X Doctrine" section (Waaagh! Doctrine) shows in the app as written in the doc: each doctrine with
  its flavour and rules, and the section's introduction and the "## The X" lore section (The Waaagh!) as
  rules on the army entry.
- A rule whose list items have bold names ("- **Krumpin' Waaagh!:** ...") shows them one to a line in
  the app, with its paragraphs kept apart.
- "1-7 models chosen from up to 3 Meks (+55 points each), up to 3 Painboys (+75 points each) and up to 3
  Weirdboys (+100 points each)" is a unit of one to seven members, each kind capped and bought at its own
  price on top of the unit's cost (Odd Boys). "Any Mek may take up to 2 grot oilers" then allows two per
  Mek, and each Weirdboy in the unit rolls his own Weirdboy Discipline power and weapon.
- A wargear entry whose text says "Only one of each heirloom may be taken per army" may be taken once
  per roster (Heirlooms of Conquest).
- A psychic weapon named "X (Psychic Weapon)" is kept apart from a weapon called X but shown as plain X
  (the Runes of Twilight Executioner beside the Exarch's executioner).

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
- An option naming a set of weapons, "All Da Kit (choppa, shoota and slugga)", is one upgrade called
  All Da Kit that carries each weapon's profile. A Rite of War that raises a unit's size ("Boyz units
  may contain up to 40 models") still counts a model upgraded from one of its members ("One Boy may be
  upgraded to a Nob") toward that size.
- A rule whose text says "An army may only include a maximum of one model with this special rule per
  1,000 points" (Da Biggest is Da Best) puts every unit with it in a category of that name, which the
  roster may hold one of for each full 1,000 points of its points limit, and at least one.
- A biomorph whose text says "adds 1 to its Strength, to a best of 8" (Improved Strength, Improved
  Toughness, Killer Impulse) is offered only to units whose models are all below that best, at the
  cost scale of the other biomorphs, and shows each model's raised value once taken.
- `homebrew/source/additional-special-rules.md` holds special rules any catalogue may use (Afterburner,
  Augmetics (X), Rupture (X) and so on). `python3 homebrew/add_gst_rules.py` adds them to the shared rules
  of `2022 - Horus Heresy.gst`, or updates the ones it added; each "## Name" section is a rule, its italic
  flavour line stays in the source. A catalogue built here still prefers a rule its own doc defines.
