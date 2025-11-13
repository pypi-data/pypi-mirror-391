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

import sys

import typer
from typing_extensions import Annotated

from bl_hector.application.use_cases import add_book, display_book, look_up_book
from bl_hector.infrastructure import ONLY_USER, DummyPermissions, SystemCalendar
from bl_hector.infrastructure.typer import services
from bl_hector.interfaces import from_json as controllers
from bl_hector.interfaces.to_terminal import LookUpBookInterface, as_json, as_text

cmd = typer.Typer()


@cmd.command()
def display(ctx: typer.Context, isbn: str) -> None:
    """Display a book from the collection."""
    with services.get_books(ctx.obj) as books:
        presenter = as_text.DisplayBook(
            lambda m: typer.echo(m), translator=services.get_translator()
        )
        interactor = display_book.Interactor(presenter, books)
        interactor.execute(display_book.Request(isbn))
        raise typer.Exit(presenter.exit_code())


@cmd.command()
def look_up(
    ctx: typer.Context,
    isbn: str,
    json: Annotated[bool, typer.Option(help="Format output in JSON.")] = False,
) -> None:
    """Look up for book information based on its ISBN number."""
    presenter: LookUpBookInterface
    if json:
        presenter = as_json.LookUpBook(lambda m: typer.echo(m))
    else:
        presenter = as_text.LookUpBook(
            lambda m: typer.echo(m), translator=services.get_translator()
        )
    interactor = look_up_book.Interactor(
        presenter, services.get_book_info_provider(), services.get_cover_provider()
    )
    interactor.execute(look_up_book.Request(isbn))
    raise typer.Exit(presenter.exit_code())


@cmd.command()
def add(ctx: typer.Context) -> None:
    """Add a book to the collection."""
    calendar = SystemCalendar()
    permissions = DummyPermissions()
    with services.get_books(ctx.obj) as books:
        presenter = as_text.AddBook(
            lambda m: typer.echo(m), translator=services.get_translator()
        )
        interactor = add_book.Interactor(presenter, books, calendar, permissions)
        controller = controllers.AddBook(sys.stdin.readline(), ONLY_USER)
        controller.call(interactor)
        raise typer.Exit(presenter.exit_code())
