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

import bl3d

InvalidValue = bl3d.InvalidValue
StringTooShort = bl3d.StringTooShort
StringTooLong = bl3d.StringTooLong
NumberTooSmall = bl3d.NumberTooSmall
NumberTooBig = bl3d.NumberTooBig
DateAndTimeWithoutTimezone = bl3d.DateAndTimeWithoutTimezone
DurationNegative = bl3d.DurationNegative


class UnknownBook(InvalidValue):
    def __init__(self, isbn: str) -> None:
        self.isbn = isbn


class NotAnIsbn(InvalidValue):
    def __init__(self, isbn: str) -> None:
        self.isbn = isbn


class MissingAuthor(InvalidValue):
    def __init__(self) -> None:
        super().__init__("Missing author!")


class BeforeCreationOfIsbn(InvalidValue):
    def __init__(self, year: int) -> None:
        super().__init__("Before creation of the ISBN system!")
        self.year = year
