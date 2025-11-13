# The MIT License (MIT)
# Copyright (c) 2025 The Nummertopia Delegation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.


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

from dexa.tui.themes import AppCustomThemes

CSS_DIRECTORY = Path(__file__).parent / "css"


class TerminalApp(App):
    """Textual app to serve as the Dexa interface.

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

        logger.info("Launching Dexa TUI", theme=theme)
        self.default_theme = theme

    def compose(self) -> ComposeResult:  # noqa: PLR6301
        """Create child widgets for the app."""
        # UPDATEME by replacing with your own widgets
        yield Label(text2art("Dexa", "tarty1"), classes="title")
        yield Label(
            "[i][b]The ultimate terminal RPN calculator.[/]", classes="description"
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
