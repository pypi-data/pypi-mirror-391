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


# UPDATEME With subcommand apps in `cli/commands/`, see documentation at:
# https://typer.tiangolo.com/tutorial/
# See recommended configuration for multicommand applications at:
# https://typer.tiangolo.com/tutorial/one-file-per-command/#main-module-mainpy
"""The all-encompassing finance manager on the command line."""

from typing import Annotated

import typer
from rich.console import Console

from sukuma import __version__
from sukuma.cli.commands.config import config_app
from sukuma.cli.commands.launch import launch_app
from sukuma.cli.styling import AppCustomThemes

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
app.add_typer(launch_app)
app.add_typer(config_app, name="config")


def version_callback(print_version: bool) -> None:
    """Print the program version in a Rich console with the Noctis theme."""
    if print_version:
        Console(theme=AppCustomThemes.NOCTIS).print(
            f":package:[declaration]Sukuma[/] [bold fstring]{__version__}[/]"
        )

        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help=":bulb: Print the current version of this program and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """The all-encompassing finance manager on the command line.

    See below for commands and options.
    """  # noqa: D401
    pass
