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


"""Parse custom loggers defined for Sukuma."""

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
