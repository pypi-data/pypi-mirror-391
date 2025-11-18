#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: file_operations.py
Author: Maria Kevin
Created: 2025-11-12
Description: File operations including search, extraction, and cleanup.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import shutil
import zipfile
from ..config import config


def partial_search_file(filename: str, search_path: str) -> str | None:
    """Partial filename search in a given path.

    Sometimes yt-dlp may alter the filename slightly, so we search for a
    partial match.
    """
    for root, _dirs, files in os.walk(search_path):
        for file in files:
            if filename in file:
                return os.path.join(root, file)
    return None


def unzip_file(source_path: str, dest_path: str, platform_key: str):
    """Unzip the downloaded ffmpeg file."""

    if platform_key == "nt":
        # Windows - assume zip file
        with zipfile.ZipFile(source_path, "r") as zip_ref:
            zip_ref.extractall(dest_path)
    else:
        # POSIX - assume tar.xz file
        import tarfile

        with tarfile.open(source_path, "r:xz") as tar_ref:
            tar_ref.extractall(dest_path)

    os.remove(source_path)


def get_first_folder_name(path: str) -> str:
    """Get the first folder name in the given path."""
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            return item
    return ""


def clean_tools(platform_key: str):
    """Clean up the tools directory by having only ffmpeg binary."""
    if platform_key == "nt":
        folder_path = os.path.join(
            config.tools_dir, get_first_folder_name(config.tools_dir)
        )
        # have only the bin folder, copy those files to tools dir, delete all
        bin_path = os.path.join(folder_path, "bin")
        # copy all the files in this bin folder to tools dir
        for item in os.listdir(bin_path):
            s = os.path.join(bin_path, item)
            d = os.path.join(config.tools_dir, item)
            if os.path.isdir(s):
                continue
            else:
                os.replace(s, d)
        shutil.rmtree(folder_path)

    elif platform_key == "posix":
        folder_path = os.path.join(
            config.tools_dir, get_first_folder_name(config.tools_dir)
        )
        # ffmpeg binary is directly inside this folder
        ffmpeg_source_path = os.path.join(folder_path, "ffmpeg")
        ffmpeg_dest_path = os.path.join(config.tools_dir, "ffmpeg")
        os.replace(ffmpeg_source_path, ffmpeg_dest_path)
        shutil.rmtree(folder_path)


def cleanup_download_dir():
    """Clean up the temporary directory."""
    if os.path.exists(config.download_dir):
        shutil.rmtree(config.download_dir)
