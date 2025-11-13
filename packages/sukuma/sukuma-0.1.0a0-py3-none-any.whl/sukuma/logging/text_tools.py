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


"""Perform basic string operations to refine logger formatting."""

from functools import lru_cache
from pathlib import Path

from nebulog import logger

logger.disable("sukuma")


class LoggerFormatter:
    """Handle formatting calculations for logger output alignment.

    Parameters
    ----------
    project_root : Path, optional
        Root directory to scan for Python files. Defaults to parent directory of this
        file.
    """

    ADDITIONAL_CHARACTERS = 4  # Additional characters for ".py" and ":" separator
    SHELL_LJUST_TEMPLATE = "[YYYY.mm.dd HH:MM:SS]+sss x critical x "
    SHELL_RJUST_TEMPLATE = " x "  # Separator between message and location
    MINIMUM_WRAPPER_WIDTH = 20

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize formatter with project root directory."""
        self.project_root = (
            project_root if project_root is not None else Path(__file__).parents[1]
        )

    @property
    @lru_cache(maxsize=1)
    def python_modules(self) -> tuple[Path, ...]:
        """Get all Python modules in the project.

        Returns
        -------
        tuple
            A tuple of Path objects containing all modules of `project_root`.
        """
        return tuple(self.project_root.glob("**/*.py"))

    @lru_cache(maxsize=1)
    def get_longest_filename(self) -> int:
        """Find the longest filename in the project.

        Returns
        -------
        int
            The length of the longest filename inside `project_root`.
        """
        if not self.python_modules:  # pragma: no cover
            return 0

        return max(len(module.stem) for module in self.python_modules)

    @staticmethod
    def _get_file_linecount(filepath: Path) -> int:
        """Count the number of lines in a single file."""
        try:
            with filepath.open("r", encoding="utf-8") as file:
                return sum(1 for _ in file)
        except (OSError, UnicodeDecodeError) as e:  # pragma: no cover
            logger.warning(f"Could not read file {filepath}: {e}")
            return 0

    @lru_cache(maxsize=1)
    def get_project_linecount_oom(self) -> int:
        """Find the largest order of magnitude of line counts in the project.

        Returns
        -------
        int
            Number of digits of the largest line count.
        """
        if not self.python_modules:  # pragma: no cover
            return 1

        largest_linecount = max(
            self._get_file_linecount(file) for file in self.python_modules
        )

        return len(str(largest_linecount))

    def get_location_padding(self) -> int:
        """Calculate the width necessary to turn location into an aligned column.

        Location is a combination of logging information comprised of `filename:line`.

        Returns
        -------
        int
            Total padding width needed for location alignment.
        """
        return (
            self.get_longest_filename()
            + self.get_project_linecount_oom()
            + self.ADDITIONAL_CHARACTERS
        )
