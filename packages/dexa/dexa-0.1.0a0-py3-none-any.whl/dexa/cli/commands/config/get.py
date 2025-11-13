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


"""Retrieve existing values from the Dexa configuration."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer

from dexa.cli.helpers import pretty_print_setting
from dexa.config import ConfigurationDomain, resolve_app_manager
from dexa.logging import setup_app_logging

config_get_app = typer.Typer(no_args_is_help=True)


@config_get_app.command()
def get(
    key: Annotated[
        str, typer.Argument(help=":key: The configuration key to be retrieved.")
    ] = None,
    path: Annotated[
        Path, typer.Option(help=":bus_stop: Specify a custom configuration file.")
    ] = None,
    secret: Annotated[
        bool,
        typer.Option(
            "--secret",
            "-s",
            help=":lock: Retrieve configuration from the secret manager instead.",
        ),
    ] = False,
) -> None:
    """:inbox_tray: Retrieve a key from the configuration file."""
    setup_app_logging(debug=False)
    domain = ConfigurationDomain.from_flag(is_secret=secret)

    logger.info("Retrieving configuration key via CLI", key=key, is_secret=secret)

    if path is not None:  # pragma: no cover
        logger.info("Using custom configuration file", config=path)

    app_manager = resolve_app_manager(domain, path)

    pretty_print_setting(app_manager, key, domain.value)

    logger.debug("Dexa exited successfully")
