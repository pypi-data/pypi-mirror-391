# TODO: Read config from pyproject.toml and fail if config is not found
import gettext
import logging
import os
from contextvars import ContextVar

from babel import Locale, UnknownLocaleError
from fastapi import Request

logger = logging.getLogger("fastapi_i18n")

LOCALE_DEFAULT = os.getenv("FASTAPI_I18N__LOCALE_DEFAULT", "en")


class Translator:
    def __init__(self, locale: str):
        locale_dir = os.getenv("FASTAPI_I18N__LOCALE_DIR")
        self.translations = gettext.translation(
            domain="messages",
            localedir=locale_dir,
            languages=[locale],
            fallback=True,
        )

    def translate(self, message: str):
        return self.translations.gettext(message)


locale: ContextVar[str] = ContextVar("locale")
translator: ContextVar[Translator] = ContextVar("translator")


async def i18n(request: Request):
    accept_language = request.headers.get("Accept-Language", LOCALE_DEFAULT)

    referer = request.headers.get("Referer", None)
    ignore_referes = os.getenv("FASTAPI_I18N__IGNORE_REFERERS", "").split(",")
    if referer in ignore_referes:
        accept_language = LOCALE_DEFAULT

    locale_value = extract_locale(accept_language)
    token_locale = locale.set(locale_value)
    token_translator = translator.set(Translator(locale=locale_value))
    try:
        yield
    finally:
        locale.reset(token_locale)
        translator.reset(token_translator)


def _(message: str) -> str:
    try:
        return translator.get().translate(message)
    except LookupError:
        logger.debug(
            "FastAPI I18N translator is not set. Returning message untranslated."
        )
        return message


def get_locale() -> str:
    """Get the current setting for locale."""
    try:
        return locale.get()
    except LookupError:
        return os.getenv("FASTAPI_I18N__LOCALE_DEFAULT", "en")


def parse_accept_language(accept_language: str) -> list[str]:
    """Return locale parts from Accept-Language header value."""
    languages = accept_language.split(",")
    locales = []

    for language in languages:
        if ";" in language:
            locale, _ = language.split(";")
        else:
            locale = language
        locales.append(locale.strip().replace("-", "_"))

    return locales


def extract_locale(accept_language: str) -> str:
    """Extract preferred locale from Accept-Language header value."""
    locales = parse_accept_language(accept_language)
    locale = locales[0]
    try:
        Locale.parse(locale)  # validate
    except UnknownLocaleError as error:
        logger.exception(
            (
                "Accept-Language header is set but contains unknown locale. "
                "Fallback to default locale."
            ),
            exc_info=error,
        )
        locale = LOCALE_DEFAULT
    return locale
