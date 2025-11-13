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

from typing import Callable, Optional

from bl_hector.application.use_cases import add_book, display_book
from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.errors import InvalidValue
from bl_hector.domain.collection_management.value_objects import Isbn
from bl_hector.interfaces import translate_error
from bl_hector.interfaces.l10n import DummyTranslator, Translator
from bl_hector.interfaces.to_terminal import ExitCodes, LookUpBookInterface


class DisplayBook(display_book.Presenter):
    def __init__(
        self,
        printer: Callable[[str], None],
        /,
        *,
        translator: Translator = DummyTranslator(),
    ) -> None:
        self.__printer = printer
        self.__exit_code = ExitCodes.USAGE
        self._ = translator
        self.__exit_code = ExitCodes.NOT_FOUND

    def not_an_isbn(self, isbn: str) -> None:
        self.__exit_code = ExitCodes.BAD_REQUEST
        self.__printer(self._("not-an-isbn"))

    def book_not_found(self, isbn: Isbn) -> None:
        self.__exit_code = ExitCodes.NOT_FOUND
        self.__printer(self._("book-not-found"))

    def see_other(self, isbn: Isbn) -> None:
        pass

    def book(self, book: Book) -> None:
        self.__exit_code = ExitCodes.OK
        self.__info(self._("book-isbn"), str(book.isbn))
        self.__info(self._("book-title"), str(book.title))
        self.__info(self._("book-year"), str(book.year))
        self.__info(self._("book-authors"), ", ".join([str(b) for b in book.authors]))
        if book.genres:
            self.__info(self._("book-genres"), ", ".join([str(g) for g in book.genres]))

    def __info(self, name: str, value: str) -> None:
        self.__printer(self._("info-line", name=name, value=value))

    def exit_code(self) -> int:
        return self.__exit_code.value


class LookUpBook(LookUpBookInterface):
    def __init__(
        self,
        printer: Callable[[str], None],
        /,
        *,
        translator: Translator = DummyTranslator(),
    ) -> None:
        self.__printer = printer
        self.__exit_code = ExitCodes.USAGE
        self._ = translator

    def not_an_isbn(self, isbn: str) -> None:
        self.__exit_code = ExitCodes.BAD_REQUEST
        self.__printer(self._("not-an-isbn"))

    def book_not_found(self, isbn: Isbn) -> None:
        self.__exit_code = ExitCodes.NOT_FOUND
        self.__printer(self._("book-not-found"))

    def book(self, book: Book) -> None:
        self.__exit_code = ExitCodes.OK
        self.__info(self._("book-isbn"), str(book.isbn))
        self.__info(self._("book-title"), str(book.title))
        self.__info(self._("book-year"), str(book.year))
        self.__info(self._("book-authors"), ", ".join([str(b) for b in book.authors]))
        if book.genres:
            self.__info(self._("book-genres"), ", ".join([str(g) for g in book.genres]))

    def __info(self, name: str, value: str) -> None:
        self.__printer(self._("info-line", name=name, value=value))

    def exit_code(self) -> int:
        return self.__exit_code.value


class AddBook(add_book.Presenter):
    def __init__(
        self,
        printer: Callable[[str], None],
        /,
        *,
        translator: Translator = DummyTranslator(),
    ) -> None:
        self.__printer = printer
        self.__exit_code = ExitCodes.USAGE
        self._ = translator

    def not_authorized(self) -> None:
        self.__exit_code = ExitCodes.USAGE
        self.__printer(self._("access-not-authorized"))

    def bad_request(self, errors: add_book.Errors) -> None:
        self.__exit_code = ExitCodes.BAD_REQUEST
        self.__printer(self._("book-cannot-be-added"))
        self.__print_error("book-isbn", errors.isbn)
        self.__print_error("book-title", errors.title)
        self.__print_error("book-year", errors.year)
        self.__print_error("book-authors", errors.authors)

    def __print_error(self, name: str, error: Optional[InvalidValue]) -> None:
        if not error:
            return
        self.__printer(
            self._("info-line", name=self._(name), value=translate_error(self._, error))
        )

    def book_already_exists(self, book: Book) -> None:
        self.__exit_code = ExitCodes.BAD_REQUEST
        self.__printer(self._("book-already-exists"))

    def book_added(self, book: Book) -> None:
        self.__exit_code = ExitCodes.OK
        self.__printer(self._("book-added-text", isbn=str(book.isbn)))

    def exit_code(self) -> int:
        return self.__exit_code.value
