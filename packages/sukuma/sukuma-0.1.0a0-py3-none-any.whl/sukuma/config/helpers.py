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


"""Helper functions for streamlining Sukuma functionality."""

from typing import TYPE_CHECKING, Literal

from pathlib import Path

from sukuma.config.manager import AppManager

if TYPE_CHECKING:
    from orbittings import Nucleus

    from sukuma.config.mappings import ConfigurationDomain


def resolve_app_manager(
    domain: "Literal['settings', 'secrets'] | ConfigurationDomain",
    custom_path: Path | None = None,
) -> "Nucleus":
    """Resolve the Orbittings Manager to be used for other operations.

    Parameters
    ----------
    domain : {"settings", "secrets"}
        Flag to treat the given `path` as a settings or secrets file.
    custom_path : Path, optional
        A custom path to load a configuration from.

    Returns
    -------
    Nucleus
        A manager object for accessing global settings or secrets.
    """
    if custom_path is None:
        return AppManager.default()

    return AppManager.custom(custom_path, domain)
