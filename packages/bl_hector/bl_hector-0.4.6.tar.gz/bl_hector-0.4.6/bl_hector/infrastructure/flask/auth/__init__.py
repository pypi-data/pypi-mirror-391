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

from typing import Any

from flask import Blueprint, current_app, flash, request, session, url_for

from bl_hector.infrastructure.flask import services
from bl_hector.infrastructure.flask.utils import presenter_to_response
from bl_hector.interfaces.to_http import Redirection, as_html

blueprint = Blueprint("auth", __name__)


@blueprint.get("")
@presenter_to_response
def root() -> Any:
    return Redirection(url_for("books.search"))


@blueprint.get("/login")
@presenter_to_response
def login() -> Any:
    session.permanent = True
    session["redirect"] = request.referrer

    auth_links = current_app.auth_links  # type: ignore[attr-defined]
    if not auth_links:
        return Redirection(url_for("aliases.root"))
    if len(auth_links) == 1:
        return Redirection(url_for(auth_links[0]["route"]))
    return as_html.SimplePresenter(
        "auth/login", links=auth_links, user=services.get_user()
    )


@blueprint.get("/redirect")
@presenter_to_response
def redirect() -> Any:
    if url := session.get("redirect", ""):
        del session["redirect"]
        return Redirection(url)
    return Redirection(url_for("aliases.root"))


@blueprint.get("/logout")
@presenter_to_response
def logout() -> Any:
    session.clear()
    flash(services.get_translator()("auth-logged-out"), "info")
    return Redirection(request.referrer or url_for("aliases.root"))
