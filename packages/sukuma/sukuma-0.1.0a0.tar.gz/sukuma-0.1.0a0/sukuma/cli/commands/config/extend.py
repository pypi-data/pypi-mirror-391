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


"""Append values to existing arrays in the Sukuma configuration."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer

from sukuma.cli.helpers import BasicConverter as Text
from sukuma.config import ConfigurationDomain, resolve_app_manager
from sukuma.logging import setup_app_logging

config_extend_app = typer.Typer(no_args_is_help=True)


HELP_MSG = (
    ":straight_ruler: Extend an array key in the configuration file.\n\n"
    "If no setting exists for the key, you cancreate an array with the single value "
    "provided.\n\n"
    ":rotating_light: [bold red]NOTE:[/] To extend a value in the configuration with a "
    "[b][i]negative[/i][/b] number, you must pass the double dash separator to prevent "
    "the application from interpreting it as a flag:\n\n"
    "[bold yellow]$[/] [green]sukuma[/] config extend somekey "
    "[blue]--[/] -1"
)


@config_extend_app.command(name="extend", help=HELP_MSG)
def extend_command(
    key: Annotated[
        str, typer.Argument(help=":key: The configuration key to be extended.")
    ],
    value: Annotated[
        Text,
        typer.Argument(
            help=":keycap_#: The value to be stored with the key.", parser=Text
        ),
    ],
    path: Annotated[
        Path, typer.Option(help=":bus_stop: Specify a custom configuration file.")
    ] = None,
    secret: Annotated[
        bool,
        typer.Option(
            "--secret",
            "-s",
            help=":lock: Store configuration in the secret manager instead.",
        ),
    ] = False,
    create: Annotated[
        bool,
        typer.Option(
            "--create-on-missing",
            "-c",
            help=(
                ":new: Add the provided value in an array if the setting is not set. "
                "Will raise an error otherwise."
            ),
        ),
    ] = False,
) -> None:
    """Extend an array key in the configuration file."""
    setup_app_logging(debug=False)
    domain = ConfigurationDomain.from_flag(is_secret=secret)

    logger.info(
        "Extending array key via CLI", key=key, value=value.output, is_secret=secret
    )

    if path is not None:  # pragma: no cover
        logger.info("Using custom configuration file", config=path)

    app_manager = resolve_app_manager(domain, path)

    if value.output is None:
        typer.echo(f'Could not parse the value "{value.input}"', err=True)

        raise typer.Exit(1)

    current_setting = app_manager.get(f"{domain.value}.{key}")

    if current_setting is None and create:
        app_manager[domain.value, key] = [value.output]

        app_manager.save(domain.value)
        exit_code = 0

    elif current_setting is None:
        typer.echo(
            f"Setting `{key}` was not found, if you wish to update the configuration, "
            "run the command with the `--create-on-missing` option",
            err=True,
        )
        exit_code = 1

    elif isinstance(current_setting, list):
        current_setting.append(value.output)
        app_manager[domain.value, key] = current_setting

        app_manager.save(domain.value)
        exit_code = 0

    else:
        typer.echo(
            f"To extend settings, the value for `{key}` must be an array, got "
            f"{current_setting} instead",
            err=True,
        )
        exit_code = 1

    if exit_code != 0:
        logger.debug("Sukuma exited successfully")

    else:
        logger.debug("Sukuma exited with an error")

    raise typer.Exit(exit_code)
