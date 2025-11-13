# Hector --- A collection manager.
# Copyright © 2023 Bioneland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Any

import typer
from sqlalchemy import create_engine

from bl_hector import __version__
from bl_hector.infrastructure.settings import CliSettings
from bl_hector.infrastructure.sqlalchemy.repositories import META_DATA

from .books import cmd as books_cmd

cli = typer.Typer()
cli.add_typer(books_cmd, name="books", help="Manage books in the collection.")


@cli.callback()
def callback(quiet: bool = False, verbose: bool = False, debug: bool = False) -> None:
    level = logging.WARN
    str_fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S %z"

    if debug:
        str_fmt = str_fmt + " (%(pathname)s:%(lineno)d)"
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    elif quiet:
        level = logging.ERROR

    logging.basicConfig(format=str_fmt, level=level, datefmt=date_fmt)


@cli.command()
def version() -> None:
    """Display application's version."""
    typer.echo(__version__)
    raise typer.Exit()


@cli.command()
def init_db(ctx: typer.Context) -> None:
    """Initialise database's schema."""
    typer.echo("Initialising schema…", nl=False)
    engine = create_engine(ctx.obj.DSN)
    META_DATA.create_all(engine)
    typer.echo(" OK!")


def build_cli(settings: CliSettings) -> Any:
    return cli(obj=settings)
