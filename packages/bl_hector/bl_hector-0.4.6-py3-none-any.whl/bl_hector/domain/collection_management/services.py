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
from .value_objects import Cover, Date, Isbn


class BookInfoProvider(ABC):
    @abstractmethod
    def look_up(self, isbn: Isbn) -> Optional[Book]:
        ...


class CoverProvider(ABC):
    @abstractmethod
    def by_isbn(self, isbn: Isbn) -> Optional[Cover]:
        ...


class Calendar(ABC):
    @abstractmethod
    def today(self) -> Date:
        ...
