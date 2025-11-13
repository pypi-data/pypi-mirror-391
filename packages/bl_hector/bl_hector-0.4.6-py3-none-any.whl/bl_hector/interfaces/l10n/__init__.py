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

from pathlib import Path
from typing import Any, Protocol

from fluent.runtime import FluentLocalization, FluentResourceLoader

DEFAULT_LOCALE = "en-GB"
LOCALES = [DEFAULT_LOCALE, "fr-FR"]
LOADER = FluentResourceLoader(str(Path(__file__).parent / "{locale}"))


class Translator(Protocol):
    def __call__(self, message_id: str, **kwargs: Any) -> str:
        ...


class DummyTranslator(Translator):
    def __call__(self, message_id: str, **kwargs: Any) -> str:
        return message_id


def localization(locale: str) -> FluentLocalization:
    if locale not in LOCALES:
        raise RuntimeError(f"Locale `{locale}` is not defined!")
    return FluentLocalization([locale] + LOCALES, ["main.ftl"], LOADER)


def translator_for(locale: str = DEFAULT_LOCALE) -> Translator:
    l10n = localization(locale or DEFAULT_LOCALE)

    def translate(message_id: str, **kwargs: Any) -> str:
        return str(l10n.format_value(message_id, kwargs))

    return translate
