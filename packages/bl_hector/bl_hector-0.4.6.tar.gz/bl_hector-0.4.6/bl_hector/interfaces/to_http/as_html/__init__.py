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

from http import HTTPStatus as HTTP
from pathlib import Path
from typing import Any, Callable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block
from werkzeug.datastructures import MultiDict

from bl_hector.application.use_cases import (
    add_book,
    display_book,
    look_up_book,
    search_books,
    update_book,
)
from bl_hector.domain.collection_management import validators
from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.value_objects import Isbn
from bl_hector.interfaces import Pager, User, l10n, translate_error
from bl_hector.interfaces.to_http import HttpMeta, HttpPresenter

ENVIRONMENT = Environment(
    loader=FileSystemLoader([Path(__file__).parent / "templates"]),
    autoescape=select_autoescape(),
    extensions=["bl_hector.interfaces.utils.PatchedPyPugJSExtension"],
)


def register_jinja_global(key: str, value: Any) -> None:
    ENVIRONMENT.globals[key] = value


def url_for(*args: Any, **kwargs: Any) -> str:
    if "url_for" not in ENVIRONMENT.globals:
        raise RuntimeError("`url_for` is not declared on the environment!")
    return ENVIRONMENT.globals["url_for"](*args, **kwargs)  # type: ignore


class HtmlMeta(HttpMeta):
    def __init__(self, /, *, status: int = HTTP.OK, is_logged_in: bool = False) -> None:
        self.__status_code: int = status
        self.__headers: dict[str, Any] = {"Content-Type": "text/html; charset=UTF-8"}
        self.__is_logged_in = is_logged_in

    def see_other(self, target: str, /, *, permanent: bool = False) -> None:
        self.__status_code = HTTP.MOVED_PERMANENTLY if permanent else HTTP.SEE_OTHER

        if "Content-Type" in self.__headers:
            del self.__headers["Content-Type"]

        self.__headers["Location"] = target

    def bad_request(self) -> None:
        self.__status_code = HTTP.BAD_REQUEST

    def not_authorized(self) -> None:
        if self.__is_logged_in:
            self.__status_code = HTTP.FORBIDDEN
        else:
            self.__status_code = HTTP.UNAUTHORIZED

    def status_code(self) -> int:
        return self.__status_code

    def headers(self) -> dict[str, Any]:
        return self.__headers


class HtmxMeta(HttpMeta):
    def __init__(self, /, *, status: int = HTTP.OK, is_logged_in: bool = False) -> None:
        self.__status_code: int = status
        self.__headers: dict[str, Any] = {"Content-Type": "text/html; charset=UTF-8"}
        self.__is_logged_in = is_logged_in

    def see_other(self, target: str, /, *, permanent: bool = False) -> None:
        self.__status_code = HTTP.MOVED_PERMANENTLY if permanent else HTTP.SEE_OTHER

        if "Content-Type" in self.__headers:
            del self.__headers["Content-Type"]

        self.__headers["HX-Location"] = target

    def replace(self, target: str) -> None:
        self.__headers["HX-Push-Url"] = target

    def bad_request(self) -> None:
        self.__status_code = HTTP.BAD_REQUEST

    def not_authorized(self) -> None:
        if self.__is_logged_in:
            self.__status_code = HTTP.FORBIDDEN
        else:
            self.__status_code = HTTP.UNAUTHORIZED

    def status_code(self) -> int:
        return self.__status_code

    def headers(self) -> dict[str, Any]:
        # Prevent problem when navigating with the back button
        self.__headers["Cache-Control"] = "no-store, max-age=0"
        return self.__headers


