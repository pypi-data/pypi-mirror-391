#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_download.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for download.py functions
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from unittest.mock import Mock, patch

from player.utils.download import download_audio


class TestDownloadAudio:
    """Tests for download_audio function."""

    @patch("player.utils.download.partial_search_file")
    @patch("subprocess.run")
    @patch("player.utils.download.is_default_ffmpeg_available")
    @patch("player.utils.download.config")
    @patch("os.makedirs")
    def test_success_with_default_ffmpeg(
        self,
        mock_makedirs,
        mock_config,
        mock_is_ffmpeg_available,
        mock_subprocess,
        mock_search,
    ):
        """Test successful audio download with default ffmpeg."""
        mock_config.download_dir = "/downloads"
        mock_is_ffmpeg_available.return_value = True
        mock_subprocess.return_value = Mock(returncode=0)
        mock_search.return_value = "/downloads/test_song.mp3"

        result = download_audio("test song")

        assert result == "/downloads/test_song.mp3"
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "yt-dlp" in call_args
        assert "ytsearch1:test song" in call_args
        assert "--ffmpeg-location" not in call_args

    @patch("player.utils.download.partial_search_file")
    @patch("subprocess.run")
    @patch("player.utils.download.get_ffmpeg")
    @patch("player.utils.download.is_default_ffmpeg_available")
    @patch("player.utils.download.config")
    @patch("os.makedirs")
    def test_success_with_custom_ffmpeg(
        self,
        mock_makedirs,
        mock_config,
        mock_is_ffmpeg_available,
        mock_get_ffmpeg,
        mock_subprocess,
        mock_search,
    ):
        """Test successful audio download with custom ffmpeg."""
        mock_config.download_dir = "/downloads"
        mock_is_ffmpeg_available.return_value = False
        mock_get_ffmpeg.return_value = "/custom/ffmpeg"
        mock_subprocess.return_value = Mock(returncode=0)
        mock_search.return_value = "/downloads/test_song.mp3"

        result = download_audio("test song")

        assert result == "/downloads/test_song.mp3"
        call_args = mock_subprocess.call_args[0][0]
        assert "--ffmpeg-location" in call_args
        assert "/custom/ffmpeg" in call_args

    @patch("builtins.print")
    @patch("player.utils.download.get_ffmpeg")
    @patch("player.utils.download.is_default_ffmpeg_available")
    @patch("player.utils.download.config")
    @patch("os.makedirs")
    def test_no_ffmpeg_available(
        self,
        mock_makedirs,
        mock_config,
        mock_is_ffmpeg_available,
        mock_get_ffmpeg,
        mock_print,
    ):
        """Test download when ffmpeg is not available."""
        mock_config.download_dir = "/downloads"
        mock_is_ffmpeg_available.return_value = False
        mock_get_ffmpeg.return_value = None

        result = download_audio("test song")

        assert result is None
        mock_print.assert_called_once()
        assert "FFmpeg not found" in str(mock_print.call_args)

    @patch("subprocess.run")
    @patch("player.utils.download.is_default_ffmpeg_available")
    @patch("player.utils.download.config")
    @patch("os.makedirs")
    def test_subprocess_error(
        self, mock_makedirs, mock_config, mock_is_ffmpeg_available, mock_subprocess
    ):
        """Test download when subprocess fails."""
        mock_config.download_dir = "/downloads"
        mock_is_ffmpeg_available.return_value = True
        mock_subprocess.return_value = Mock(returncode=1, stderr="Download failed")

        result = download_audio("test song")

        assert result is None
