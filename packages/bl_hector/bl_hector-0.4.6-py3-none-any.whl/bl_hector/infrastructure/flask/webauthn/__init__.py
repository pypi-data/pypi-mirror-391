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

from datetime import datetime as dt
from http import HTTPStatus as HTTP
from typing import Any
from uuid import uuid4

from flask import Blueprint, request, session, url_for

from bl_hector.domain.administration.entities import User
from bl_hector.domain.administration.services import create_challenge_for
from bl_hector.domain.administration.value_objects import UserId
from bl_hector.infrastructure import ONLY_USER
from bl_hector.infrastructure.flask import services
from bl_hector.infrastructure.flask.utils import presenter_to_response
from bl_hector.interfaces.to_http import Redirection, as_html, as_json

from . import security

blueprint = Blueprint("webauthn", __name__)


@blueprint.get("/login")
@presenter_to_response
def login() -> Any:
    # For the time being, Hector only has one user with one credential
    if not (user := services.get_users().by_login(ONLY_USER)):
        return Redirection(url_for("webauthn.register"))

    if not (credentials := services.get_credentials().for_user(user)):
        return Redirection(url_for("webauthn.register"))

    challenge = create_challenge_for(user)
    services.get_challenges().add(challenge)

    return as_html.SimplePresenter(
        "webauthn/login",
        user=services.get_user(),
        options=security.authentication_options(
            services.get_relying_party(), user, credentials, challenge
        ),
    )


@blueprint.post("/verify-credential")
@presenter_to_response
def verify_credential() -> Any:
    if not (user := services.get_users().by_login(ONLY_USER)):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    if not (challenge := services.get_challenges().valid_for(user, dt.now())):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    if not (credentials := services.get_credentials().for_user(user)):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    if not security.verify_credentials(
        request.get_data(),
        challenge,
        services.get_relying_party(),
        user,
        credentials,
    ):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    session["user_id"] = user.id
    return as_json.Dict({"verified": True}, status_code=HTTP.OK)


@blueprint.get("/register")
@presenter_to_response
def register() -> Any:
    if not (user := services.get_users().by_login(ONLY_USER)):
        user = User(UserId(str(uuid4())), ONLY_USER, "The only user")
        services.get_users().add(user)

    if services.get_credentials().for_user(user):
        return Redirection(url_for("webauthn.login"))

    challenge = create_challenge_for(user)
    services.get_challenges().add(challenge)

    return as_html.SimplePresenter(
        "webauthn/register",
        user=services.get_user(),
        options=security.credential_creation_options(
            services.get_relying_party(), user, challenge
        ),
    )


@blueprint.post("/add-credential")
@presenter_to_response
def add_credential() -> Any:
    if not (user := services.get_users().by_login(ONLY_USER)):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    if not (challenge := services.get_challenges().valid_for(user, dt.now())):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    if not (
        credential := security.parse_credentials(
            request.get_data(), challenge, services.get_relying_party(), user
        )
    ):
        return as_json.Dict({"verified": False}, status_code=HTTP.BAD_REQUEST)

    services.get_credentials().add(credential)
    return as_json.Dict({"verified": True}, status_code=HTTP.CREATED)
