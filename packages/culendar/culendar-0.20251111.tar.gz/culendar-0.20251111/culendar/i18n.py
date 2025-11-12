import importlib.resources
from gettext import translation
from locale import (
    LC_ALL,
    Error,
    setlocale,
)
from os import environ
from pathlib import Path
from sys import (
    platform,
    stderr,
)
from typing import (
    Callable,
    cast,
)

DOMAIN = 'culendar'


def get_default_lang() -> str:
    """Inspired from gajim source code"""
    if platform == 'win32':
        from ctypes import windll  # type: ignore[attr-defined]
        from locale import windows_locale
        user_default_ui_language = windll.kernel32.GetUserDefaultUILanguage()
        return windows_locale[user_default_ui_language]
    elif platform == 'darwin':
        from AppKit import NSLocale  # type: ignore
        return NSLocale.currentLocale().languageCode()
    else:
        from locale import getdefaultlocale
        return getdefaultlocale()[0] or 'en'


def get_translation_func() -> Callable:
    try:
        setlocale(LC_ALL, '')
    except Error as error:
        print(error, file=stderr)
    LANG = get_default_lang()
    if platform == 'win32':
        # Set the env var on Windows because gettext.find() uses it to find the translation
        # Use LANGUAGE instead of LANG to keep settings like LC_TIME
        environ['LANGUAGE'] = LANG
    package_dir = cast(Path, importlib.resources.files(DOMAIN))
    locale_dir = package_dir / 'locale'
    try:
        _translation = translation(DOMAIN, locale_dir)
        _gettext = _translation.gettext
        try:
            from locale import bindtextdomain as locale_bindtextdomain
            locale_bindtextdomain(DOMAIN, locale_dir)
        except ImportError:
            pass
    except OSError:
        from gettext import NullTranslations
        _translation = NullTranslations()  # type: ignore[assignment]
        _gettext = _translation.gettext
        print('No translations found for', LANG, file=stderr)
    return _gettext


_ = get_translation_func()

__all__ = ['_']
