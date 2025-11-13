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

from typing import Any, Optional

from werkzeug.datastructures import MultiDict

from bl_hector.application.use_cases import add_book, search_books, update_book
from bl_hector.interfaces import Pager
from bl_hector.interfaces.exceptions import BadRequest


class SearchBooks:
    def __init__(self, data: MultiDict[str, Any]) -> None:
        self.__do_search = bool(data)
        self.request = search_books.Request(
            isbn=str(v) if (v := data.get("isbn")) else None,
            title=str(v) if (v := data.get("title")) else None,
            year=int(v) if (v := data.get("year")) else None,
            author=str(v) if (v := data.get("author")) else None,
            genre=str(v) if (v := data.get("genre")) else None,
            page_number=int(v) if (v := data.get("page")) else 1,
            page_size=Pager.PAGE_SIZE,
        )

    def call(self, interactor: search_books.Interactor) -> None:
        if self.__do_search:
            interactor.execute(self.request)


class AddBook:
    request: Optional[add_book.Request] = None

    def __init__(self, data: MultiDict[str, Any], user_id: str = "") -> None:
        try:
            self.request = add_book.Request(
                user_id=user_id,
                isbn=str(data.get("isbn", "")),
                title=str(data.get("title", "")),
                year=int(data.get("year", "")),
                authors=[a.strip() for a in data.get("authors", "").split(",")],
                genres=[g.strip() for g in data.get("genres", "").split(",")],
                cover=str(data.get("cover", "")),
            )
        except Exception:
            pass

    def call(self, interactor: add_book.Interactor) -> None:
        if self.request:
            interactor.execute(self.request)
        else:
            raise BadRequest()


class UpdateBook:
    request: Optional[update_book.Request] = None

    def __init__(self, isbn: str, data: MultiDict[str, Any], user_id: str = "") -> None:
        try:
            self.request = update_book.Request(
                user_id=user_id,
                isbn=isbn,
                title=str(data.get("title", "")),
                year=int(data.get("year", "")),
                authors=[a.strip() for a in data.get("authors", "").split(",")],
                genres=[g.strip() for g in data.get("genres", "").split(",")],
                cover=str(data.get("cover", "")),
            )
        except Exception:
            pass

    def call(self, interactor: update_book.Interactor) -> None:
        if self.request:
            interactor.execute(self.request)
        else:
            raise BadRequest()
