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


"""Manage configuration for Sukuma via the CLI."""

import typer

from sukuma.cli.commands.config.extend import config_extend_app
from sukuma.cli.commands.config.get import config_get_app
from sukuma.cli.commands.config.set import config_set_app
from sukuma.cli.commands.config.unset import config_unset_app

config_app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="rich",
    help=":gear: Perform operations with Sukuma configuration.",
)

config_app.add_typer(config_get_app)
config_app.add_typer(config_set_app)
config_app.add_typer(config_unset_app)
config_app.add_typer(config_extend_app)
