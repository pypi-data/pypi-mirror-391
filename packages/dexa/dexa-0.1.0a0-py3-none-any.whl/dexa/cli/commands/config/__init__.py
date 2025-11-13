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


"""Manage configuration for Dexa via the CLI."""

import typer

from dexa.cli.commands.config.extend import config_extend_app
from dexa.cli.commands.config.get import config_get_app
from dexa.cli.commands.config.set import config_set_app
from dexa.cli.commands.config.unset import config_unset_app

config_app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help=":gear: Perform operations with Dexa configuration.",
)

config_app.add_typer(config_get_app)
config_app.add_typer(config_set_app)
config_app.add_typer(config_unset_app)
config_app.add_typer(config_extend_app)
