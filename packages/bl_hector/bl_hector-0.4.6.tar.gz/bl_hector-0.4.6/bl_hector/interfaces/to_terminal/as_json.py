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

import json
from typing import Callable

from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.value_objects import Isbn
from bl_hector.interfaces.to_terminal import ExitCodes, LookUpBookInterface


class LookUpBook(LookUpBookInterface):
    def __init__(self, printer: Callable[[str], None]) -> None:
        self.__printer = printer
        self.__exit_code = ExitCodes.USAGE

    def not_an_isbn(self, isbn: str) -> None:
        self.__exit_code = ExitCodes.BAD_REQUEST

    def book_not_found(self, isbn: Isbn) -> None:
        self.__exit_code = ExitCodes.NOT_FOUND

    def book(self, book: Book) -> None:
        self.__exit_code = ExitCodes.OK
        data = {
            "isbn": str(book.isbn),
            "title": str(book.title),
            "year": int(book.year),
            "authors": [str(b) for b in book.authors],
        }
        if book.genres:
            data["genres"] = [str(g) for g in book.genres]
        if book.cover:
            data["cover"] = str(book.cover)

        self.__printer(json.dumps(data))

    def exit_code(self) -> int:
        return self.__exit_code.value
