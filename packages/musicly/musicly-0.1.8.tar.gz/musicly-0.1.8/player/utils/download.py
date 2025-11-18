#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: download.py
Author: Maria Kevin
Created: 2025-11-12
Description: Download audio using YT-DLP.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import subprocess
from ..config import config
from .ffmpeg import get_ffmpeg, is_default_ffmpeg_available
from .file_operations import partial_search_file


def download_audio(name: str):
    """Download audio by name using YT-DLP."""

    # Create download directory if it doesn't exist
    os.makedirs(config.download_dir, exist_ok=True)

    # yt-dlp ytsearch1:"Artist - Track Name" -x --audio-format mp3
    # -o "%(title)s.%(ext)s"
    path = f"{name}.mp3"
    full_path = os.path.join(config.download_dir, path)
    cmd = [
        "yt-dlp",
        f"ytsearch1:{name}",
        "-x",
        "--audio-format",
        "mp3",
    ]

    # Conditionally append ffmpeg location if available
    if not is_default_ffmpeg_available():
        custom_ffmpeg_location = get_ffmpeg()
        if custom_ffmpeg_location:
            cmd.extend(["--ffmpeg-location", custom_ffmpeg_location])
        else:
            print("FFmpeg not found. Please install FFmpeg to proceed.")
            return None

    cmd.extend(["-o", full_path])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error downloading audio: {result.stderr}")
        return None

    return partial_search_file(path, config.download_dir)


def get_existing_audio(name: str) -> str | None:
    """Check if audio file already exists for the given name."""
    path = f"{name}.mp3"
    return partial_search_file(path, config.download_dir)


def get_or_download_audio(name: str) -> str | None:
    """Get existing audio file or download if not found."""
    existing_file = get_existing_audio(name)
    if existing_file:
        return existing_file
    return download_audio(name)
