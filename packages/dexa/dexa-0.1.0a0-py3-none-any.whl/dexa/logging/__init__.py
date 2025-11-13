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


"""Define logging capabilities for Dexa."""

from nebulog import install, logger

from dexa.config.constants import get_default_log_path
from dexa.logging.formatters import file_formatter


def setup_app_logging(*, debug: bool = False) -> None:
    """Configure the available loggers at Dexa runtime.

    Parameters
    ----------
    debug : bool, default False
        Define whether logs will be called at the DEBUG level or a higher level
        depending on the type of logger.
    """
    file_log_level = "DEBUG" if debug else "INFO"
    shell_log_level = "DEBUG" if debug else "WARNING"

    install(level=shell_log_level)

    logger.enable("")

    logger.add(
        get_default_log_path("app.log"),
        format=file_formatter,
        level=file_log_level,
        rotation="10 MB",
        retention="30 days",
        backtrace=False,
    )

    # Special log file for bug reporting, containing only the last run produced
    logger.add(
        get_default_log_path("report.log"),
        format=file_formatter,
        level="TRACE",
        mode="w",
        backtrace=False,
    )

    logger.add(
        get_default_log_path("app.jsonl"),
        serialize=True,
        rotation="10 MB",
        retention="30 days",
        backtrace=False,
    )


__all__ = ["file_formatter", "setup_app_logging"]
