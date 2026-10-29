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
python3 homebrew/build_catalogue.py homebrew/source/traders-militant.md "Homebrew - Traders Militant.cat"
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
  In an Exarch unit, a model taken more than once is split into one entry per model ("Exarch",
  "Exarch 2", ...), so each Exarch picks its own shrine and that shrine's weapon options. A note under the Options
  "_No more than 3 Exarchs in the unit may select the same Aspect Shrine._" caps each shrine within the unit;
  "_The unit may contain up to 7 models, no more than 4 of any one kind ..._" caps each kind of model and all
  of them together (an upgraded model, such as a Skyrunner Officer, becomes a model of its own kind and costs
  the model it was upgraded from as well). The weapon a shrine gives is the default pick of its exchange and may
  be kept; "Twin-linked Avenger Catapult" is its own twin-linked weapon.
- A datasheet rule "Warlord: Storm of Silence" naming a "### Warlord: Storm of Silence" section is a trait the
  model takes once it is the Warlord, in place of the Warlord Traits pick.
- A rule whose words before an apostrophe name an entry ("Scorpion's Sting (X)" and the Scorpion) gets a copy
  under each name a weapon uses ("Scorpion's Sting (1)"), so the list apps link the rule, not the vehicle.
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
- A "####" heading inside a datasheet that has its own Unit Composition (the Retainers Militant's Adjuevant
  Medicae, Navigator Nobilis and the rest) is a model the unit may include: it keeps its own profile, wargear,
  rules and options, and sits in a "Retainers" group on the unit at the cost and count its option row gives
  ("one of each", "up to two"). A retainer whose row starts "If the army includes a Detachment with the X
  Faction/Sub-faction" only shows while the roster has that army's selection (the Mechanicum, Legio Custodes,
  Sisters of Silence, Solar Auxilia or Imperialis Militia entry of the game system, the Asuryani or Rillietann
  army entry, or a unit with the Legiones Astartes category).
- A "Force Organisation" table headed "X Detachment (Primary only)" with rows such as "HQ: 1 Compulsory" and
  "Elites: 2 Compulsory, +3 Optional" is a Force Organisation Chart of the catalogue's own (the Aegis Militant
  Detachment), taken once per army. Allied and Lords of War Detachments stay the game system's.
- A rule under "## Army-wide Special Rules" that says a model "must select one" of the "####" headings below
  it (Warrants of Trade) is a required pick of one on every unit with the rule, hidden and optional when the
  unit is in an Allied Detachment.
- "A Rogue Trader that takes Indomitus Terminator Armour gains +1 Wound and the Heavy Sub-type": once the model has
  the item, its profile shows the extra Wound and the Sub-type in its Unit Type, and it has the Sub-type's category.
- A doc title without "for The" ("Traders Militant Horus Heresy 2.0 - Homebrew Conversion") still names the
  faction ("Traders Militant").
- Army-building limits a list's rules set beyond what its datasheets say live in their own module, named in
  `FACTION_LIMITS` in build_catalogue.py and run after the catalogue is built. `traders_militant_limits.py`:
  - Each Detachment is counted by the faction selection every catalogue requires in a force (the Allegiance
    entry: "Mechanicum", "XIII: Ultramarines", a homebrew army entry), and Xenos Detachments by the Xenos Army
    category.
  - Each Warrant of Trade carries its Limitations as limits on the Warrant, so the app flags the Warrant the army
    breaks: Compliance (no Xenos Detachments; at most one Agents of the Emperor or Warmaster Detachment), Conquest
    (at most one Xenos Detachment; no Agents Detachments), Exploration (exactly one Xenos Detachment; at most one
    Legiones Astartes Detachment, counting Blackshields and Shattered Legions; at most two Mechanicum; no Agents
    Detachments) and Warrant-Breaker (Allied and Optional Detachments only from Xenos or Imperial Army Factions;
    no Faction more than twice). Agents of the Emperor are Legio Custodes and Sisters of Silence; Agents of the
    Warmaster are Daemons of the Ruinstorm and Bound Daemons. The Imperial Army is Solar Auxilia, Imperialis
    Militia and the homebrew Astra Militarum.
  - The Aegis Militant Detachment may take one Clade Assassins, Nathaniel Garro or Tylos Rubio (Loyalist) or
    Cults Abominatio (Traitor) unit from LI - Assassins and Agents as an Elites choice, shown as the official
    catalogues show them (Garro and Rubio with Legacies). It counts toward the Elites maximum but not the two
    Compulsory Elites, and only one may be taken.
  - "Allied Detachments (one per 1,000 points)", taken automatically in the Aegis Militant Detachment, is flagged
    when the army has more Allied Detachments than one per full 1,000 points of its points limit, plus one for
    the Detachment a Warrant's Effects add (Compliance: an Agents Detachment; Conquest: a Xenos Detachment;
    Exploration: up to two Mechanicum Detachments).
