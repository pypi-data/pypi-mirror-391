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


"""Launch the Sukuma interface."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer

from sukuma.config import resolve_app_manager
from sukuma.logging import setup_app_logging
from sukuma.tui.main_window import TerminalApp

launch_app = typer.Typer(rich_markup_mode="rich")


@launch_app.command()
def launch(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help=(
                ":bus_stop: Specify a custom configuration file to launch the "
                "application."
            ),
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help=(
                ":bug: Log operations to the terminal at the "
                "[b][logging.level.debug]DEBUG[/logging.level.debug][/b] level."
            ),
        ),
    ] = False,
) -> None:
    """:pager: Launch the Sukuma interface."""
    setup_app_logging(debug=debug)

    logger.info("Calling Sukuma via CLI")

    if config is not None:  # pragma: no cover
        logger.info("Using custom configuration file", config=config)

    app_manager = resolve_app_manager("settings", config)

    interface = TerminalApp(app_manager.settings.theme)

    interface.run()

    logger.debug("Sukuma exited successfully")
