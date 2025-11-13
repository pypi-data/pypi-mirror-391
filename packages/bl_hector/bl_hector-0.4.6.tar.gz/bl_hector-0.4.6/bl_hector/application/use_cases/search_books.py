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

from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.errors import InvalidValue
from bl_hector.domain.collection_management.repositories import Books
from bl_hector.domain.collection_management.value_objects import (
    Author,
    Genre,
    Isbn,
    Title,
    Year,
)


@dataclass(frozen=True)
class Request:
    isbn: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    page_number: Optional[int] = None
    page_size: Optional[int] = None


@dataclass
class Errors:
    isbn: Optional[InvalidValue] = None
    title: Optional[InvalidValue] = None
    year: Optional[InvalidValue] = None
    author: Optional[InvalidValue] = None
    genre: Optional[InvalidValue] = None

    def __bool__(self) -> bool:
        return any([getattr(self, f.name) for f in fields(self)])


class Presenter(ABC):
    @abstractmethod
    def bad_request(self, errors: Errors) -> None:
        ...

    @abstractmethod
    def book(self, book: Book) -> None:
        ...


@dataclass(frozen=True)
class Interactor:
    presenter: Presenter
    books: Books

    def execute(self, request: Request) -> None:
        if errors := self.__validate_request(request):
            return self.presenter.bad_request(errors)

        books = self.books.search(
            isbn=Isbn.instanciate(request.isbn) if request.isbn else None,
            title=Title.instanciate(request.title) if request.title else None,
            year=Year.instanciate(request.year) if request.year else None,
            author=Author.instanciate(request.author) if request.author else None,
            genre=Genre.instanciate(request.genre) if request.genre else None,
            page_number=request.page_number,
            page_size=request.page_size,
        )
        for book in books:
            self.presenter.book(book)

    def __validate_request(self, request: Request) -> Errors:
        errors = Errors()
        if request.isbn:
            try:
                Isbn.instanciate(request.isbn)
            except InvalidValue as exc:
                errors.isbn = exc
        if request.title:
            try:
                Title.instanciate(request.title)
            except InvalidValue as exc:
                errors.title = exc
        if request.year is not None:
            try:
                Year.instanciate(request.year)
            except InvalidValue as exc:
                errors.year = exc
        if request.author:
            try:
                Author.instanciate(request.author)
            except InvalidValue as exc:
                errors.author = exc
        if request.genre:
            try:
                Genre.instanciate(request.genre)
            except InvalidValue as exc:
                errors.genre = exc
        return errors
