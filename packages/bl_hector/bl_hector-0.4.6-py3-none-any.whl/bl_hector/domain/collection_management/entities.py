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

from dataclasses import dataclass
from typing import Optional

from .errors import MissingAuthor
from .value_objects import Author, Cover, Date, Genre, Isbn, Title, Year


@dataclass
class Book:
    added_on: Date
    updated_on: Date
    isbn: Isbn
    title: Title
    year: Year
    authors: list[Author]
    genres: list[Genre]
    cover: Optional[Cover] = None

    @classmethod
    def instanciate(
        cls,
        added_on: Date,
        updated_on: Date,
        isbn: Isbn,
        title: Title,
        year: Year,
        authors: list[Author],
        genres: list[Genre],
        cover: Optional[Cover] = None,
    ) -> "Book":
        if not authors:
            raise MissingAuthor()
        return Book(added_on, updated_on, isbn, title, year, authors, genres, cover)
