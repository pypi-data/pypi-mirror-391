#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: player_service.py
Author: Maria Kevin
Created: 2025-11-13
Description: Service layer for music player business logic.
Isolates download, playback, and state management from GUI.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

import threading
from typing import Callable, Optional
from just_playback import Playback

from ..utils.download import get_or_download_audio
from ..utils.ffmpeg import is_default_ffmpeg_available, get_ffmpeg


class PlayerService:
    """Service class that handles all music player operations."""

    def __init__(self):
        self.playback: Optional[Playback] = None
        self.current_audio_path: Optional[str] = None
        self.is_playing: bool = False
        self._download_thread: Optional[threading.Thread] = None
        self._playback_thread: Optional[threading.Thread] = None

    def search_and_download(
        self,
        query: str,
        on_progress: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Search and download audio in a background thread.

        Args:
            query: Song name to search
            on_progress: Callback for progress updates (message)
            on_complete: Callback on success (query, file_path)
            on_error: Callback on error (error_message)
        """

        def _download():
            try:
                if on_progress:
                    on_progress(f"Searching for: {query}")

                # Check FFmpeg
                if not is_default_ffmpeg_available():
                    if on_progress:
                        on_progress("FFmpeg not found, downloading...")
                    ffmpeg_path = get_ffmpeg()
                    if not ffmpeg_path:
                        if on_error:
                            on_error("Failed to download FFmpeg")
                        return

                if on_progress:
                    on_progress(f"Downloading: {query}")

                audio_path = get_or_download_audio(query)

                if not audio_path:
                    if on_error:
                        on_error("Failed to download audio")
                    return

                self.current_audio_path = audio_path

                if on_complete:
                    on_complete(query, audio_path)

            except Exception as e:
                if on_error:
                    on_error(f"Error: {str(e)}")

        self._download_thread = threading.Thread(target=_download, daemon=True)
        self._download_thread.start()

    def load_and_play(
        self,
        audio_path: str,
        on_playback_start: Optional[Callable[[], None]] = None,
        on_playback_end: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Load and play audio file.

        Args:
            audio_path: Path to audio file
            on_playback_start: Callback when playback starts
            on_playback_end: Callback when playback ends
        """
        if self.playback:
            self.playback.stop()

        self.playback = Playback()
        self.playback.load_file(audio_path)
        self.playback.play()
        self.is_playing = True

        if on_playback_start:
            on_playback_start()

        def _monitor_playback():
            while self.playback and self.playback.active:
                pass
            self.is_playing = False
            if on_playback_end:
                on_playback_end()

        self._playback_thread = threading.Thread(
            target=_monitor_playback,
            daemon=True,
        )
        self._playback_thread.start()

    def toggle_pause(self) -> bool:
        """
        Toggle play/pause state.

        Returns:
            Current playing state after toggle
        """
        if not self.playback:
            return False

        if self.is_playing:
            self.playback.pause()
            self.is_playing = False
        else:
            self.playback.resume()
            self.is_playing = True

        return self.is_playing

    def get_current_time(self) -> float:
        """Get current playback position in seconds."""
        if self.playback and self.playback.active:
            return self.playback.curr_pos
        return 0.0

    def get_duration(self) -> float:
        """Get total duration in seconds."""
        if self.playback:
            return self.playback.duration
        return 0.0

    def seek(self, position: float) -> None:
        """Seek to position in seconds."""
        if self.playback:
            self.playback.seek(position)

    def stop(self) -> None:
        """Stop playback and cleanup."""
        if self.playback:
            self.playback.stop()
            self.playback = None
        self.is_playing = False

    def cleanup(self) -> None:
        """Cleanup resources."""
        self.stop()
        if self._download_thread and self._download_thread.is_alive():
            self._download_thread.join(timeout=1)
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1)
