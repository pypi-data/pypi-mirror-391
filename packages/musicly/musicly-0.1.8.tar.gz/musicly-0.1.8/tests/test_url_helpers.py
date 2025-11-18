#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_url_helpers.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for URL helper functions
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import tempfile
from unittest.mock import Mock, MagicMock, patch

from player.utils.url_helpers import (
    get_path_from_url,
    get_extension_from_url,
    download_with_chunk,
)


class TestGetPathFromUrl:
    """Tests for get_path_from_url function."""

    def test_valid_url(self):
        """Test extracting path from a valid URL."""
        url = "https://example.com/path/to/file.zip"
        result = get_path_from_url(url)
        assert result == "/path/to/file.zip"

    def test_no_path(self):
        """Test URL with no path."""
        url = "https://example.com"
        result = get_path_from_url(url)
        assert result == ""

    def test_with_query_params(self):
        """Test URL with query parameters."""
        url = "https://example.com/file.zip?param=value"
        result = get_path_from_url(url)
        assert result == "/file.zip"


class TestGetExtensionFromUrl:
    """Tests for get_extension_from_url function."""

    def test_zip_extension(self):
        """Test extracting .zip extension from URL."""
        url = "https://example.com/download/file.zip"
        result = get_extension_from_url(url)
        assert result == ".zip"

    def test_tar_xz_extension(self):
        """Test extracting .xz extension from URL."""
        url = "https://example.com/ffmpeg-release.tar.xz"
        result = get_extension_from_url(url)
        assert result == ".xz"

    def test_no_extension(self):
        """Test URL with no file extension."""
        url = "https://example.com/file"
        result = get_extension_from_url(url)
        assert result == ""

    def test_no_path(self):
        """Test URL with no path."""
        url = "https://example.com"
        result = get_extension_from_url(url)
        assert result is None


class TestDownloadWithChunk:
    """Tests for download_with_chunk function."""

    @patch("urllib.request.urlopen")
    def test_successful_download(self, mock_urlopen):
        """Test successful chunked download."""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.side_effect = [b"chunk1", b"chunk2", b""]
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            download_with_chunk("https://example.com/file", tmp_path)

            # Verify file was written
            with open(tmp_path, "rb") as f:
                content = f.read()
                assert content == b"chunk1chunk2"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @patch("urllib.request.urlopen")
    @patch("builtins.print")
    def test_download_failure(self, mock_print, mock_urlopen):
        """Test download failure handling."""
        mock_urlopen.side_effect = Exception("Network error")

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            download_with_chunk("https://example.com/file", tmp_path)
            mock_print.assert_called_once()
            assert "Failed to download" in str(mock_print.call_args)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
