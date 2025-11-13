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

from functools import wraps
from typing import Any, Callable

from flask import Response, request

from bl_hector.interfaces.to_http import HttpPresenter


class Htmx:
    def __bool__(self) -> bool:
        return "HX-Request" in request.headers

    @property
    def target(self) -> str:
        return request.headers.get("HX-Target", "")


def presenter_to_response(f: Callable[..., HttpPresenter]) -> Callable[[], Response]:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Response:
        presenter = f(*args, **kwargs)
        return Response(
            status=presenter.status_code(),
            headers=presenter.headers(),
            response=presenter.data(),
        )

    return decorated_function


htmx = Htmx()
