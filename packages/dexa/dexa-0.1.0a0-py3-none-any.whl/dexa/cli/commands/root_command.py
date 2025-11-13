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


# UPDATEME With subcommand apps in `cli/commands/`, see documentation at:
# https://typer.tiangolo.com/tutorial/
# See recommended configuration for multicommand applications at:
# https://typer.tiangolo.com/tutorial/one-file-per-command/#main-module-mainpy
"""The ultimate terminal RPN calculator."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer
from rich.console import Console

from dexa import __version__
from dexa.cli.commands.config import config_app
from dexa.cli.styling import AppCustomThemes
from dexa.config import resolve_app_manager
from dexa.logging import setup_app_logging
from dexa.tui.main_window import TerminalApp

app = typer.Typer(rich_markup_mode="rich")
app.add_typer(config_app, name="config")


def version_callback(print_version: bool) -> None:
    """Print the program version in a Rich console with the Noctis theme."""
    if print_version:
        Console(theme=AppCustomThemes.NOCTIS).print(
            f":package:[declaration]Dexa[/] [bold fstring]{__version__}[/]"
        )

        raise typer.Exit


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help=(
                ":bus_stop: Specify a custom configuration file to launch the "
                "application."
            ),
        ),
    ] = None,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help=":bulb: Print the current version of this program and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help=(
                ":bug: Log operations to the terminal at the "
                "[b][logging.level.debug]DEBUG[/logging.level.debug][/b] level."
            ),
        ),
    ] = False,
) -> None:
    """:pager: Launch the Dexa interface."""
    setup_app_logging(debug=debug)

    if ctx.invoked_subcommand is None:
        logger.info("Calling Dexa via CLI")

        if config is not None:  # pragma: no cover
            logger.info("Using custom configuration file", config=config)

        app_manager = resolve_app_manager("settings", config)

        interface = TerminalApp(app_manager.settings.theme)
        interface.run()

        logger.debug("Dexa exited successfully")
