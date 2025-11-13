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

from datetime import timedelta
from typing import Any

from flask import Flask, g, get_flashed_messages, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from bl_hector import __version__
from bl_hector.infrastructure.flask import services
from bl_hector.infrastructure.flask.aliases import blueprint as aliases
from bl_hector.infrastructure.flask.auth import blueprint as auth
from bl_hector.infrastructure.flask.books import blueprint as books
from bl_hector.infrastructure.flask.utils import presenter_to_response
from bl_hector.infrastructure.settings import WsgiSettings
from bl_hector.interfaces import l10n
from bl_hector.interfaces.exceptions import BadRequest
from bl_hector.interfaces.to_http import as_html


def build_app(settings: WsgiSettings) -> Flask:
    services.define_settings(settings)

    app = Flask(__name__)

    if settings.PROXIED:
        app.wsgi_app = ProxyFix(  # type: ignore[method-assign]
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

    app.config.update(
        SECRET_KEY=settings.SECRET_KEY,
        SESSION_COOKIE_NAME=settings.COOKIE_NAME,
        PERMANENT_SESSION_LIFETIME=timedelta(days=settings.SESSION_DURATION_DAYS),
    )

    register_blueprints(app, settings)
    register_jinja_globals()

    app.teardown_appcontext(services.teardown_connection)

    @app.before_request
    def guess_locale() -> None:
        g.locale = (
            request.accept_languages.best_match(l10n.LOCALES) or l10n.DEFAULT_LOCALE
        )

    @app.errorhandler(BadRequest)  # type: ignore[type-var]
    @presenter_to_response
    def handle_bad_request(e: Exception) -> Any:
        presenter = as_html.BadRequest(user=services.get_user())
        return presenter

    return app


def register_blueprints(app: Flask, settings: WsgiSettings) -> None:
    app.register_blueprint(aliases, url_prefix="/")
    app.register_blueprint(books, url_prefix="/books")

    app.register_blueprint(auth, url_prefix="/auth")
    app.auth_links = []  # type: ignore[attr-defined]
    if settings.AUTHORIZED_IP:
        from bl_hector.infrastructure.flask.ip import blueprint as ip

        app.register_blueprint(ip, url_prefix="/auth/ip")
        app.auth_links.append(  # type: ignore[attr-defined]
            {"route": "ip.login", "label": "IP", "icon": "network-wired"}
        )
    if settings.WEBAUTHN:
        from bl_hector.infrastructure.flask.webauthn import blueprint as webauthn

        app.register_blueprint(webauthn, url_prefix="/auth/webauthn")
        app.auth_links.append(  # type: ignore[attr-defined]
            {"route": "webauthn.login", "label": "WebAuthn", "icon": "key"}
        )
    if settings.TOTP:
        from bl_hector.infrastructure.flask.totp import blueprint as totp

        app.register_blueprint(totp, url_prefix="/auth/totp")
        app.auth_links.append(  # type: ignore[attr-defined]
            {"route": "totp.login", "label": "TOTP", "icon": "clock"}
        )


def register_jinja_globals() -> None:
    from bl_hector.interfaces.to_http import as_html as presenters

    presenters.register_jinja_global("version", __version__)
    presenters.register_jinja_global("url_for", url_for)
    presenters.register_jinja_global("get_flashed_messages", get_flashed_messages)
