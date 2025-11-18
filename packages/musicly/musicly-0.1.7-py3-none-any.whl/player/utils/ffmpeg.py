#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: ffmpeg.py
Author: Maria Kevin
Created: 2025-11-12
Description: FFmpeg binary management functions.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
from ..config import config
from .url_helpers import get_extension_from_url, download_with_chunk
from .file_operations import unzip_file, clean_tools
import shutil


def get_ffmpeg():
    """Download ffmpeg binary if not present."""
    platform_key = os.name  # 'nt' for Windows, 'posix' for Linux/Mac

    ffmpeg_path = config.ffmpeg_paths.get(platform_key)

    if ffmpeg_path and os.path.exists(ffmpeg_path):
        return ffmpeg_path

    download_ffmpeg(platform_key)

    return ffmpeg_path


def download_ffmpeg(platform_key: str) -> str | None:
    """Download ffmpeg binary from cloud URL."""
    url = config.ffmpeg_cloud_urls.get(platform_key)

    if not url:
        return None

    ffmpeg_path = config.ffmpeg_paths.get(platform_key)
    if not ffmpeg_path:
        return None

    os.makedirs(config.tools_dir, exist_ok=True)
    ext = get_extension_from_url(url)
    if not ext:
        ext = ".zip"  # default to .zip if extension cannot be determined
    temp_file_path = ffmpeg_path + ext

    download_with_chunk(url, temp_file_path)

    # unzip it and remove temp file, depending on the platform
    unzip_file(
        source_path=temp_file_path,
        dest_path=config.tools_dir,
        platform_key=platform_key,
    )

    clean_tools(platform_key)

    return ffmpeg_path


def is_default_ffmpeg_available() -> bool:
    """Check if the default ffmpeg is available in the system PATH."""
    return shutil.which("ffmpeg") is not None
