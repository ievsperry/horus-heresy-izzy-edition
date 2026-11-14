Horus Heresy — Izzy Edition
===========================

Army-building data for **The Horus Heresy: Age of Darkness (2.0)**, for [New Recruit](https://www.newrecruit.eu/) and
BattleScribe. The game system is called **Horus Heresy - Izzy Juan (2026)**.

This repository is a fork of [BSData/horus-heresy](https://github.com/BSData/horus-heresy). It keeps the official
army lists, applies the Liber FAQs and errata, and adds:

- **14 homebrew armies**, from Adepta Sororitas to Tyranids;
- **expansions to the official armies**: new units, Rites of War, Advanced Reactions and Warlord Traits for the
  Daemons of the Ruinstorm, Titan Legions, Sisters of Silence, Solar Auxilia, Imperialis Militia, Mechanicum, Legio
  Custodes and the Legiones Astartes, and Corrupted Clade Assassins for Traitor armies;
- **house rules** that apply to every list.

It is maintained by the community for personal, non-commercial play, and is in no way endorsed by Games Workshop,
BattleScribe or New Recruit.

## Using the data

New Recruit is recommended; BattleScribe is no longer maintained.

- **Add it to your app** with this data index URL, which always points at the latest release:

  ```
  https://github.com/ievsperry/horus-heresy-izzy-edition/releases/latest/download/horus-heresy-izzy-edition.latest.bsi
  ```

  The app then offers each update as catalogue revisions go up.
- **Or download the files** from the [latest release](https://github.com/ievsperry/horus-heresy-izzy-edition/releases/latest):
  `catalogues.zip` holds every `.gst` and `.cat` file, and the `.bsr` file is a one-file download for BattleScribe.

Found a mistake, or want something added? [Open an issue](https://github.com/ievsperry/horus-heresy-izzy-edition/issues).

## What's in it

### Official armies

The `2022 - *.cat` files are the official lists, with the Liber FAQ, Errata and Balance Changes applied.

| Catalogue | Army |
| --- | --- |
| `2022 - Horus Heresy.gst` | The game system: core rules, weapons, Force Organisation charts, allegiances |
| `2022 - Legiones Astartes.cat` and `2022 - LA - <Legion>.cat` | The 18 Legions (Liber Astartes and Liber Hereticus) |
| `Shattered Legions.cat`, `2022 - BG - Blackshields.cat` | Shattered Legions and Blackshields |
| `2022 - Mechanicum.cat`, `2022 - Questoris Household.cat`, `2022 - Titan Legions.cat` | Liber Mechanicum, with `2022 - Mech Library.cat` |
| `2022 - LI - Solar Auxilia.cat`, `2022 - Imperialis Militia.cat`, `2022 - LI - Custodes.cat`, `2022 - LI - Sisters Of Silence.cat`, `2022 - LI - Assassins.cat` | Liber Imperium |
| `2022 - Daemons - Daemons of the Ruinstorm.cat`, `2022 - Daemons - Bound Daemons.cat` | Daemons, with `Daemon Library.cat` |

### Homebrew armies

Each `Homebrew - *.cat` file is built from its own conversion doc in [`homebrew/source`](homebrew/source).

| Catalogue | Allegiance | Source doc |
| --- | --- | --- |
| Adepta Sororitas | Loyalist or Traitor | `adepta-sororitas.md` |
| Aeldari (Anhrathe) | Xenos | `anhrathe.md` |
| Aeldari (Asuryani) | Xenos | `asuryani.md` |
| Aeldari (Drukhari) | Xenos | `drukhari.md` |
| Aeldari (Rillietann) | Xenos | `rillietann.md` |
| Armies of Dark Compliance | Traitor | built from the Imperialis Militia and Legiones Astartes lists |
| Astra Militarum | Loyalist or Traitor | `astra-militarum.md` |
| Grey Knights | Loyalist | `grey-knights.md` |
| Leagues of Votann | Loyalist, Traitor or Xenos | `leagues-of-votann.md` |
| Necrons | Xenos | `necrons.md` |
| Orks | Xenos | `orks.md` |
| T'au Empire | Xenos | `tau.md` |
| Traders Militant | Loyalist or Traitor | `traders-militant.md` |
| Tyranids | Xenos | `tyranids.md` |

The Xenos factions use a Xenos allegiance added to the game system.

### Expansions to the official armies

These docs add to an official catalogue rather than making a new one.

| Expansion | Adds to | Source doc | Script |
| --- | --- | --- | --- |
| Daemons of the Ruinstorm: new units, Daemonic Assassins, Ætheric Blessings, Rites of War | Daemons of the Ruinstorm | `ruinstorm.md` | `add_ruinstorm.py` |
| Ætheric Dominions, Advanced Reactions and Ruinstorm Warlord Traits | Daemon Library (every army that picks a Dominion), Daemons of the Ruinstorm | `ruinstorm.md` | `apply_ruinstorm_dominions.py` |
| Titan Legions: Moderati, Enginseers, Ballistarii, Titan Maniple, Rites of War | Titan Legions, Mech Library | `titan-legions.md` | `add_titan_legions.py` |
| Agents of the Warmaster: Corrupted Clade Assassins for Traitor Detachments | LI - Assassins and Agents, linked from every army that can take the Cults Abominatio | `corrupted-assassins.md` | `add_corrupted_assassins.py` |
| Sisters of Silence (Liber Imperatus) | LI - Sisters of Silence | `sisters-of-silence.md` | `add_sisters_of_silence.py` |
| Solar Auxilia (Liber Imperatus) | LI - Solar Auxilia | `solar-auxilia.md` | `add_solar_auxilia.py` |
| Imperialis Militia (Liber Imperatus) | Imperialis Militia | `imperialis-militia.md` | `add_imperialis_militia.py` |
| Liber Ingenium | Mechanicum, Questoris Household | `mechanicum.md` | `add_mechanicum.py` |
| Liber Centura | Legiones Astartes (every Legion) | `centura.md` | `add_centura.py` |
| Legio Custodes (Liber Imperatus) | LI - Custodes | `legio-custodes.md` | written into the catalogue directly |
| Saturnine Terminators, Dreadnought and Command Squad | Legiones Astartes | `saturnine.md` | `add_saturnine_command_squad.py` (the rest written directly) |
| Liber Izonian custom units | Several official catalogues | `custom-units.md` | `add_custom_units.py` |
| Liber Panoptica updates | Game system and official catalogues | `panoptica.md` | `apply_panoptica_update.py` |

### Game-system changes and house rules

- **Shared rules and weapons:** [`additional-special-rules.md`](homebrew/source/additional-special-rules.md) and
  [`additional-weapons.md`](homebrew/source/additional-weapons.md) hold the special rules and weapon profiles any
  catalogue may use, including optional rules such as Rapid Fire (X) and Line (X).
- **FAQs:** the Core Rulebook and Liber Panoptica FAQ, Errata and Balance Changes are applied to the game system and
  the official catalogues.
- **House rules:**
  - Smoke launchers (and Ork smoke bombz) work the same way in every list.
  - The Shattered Veil limits a Daemons of the Ruinstorm Allied Detachment.

The full list, with what each script does, is in the [homebrew README](homebrew/README.md).

## How the homebrew data is made

Each homebrew army and expansion starts as a conversion doc: a Claude Doc that people read and comment on. A copy of
the doc's text is kept as Markdown in [`homebrew/source`](homebrew/source), and that copy is what the scripts read.

1. Edit the doc, then export it to Markdown and replace its file in `homebrew/source`.
2. Rebuild the data from the repository root:
   - **A homebrew army:** `python3 homebrew/build_catalogue.py homebrew/source/tau.md "Homebrew - T'au Empire.cat"`.
     The builder reads the doc's datasheets, options, armoury, rules and Rites of War. Each unit's starting cost always
     matches the doc's points, and IDs come from entry names, so saved rosters keep loading. A faction can add its own
     army-building limits in a module named in `FACTION_LIMITS` (for example `tau_rites.py`).
   - **An expansion:** run its `add_*.py` script once. It builds the doc's units with the same builder, then writes
     them into the official catalogue as text, so the official file keeps its formatting. These scripts refuse to run
     twice; to redo one, start from the catalogue as it was before the expansion (the homebrew README says how for each).
3. Run the checks below and open a pull request. Don't hand-edit a built catalogue: the next rebuild overwrites it.

Every catalogue a change touches gets a higher `revision`, which is how New Recruit and BattleScribe know to update.

## Repository layout

```
*.gst, *.cat              the data files the apps load
homebrew/                 the scripts that build and change them
  build_catalogue.py      the builder: a conversion doc to a catalogue
  expansion_tools.py      shared machinery for the add_*.py expansion scripts
  add_*.py, apply_*.py    one script per expansion, FAQ or game-system change
  *_rites.py, *_limits.py army-building limits for one faction
  source/                 the conversion docs, as Markdown
  README.md               what every script and catalogue does, in detail
tests/                    New Recruit roster tests
.github/workflows/        validation, tests and releases
.github/scripts/          publish_catpkg.py, which builds the release files
raw/                      reference data (books.json)
```

## Checks

Every push and pull request runs two GitHub Actions:

- **Datafile Basic Validity** parses every `.gst`, `.cat` and `.cattemplate` file as XML. To run it locally:

  ```bash
  python3 -c "from pathlib import Path; from xml.etree import ElementTree as E; fs=[p for g in ('*.cat','*.gst','*.cattemplate') for p in Path('.').glob(g)]; [E.parse(f) for f in fs]; print('Validated', len(fs), 'datafiles')"
  ```

- **Test in New Recruit** loads the rosters in [`tests`](tests) in New Recruit and checks their results. To add a test:
  1. Export a roster from New Recruit or BattleScribe.
  2. Rename it from `.ros` to `.test` and put it in [`tests`](tests).
  3. Add a case to [`tests.py`](tests/tests.py):

     ```python
     def test_NameOfTest(self):
         self.load_list('Name of Roster file with no extension')
         errors = self.get_error_list()
         self.assertEqual(0, len(errors), "This list has validation errors")
     ```

     Other checks, such as the points of a unit, are in the same file.
  4. Open a pull request to have GitHub run it, or run it locally with Python, `selenium`, `webdriver-manager` and
     Google Chrome.

## Releases

1. Push a tag starting with `v` (for example `v2.1.13`). **Release Datafiles** makes a GitHub release with
   `catalogues.zip`.
2. Publishing or editing a release runs **Publish catpkg**, which attaches what the apps update from:
   - a `.catz` or `.gstz` for each data file;
   - the repository description (`horus-heresy-izzy-edition.catpkg.json`);
   - the data index (`.latest.bsi` and `.<tag>.bsi`);
   - a one-file `.bsr` download.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for editing the data in the BattleScribe Data Editor, and the
[pull request template](pull_request_template.md) for what a pull request should describe. Homebrew changes go
through the conversion docs and scripts above, not by hand.

### Standards for the official data

These come from the BSData project and still apply.

- **Names:** remove the "Legion" prefix from units, unless the unit has a non-Legion equivalent (Legion Baneblade).
- **Units and models:** every unit has a unit entry with a model entry inside it, even a single-model unit, so model
  counts stay accurate.
- **Visibility:**
  - Units are hidden by default, with a modifier setting Hidden to False when the force has the matching selection
    (with "all child selections" checked).
  - Upgrades are shown by default, with a modifier hiding them when the "off" condition is selected.
- **Rites of War:** Solar Auxilia and Imperialis Militia units carry the "SA or IM Unit" category for Rites that
  count them; Lords of War do not.
- **`.cattemplate` files** were used with [BSCopy](https://github.com/nstephenh/BSCopy) to copy the first Legion to
  all 18. The template is not maintained, so re-running BSCopy is not recommended.

## Sources and licences

- **Official books:** The Horus Heresy: Age of Darkness Rulebook, Liber Astartes, Liber Hereticus, Liber Mechanicum
  and Liber Imperium, with their FAQ and Errata documents, the Legacies of the Age of Darkness PDFs and the Exemplary
  Battles PDFs published by Warhammer Community (links below).
- **Liber Panoptica:** the conversions from its supplements (Liber Imperatus, Liber Ingenium, Liber Antiquia and
  others) are licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). These reworked
  versions are for personal, non-commercial playtesting.
- **Other homebrew armies** are adapted from earlier Warhammer 40,000 editions. Their points and profiles are
  playtest values; each doc's Sources section says where it comes from.
- **Upstream:** the original data is from the [BSData](https://www.bsdata.net/) community. The 1st edition data is in
  [BSData/horus-heresy-1e](https://github.com/BSData/horus-heresy-1e).

<details>
<summary>Reference documents</summary>

* Horus Heresy: Age of Darkness Rulebook
* [Warhammer: The Horus Heresy – Age of Darkness Rulebook Errata and FAQ V1.2](https://assets.warhammer-community.com/horusheresy_faqs&errata_rulebook_eng_24.09-mx5kndri3o.pdf)
* Liber Astartes (Book)
* Liber Hereticus (Book)
* "Both Astartes Army books" refers to the first section of both of the above books, as they are identical
* Liber Mechanicum (Book)
* Liber Imperium (Book)
* [Liber Astartes Errata and FAQ V1.2](https://assets.warhammer-community.com/horusheresy_faqs&errata_liberastartes_eng_24.09-oytusbjk5r.pdf)
* [Liber Hereticus Errata and FAQ V1.2](https://assets.warhammer-community.com/horusheresy_faqs&errata_liberhereticus_eng_24.09-exfs3zjfaw.pdf)
* [Liber Mechanicum Errata and FAQ V1.1](https://assets.warhammer-community.com/horusheresy_faqs&errata_libermechanicum_eng_24.09-ngyszpxnmn.pdf)
* [Liber Imperium Errata and FAQ V1.1](https://assets.warhammer-community.com/horusheresy_faqs&errata_liberimperium_eng_24.09-sgghybudv2.pdf)
* [The Siege of Cthonia V1.0](https://assets.warhammer-community.com/horusheresy_faqs&errata_siegeofcthonia_eng_24.09-684ujhnvfl.pdf)
* [Warsmith Dominus](https://assets.warhammer-community.com/horusheresy_additionalrules_warsmith_dominus_eng-9ngn2fiegx-mt2z5uei0r.pdf)
* [Ka'bandha](https://assets.warhammer-community.com/horusheresy_additionalrules_ka'bandha_eng_24.09-qn4rwnyoca.pdf)
* [Legion Javelin](https://assets.warhammer-community.com/horusheresy_additionalrules_legionjavelinsquadron_eng_24.09-hgogyoypdg.pdf)
* [Arvus Lighter](https://assets.warhammer-community.com/horusheresy_additionalrules_arvus_lighter_eng_05-jjogiky2h4-t4zpnlxhei.pdf)
* [Legion Mastodon](https://assets.warhammer-community.com/horusheresy_additionalrules_legionmastodon_eng_24.09-c0kpx1cgno.pdf)
* [Legacies of The Age of Darkness Legions v1.3 PDF](https://assets.warhammer-community.com/dave-s-downloads-25-09/horusheresy_legaciesoftheageofdarkness_legionesastartes_eng_24.09.23.pdf)
* [Legacies of The Age of Darkness: Imperialis Militia V1.1](https://assets.warhammer-community.com/horusheresy_legaciesoftheageofdarkness_imperialismilitia_eng_24.09-tyq53ht49b.pdf)
* [Legacies of The Age of Darkness: Mechanicum v1.0 PDF](https://assets.warhammer-community.com/horusheresy_legaciesoftheageofdarkness_mechanicum_eng_24.09-odihunq81s.pdf)
* [Legacies of The Age of Darkness: Daemons of the Ruinstorm V1.0](https://assets.warhammer-community.com/horusheresy_legaciesoftheageofdarkness_daemonsoftheruinstorm_eng_24.09-lufp0xm3vt.pdf)
* [Legacies of The Age of Darkness: Solar Auxilia V1.1](https://assets.warhammer-community.com/horusheresy_legaciesoftheageofdarkness_solarauxilia_eng_24.09-ws4kir7amo.pdf)
* [Exemplary Battles of the Age of Darkness: The Axandria IV Incident](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thealexandriaivincident_eng_24.09-2q9tvfdyql.pdf) 
* [Exemplary Battles of the Age of Darkness: The Depths of Tredecimmia](https://assets.warhammer-community.com/dave-s-downloads-25-09/horusheresy_exemplarybattles_thedepthsoftredecimmia_eng_24.09.23.pdf)
* [Exemplary Battles of the Age of Darkness: Liberation of Constanix II](https://assets.warhammer-community.com/horusheresy_exemplarybattles_liberationofconstanixii_eng_24.09-xn2k0tfbto.pdf)
* [Exemplary Battles of the Age of Darkness: The Burning of Ohmn-Mat](https://assets.warhammer-community.com/horusheresy_exemplarybattles_theburningofohmn-mat_eng_24-vno3sfye0y.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Trisolian: Vengeful Spirit](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebattleoftrisolian_vengefulspirit_eng_24.09-frcwsgxbix.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Felweather Keep](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebattleforfelweatherkeep_eng_24.09-oqvigqdtrz.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Kalium Gate](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebattleforkaliumgate_eng_24.09-ygtmebjf82.pdf)
* [Exemplary Battles of the Age of Darkness: The Scouring of Gilden's Star](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thescouringofgilden'sstar_eng_24.09-cgf4kmmr28.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Nyrcon City](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebattleofnyrconcity_eng_24.09-euuqt6gegh.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Perditus Umbral-51](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebattleofperditusumbral51_eng_24.09-g3s1261myg.pdf)
* [Exemplary Battles of the Age of Darkness: The Breaking of the Perfect Fortress](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thebreakingoftheperfectfortress_eng_24.09-5ds3vom7i0.pdf)
* [Exemplary Battles of the Age of Darkness: Assault On Castrum Velx](https://assets.warhammer-community.com/horusheresy_exemplarybattles_assaultoncastrumvelx_eng_24.09-qjasoqqvgz.pdf)
* [Exemplary Battles of the Age of Darkness: The Death of Conopus](https://assets.warhammer-community.com/horusheresy_exemplarybattles_thedeathofcanopus_eng_24.09-yq4yzvecwa.pdf)
* [Exemplary Battles of the Age of Darkness: The Battle of Pluto: Hydra's Devestation](https://assets.warhammer-community.com/dave-s-downloads-25-09/horusheresy_exemplarybattles_thebattieofpluto_hydra'sdevestation_eng_24.09.pdf)
* [Exemplary Battles of Age of Darkness: Unit Update v1.1 PDF](https://assets.warhammer-community.com/horusheresy_exemplarybattles_exemplarybattlesunitupdate_eng_24.09-zvqxjklhwo.pdf)

</details>
