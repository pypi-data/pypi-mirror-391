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

import datetime
import logging
from typing import Optional

import isbnlib

from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.services import (
    BookInfoProvider as BookInfoProviderABC,
)
from bl_hector.domain.collection_management.value_objects import (
    Author,
    Date,
    Isbn,
    Title,
    Year,
)


class BookInfoProvider(BookInfoProviderABC):
    def look_up(self, isbn: Isbn) -> Optional[Book]:
        try:
            meta = isbnlib.meta(str(isbn))
            if not meta:
                return None

            today = Date.instanciate(datetime.date.today())
            return Book.instanciate(
                today,
                today,
                isbn,
                Title.instanciate(meta.get("Title", "")),
                Year.instanciate(int(meta.get("Year", ""))),
                [Author.instanciate(a) for a in meta.get("Authors", "")],
                [],
            )
        except Exception as exc:
            logging.error(str(exc))
            return None