- "For every five models in the unit, one ... may" is a one-in-five limit like "For every 5 models,". "either or
  both Bolt Pistols" swaps each pistol; "both Bolt Pistols for one of" swaps the pair for one item. "its A or B for
  one of", when the model has both, is a swap of each. "Any model without a X may take" reads as "Any model".
  "The entire unit may take: Haywire grenades, +3 points each" costs that per model.
- "Needle Cannon (with Suspensor Web)" is the weapon and the Suspensor Web; brackets that only name the weapon's own
  profiles ("Reaper Launcher (with Starswarm, Starshot, and Starhawk Missiles)") are the weapon. "Executor
  Great-Blade with in-built Vratine Bolter" is both weapons. Armoury rows "X (Ranged)" and "X (Melee)" are one
  weapon X with both profiles, also when the names differ only by a plural ("Haywire Grenade (melee)" and
  "Haywire grenades (ranged)") or the other profile is a "X – melee" row. A wargear item and a weapon with the same name
  (Stikkbombz, which count as frag grenades, and their thrown profile) stay two entries, and each shows the
  other's profile, so a unit sees both whichever one it takes. A free option repeating the weapon the swap starts with is left out.
- "its Halian Heavy Jetbike's Heavy Snare Cannon" works like "either or both of its X's Y": the weapon the wargear
  says it has ("A Halian Heavy Jetbike has a Heavy Snare Cannon") joins the model's wargear.
- An option item the doc does not define is looked for before it becomes a named placeholder: "Chainsword and
  Laspistol" is both items, and "Storm Axe" or "Charnabal Weapon" is the official catalogues' or the game system's
  entry (any game system entry by name, singular or plural). A game system weapon whose profiles sit in its own
  entries ("Missile Launcher": frag, krak) is a weapon too. This fills options that used to be empty in the
  Traders Militant, Astra Militarum and Aeldari lists.
