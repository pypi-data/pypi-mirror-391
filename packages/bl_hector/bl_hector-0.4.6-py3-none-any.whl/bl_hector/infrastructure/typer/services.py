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
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine
from typer import Exit

from bl_hector.infrastructure.isbnlib import BookInfoProvider
from bl_hector.infrastructure.requests import CoverProvider
from bl_hector.infrastructure.settings import CliSettings
from bl_hector.infrastructure.sqlalchemy.repositories import Books
from bl_hector.interfaces import l10n


def get_book_info_provider() -> BookInfoProvider:
    return BookInfoProvider()


def get_cover_provider() -> CoverProvider:
    return CoverProvider()


@contextmanager
def get_books(settings: CliSettings) -> Iterator[Books]:
    options: dict[str, Any] = {}
    if settings.DEBUG_SQL:
        options["echo"] = True
        options["echo_pool"] = "debug"

    engine = create_engine(settings.DSN, **options)
    connection = engine.connect()

    try:
        yield Books(connection)
    except Exit:
        # Raising an `Exit` is the way to end a typer command.
        connection.commit()
        raise
    except Exception as exc:
        logging.exception(exc)
        connection.rollback()
    else:
        connection.commit()


def get_translator() -> l10n.Translator:
    def wrapper(message_id: str, **kwargs: Any) -> str:
        return l10n.localization(l10n.DEFAULT_LOCALE).format_value(message_id, kwargs)

    return wrapper
