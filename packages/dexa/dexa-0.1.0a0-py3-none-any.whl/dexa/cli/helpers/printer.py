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


"""Helper functions designed to print unconventional types in Rich consoles."""

from rich.pretty import pprint

from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList


def pretty_print_setting(manager, key, config_type):
    """Print a Orbittings setting as a literal value on a Rich console.

    Parameters
    ----------
    manager : Nucleus
        A Orbittings manager instance.
    key : str, None
        The key to retrieve from `config_type`.
    config_type : str
        The OrbitalSystem object to inspect for `key`.
    """
    if key is None:
        _print_entire_config(manager, config_type)
    else:
        _print_specific_setting(manager, key, config_type)


def _print_entire_config(manager, config_type):
    """Print the entire Orbittings configuration as a dictionary on a Rich console."""
    config_dict = manager[config_type].to_dict()

    pprint(config_dict)


def _print_specific_setting(manager, key, config_type):
    """Print a Orbittings setting with their adequate type on a Rich console."""
    value = manager[config_type, key]
    formatted_value = _format_value_for_printing(value)

    pprint(formatted_value)


def _format_value_for_printing(value):
    """Format box and list Dynaconf objects to their respective literals."""
    if isinstance(value, DynaBox):
        return value.to_dict()

    if isinstance(value, BoxList):
        return value.to_list()

    return value
