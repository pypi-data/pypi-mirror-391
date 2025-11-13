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


"""Configuration manager for Dexa."""

from typing import Literal, Self

from pathlib import Path

from orbittings import Nucleus

from dexa.config.constants import generate_default_config_schema, get_default_config
from dexa.config.mappings import ConfigurationDomain, EnvvarPrefix


class AppManager(Nucleus):
    """Extend the Orbittings `Nucleus` class to manage Dexa configuration.

    Creates an instance of a `Nucleus` object with preset default contents and base
    directory, both defined in the `constants` module.
    """

    def __init__(self):
        """Initialise the manager by calling the `Nucleus` superclass."""
        super().__init__(
            default_contents=generate_default_config_schema(),
            base_dir=get_default_config(),
        )

    @classmethod
    def default(cls) -> Self:
        """Provide an `AppManager` instance with default settings and secrets files."""
        instance = cls()
        instance.add("settings", envvar_prefix=EnvvarPrefix.SETTINGS.value)
        instance.add("secrets", envvar_prefix=EnvvarPrefix.SECRETS.value)

        return instance

    @classmethod
    def custom(
        cls, path: Path, domain: Literal["settings", "secrets"] | ConfigurationDomain
    ) -> Self:
        """Provide a manager instance with a single domain and custom definitions.

        Parameters
        ----------
        path : Path
            Path to a valid custom TOML configuration file for Dexa.
        domain : {"settings", "secrets"}
            Flag to treat the given `path` as a settings or secrets file.

        Returns
        -------
        AppManager
            A manager instance with a single domain and custom definitions.
        """
        instance = cls()
        domain = ConfigurationDomain(domain)

        if domain == ConfigurationDomain.SETTINGS:
            instance.add(
                domain.value,
                custom_config=path,
                envvar_prefix=EnvvarPrefix.SETTINGS.value,
            )

        else:
            instance.add(
                domain.value,
                custom_config=path,
                envvar_prefix=EnvvarPrefix.SECRETS.value,
            )

        return instance
