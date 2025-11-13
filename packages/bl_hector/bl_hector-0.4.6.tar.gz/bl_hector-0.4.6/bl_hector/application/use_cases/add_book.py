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
from dataclasses import dataclass, fields
from typing import Optional

from bl_hector.domain.administration.enumerations import Permissions as P
from bl_hector.domain.administration.repositories import Permissions
from bl_hector.domain.administration.value_objects import UserId
from bl_hector.domain.collection_management import validators
from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.errors import InvalidValue
from bl_hector.domain.collection_management.repositories import Books
from bl_hector.domain.collection_management.services import Calendar
from bl_hector.domain.collection_management.value_objects import (
    Author,
    Cover,
    Genre,
    Isbn,
    Title,
    Year,
)


@dataclass(frozen=True)
class Request:
    user_id: str
    isbn: str
    title: str
    year: int
    authors: list[str]
    genres: list[str]
    cover: str = ""


@dataclass
class Errors:
    isbn: Optional[InvalidValue] = None
    title: Optional[InvalidValue] = None
    year: Optional[InvalidValue] = None
    authors: Optional[InvalidValue] = None

    def __bool__(self) -> bool:
        return any([getattr(self, f.name) for f in fields(self)])


class Presenter(ABC):
    @abstractmethod
    def not_authorized(self) -> None:
        ...

    @abstractmethod
    def bad_request(self, errors: Errors) -> None:
        ...

    @abstractmethod
    def book_already_exists(self, book: Book) -> None:
        ...

    @abstractmethod
    def book_added(self, book: Book) -> None:
        ...


@dataclass(frozen=True)
class Interactor:
    presenter: Presenter
    books: Books
    calendar: Calendar
    permissions: Permissions

    def execute(self, request: Request) -> None:
        if not self.__is_authorized(request.user_id):
            return self.presenter.not_authorized()

        if errors := self.__validate_request(request):
            return self.presenter.bad_request(errors)

        today = self.calendar.today()
        book = Book.instanciate(
            today,
            today,
            Isbn.instanciate(request.isbn),
            Title.instanciate(request.title),
            Year.instanciate(request.year),
            [Author.instanciate(a) for a in request.authors if a],
            [Genre.instanciate(g) for g in request.genres if g],
            Cover.instanciate(request.cover) if request.cover else None,
        )

        if books := self.books.search(isbn=book.isbn):
            return self.presenter.book_already_exists(books[0])

        self.books.add(book)
        self.presenter.book_added(book)

    def __is_authorized(self, user_id: str) -> bool:
        return self.permissions.is_authorized_to(UserId(user_id), P.ADD_BOOK)

    def __validate_request(self, request: Request) -> Errors:
        return Errors(
            isbn=validators.isbn(request.isbn),
            title=validators.title(request.title),
            year=validators.year(request.year),
            authors=validators.authors(request.authors),
        )
