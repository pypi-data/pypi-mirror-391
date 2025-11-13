# pvman
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


"""Store or override values in the pvman configuration."""

from typing import Annotated

from pathlib import Path

from nebulog import logger

import typer

from pvman.cli.helpers import BasicConverter as Text
from pvman.config import ConfigurationDomain, resolve_app_manager
from pvman.logging import setup_app_logging

config_set_app = typer.Typer(no_args_is_help=True)


HELP_MSG = (
    ":floppy_disk: Store a key in the configuration file.\n\n"
    ":rotating_light: [bold red]NOTE:[/] To store a [b][i]negative[/i][/b] number in "
    "the configuration, you must pass the double dash separator to prevent the "
    "application from interpreting the value as a flag:\n\n"
    "[bold yellow]$[/] [green]pvman[/] config set somekey "
    "[blue]--[/] -1"
)


@config_set_app.command(name="set", help=HELP_MSG)
def set_command(
    key: Annotated[
        str, typer.Argument(help=":key: The configuration key to be stored.")
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
) -> None:
    """Store a key in the configuration file."""
    setup_app_logging(debug=False)
    domain = ConfigurationDomain.from_flag(is_secret=secret)

    logger.info(
        "Storing configuration key via CLI",
        key=key,
        value=value.output,
        is_secret=secret,
    )

    if path is not None:  # pragma: no cover
        logger.info("Using custom configuration file", config=path)

    app_manager = resolve_app_manager(domain, path)

    if value.output is None:
        typer.echo(f'Could not parse the value "{value.input}"', err=True)

        raise typer.Exit(1)

    app_manager[domain.value, key] = value.output
    app_manager.save(domain.value)

    logger.debug("pvman exited successfully")
