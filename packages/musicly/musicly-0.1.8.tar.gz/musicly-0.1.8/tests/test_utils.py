#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_utils.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for utils functions
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import tempfile
import zipfile
import tarfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the functions to test
from player.utils.url_helpers import (
    get_path_from_url,
    get_extension_from_url,
    download_with_chunk,
)
from player.utils.file_operations import (
    partial_search_file,
    unzip_file,
    get_first_folder_name,
    clean_tools,
    cleanup_download_dir,
)
from player.utils.ffmpeg import (
    get_ffmpeg,
    download_ffmpeg,
    is_default_ffmpeg_available,
)
from player.utils.download import download_audio


# ===========================
# URL Helpers Tests
# ===========================


class TestUrlHelpers:
    """Tests for url_helpers.py functions."""

    def test_get_path_from_url_valid(self):
        """Test extracting path from a valid URL."""
        url = "https://example.com/path/to/file.zip"
        result = get_path_from_url(url)
        assert result == "/path/to/file.zip"

    def test_get_path_from_url_no_path(self):
        """Test URL with no path."""
        url = "https://example.com"
        result = get_path_from_url(url)
        assert result == ""

    def test_get_path_from_url_with_query(self):
        """Test URL with query parameters."""
        url = "https://example.com/file.zip?param=value"
        result = get_path_from_url(url)
        assert result == "/file.zip"

    def test_get_extension_from_url_zip(self):
        """Test extracting .zip extension from URL."""
        url = "https://example.com/download/file.zip"
        result = get_extension_from_url(url)
        assert result == ".zip"

    def test_get_extension_from_url_tar_xz(self):
        """Test extracting .xz extension from URL."""
        url = "https://example.com/ffmpeg-release.tar.xz"
        result = get_extension_from_url(url)
        assert result == ".xz"

    def test_get_extension_from_url_no_extension(self):
        """Test URL with no file extension."""
        url = "https://example.com/file"
        result = get_extension_from_url(url)
        assert result in ["", None]

    def test_get_extension_from_url_no_path(self):
        """Test URL with no path."""
        url = "https://example.com"
        result = get_extension_from_url(url)
        assert result in [None, ""]

    @patch("urllib.request.urlopen")
    def test_download_with_chunk_success(self, mock_urlopen):
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
    def test_download_with_chunk_failure(self, mock_print, mock_urlopen):
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


# ===========================
# File Operations Tests
# ===========================


