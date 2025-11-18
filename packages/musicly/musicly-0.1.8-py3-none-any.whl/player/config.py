#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: config.py
Author: Maria Kevin
Created: 2025-11-12
Description: Configuration settings for the music player.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"
import os
from platformdirs import user_data_dir

appname = "musicly"


parent_data_dir = user_data_dir(appname, ensure_exists=True)


class Config(object):
    def __init__(self):
        self.download_dir = os.path.join(parent_data_dir, "downloads")

        self.tools_dir = os.path.join(parent_data_dir, "tools")

        self.ffmpeg_paths = {
            "nt": os.path.join(parent_data_dir, "tools", "ffmpeg.exe"),
            "posix": os.path.join(parent_data_dir, "tools", "ffmpeg"),
        }

        self.ffmpeg_cloud_urls = {
            "nt": (
                "https://github.com/BtbN/FFmpeg-Builds/releases/download/"
                "latest/ffmpeg-n7.1-latest-win64-lgpl-shared-7.1.zip"
            ),
            "posix": (
                "https://johnvansickle.com/ffmpeg/releases/"
                "ffmpeg-release-amd64-static.tar.xz"
            ),
        }


config = Config()
