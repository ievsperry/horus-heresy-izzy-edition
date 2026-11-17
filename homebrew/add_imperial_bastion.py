#!/usr/bin/env python3
"""Add the Imperial Bastion (homebrew/source/imperial-fortifications.md) to 2022 - Horus Heresy.gst.

usage: python3 homebrew/add_imperial_bastion.py

It joins the four Imperial and Traitor Fortifications add_imperial_fortifications.py added, the same way: a
Fortification choice beside the game system's own, which faction_fortifications.py hides from the armies that may
not take Imperial Fortifications (IMPERIAL). It refuses to run twice."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import add_imperial_fortifications as aif  # noqa: E402

if __name__ == "__main__":
    aif.main(only=["Imperial Bastion"])