class TestFileOperations:
    """Tests for file_operations.py functions."""

    def test_partial_search_file_exact_match(self):
        """Test finding file with exact name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test_song.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song.mp3", tmpdir)
            assert result == test_file

    def test_partial_search_file_partial_match(self):
        """Test finding file with partial name match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file with modified name
            test_file = os.path.join(tmpdir, "test_song_modified_by_ytdlp.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song", tmpdir)
            assert result == test_file

    def test_partial_search_file_not_found(self):
        """Test when file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = partial_search_file("nonexistent.mp3", tmpdir)
            assert result is None

    def test_partial_search_file_subdirectory(self):
        """Test finding file in subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            test_file = os.path.join(subdir, "test_song.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song", tmpdir)
            assert result == test_file

    def test_unzip_file_windows_zip(self):
        """Test unzipping a .zip file (Windows)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test zip file
            zip_path = os.path.join(tmpdir, "test.zip")
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("test_file.txt", "test content")

            dest_path = os.path.join(tmpdir, "extracted")
            os.makedirs(dest_path)

            unzip_file(zip_path, dest_path, "nt")

            # Verify extraction
            extracted_file = os.path.join(dest_path, "test_file.txt")
            assert os.path.exists(extracted_file)
            assert not os.path.exists(zip_path)  # Source should be removed

    def test_unzip_file_posix_tar_xz(self):
        """Test unzipping a .tar.xz file (POSIX)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test tar.xz file
            tar_path = os.path.join(tmpdir, "test.tar.xz")
            inner_tar_path = os.path.join(tmpdir, "test.tar")

            # Create tar file first
            with tarfile.open(inner_tar_path, "w") as tf:
                test_content_file = os.path.join(tmpdir, "temp_content.txt")
                with open(test_content_file, "w") as f:
                    f.write("test content")
                tf.add(test_content_file, arcname="test_file.txt")

            # Compress with xz
            import lzma

            with open(inner_tar_path, "rb") as f_in:
                with lzma.open(tar_path, "wb") as f_out:
                    f_out.write(f_in.read())

            os.remove(inner_tar_path)

            dest_path = os.path.join(tmpdir, "extracted")
            os.makedirs(dest_path)

            unzip_file(tar_path, dest_path, "posix")

            # Verify extraction
            extracted_file = os.path.join(dest_path, "test_file.txt")
            assert os.path.exists(extracted_file)
            assert not os.path.exists(tar_path)  # Source should be removed

    def test_get_first_folder_name(self):
        """Test getting the first folder name in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some folders and files
            folder1 = os.path.join(tmpdir, "first_folder")
            folder2 = os.path.join(tmpdir, "second_folder")
            file1 = os.path.join(tmpdir, "file.txt")

            os.makedirs(folder1)
            os.makedirs(folder2)
            Path(file1).touch()

            result = get_first_folder_name(tmpdir)
            # Result should be one of the folders (order may vary)
            assert result in ["first_folder", "second_folder"]

    def test_get_first_folder_name_no_folders(self):
        """Test when no folders exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only files
            Path(os.path.join(tmpdir, "file1.txt")).touch()
            Path(os.path.join(tmpdir, "file2.txt")).touch()

            result = get_first_folder_name(tmpdir)
            assert result == ""

    @patch("player.utils.file_operations.config")
    def test_clean_tools_windows(self, mock_config):
        """Test cleaning tools directory on Windows."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config.tools_dir = tmpdir

            # Create directory structure mimicking ffmpeg extraction
            ffmpeg_folder = os.path.join(tmpdir, "ffmpeg-7.1-win64")
            bin_folder = os.path.join(ffmpeg_folder, "bin")
            os.makedirs(bin_folder)

            # Create files in bin folder
            ffmpeg_exe = os.path.join(bin_folder, "ffmpeg.exe")
            ffplay_exe = os.path.join(bin_folder, "ffplay.exe")
            Path(ffmpeg_exe).touch()
            Path(ffplay_exe).touch()

            clean_tools("nt")

            # Verify files were moved to tools_dir and folder was removed
            assert os.path.exists(os.path.join(tmpdir, "ffmpeg.exe"))
            assert os.path.exists(os.path.join(tmpdir, "ffplay.exe"))
            assert not os.path.exists(ffmpeg_folder)

    @patch("player.utils.file_operations.config")
    def test_clean_tools_posix(self, mock_config):
        """Test cleaning tools directory on POSIX systems."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config.tools_dir = tmpdir

            # Create directory structure mimicking ffmpeg extraction
            ffmpeg_folder = os.path.join(tmpdir, "ffmpeg-release-amd64")
            os.makedirs(ffmpeg_folder)

            # Create ffmpeg binary in the folder
            ffmpeg_bin = os.path.join(ffmpeg_folder, "ffmpeg")
            Path(ffmpeg_bin).touch()

            clean_tools("posix")

            # Verify ffmpeg was moved to tools_dir and folder was removed
            assert os.path.exists(os.path.join(tmpdir, "ffmpeg"))
            assert not os.path.exists(ffmpeg_folder)

    @patch("player.utils.file_operations.config")
    def test_cleanup_download_dir(self, mock_config):
        """Test cleaning up download directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            download_dir = os.path.join(tmpdir, "downloads")
            os.makedirs(download_dir)

            # Create some files
            Path(os.path.join(download_dir, "song1.mp3")).touch()
            Path(os.path.join(download_dir, "song2.mp3")).touch()

            mock_config.download_dir = download_dir

            cleanup_download_dir()

            # Verify directory was removed
            assert not os.path.exists(download_dir)

    @patch("player.utils.file_operations.config")
    def test_cleanup_download_dir_not_exists(self, mock_config):
        """Test cleanup when directory doesn't exist."""
        mock_config.download_dir = "/nonexistent/path"

        # Should not raise an error
        cleanup_download_dir()


