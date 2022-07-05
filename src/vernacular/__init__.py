import os
import typing as t
import logging
import contextvars
from pathlib import Path
from importlib.metadata import entry_points
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import starts_with, not_
from vernacular.store import Translation, Translations
from vernacular.utils import iter_translation_files


Logger = logging.getLogger(__name__)
COMPILE = os.environ.get('COMPILE_MO_FILES', False)
Language = contextvars.ContextVar('language')


def translations(path: Path) -> t.List[Translation]:
    return [
        Translation(domain=mofile.stem, locale=locale, mofile=mofile)
        for locale, mofile in iter_translation_files(
                path, can_compile=COMPILE
        )
    ]


def from_entrypoints(
        restrict: t.Optional[BaseMatcher] = not_(starts_with('test_')),
        key: str = 'vernacular.translation_directory'):
    translations = Translations()
    eps = entry_points()
    if (i18n_defs := eps.get(key)) is not None:
        for definition in i18n_defs:
            if restrict and not restrict.matches(definition.name):
                continue

            i18_files = definition.load()
            for translation in i18_files():
                translations.add(translation)
                Logger.debug(
                    f"Loading i18n registration: {translation}."
                )
    return translations


def translations_test_folder():
    return translations(Path(__file__).parent / 'locales')


def clean_translations_test_folder():
    """removes all the .mo - for test purposes
    """
    path = Path(__file__).parent / 'locales'
    for lang in path.iterdir():
        messages = lang / 'LC_MESSAGES'
        for child in messages.iterdir():
            if child.suffix == '.mo':
                child.unlink()
