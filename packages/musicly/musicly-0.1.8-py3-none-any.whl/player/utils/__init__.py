#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: __init__.py
Author: Maria Kevin
Created: 2025-11-12
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from .download import download_audio
from .ffmpeg import get_ffmpeg, download_ffmpeg
from .file_operations import (
    partial_search_file,
    unzip_file,
    clean_tools,
    get_first_folder_name,
    cleanup_download_dir,
)
from .url_helpers import (
    get_path_from_url,
    get_extension_from_url,
    download_with_chunk,
)


__all__ = [
    "download_audio",
    "get_ffmpeg",
    "download_ffmpeg",
    "partial_search_file",
    "unzip_file",
    "clean_tools",
    "get_first_folder_name",
    "get_path_from_url",
    "get_extension_from_url",
    "download_with_chunk",
    "cleanup_download_dir",
]
