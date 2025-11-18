#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: player.py
Author: Maria Kevin
Created: 2025-11-13
Description: Textual user interface for the player module.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Static, Button, Input, ProgressBar
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from typing import Optional

from .player_service import PlayerService


class MusicPlayer(App):
    CSS_PATH = "gui.tcss"

    BINDINGS = [
        Binding(key="space", action="toggle_pause", description="Play/Pause"),
        Binding(key="left", action="skip_backward", description="-10s"),
        Binding(key="right", action="skip_forward", description="+10s"),
        Binding(key="l", action="toggle_loop", description="Loop"),
        Binding(key="s", action="focus_search", description="Search"),
        Binding(key="q", action="quit", description="Quit"),
    ]

    is_playing = reactive(False)
    current_time = reactive(0)
    total_time = reactive(180)  # 3 minutes default
    status_message = reactive("No Song Playing")
    is_downloading = reactive(False)
    download_progress = reactive(0)
    loop_enabled = reactive(False)

    def __init__(self, initial_query: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_service = PlayerService()
        self.initial_query = initial_query
        self._update_timer = None
        self._download_timer = None

    def compose(self) -> ComposeResult:
        with Container(id="player-container"):
            yield Static(self.status_message, id="title")
            yield Static("0:00 / 0:00", id="duration")
            with Horizontal(id="progress-container"):
                yield ProgressBar(
                    total=100,
                    show_eta=False,
                    show_percentage=False,
                    show_bar=True,
                    id="progress",
                )
            with Horizontal(id="controls"):
                yield Button("▶", id="pause-btn", variant="primary")
                yield Button("🔁", id="loop-btn", variant="default")
            with Horizontal(id="search-container"):
                yield Input(
                    placeholder="Search for a song...",
                    id="search-input",
                )
                yield Button("⏎", id="search-btn", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#progress", ProgressBar).update(progress=0)

        # If initial query provided, search automatically
        if self.initial_query:
            self.status_message = f"Searching: {self.initial_query}"
            self.update_status_display()
            self.start_download(self.initial_query)

        # Start update timer
        self.set_interval(0.5, self.update_playback_position)

        # Update loop button appearance
        self.update_loop_button()

    def action_toggle_pause(self) -> None:
        """Toggle play/pause."""
        # If song ended, restart playback
        playback = self.player_service.playback
        if playback and not playback.active:
            if self.player_service.current_audio_path:
                self.player_service.load_and_play(
                    audio_path=self.player_service.current_audio_path,
                    on_playback_start=self.on_playback_start,
                    on_playback_end=self.on_playback_end,
                )
        else:
            new_state = self.player_service.toggle_pause()
            self.is_playing = new_state
            btn = self.query_one("#pause-btn", Button)
            btn.label = "⏸" if self.is_playing else "▶"

    def action_focus_search(self) -> None:
        """Focus on search input."""
        self.query_one("#search-input", Input).focus()

    def action_skip_backward(self) -> None:
        """Skip backward by 10 seconds."""
        self.skip_backward()

    def action_skip_forward(self) -> None:
        """Skip forward by 10 seconds."""
        self.skip_forward()

    def action_toggle_loop(self) -> None:
        """Toggle loop mode."""
        self.toggle_loop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "pause-btn":
            self.action_toggle_pause()
        elif event.button.id == "search-btn":
            self.search_song()
        elif event.button.id == "loop-btn":
            self.toggle_loop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "search-input":
            self.search_song()

    def search_song(self) -> None:
        """Search and download a song."""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()
        if query:
            search_input.value = ""
            search_input.blur()
            self.start_download(query)

    def start_download(self, query: str) -> None:
        """Start downloading a song."""
        self.status_message = f"Searching: {query}"
        self.is_downloading = True
        self.download_progress = 0

        # Reset progress bar explicitly
        progress = self.query_one("#progress", ProgressBar)
        progress.update(total=100, progress=0)

        self.update_status_display()
        self.update_download_display()

        # Start fake progress animation (5-6 seconds)
        if self._download_timer:
            self._download_timer.stop()
        self._download_timer = self.set_interval(0.1, self.update_download_progress)

        self.player_service.search_and_download(
            query=query,
            on_progress=self.on_download_progress,
            on_complete=self.on_download_complete,
            on_error=self.on_download_error,
        )

    def on_download_progress(self, message: str) -> None:
        """Handle download progress updates."""
        self.status_message = message
        self.call_from_thread(self.update_status_display)

    def on_download_complete(self, query: str, audio_path: str) -> None:
        """Handle successful download."""
        self.is_downloading = False
        self.download_progress = 100
        self.status_message = f"♪ {query}"

        # Stop download timer
        if self._download_timer:
            self._download_timer.stop()
            self._download_timer = None

        self.call_from_thread(self.update_status_display)
        self.call_from_thread(self.update_download_display)

        # Start playback
        self.player_service.load_and_play(
            audio_path=audio_path,
            on_playback_start=self.on_playback_start,
            on_playback_end=self.on_playback_end,
        )

    def on_download_error(self, error_message: str) -> None:
        """Handle download errors."""
        self.is_downloading = False
        self.status_message = f"Error: {error_message}"

        # Stop download timer
        if self._download_timer:
            self._download_timer.stop()
            self._download_timer = None

        self.call_from_thread(self.update_status_display)
        self.call_from_thread(self.update_download_display)

    def on_playback_start(self) -> None:
        """Handle playback start."""
        self.is_playing = True
        self.call_from_thread(self.update_button_state)

    def on_playback_end(self) -> None:
        """Handle playback end."""
        self.is_playing = False
        self.call_from_thread(self.update_button_state)

        # If loop enabled, restart playback
        if self.loop_enabled and self.player_service.current_audio_path:
            self.player_service.load_and_play(
                audio_path=self.player_service.current_audio_path,
                on_playback_start=self.on_playback_start,
                on_playback_end=self.on_playback_end,
            )

    def update_button_state(self) -> None:
        """Update play/pause button state."""
        btn = self.query_one("#pause-btn", Button)
        btn.label = "⏸" if self.is_playing else "▶"

    def update_status_display(self) -> None:
        """Update status/title display."""
        title = self.query_one("#title", Static)
        title.update(self.status_message)

    def toggle_loop(self) -> None:
        """Toggle loop mode."""
        self.loop_enabled = not self.loop_enabled
        self.update_loop_button()

    def update_loop_button(self) -> None:
        """Update loop button appearance."""
        btn = self.query_one("#loop-btn", Button)
        if self.loop_enabled:
            btn.variant = "success"
        else:
            btn.variant = "default"

    def skip_backward(self) -> None:
        """Skip backward by 10 seconds."""
        if self.player_service.playback and self.is_playing:
            current = self.player_service.get_current_time()
            new_time = max(0, current - 10)
            self.player_service.seek(new_time)

    def skip_forward(self) -> None:
        """Skip forward by 10 seconds."""
        if self.player_service.playback and self.is_playing:
            current = self.player_service.get_current_time()
            duration = self.player_service.get_duration()
            new_time = min(duration, current + 10)
            self.player_service.seek(new_time)

    def update_download_progress(self) -> None:
        """Update fake download progress (simulates 5-6 second download)."""
        if self.is_downloading and self.download_progress < 95:
            # Increment by ~1.7r every 0.1s = ~6 seconds to reach 95%
            self.download_progress = min(95, self.download_progress + 1.7)
            self.update_download_display()

    def update_download_display(self) -> None:
        """Update display to show download progress or playback progress."""
        if self.is_downloading:
            # Show download progress with time format
            duration = self.query_one("#duration", Static)
            progress = self.query_one("#progress", ProgressBar)

            # Calculate fake time based on progress (10 sec total)
            elapsed_sec = int((self.download_progress / 100) * 10)
            duration.update(f"{elapsed_sec}s")
            progress.update(total=100, progress=int(self.download_progress))
        else:
            # Show playback progress
            self.update_display()

    def update_playback_position(self) -> None:
        """Update playback position periodically."""
        if not self.is_downloading:
            if self.player_service.playback and self.is_playing:
                self.current_time = int(self.player_service.get_current_time())
                self.total_time = int(self.player_service.get_duration())

                if self.total_time > 0:
                    self.update_display()

    def update_display(self) -> None:
        """Update duration and progress bar."""
        duration = self.query_one("#duration", Static)
        progress = self.query_one("#progress", ProgressBar)

        current_min = self.current_time // 60
        current_sec = self.current_time % 60
        total_min = self.total_time // 60
        total_sec = self.total_time % 60

        duration.update(
            f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}"
        )

        # Update progress bar based on playback position
        if self.total_time > 0:
            playback_progress = (self.current_time / self.total_time) * 100
            progress.update(total=100, progress=int(playback_progress))

    def on_shutdown_request(self, event) -> None:
        """Cleanup on shutdown."""
        self.player_service.cleanup()

    def action_quit(self) -> None:
        """Quit the app."""
        self.player_service.cleanup()
        self.exit()


def run_player(song_name: Optional[str] = None) -> None:
    """Run the music player GUI.

    Args:
        song_name: Optional song name to search and play immediately
    """
    app = MusicPlayer(initial_query=song_name)
    app.run()


if __name__ == "__main__":
    run_player()