class HtmlContent:
    def __init__(self, target: str, context: Optional[dict[str, Any]] = None) -> None:
        self.__template, self.__fragment = self.__parse(target)
        self.__context = context or {}

    def __parse(self, target: str) -> tuple[str, str]:
        e = target.split("#", 1)
        t, f = (e[0], "") if len(e) == 1 else (e[0], e[1])
        return t.removesuffix(".pug") + ".pug", f

    def __str__(self) -> str:
        if self.__fragment:
            return render_block(  # type: ignore
                ENVIRONMENT, self.__template, self.__fragment, **self.__context
            )
        return ENVIRONMENT.get_template(self.__template).render(**self.__context)

    def set(self, key: str, value: Any) -> None:
        self.__context[key] = value

    def append(self, key: str, value: Any) -> None:
        if key not in self.__context:
            self.__context[key] = []
        self.__context[key].append(value)

    def delete(self, key: str) -> None:
        if key in self.__context:
            del self.__context[key]

    def not_authorized(self) -> None:
        if "user" in self.__context:
            self.__context["error"] = self.__translate("access-forbidden")
        else:
            self.__context["error"] = self.__translate("access-not-authorized")

    def __translate(self, message: str) -> str:
        if "_" in self.__context:
            return str(self.__context["_"](message))
        return message


class HtmlOverHttpMixin:
    meta: HttpMeta
    content: HtmlContent

    def status_code(self) -> int:
        return self.meta.status_code()

    def headers(self) -> dict[str, str]:
        return self.meta.headers()

    def data(self) -> str:
        return str(self.content)

    def not_authorized(self) -> None:
        self.meta.not_authorized()
        self.content.not_authorized()


class SimplePresenter(HtmlOverHttpMixin, HttpPresenter):
    def __init__(
        self, template: str, /, *, user: Optional[User] = None, **context: Any
    ) -> None:
        self.meta = HtmlMeta()
        self.content = HtmlContent(
            template,
            {
                "user": user,
                "_": l10n.translator_for(user.locale if user else ""),
                **context,
            },
        )


class BadRequest(HtmlOverHttpMixin, HttpPresenter):
    def __init__(self, /, *, user: Optional[User] = None) -> None:
        _ = l10n.translator_for(user.locale if user else "")
        self.meta = HtmlMeta(status=HTTP.BAD_REQUEST)
        self.content = HtmlContent(
            "error", {"user": user, "_": _, "message": _("bad-request")}
        )


class SearchBooksOptionalFragment(
    HtmlOverHttpMixin, HttpPresenter, search_books.Presenter
):
    def __init__(
        self,
        data: MultiDict[str, Any],
        /,
        *,
        fragment: str = "",
        user: Optional[User] = None,
    ) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        pager = Pager(url_for("books.search", **data))

        if fragment:
            self.meta = HtmxMeta()
            self.meta.replace(
                url_for(
                    "books.search",
                    # Remove empty values and page number
                    **{k: v for k, v in data.items() if v and k != "page"},
                )
            )
        else:
            self.meta = HtmlMeta()

        self.content = HtmlContent(
            f"books/search#{fragment}",
            {"_": self._, "user": user, "data": data, "errors": {}, "pager": pager},
        )

        if data:  # Handle the case when the search returns no book.
            self.content.set("books", [])

    def bad_request(self, errors: search_books.Errors) -> None:
        self.content.set(
            "errors",
            {
                "isbn": translate_error(self._, errors.isbn),
                "title": translate_error(self._, errors.title),
                "year": translate_error(self._, errors.year),
                "author": translate_error(self._, errors.author),
                "genre": translate_error(self._, errors.genre),
            },
        )
        self.content.delete("books")

    def book(self, book: Book) -> None:
        self.content.append(
            "books",
            {
                "isbn": str(book.isbn),
                "title": str(book.title),
                "year": int(book.year),
                "authors": [str(a) for a in book.authors],
                "genres": [str(g) for g in book.genres],
                "cover": str(book.cover) if book.cover else "",
            },
        )