- A swap of an item the model only gets from another swap ("The Troop Master may exchange its Shotgun for:
  Laspistol", then "may exchange a Laspistol for one of") joins that swap at both costs; when the first swap gives
  two items ("Laspistol and Close Combat Weapon"), each part may be swapped, so every combination is offered.
- "exchange a Laspistol for", "up to two Centreline Mounted Twin-Linked Lascannons, each for", counts up to twelve
  ("Eight Hull (Front) Mounted Hellstrike Missiles"), "Special Rules: None", a wargear heading naming its bearer
  ("Ambulator Frame (Ireton MaSade)") and "Two Dreadnought Power Gloves with in-built Twin-Linked Bolters" are read.
- From the official catalogues the Builder also takes items behind a mount ("Centreline Mounted Enhanced Arachnus
  Blaze Cannon"), "Twin-Linked X" (X's profiles with Twin-linked), and singular or plural names ("Spectra Cloak" is
  "Spectra Cloaks"). An official rule spelt another way ("Ex Oblivio", "Ex-Oblivio") is linked by its own name.
- Items the doc names but leaves to the official lists (Auric Warplate, Execution Blade, Legio Custodes,
  Ex Oblivio) are copied from the official catalogues, keeping their profiles, text and the core rules they
  link; "Melta Bombs" and "Psyk-Out Grenades" are the game system's Meltabombs and Psyk-out Granades. "Force
  Weapon", when the armoury lists Force Axe, Maul, Staff and Sword, is a pick of one of them.
- A "| Wargear | Effect |" table under one heading ("Forceshield, Improved Forceshield and Holo-Suit") is an
  item per row. A "| Relic | Effect | Cost |" table whose text says "A Rogue Trader Militant may take one" is a
  group of that heading's name on that unit.
- "Any Militant Bodyguard or Trader-Militant Standard Bearer may exchange" applies to both models. "their
  Laspistol and/or Power Weapon, each for one of" is a separate swap of each. "either or both of its Arkadia
  Pattern Grav-Attack's Heavy Bolters" swaps the weapons the wargear says it has. An options table with no
  heading, a "Dedicated Transport: ..." line, "0-1 per army." (one per roster), a "## Troops" section that says
  "These units are Dedicated Transports.", and a note written after the Special Rules list are all read.

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
- A "**Name.** text" rule ends at the next heading, so a table or list under a following "####" heading no
  longer joins the rule before it.
- In the official catalogues, Expansion FAQ limits that depend on play or on the Detachment (Armoured Fist Pattern
  Cohorts: Infantry must start Embarked, no models with Movement 0, no Fortifications, Line only in a Primary
  Detachment) are rule text only; the Armoured Fist Troops choice itself takes any one Leman Russ Strike or Assault
  Squadron and gains Line as a Compulsory Troops choice.
- Traders Militant: Traders Militant Elites taken as Troops in an Allied Detachment are rule text only.

## Game system and official catalogue tools

These scripts change `2022 - Horus Heresy.gst` and the official catalogues; run them from the repo root.

- `homebrew/source/additional-special-rules.md` holds special rules any catalogue may use (Afterburner,
  Augmetics (X), Rupture (X) and so on). `python3 homebrew/add_gst_rules.py` adds them to the shared rules
  of `2022 - Horus Heresy.gst`, or updates the ones it added; each "## Name" section is a rule, its italic
  flavour line stays in the source. A catalogue built here still prefers a rule its own doc defines. A rule the
  game system already has under its own id (in its shared rules or a Unit Sub-type) has its text set to the
  source's; pass `--keep-existing` to leave those alone. The file holds the Imperatus Special Rules and Unit
  Sub-types (Anathema, Asuryani, Corrupted, Guardian, Rillietann, Sycophantica). Optional rules are marked "Optional rule:": Concussion (X)
  and Cover (X+) are new rules, while Grenades and Unwieldy keep their core text with the optional rule added
  after it.
- `python3 homebrew/sync_catalogue_rules.py` gives the official catalogues' own copies of shared rules (the
  Custodes Auramite Talon, Gravitic Repulsion, Master of the Shield-Hosts and Slayer of Kings, the Solar Auxilia
  Command Tank, the Sisters of Silence Vigilant Covenant) the text `additional-special-rules.md` has for them.
  Running it again changes nothing.
- `python3 homebrew/add_imperatus_wargear.py` adds the Imperatus Archaeotechnological Relics (Apex Digital Weapon,
  Displacer Matrix, Grav-Wave Generator) to the game system as a one-per-model group the Solar Auxilia Legate
  Marshal may take, and the Imperialis Militia Force Commander may take with the Armoury of Old Night Provenance
  or the Merchant Princeling or Connoisseur of Alien Curios Warlord Traits. It also sets the Diabolism, Anathemata
  and Navis Astrologis disciplines to the Imperatus text. Running it again changes nothing.
- `homebrew/source/additional-weapons.md` holds weapon profiles for every catalogue. `python3
  homebrew/add_gst_weapons.py` updates every matching weapon profile in the game system and the official
  catalogues to them (names matched ignoring case and punctuation, melee to melee and ranged to ranged), adds
  a melee profile to an entry that had only other ones (Krak Grenades, Ripper Gun), and adds the weapons the
  game system lacks to its shared entries. The Extrinsica Melee Weapons carry their points, the Extrinsica
  rule and a category allowing one per army. Homebrew catalogues take these changes from their own sources.
