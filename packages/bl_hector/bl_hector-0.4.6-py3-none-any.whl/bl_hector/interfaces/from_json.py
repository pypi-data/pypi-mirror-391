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
import logging

from bl_hector.application.use_cases import add_book


class AddBook:
    def __init__(self, data: str, user_id: str = "") -> None:
        self.__data = data
        self.__user_id = user_id

    def call(self, interactor: add_book.Interactor) -> None:
        if not self.__data:
            return

        try:
            data = json.loads(self.__data)
        except Exception as exc:
            logging.error(f"AddBook: {exc}")
            logging.exception(exc)
            data = {}

        interactor.execute(
            add_book.Request(
                user_id=self.__user_id,
                isbn=str(data.get("isbn", "")),
                title=str(data.get("title", "")),
                year=int(data.get("year", "0")),
                authors=data.get("authors", []),
                genres=data.get("genres", []),
                cover=str(data.get("cover", "")),
            )
        )
