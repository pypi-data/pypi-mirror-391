# Hector --- A collection manager.
# Copyright © 2023, 2024 Bioneland
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
from urllib.parse import urlparse

from flask import g, request, session
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

from bl_hector.domain.administration.entities import RelyingParty
from bl_hector.infrastructure import DummyPermissions, SystemCalendar
from bl_hector.infrastructure.isbnlib import BookInfoProvider
from bl_hector.infrastructure.requests import CoverProvider
from bl_hector.infrastructure.settings import WsgiSettings
from bl_hector.infrastructure.sqlalchemy.repositories import (
    Books,
    Challenges,
    Credentials,
    Users,
)
from bl_hector.interfaces import User, l10n

__SETTINGS: Optional[WsgiSettings] = None


def define_settings(settings: WsgiSettings) -> None:
    global __SETTINGS
    __SETTINGS = settings


def get_settings() -> WsgiSettings:
    if not __SETTINGS:
        raise RuntimeError("You must define the settings!")
    return __SETTINGS


def get_connection() -> Connection:
    s = get_settings()
    if "connection" not in g:
        options: dict[str, Any] = {}
        if s.DEBUG_SQL:
            options["echo"] = True
            options["echo_pool"] = "debug"

        engine = create_engine(s.DSN, **options)
        g.setdefault("connection", engine.connect())

    return g.connection  # type: ignore[no-any-return]


def teardown_connection(exception: Optional[BaseException]) -> None:
    if connection := g.pop("connection", None):
        if exception:
            connection.rollback()
        else:
            connection.commit()
        connection.close()


def get_books() -> Books:
    return Books(get_connection())


def get_users() -> Users:
    return Users(get_connection())


def get_credentials() -> Credentials:
    return Credentials(get_connection())


def get_challenges() -> Challenges:
    return Challenges(get_connection())


def get_calendar() -> SystemCalendar:
    return SystemCalendar()


def get_permissions() -> DummyPermissions:
    return DummyPermissions()


def get_book_info_provider() -> BookInfoProvider:
    return BookInfoProvider()


def get_cover_provider() -> CoverProvider:
    return CoverProvider()


def get_user() -> User:
    if "user" not in g:
        if user_id := session.get("user_id", ""):
            permissions = get_permissions().for_user(user_id)
        else:
            permissions = []
        locale = g.get("locale", "")

        g.setdefault("user", User(user_id, locale, permissions))
    return g.user  # type: ignore[no-any-return]


def get_relying_party() -> RelyingParty:
    return RelyingParty(
        id=str(urlparse(request.base_url).hostname),
        name="hector",
        origin=f"http://{urlparse(request.base_url).hostname}:3000",
    )


def get_translator() -> l10n.Translator:
    user = get_user()
    return l10n.translator_for(user.locale if user else "")
