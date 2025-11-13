# Sukuma
# Copyright (C) 2025 The Nummertopia Delegation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Configuration manager for Sukuma."""

from typing import Literal, Self

from pathlib import Path

from orbittings import Nucleus

from sukuma.config.constants import generate_default_config_schema, get_default_config
from sukuma.config.mappings import ConfigurationDomain, EnvvarPrefix


class AppManager(Nucleus):
    """Extend the Orbittings `Nucleus` class to manage Sukuma configuration.

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
            Path to a valid custom TOML configuration file for Sukuma.
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
