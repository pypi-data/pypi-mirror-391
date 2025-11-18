#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: __init__.py
Author: Maria Kevin
Created: 2025-11-13
Description: GUI package for the music player.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from .player import run_player, MusicPlayer
from .player_service import PlayerService

__all__ = ["run_player", "MusicPlayer", "PlayerService"]
