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


"""Retrieve foundational values for enabling standard behaviour for Dexa."""

from pathlib import Path

from platformdirs import user_config_path, user_log_path

from dexa import __version__


def get_default_config() -> Path:
    """Retrieve the default configuration path for Dexa.

    Returns
    -------
    Path
        A Path object pointing to the User Config Path where configuration for
        Dexa will be stored.
    """
    return user_config_path("dexa")


def get_default_log_path(filename: str | Path) -> Path:
    """Retrieve the default path to store Dexa logs.

    Parameters
    ----------
    filename : str, Path
        Name of the file to be created inside the User Log Path.

    Returns
    -------
    Path
        A Path object pointing to the User Log Path where a file for Dexa logs
        will be stored.
    """
    return user_log_path("dexa") / filename


def generate_default_config_schema():
    """Create the default configuration schema for Dexa.

    Returns
    -------
    dict
        A dictionary containing the keys and values for the vanilla Dexa
        configuration, wrapped inside a function to avoid mutation issues.
    """
    return {
        "VERSION": __version__,
        "THEME": "noctis",
        # UPDATEME with future default sections to be included
    }
