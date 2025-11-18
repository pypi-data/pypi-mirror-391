#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_ffmpeg.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for ffmpeg.py functions
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from unittest.mock import patch

from player.utils.ffmpeg import (
    get_ffmpeg,
    download_ffmpeg,
    is_default_ffmpeg_available,
)


class TestIsDefaultFfmpegAvailable:
    """Tests for is_default_ffmpeg_available function."""

    @patch("shutil.which")
    def test_ffmpeg_available(self, mock_which):
        """Test when ffmpeg is available in PATH."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        assert is_default_ffmpeg_available() is True

    @patch("shutil.which")
    def test_ffmpeg_not_available(self, mock_which):
        """Test when ffmpeg is not available in PATH."""
        mock_which.return_value = None
        assert is_default_ffmpeg_available() is False


class TestGetFfmpeg:
    """Tests for get_ffmpeg function."""

    @patch("player.utils.ffmpeg.config")
    @patch("os.path.exists")
    def test_ffmpeg_exists(self, mock_exists, mock_config):
        """Test get_ffmpeg when binary already exists."""
        mock_config.ffmpeg_paths = {"nt": "/path/to/ffmpeg.exe"}
        mock_exists.return_value = True

        with patch("os.name", "nt"):
            result = get_ffmpeg()
            assert result == "/path/to/ffmpeg.exe"

    @patch("player.utils.ffmpeg.download_ffmpeg")
    @patch("player.utils.ffmpeg.config")
    @patch("os.path.exists")
    def test_ffmpeg_needs_download(self, mock_exists, mock_config, mock_download):
        """Test get_ffmpeg when binary needs to be downloaded."""
        ffmpeg_path = "/path/to/ffmpeg.exe"
        mock_config.ffmpeg_paths = {"nt": ffmpeg_path}
        mock_exists.return_value = False

        with patch("os.name", "nt"):
            result = get_ffmpeg()
            mock_download.assert_called_once_with("nt")
            assert result == ffmpeg_path


class TestDownloadFfmpeg:
    """Tests for download_ffmpeg function."""

    @patch("player.utils.ffmpeg.clean_tools")
    @patch("player.utils.ffmpeg.unzip_file")
    @patch("player.utils.ffmpeg.download_with_chunk")
    @patch("player.utils.ffmpeg.config")
    @patch("os.makedirs")
    def test_successful_download(
        self, mock_makedirs, mock_config, mock_download, mock_unzip, mock_clean
    ):
        """Test successful ffmpeg download."""
        mock_config.ffmpeg_cloud_urls = {"nt": "https://example.com/ffmpeg.zip"}
        mock_config.ffmpeg_paths = {"nt": "/path/to/ffmpeg.exe"}
        mock_config.tools_dir = "/path/to/tools"

        result = download_ffmpeg("nt")

        assert result == "/path/to/ffmpeg.exe"
        mock_download.assert_called_once()
        mock_unzip.assert_called_once()
        mock_clean.assert_called_once_with("nt")

    @patch("player.utils.ffmpeg.config")
    def test_no_url_configured(self, mock_config):
        """Test download_ffmpeg when no URL is configured."""
        mock_config.ffmpeg_cloud_urls = {}
        result = download_ffmpeg("unknown_platform")
        assert result is None

    @patch("player.utils.ffmpeg.config")
    def test_no_path_configured(self, mock_config):
        """Test download_ffmpeg when no path is configured."""
        mock_config.ffmpeg_cloud_urls = {"nt": "https://example.com/ffmpeg.zip"}
        mock_config.ffmpeg_paths = {}
        result = download_ffmpeg("nt")
        assert result is None
