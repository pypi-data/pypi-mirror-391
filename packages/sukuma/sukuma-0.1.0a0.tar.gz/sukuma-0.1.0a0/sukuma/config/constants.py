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


"""Retrieve foundational values for enabling standard behaviour for Sukuma."""

from pathlib import Path

from platformdirs import user_config_path, user_log_path

from sukuma import __version__


def get_default_config() -> Path:
    """Retrieve the default configuration path for Sukuma.

    Returns
    -------
    Path
        A Path object pointing to the User Config Path where configuration for
        Sukuma will be stored.
    """
    return user_config_path("sukuma")


def get_default_log_path(filename: str | Path) -> Path:
    """Retrieve the default path to store Sukuma logs.

    Parameters
    ----------
    filename : str, Path
        Name of the file to be created inside the User Log Path.

    Returns
    -------
    Path
        A Path object pointing to the User Log Path where a file for Sukuma logs
        will be stored.
    """
    return user_log_path("sukuma") / filename


def generate_default_config_schema():
    """Create the default configuration schema for Sukuma.

    Returns
    -------
    dict
        A dictionary containing the keys and values for the vanilla Sukuma
        configuration, wrapped inside a function to avoid mutation issues.
    """
    return {
        "VERSION": __version__,
        "THEME": "noctis",
        # UPDATEME with future default sections to be included
    }
