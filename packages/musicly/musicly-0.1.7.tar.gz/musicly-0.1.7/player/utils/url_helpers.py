#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: url_helpers.py
Author: Maria Kevin
Created: 2025-11-12
Description: Basic URL helper functions.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import urllib.request
import urllib.parse


def get_path_from_url(url: str) -> str:
    """Get file path from URL."""
    parsed_url = urllib.parse.urlparse(url)
    return parsed_url.path if parsed_url.path else ""


def get_extension_from_url(url: str) -> str | None:
    """Get file extension from URL."""
    path = get_path_from_url(url)
    if not path:
        return None
    _, ext = os.path.splitext(path)
    return ext


def download_with_chunk(url, dest_path, chunk_size=8192):
    """Download file from URL with chunked reading."""
    try:
        with urllib.request.urlopen(url) as response:
            with open(dest_path, "wb") as out_file:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
    except Exception as e:
        print(f"Failed to download: {e}")
