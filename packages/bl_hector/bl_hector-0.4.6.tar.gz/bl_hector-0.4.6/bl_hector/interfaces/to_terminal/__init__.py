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
from enum import Enum

from bl_hector.application.use_cases import look_up_book


class ExitCodes(Enum):
    OK = 0
    USAGE = 1
    NOT_FOUND = 2
    BAD_REQUEST = 3


class WithExitCode(ABC):
    @abstractmethod
    def exit_code(self) -> int:
        ...


class LookUpBookInterface(look_up_book.Presenter, WithExitCode):
    """
    Interface required when using more than one presenter
    inside a route/command, so MyPy can do it's job!
    """
