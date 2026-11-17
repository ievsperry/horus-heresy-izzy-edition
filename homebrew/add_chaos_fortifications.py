#!/usr/bin/env python3
"""Add the Chaos and Ruinstorm Fortifications (homebrew/source/chaos-fortifications.md) to 2022 - Horus Heresy.gst.

usage: python3 homebrew/add_chaos_fortifications.py

The doc's four Fortifications (Sacrificial Circle, Daemon Pit, Desecrated Stronghold, Warp-Flayer Turret Battery)
become Fortification choices in the game system beside its standard Fortifications, built the way
add_imperial_fortifications.py builds the Imperial ones (twin-linked weapons link the game system's own entries,
Reinforced Armoured Plating sets Armour 13 on the profile). Each is hidden in a Detachment that holds neither the
Traitor allegiance nor the Daemons of the Ruinstorm army entry. It refuses to run twice."""
import sys

sys.path.insert(0, "homebrew")
import add_imperial_fortifications as aif  # noqa: E402

DOC = "homebrew/source/chaos-fortifications.md"
VISIBLE = {"f9c0-0c5a-3e24-58c7": "Traitor", "afca-3047-fb26-d097": "Daemons of the Ruinstorm"}

if __name__ == "__main__":
    aif.main(DOC, "Chaos Fortifications", "chaos-fortifications", VISIBLE)
