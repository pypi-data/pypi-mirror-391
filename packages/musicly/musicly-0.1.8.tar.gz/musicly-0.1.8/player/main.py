#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Author: Maria Kevin
Created: 2025-11-09
Description: A terminal-based music player that allows users to search and
play songs directly from the command line.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from typer import Typer, Argument
from typing import Optional

from .gui.player import run_player

app = Typer()

# Default argument for name parameter
_DEFAULT_NAME_HELP = "The name of the song to play, example: 'All the stars'"
_ARGUMENT_NAME = Argument(None, help=_DEFAULT_NAME_HELP)


@app.command()
def play(
    name: Optional[str] = _ARGUMENT_NAME,
):
    """Play a song by name using the GUI player."""
    run_player(song_name=name)


if __name__ == "__main__":
    app()
