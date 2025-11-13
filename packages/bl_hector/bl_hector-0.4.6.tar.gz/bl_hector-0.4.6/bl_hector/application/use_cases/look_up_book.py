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
from dataclasses import dataclass

from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.errors import InvalidValue
from bl_hector.domain.collection_management.services import (
    BookInfoProvider,
    CoverProvider,
)
from bl_hector.domain.collection_management.value_objects import Isbn


@dataclass(frozen=True)
class Request:
    isbn: str


class Presenter(ABC):
    @abstractmethod
    def not_an_isbn(self, isbn: str) -> None:
        ...

    @abstractmethod
    def book_not_found(self, isbn: Isbn) -> None:
        ...

    @abstractmethod
    def book(self, book: Book) -> None:
        ...


@dataclass(frozen=True)
class Interactor:
    presenter: Presenter
    info_provider: BookInfoProvider
    cover_provider: CoverProvider

    def execute(self, request: Request) -> None:
        try:
            isbn = Isbn.instanciate(request.isbn)
        except InvalidValue:
            return self.presenter.not_an_isbn(request.isbn)

        if not (book := self.info_provider.look_up(isbn)):
            return self.presenter.book_not_found(isbn)

        book.cover = self.cover_provider.by_isbn(isbn)

        return self.presenter.book(book)
