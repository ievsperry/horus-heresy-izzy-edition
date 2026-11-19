#!/usr/bin/env python3
"""Add the Imperial Bastion and Grand Bastion (homebrew/source/imperial-fortifications.md) to 2022 - Horus Heresy.gst.

usage: python3 homebrew/add_imperial_bastion.py

They join the four Imperial and Traitor Fortifications add_imperial_fortifications.py added, the same way: a
Fortification choice beside the game system's own, which faction_fortifications.py hides from the armies that may
not take Imperial Fortifications (IMPERIAL). A Bastion the game system already has is left as it is."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_imperial_fortifications as aif  # noqa: E402

BASTIONS = ["Imperial Bastion", "Grand Bastion"]

if __name__ == "__main__":
    for name in BASTIONS:
        try:
            aif.main(only=[name])
        except SystemExit as e:  # already added
            print(e)
