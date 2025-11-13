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

from flask import Blueprint, flash, request, session, url_for

from bl_hector.infrastructure.flask import services
from bl_hector.infrastructure.flask.utils import presenter_to_response
from bl_hector.interfaces.to_http import Redirection

blueprint = Blueprint("ip", __name__)


@blueprint.get("/login")
@presenter_to_response
def login() -> Any:
    _ = services.get_translator()
    if not authorized():
        flash(_("ip-login-error"), "error")
        return Redirection(url_for("auth.login"))

    session["user_id"] = "anonymous"

    flash(_("ip-login-success"), "success")
    return Redirection(url_for("auth.redirect"))


def authorized() -> bool:
    authorized_ip = services.get_settings().AUTHORIZED_IP
    client_ip = request.headers.get("X-Remote-IP", request.remote_addr) or ""
    return client_ip.startswith(authorized_ip.rstrip("*"))
