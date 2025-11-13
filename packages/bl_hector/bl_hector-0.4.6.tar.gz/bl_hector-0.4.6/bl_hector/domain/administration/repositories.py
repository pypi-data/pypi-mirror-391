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

import datetime
from abc import ABC, abstractmethod
from typing import Optional

from .entities import Challenge, Credential, User
from .enumerations import Permissions as P
from .value_objects import UserId


class Users(ABC):
    @abstractmethod
    def by_login(self, login: str) -> Optional[User]:
        ...

    @abstractmethod
    def add(self, user: User) -> None:
        ...


class Credentials(ABC):
    @abstractmethod
    def for_user(self, user: User) -> list[Credential]:
        ...

    @abstractmethod
    def add(self, credential: Credential) -> None:
        ...


class Challenges(ABC):
    @abstractmethod
    def valid_for(self, user: User, now: datetime.datetime) -> Optional[Challenge]:
        ...

    @abstractmethod
    def add(self, challenge: Challenge) -> None:
        ...


class Permissions(ABC):
    @abstractmethod
    def is_authorized_to(self, user_id: UserId, permission: P) -> bool:
        ...
