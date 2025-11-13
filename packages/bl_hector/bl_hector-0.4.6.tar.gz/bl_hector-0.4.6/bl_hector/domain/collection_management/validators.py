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

from typing import Optional

from .errors import InvalidValue, MissingAuthor
from .value_objects import Author, Isbn, Title, Year


def isbn(value: str) -> Optional[InvalidValue]:
    try:
        Isbn.instanciate(value)
    except InvalidValue as exc:
        return exc
    return None


def title(value: str) -> Optional[InvalidValue]:
    try:
        Title.instanciate(value)
    except InvalidValue as exc:
        return exc
    return None


def year(value: int) -> Optional[InvalidValue]:
    try:
        Year.instanciate(value)
    except InvalidValue as exc:
        return exc
    return None


def authors(value: list[str]) -> Optional[InvalidValue]:
    try:
        # FIXME: This domain constraint should live in the domain!
        if len([Author.instanciate(a) for a in value if a]) == 0:
            raise MissingAuthor()
    except InvalidValue as exc:
        return exc
    return None