# ===========================
# FFmpeg Tests
# ===========================


class TestFFmpeg:
    """Tests for ffmpeg.py functions."""

    @patch("shutil.which")
    def test_is_default_ffmpeg_available_true(self, mock_which):
        """Test when ffmpeg is available in PATH."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        assert is_default_ffmpeg_available() is True

    @patch("shutil.which")
    def test_is_default_ffmpeg_available_false(self, mock_which):
        """Test when ffmpeg is not available in PATH."""
        mock_which.return_value = None
        assert is_default_ffmpeg_available() is False

    @patch("player.utils.ffmpeg.config")
    @patch("os.path.exists")
    def test_get_ffmpeg_exists(self, mock_exists, mock_config):
        """Test get_ffmpeg when binary already exists."""
        mock_config.ffmpeg_paths = {"nt": "/path/to/ffmpeg.exe"}
        mock_exists.return_value = True

        with patch("os.name", "nt"):
            result = get_ffmpeg()
            assert result == "/path/to/ffmpeg.exe"

    @patch("player.utils.ffmpeg.download_ffmpeg")
    @patch("player.utils.ffmpeg.config")
    @patch("os.path.exists")
    def test_get_ffmpeg_download(self, mock_exists, mock_config, mock_download):
        """Test get_ffmpeg when binary needs to be downloaded."""
        ffmpeg_path = "/path/to/ffmpeg.exe"
        mock_config.ffmpeg_paths = {"nt": ffmpeg_path}
        mock_exists.return_value = False

        with patch("os.name", "nt"):
            result = get_ffmpeg()
            mock_download.assert_called_once_with("nt")
            assert result == ffmpeg_path

    @patch("player.utils.ffmpeg.clean_tools")
    @patch("player.utils.ffmpeg.unzip_file")
    @patch("player.utils.ffmpeg.download_with_chunk")
    @patch("player.utils.ffmpeg.config")
    @patch("os.makedirs")
    def test_download_ffmpeg_success(
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
    def test_download_ffmpeg_no_url(self, mock_config):
        """Test download_ffmpeg when no URL is configured."""
        mock_config.ffmpeg_cloud_urls = {}
        result = download_ffmpeg("unknown_platform")
        assert result is None

    @patch("player.utils.ffmpeg.config")
    def test_download_ffmpeg_no_path(self, mock_config):
        """Test download_ffmpeg when no path is configured."""
        mock_config.ffmpeg_cloud_urls = {"nt": "https://example.com/ffmpeg.zip"}
        mock_config.ffmpeg_paths = {}
        result = download_ffmpeg("nt")
        assert result is None


# ===========================
# Download Tests
# ===========================


class TestDownload:
    """Tests for download.py functions."""

    @patch("player.utils.download.partial_search_file")
    @patch("subprocess.run")
    @patch("player.utils.download.is_default_ffmpeg_available")
    @patch("player.utils.download.config")
    @patch("os.makedirs")
    def test_download_audio_success_default_ffmpeg(
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
    def test_download_audio_success_custom_ffmpeg(
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
    def test_download_audio_no_ffmpeg(
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
    def test_download_audio_subprocess_error(
        self, mock_makedirs, mock_config, mock_is_ffmpeg_available, mock_subprocess
    ):
        """Test download when subprocess fails."""
        mock_config.download_dir = "/downloads"
        mock_is_ffmpeg_available.return_value = True
        mock_subprocess.return_value = Mock(returncode=1, stderr="Download failed")

        result = download_audio("test song")

        assert result is None
