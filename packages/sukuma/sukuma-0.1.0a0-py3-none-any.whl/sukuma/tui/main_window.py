# Sukuma
# Copyright (C) 2025 The Nummertopia Delegation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


# UPDATEME With additional components in `tui/components/`
# See Textual documentation at:
# https://textual.textualize.io/tutorial/
"""Assemble a Textual application for a terminal user interface."""

from typing import ClassVar

from pathlib import Path

from nebulog import logger

from textual.app import App, ComposeResult
from textual.widgets import Footer, Label

from art import text2art

from sukuma.tui.themes import AppCustomThemes

CSS_DIRECTORY = Path(__file__).parent / "css"


class TerminalApp(App):
    """Textual app to serve as the Sukuma interface.

    Parameters
    ----------
    theme : str
        Theme name to launch the application with.
    """

    CSS_PATH: ClassVar = [
        CSS_DIRECTORY / "demo.tcss",  # UPDATEME by removing when no longer needed
        CSS_DIRECTORY / "noctis.tcss",
    ]

    def __init__(self, theme: str) -> None:
        """Initialise the Terminal User Interface."""
        super().__init__()

        logger.info("Launching Sukuma TUI", theme=theme)
        self.default_theme = theme

    def compose(self) -> ComposeResult:  # noqa: PLR6301
        """Create child widgets for the app."""
        # UPDATEME by replacing with your own widgets
        yield Label(text2art("Sukuma", "tarty1"), classes="title")
        yield Label(
            "[i][b]The all-encompassing finance manager on the command line.[/]",
            classes="description",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Execute instructions when launching the interface."""
        logger.info("Mounting the application interface")

        for theme in AppCustomThemes:
            self.register_theme(theme.value)

        self.theme = self.default_theme


if __name__ == "__main__":
    app = TerminalApp("noctis")
    app.run()
