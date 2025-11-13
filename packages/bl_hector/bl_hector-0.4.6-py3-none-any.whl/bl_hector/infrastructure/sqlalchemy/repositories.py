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
from typing import Any, Optional

from sqlalchemy import Column
from sqlalchemy import Date as DateType
from sqlalchemy import (
    DateTime,
    LargeBinary,
    MetaData,
    SmallInteger,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import Connection

from bl_hector.domain.administration.entities import Challenge, Credential, User
from bl_hector.domain.administration.repositories import Challenges as IChallenges
from bl_hector.domain.administration.repositories import Credentials as ICredentials
from bl_hector.domain.administration.repositories import Users as IUsers
from bl_hector.domain.administration.value_objects import (
    ChallengeId,
    ChallengeValue,
    UserId,
)
from bl_hector.domain.collection_management.entities import Book
from bl_hector.domain.collection_management.errors import UnknownBook
from bl_hector.domain.collection_management.repositories import Books as IBooks
from bl_hector.domain.collection_management.value_objects import (
    Author,
    Cover,
    Date,
    Genre,
    Isbn,
    Title,
    Year,
)

META_DATA = MetaData()
DEFAULT_PAGE_SIZE = 100


books = Table(
    "books",
    META_DATA,
    Column("isbn", String(Isbn.MAX), primary_key=True),
    Column("title", String(Title.MAX)),
    Column("year", SmallInteger()),
    Column("authors", String()),
    Column("genres", String()),
    Column("cover", String()),
    Column("added_on", DateType()),
    Column("updated_on", DateType()),
)


class Books(IBooks):
    def __init__(self, connection: Connection) -> None:
        self.__connection = connection

    def by_isbn(self, isbn: Isbn) -> Optional[Book]:
        stmt = select(books).where(books.c.isbn == str(isbn)).limit(1)
        if row := self.__connection.execute(stmt).first():
            return self.__row_to_book(row)
        return None

    def search(
        self,
        /,
        *,
        isbn: Optional[Isbn] = None,
        title: Optional[Title] = None,
        year: Optional[Year] = None,
        author: Optional[Author] = None,
        genre: Optional[Genre] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> list[Book]:
        stmt = select(books)
        if isbn:
            stmt = stmt.where(books.c.isbn == str(isbn))
        if title:
            stmt = stmt.where(books.c.title.contains(str(title)))
        if year:
            stmt = stmt.where(books.c.year == int(year))
        if author:
            stmt = stmt.where(books.c.authors.contains(str(author)))
        if genre:
            stmt = stmt.where(books.c.genres.contains(str(genre)))

        stmt = stmt.order_by(books.c.year.desc()).order_by(books.c.title)

        if page_number:
            size = page_size or DEFAULT_PAGE_SIZE
            stmt = stmt.offset((page_number - 1) * size)
            stmt = stmt.limit(size)

        return [self.__row_to_book(row) for row in self.__connection.execute(stmt)]

    def __row_to_book(self, row: Any) -> Book:
        return Book(
            Date(row.added_on),
            Date(row.updated_on),
            Isbn(row.isbn),
            Title(row.title),
            Year(row.year),
            [Author(r.strip()) for r in row.authors.split(",") if r],
            [Genre(r.strip()) for r in row.genres.split(",") if r],
            Cover(row.cover) if row.cover else None,
        )

    def add(self, book: Book) -> None:
        stmt = insert(books).values(
            added_on=book.added_on.to_date(),
            updated_on=book.updated_on.to_date(),
            isbn=str(book.isbn),
            title=str(book.title),
            year=int(book.year),
            authors=", ".join([str(a) for a in book.authors]),
            genres=", ".join([str(g) for g in book.genres]),
            cover=str(book.cover) if book.cover else None,
        )
        self.__connection.execute(stmt)

    def update(self, book: Book) -> None:
        if not self.by_isbn(book.isbn):
            raise UnknownBook(str(book.isbn))
        stmt = (
            update(books)
            .values(
                updated_on=book.updated_on.to_date(),
                title=str(book.title),
                year=int(book.year),
                authors=", ".join([str(a) for a in book.authors]),
                genres=", ".join([str(g) for g in book.genres]),
                cover=str(book.cover) if book.cover else None,
            )
            .where(books.c.isbn == str(book.isbn))
        )
        self.__connection.execute(stmt)


users = Table(
    "users",
    META_DATA,
    Column("id", String(UserId.MAX), primary_key=True),
    Column("login", String()),
    Column("name", String()),
)


class Users(IUsers):
    def __init__(self, connection: Connection) -> None:
        self.__connection = connection

    def by_login(self, login: str) -> Optional[User]:
        stmt = select(users).where(users.c.login == login).limit(1)
        if row := self.__connection.execute(stmt).first():
            return User(UserId(row.id), row.login, row.name)
        return None

    def add(self, user: User) -> None:
        stmt = insert(users).values(
            id=str(user.id),
            login=user.login,
            name=user.name,
        )
        self.__connection.execute(stmt)


credentials = Table(
    "credentials",
    META_DATA,
    Column("id", LargeBinary(), primary_key=True),
    Column("public_key", LargeBinary()),
    Column("user_id", String(UserId.MAX)),
)


class Credentials(ICredentials):
    def __init__(self, connection: Connection) -> None:
        self.__connection = connection

    def for_user(self, user: User) -> list[Credential]:
        stmt = select(credentials).where(credentials.c.user_id == str(user.id))
        return [
            Credential(row.id, row.public_key, UserId(row.user_id))
            for row in self.__connection.execute(stmt).all()
        ]

    def add(self, creds: Credential) -> None:
        stmt = insert(credentials).values(
            id=creds.id,
            public_key=creds.public_key,
            user_id=str(creds.user_id),
        )
        self.__connection.execute(stmt)


challenges = Table(
    "challenges",
    META_DATA,
    Column("id", String(ChallengeId.MAX), primary_key=True),
    Column("value", String(ChallengeValue.MAX)),
    Column("expiration", DateTime()),
    Column("user_id", String(UserId.MAX)),
)


class Challenges(IChallenges):
    def __init__(self, connection: Connection) -> None:
        self.__connection = connection

    def add(self, challenge: Challenge) -> None:
        self.__clean_up_for(challenge.user_id)

        stmt = insert(challenges).values(
            id=str(challenge.id),
            value=str(challenge.value),
            expiration=challenge.expiration,
            user_id=str(challenge.user_id),
        )
        self.__connection.execute(stmt)

    def __clean_up_for(self, user_id: UserId) -> None:
        stmt = delete(challenges).where(challenges.c.user_id == str(user_id))
        self.__connection.execute(stmt)

    def valid_for(self, user: User, now: datetime.datetime) -> Optional[Challenge]:
        stmt = (
            select(challenges)
            .where(challenges.c.user_id == str(user.id))
            .where(challenges.c.expiration > now)
        )
        if result := self.__connection.execute(stmt).first():
            return Challenge(
                ChallengeId(result.id),
                ChallengeValue(result.value),
                result.expiration,
                UserId(result.user_id),
            )
        return None
