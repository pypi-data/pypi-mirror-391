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


"""Define logging capabilities for Sukuma."""

from nebulog import install, logger

from sukuma.config.constants import get_default_log_path
from sukuma.logging.formatters import file_formatter


def setup_app_logging(*, debug: bool = False) -> None:
    """Configure the available loggers at Sukuma runtime.

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
