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

from typing import Any, cast
from uuid import uuid4

import pyotp
from flask import Blueprint, flash, request, session, url_for

from bl_hector.domain.administration.entities import User
from bl_hector.domain.administration.value_objects import UserId
from bl_hector.infrastructure import ONLY_USER
from bl_hector.infrastructure.flask import services
from bl_hector.infrastructure.flask.utils import presenter_to_response
from bl_hector.infrastructure.settings import TotpSettings
from bl_hector.interfaces.to_http import Redirection, as_html

blueprint = Blueprint("totp", __name__)


@blueprint.get("/login")
@presenter_to_response
def login() -> Any:
    return as_html.SimplePresenter("totp/login", user=services.get_user())


@blueprint.post("/login")
@presenter_to_response
def login_POST() -> Any:
    _ = services.get_translator()
    # TOTP settings must be defined for this route to be accessible.
    # Other alternatives: 1) check presence with `if` or 2) ignore type.
    TOTP = cast(TotpSettings, services.get_settings().TOTP)

    totp = pyotp.TOTP(TOTP.SECRET)
    if not totp.verify(request.form.get("password", "")):
        flash(_("totp-login-error"), "error")
        return Redirection(url_for("totp.login"))

    if not (user := services.get_users().by_login(ONLY_USER)):
        user = User(UserId(str(uuid4())), ONLY_USER, "The only user")
        services.get_users().add(user)

    session["user_id"] = user.id

    flash(_("totp-login-success"), "success")
    return Redirection(url_for("auth.redirect"))
