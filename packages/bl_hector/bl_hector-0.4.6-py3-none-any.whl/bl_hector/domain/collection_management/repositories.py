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

from abc import ABC, abstractmethod
from typing import Optional

from .entities import Book
from .value_objects import Author, Genre, Isbn, Title, Year


class Books(ABC):
    @abstractmethod
    def by_isbn(self, isbn: Isbn) -> Optional[Book]:
        ...

    @abstractmethod
    def search(
        self,
        /,
        *,
        isbn: Optional[Isbn] = None,
        title: Optional[Title] = None,
        year: Optional[Year] = None,
        author: Optional[Author] = None,
        genre: Optional[Genre] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> list[Book]:
        ...

    @abstractmethod
    def add(self, book: Book) -> None:
        ...

    @abstractmethod
    def update(self, book: Book) -> None:
        ...
