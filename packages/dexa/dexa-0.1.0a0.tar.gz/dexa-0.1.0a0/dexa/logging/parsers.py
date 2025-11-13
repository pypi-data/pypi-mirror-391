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


"""Parse custom loggers defined for Dexa."""

import re
from datetime import datetime

FILE_PARSER = re.compile(
    r"""
        (?P<ts>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{3})
        \s\|\s
        \d:\d{2}:\d{2}.\d{6}
        \s\|\s
        (?P<level>\w+)
        \s+\|\s
        (?P<module>\w+)\.py:(?P<line>\d+)
        \s+\|\s
        (?P<message>\S.*?)
        \s*¶  # Extra is deliberately omitted, use JSON serialised logger instead
    """,
    re.VERBOSE,
)


def log_caster(groups: dict) -> None:  # pragma: no cover
    """Convert the parts of a parsed log record line into convenient Python types.

    Parameters
    ----------
    groups : dict
        The Loguru record dictionary with the information about the logging context.
    """
    groups["ts"] = datetime.strptime(groups["ts"], "%Y-%m-%d %H:%M:%S.%f")
    groups["line"] = int(groups["line"])
