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


"""Mapping objects for the Dexa configuration manager."""

from enum import Enum


class EnvvarPrefix(Enum):
    """Environment variable prefixes for Dexa configuration."""

    SETTINGS = "DEXA"
    SECRETS = "DEXA_SECRET"


class ConfigurationDomain(Enum):
    """Configuration domain identifiers."""

    SETTINGS = "settings"
    SECRETS = "secrets"

    @classmethod
    def from_flag(cls, *, is_secret: bool) -> "ConfigurationDomain":
        """Return the appropriate domain based on the secret flag.

        Parameters
        ----------
        is_secret : bool
            Whether the configuration is secret/sensitive.

        Returns
        -------
        ConfigurationDomain
            The corresponding configuration domain.
        """
        return cls.SECRETS if is_secret else cls.SETTINGS
