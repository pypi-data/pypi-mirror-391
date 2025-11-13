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


"""Remove values from the Sukuma configuration."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer

from sukuma.config import ConfigurationDomain, resolve_app_manager
from sukuma.logging import setup_app_logging

config_unset_app = typer.Typer(no_args_is_help=True)


@config_unset_app.command()
def unset(
    key: Annotated[
        str, typer.Argument(help=":key: The configuration key to be removed.")
    ],
    path: Annotated[
        Path, typer.Option(help=":bus_stop: Specify a custom configuration file.")
    ] = None,
    secret: Annotated[
        bool,
        typer.Option(
            "--secret",
            "-s",
            help=":lock: Retrieve configuration from the secret manager instead.",
        ),
    ] = False,
) -> None:
    """:fire: [red]Remove[/] a top-level key from the configuration."""
    setup_app_logging(debug=False)
    domain = ConfigurationDomain.from_flag(is_secret=secret)

    logger.info("Removing configuration key via CLI", key=key, is_secret=secret)

    if path is not None:  # pragma: no cover
        logger.info("Using custom configuration file", config=path)

    app_manager = resolve_app_manager(domain, path)

    app_manager.unset(f"{domain.value}.{key}")
    app_manager.save(domain.value)

    logger.debug("Sukuma exited successfully")
