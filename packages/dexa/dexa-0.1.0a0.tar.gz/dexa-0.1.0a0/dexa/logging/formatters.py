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


"""Custom logger formatting utilities for Dexa."""

from dexa.logging.text_tools import LoggerFormatter

LOGGER_FORMATTER = LoggerFormatter()

_FILE_BASE_TEMPLATE = (
    "{time:%Y-%m-%d %H:%M:%S}.{time:SSS} | "
    "{elapsed} | "
    "{level:<8} | "  # Based on the default levels in Loguru (max. 8 in "CRITICAL")
    "{location_string} | "
    "{message:<60} ¶"
)

FILE_FORMATTER_WITH_EXTRA = _FILE_BASE_TEMPLATE + " {extra}\n{exception}"
FILE_FORMATTER_WITHOUT_EXTRA = _FILE_BASE_TEMPLATE + "\n{exception}"


def _format_location_string(record: dict) -> str:
    """Extract and format location information as `file:line`."""
    file_name = record["file"].name
    line_number = record["line"]
    padding = LOGGER_FORMATTER.get_location_padding()

    return f"{file_name}:{line_number}".ljust(padding)


def file_formatter(record: dict) -> str:
    """Define the default formatting for Loguru calls to be stored in the log files.

    Parameters
    ----------
    record : dict
        The Loguru record dictionary with the information about the logging context.

    Returns
    -------
    str
        A formatted string with standardised padding for the individual parts of the log
        entry.
    """
    record.update({"location_string": _format_location_string(record)})

    if record["extra"]:
        return FILE_FORMATTER_WITH_EXTRA

    return FILE_FORMATTER_WITHOUT_EXTRA
