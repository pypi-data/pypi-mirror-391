#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_file_operations.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for file_operations.py functions
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import os
import tarfile
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from player.utils.file_operations import (
    partial_search_file,
    unzip_file,
    get_first_folder_name,
    clean_tools,
    cleanup_download_dir,
)


class TestPartialSearchFile:
    """Tests for partial_search_file function."""

    def test_exact_match(self):
        """Test finding file with exact name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test_song.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song.mp3", tmpdir)
            assert result == test_file

    def test_partial_match(self):
        """Test finding file with partial name match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file with modified name
            test_file = os.path.join(tmpdir, "test_song_modified_by_ytdlp.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song", tmpdir)
            assert result == test_file

    def test_not_found(self):
        """Test when file is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = partial_search_file("nonexistent.mp3", tmpdir)
            assert result is None

    def test_in_subdirectory(self):
        """Test finding file in subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            test_file = os.path.join(subdir, "test_song.mp3")
            Path(test_file).touch()

            result = partial_search_file("test_song", tmpdir)
            assert result == test_file


class TestUnzipFile:
    """Tests for unzip_file function."""

    def test_windows_zip(self):
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

    def test_posix_tar_xz(self):
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


class TestGetFirstFolderName:
    """Tests for get_first_folder_name function."""

    def test_with_folders(self):
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

    def test_no_folders(self):
        """Test when no folders exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only files
            Path(os.path.join(tmpdir, "file1.txt")).touch()
            Path(os.path.join(tmpdir, "file2.txt")).touch()

            result = get_first_folder_name(tmpdir)
            assert result == ""


class TestCleanTools:
    """Tests for clean_tools function."""

    @patch("player.utils.file_operations.config")
    def test_windows(self, mock_config):
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
    def test_posix(self, mock_config):
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


class TestCleanupDownloadDir:
    """Tests for cleanup_download_dir function."""

    @patch("player.utils.file_operations.config")
    def test_cleanup_existing_dir(self, mock_config):
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
    def test_cleanup_nonexistent_dir(self, mock_config):
        """Test cleanup when directory doesn't exist."""
        mock_config.download_dir = "/nonexistent/path"

        # Should not raise an error
        cleanup_download_dir()
