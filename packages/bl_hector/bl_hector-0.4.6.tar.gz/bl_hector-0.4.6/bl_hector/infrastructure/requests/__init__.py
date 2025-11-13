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

import base64
import logging
from typing import Optional

import requests

from bl_hector.domain.collection_management.services import (
    CoverProvider as CoverProviderABC,
)
from bl_hector.domain.collection_management.value_objects import Cover, Isbn


class CoverProvider(CoverProviderABC):
    def by_isbn(self, isbn: Isbn) -> Optional[Cover]:
        try:
            if data_url := self.__to_data_url(requests.get(self.__get_url(isbn))):
                return Cover.instanciate(data_url)
            return None
        except Exception as exc:
            logging.error(str(exc))
            return None

    def __get_url(self, isbn: Isbn) -> str:
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

    def __to_data_url(self, response: requests.Response) -> str:
        if response.headers.get("Content-Type", "").startswith("image/"):
            content = base64.b64encode(response.content).decode()
            return f"data:image/jpeg;base64,{content}"
        return ""