class SearchBooksFragment(SearchBooksOptionalFragment):
    def __init__(
        self,
        fragment: str,
        data: MultiDict[str, Any],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        super().__init__(data, fragment=fragment, user=user)


class SearchBooks(SearchBooksOptionalFragment):
    def __init__(
        self, data: MultiDict[str, Any], /, *, user: Optional[User] = None
    ) -> None:
        super().__init__(data, user=user)


class AddBookForm(HtmlOverHttpMixin, HttpPresenter):
    def __init__(self, /, *, user: Optional[User] = None) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        self.meta = HtmlMeta(is_logged_in=bool(user))
        self.content = HtmlContent(
            "books/add", {"user": user, "_": self._, "data": {}, "errors": {}}
        )


class AddBookOptionalFragment(HtmlOverHttpMixin, HttpPresenter, add_book.Presenter):
    def __init__(
        self,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        fragment: str = "",
        user: Optional[User] = None,
    ) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        if fragment:
            self.meta = HtmxMeta(is_logged_in=bool(user))
        else:
            self.meta = HtmlMeta(is_logged_in=bool(user))
        self.content = HtmlContent(
            f"books/add#{fragment}",
            {"user": user, "_": self._, "data": data, "errors": {}},
        )
        self.__notify = notify

    def bad_request(self, errors: add_book.Errors) -> None:
        self.content.set(
            "errors",
            {
                "isbn": translate_error(self._, errors.isbn),
                "title": translate_error(self._, errors.title),
                "year": translate_error(self._, errors.year),
                "authors": translate_error(self._, errors.authors),
            },
        )

    def book_already_exists(self, book: Book) -> None:
        self.__notify(self._("book-already-exists"), "info")
        self.meta.see_other(url_for("books.display", isbn=str(book.isbn)))

    def book_added(self, book: Book) -> None:
        self.__notify(
            self._(
                "book-added-html",
                isbn=str(book.isbn),
                url=url_for("books.display", isbn=str(book.isbn)),
            ),
            "success",
        )
        self.meta.see_other(url_for("books.add"))


class AddBookFragment(AddBookOptionalFragment):
    def __init__(
        self,
        fragment: str,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        super().__init__(data, notify, fragment=fragment, user=user)


class AddBook(AddBookOptionalFragment):
    def __init__(
        self,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        super().__init__(data, notify, user=user)


class LookUpBook(HtmlOverHttpMixin, HttpPresenter, look_up_book.Presenter):
    def __init__(self, isbn: str, /, *, user: Optional[User] = None) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        self.meta = HtmlMeta()
        self.content = HtmlContent(
            "books/add#form",
            {"user": user, "_": self._, "data": {"isbn": isbn}, "errors": {}},
        )

    def not_an_isbn(self, isbn: str) -> None:
        self.content.set("isbn", isbn)
        self.content.set("errors", {"isbn": self._("not-an-isbn")})

    def book_not_found(self, isbn: Isbn) -> None:
        self.content.set("isbn", str(isbn))
        self.content.set("errors", {"isbn": self._("unknown-isbn")})

    def book(self, book: Book) -> None:
        self.content.set(
            "data",
            {
                "isbn": str(book.isbn),
                "title": str(book.title),
                "year": int(book.year),
                "authors": ", ".join([str(a) for a in book.authors]),
                "genres": ", ".join([str(g) for g in book.genres]),
                "cover": str(book.cover) if book.cover else "",
            },
        )


class DisplayBook(HtmlOverHttpMixin, HttpPresenter, display_book.Presenter):
    def __init__(
        self, notify: Callable[[str, str], None], /, *, user: Optional[User] = None
    ) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        self.meta = HtmlMeta(is_logged_in=bool(user))
        self.content = HtmlContent(
            "books/display", {"user": user, "_": self._, "book": {}}
        )
        self.__notify = notify

    def not_an_isbn(self, isbn: str) -> None:
        self.__notify(self._("not-an-isbn"), "warning")
        self.meta.see_other(url_for("books.search"))

    def book_not_found(self, isbn: Isbn) -> None:
        self.__notify(self._("book-does-not-exist"), "warning")
        self.meta.see_other(url_for("books.search"))

    def see_other(self, isbn: Isbn) -> None:
        self.meta.see_other(url_for("books.display", isbn=str(isbn)), permanent=True)

    def book(self, book: Book) -> None:
        self.content.set(
            "book",
            {
                "added_on": self._("date", date=book.added_on.to_date()),
                "updated_on": (
                    self._("date", date=book.updated_on.to_date())
                    if book.updated_on != book.added_on
                    else "-"
                ),
                "isbn": str(book.isbn),
                "title": str(book.title),
                "year": int(book.year),
                "authors": ", ".join([str(a) for a in book.authors]),
                "genres": ", ".join([str(g) for g in book.genres]),
                "cover": str(book.cover) if book.cover else "",
            },
        )


class UpdateBookForm(HtmlOverHttpMixin, HttpPresenter, display_book.Presenter):
    def __init__(
        self,
        isbn: str,
        notify: Callable[[str, str], None],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        self.meta = HtmlMeta(is_logged_in=bool(user))
        self.content = HtmlContent(
            "books/update",
            {"user": user, "_": self._, "isbn": isbn, "data": {}, "errors": {}},
        )
        self.__notify = notify

    def not_an_isbn(self, isbn: str) -> None:
        self.__notify(self._("not-an-isbn"), "warning")
        self.meta.see_other(url_for("books.search"))

    def book_not_found(self, isbn: Isbn) -> None:
        self.__notify(self._("book-does-not-exist"), "warning")
        self.meta.see_other(url_for("books.search"))

    def see_other(self, isbn: Isbn) -> None:
        self.meta.see_other(url_for("books.display", isbn=str(isbn)), permanent=True)

    def book(self, book: Book) -> None:
        self.content.set(
            "data",
            {
                "isbn": str(book.isbn),
                "title": str(book.title),
                "year": int(book.year),
                "authors": ", ".join([str(a) for a in book.authors]),
                "genres": ", ".join([str(g) for g in book.genres]),
                "cover": str(book.cover) if book.cover else "",
            },
        )


class UpdateBookOptionalFragment(
    HtmlOverHttpMixin, HttpPresenter, update_book.Presenter
):
    def __init__(
        self,
        isbn: str,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        fragment: str = "",
        user: Optional[User] = None,
    ) -> None:
        self._ = l10n.translator_for(user.locale if user else "")
        if fragment:
            self.meta = HtmxMeta(is_logged_in=bool(user))
        else:
            self.meta = HtmlMeta(is_logged_in=bool(user))
        self.content = HtmlContent(
            f"books/update#{fragment}",
            {"user": user, "_": self._, "isbn": isbn, "data": data, "errors": {}},
        )
        self.__notify = notify

    def bad_request(self, errors: update_book.Errors) -> None:
        self.content.set(
            "errors",
            {
                "title": translate_error(self._, errors.title),
                "year": translate_error(self._, errors.year),
                "authors": translate_error(self._, errors.authors),
            },
        )

    def book_not_found(self, isbn: Isbn) -> None:
        self.__notify(self._("book-not-found"), "warning")
        self.meta.see_other(url_for("books.search"))

    def book_updated(self, book: Book) -> None:
        self.__notify(self._("update-book-success"), "success")
        self.meta.see_other(url_for("books.display", isbn=str(book.isbn)))


class UpdateBookFragment(UpdateBookOptionalFragment):
    def __init__(
        self,
        fragment: str,
        isbn: str,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        super().__init__(isbn, data, notify, fragment=fragment, user=user)


class UpdateBook(UpdateBookOptionalFragment):
    def __init__(
        self,
        isbn: str,
        data: MultiDict[str, Any],
        notify: Callable[[str, str], None],
        /,
        *,
        user: Optional[User] = None,
    ) -> None:
        super().__init__(isbn, data, notify, user=user)


class ValidateBook(HtmlOverHttpMixin, HttpPresenter):
    def __init__(
        self, data: MultiDict[str, Any], /, *, user: Optional[User] = None
    ) -> None:
        if len(data.keys()) != 1:
            raise RuntimeError("Only one attribute can be validated at a time!")
        attribute = list(data.keys())[0]
        value = data[attribute]

        self._ = l10n.translator_for(user.locale if user else "")
        errors = self.__validate(attribute, value)
        context = {"user": user, "_": self._, "data": data, "errors": errors}

        self.meta = HtmlMeta()
        # We use `search` as it contains all fields as not required.
        self.content = HtmlContent(f"books/search#{attribute}", context)

    def __validate(self, attribute: str, value: str) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not value:
            return errors

        if attribute == "isbn":
            errors["isbn"] = translate_error(
                self._, add_book.Errors(isbn=validators.isbn(value)).isbn
            )
        if attribute == "year":
            errors["year"] = translate_error(
                self._, add_book.Errors(year=validators.year(int(value))).year
            )

        return errors