- The game system also holds a **Power Pack** wargear entry (0 points, for Infantry Characters). It carries a
  Power Pack Weapons group allowing up to two of the Power Pack Weapons from `additional-weapons.md`: Circular
  Stone Saw (+5 points), Stone Burner (+10 points), Gem Extractor and Kinfolk Arc Welder. No unit links to it
  yet.
- `python3 homebrew/apply_core_faq.py` applies the Liber FAQ, Errata and Balance Changes for the Core Rulebook
  to the rules `2022 - Horus Heresy.gst` holds (Blind, Concussive (X), Force, Hit & Run, the Unit Type rules,
  Telekine Dome and so on). Running it again changes nothing.
- `python3 homebrew/apply_expansion_faq.py` applies the Liber Panoptica FAQ, Errata and Balance Changes for the
  army books, Legacies and Exemplary Battles to the official game system and catalogues: points, characteristics,
  Unit Types, special rules, options, Force Organisation slots and rule text. It is written against the current
  data, so running it again changes nothing, and it lists any change it could not place. Its edit operations
  (find an entry by a name path, set a cost or characteristic, add or drop a rule, retarget a weapon option and so
  on) live in `homebrew/faq_tools.py`; they edit the XML text in place, so each file keeps its own formatting, and
  only link to rules and entries a catalogue can see through its imports. A full run takes a minute or two.
  It covers Liber Astartes, Liber Hereticus, Liber Mechanicum, Liber Imperium, the Legacies books (Legiones
  Astartes, Mechanicum, Solar Auxilia, Assassins, Imperialis Militia, Daemons of the Ruinstorm), the campaign books
  (Martian Civil War, Beta-Garmon, Siege of Cthonia) and the Exemplary Battles. The Blackshields Oaths (Panoply of
  Old, The Spoils of Victory) are game system rules, so their changes are made there. Clarifications with no data
  entry (how a rule is played) are left out.
- `python3 homebrew/add_twin_linked.py` gives every twin-linked weapon its own entry. Wherever a catalogue names a
  "Twin-linked <weapon>" and the weapons list has <weapon> but not the twin-linked one, it adds a "Twin-linked
  <weapon>" row to the "Twin-linked Weapons" section of `additional-weapons.md` (the weapon's profile plus the
  Twin-linked special rule), runs `add_gst_weapons.py` to put it in the game system, and points the options that
  show the twin-linked weapon (by name, or by carrying a separate Twin-linked rule) at the new entry. Running it
  again changes nothing.
- `homebrew/expansion_tools.py` holds what the expansion scripts below share: building the doc's units with the
  Builder, moving them into an official catalogue linked to the official entries wherever those exist, and editing
  the official file as text so it keeps its formatting.
- `python3 homebrew/add_sisters_of_silence.py` adds the Liber Imperatus Sisters of Silence expansion (the Claude Doc
  "Sisters of Silence Horus Heresy 2.0 - Homebrew Conversion", kept as `source/sisters-of-silence.md`) to
  `2022 - LI - Sisters Of Silence.cat`. build_catalogue.py's Builder reads the doc's datasheets; their units then
  move into the official file as text, linked to the official entries wherever the catalogue, its libraries or the
  game system already have them (Vratine Bolter, Execution Blade, Silent Sisterhood (X)), so only new weapons and
  wargear are added. Each unit carries its Chamber as the official units do (the Chamber's category and its
  required Silent Sisterhood (Chamber of X) entry; an Oblivion or Judgement HQ also counts as that Chamber's HQ),
  with the Anathema Sub-type. It also writes:
  - the root entries (vehicles and walkers hidden in a Zone Mortalis force, Sikari Dar and the Knight Ensign
    Covenant one per army) and the Dedicated Transports each datasheet names, by size;
  - the two-pistol swaps (one group of two pistols and one-pistol swaps, Perditor heavy weapons one in five; one
    group for swapping both, which empties the first), the Caedecii's Sinistrae Magnificat (one per unit, and no
    Spiculus Bolt Launcher or Vratine Missile Launcher on the model that has it);
  - Sikari Dar's Eater of Daemons Warlord Trait (the Warlord whenever she is in the Primary Detachment) and her two
    extra Fast Attack choices, which must be Pursuer Cadres and do not count toward the Chamber of Oblivion limit
    (the Crusade chart's Fast Attack maximum and the Chamber limit each rise by one per Pursuer Cadre, up to two);
  - the doc's extra options on official units (Indictor Axe for the Knight Abyssal, Knight Centura and Raptora;
    the Questora's and Eradicator's new Vratine Bolter swaps; Artificer Armour for Knight Vestals; Charnabal or
    Power Weapons for Subjugators) and the Silent Sisterhood Grav-Rhino and Rhino for the official Cadres that may
    take them, as an alternative to their Kharon Pattern Acquisitor, while they have no more than twelve models.
  It refuses to run on a catalogue that already has the expansion.
- `python3 homebrew/add_solar_auxilia.py` adds the Liber Imperatus Solar Auxilia expansion (the Claude Doc "Solar
  Auxilia Horus Heresy 2.0 - Homebrew Conversion", kept as `source/solar-auxilia.md`) to `2022 - LI - Solar
  Auxilia.cat`, after its three new rules (Advanced Weapons, Blitz Barrage, Concentrated Fire) are in
  `additional-special-rules.md` and the game system. The units take the official catalogue's names ("Breacher
  Section", not "Solar Auxilia Breacher Section"). It also writes:
  - the Breacher, Infantry Support, Carnodon, Light Armoured and Verticalis Drop Tercios as the official Tercios are
    built (one choice of up to three Sections; the Carnodon Tercio takes the official Carnodon Strike Squadrons),
    and the Sabre Battery (0-3) in the official Artillery Tercio;
  - the Sections' Dedicated Transports by size (Aurox or Termite up to ten models, Chimera up to twelve, Dracosan or
    Hades at any size; Arvus or Kelaino for the Verticalis Drop Sections), hidden in a Zone Mortalis force;
  - the eight new Cohort Doctrines in the official pick (Apostle only for a Traitor Detachment, Legion-Sworn only
    for an Allied one, Scourge never for an Allied one) with the slots they open (Possessed Auxilia, Furibundus,
    Extremis, Aethon, Hellhound, Infantry Support Tercio, Macharius, Aello), and the doc's additions to the Iron and
    Siege Pattern Cohorts' text;
  - the Armoured Fist, Dictatii (one per army, +1 BS and +2 Hull Points shown on the vehicle) and Ordnance Corps
    Marshals on the vehicles the doc names, one per model; the new Warlord Traits beside the official pick (Super-Heavy
    Armoured Legate only with Steel Fury Pattern Cohorts); Ireton MaSade's Master of the Battlefield, his Cohort
    Doctrines and his Extremis Warsuit with the Mechanised profile; the Battle Psyker's Core Psychic Discipline
    (Anathemata too with Apostle Pattern Cohorts); the Deathstrike's warhead and the Manticore's four missiles;
  - the extra options on official units: Companion and Tactical Command Section swaps and Heavy Void Armour for the
    whole unit, new Veletarii loadouts and Prime weapons, the Arvus Transport's hull weapon, Twin-Linked and Flare
    Shield, the Leman Russ Command Tank's turret, the Leman Russ Squadrons' turrets (per tank), the Macharius hull
    and sponson weapons, Dozer Blade and Flare Shield, the Malcador's side weapons and Siege Retrofit, and a second
    Valdor (235 points) with its centreline weapon.
  The doc's Aethon Heavy Sentinel Squadron is a Fast Attack unit of its own; the official Aethon entry is left as it
  is. Cohort Doctrine limits on unit counts and play are rule text only.
  It refuses to run on a catalogue that already has the expansion.
