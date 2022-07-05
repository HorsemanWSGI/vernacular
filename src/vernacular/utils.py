import polib
import re
import logging
import typing as t
from pathlib import Path


Logger = logging.getLogger(__name__)
language_matcher = re.compile(r'^([a-z]{2,3})(?:[-_]([A-Z]{2,3}))?$')


class LanguageTag(t.NamedTuple):
    language: str
    variant: t.Optional[str] = None

    @property
    def locale(self):
        if not self.variant:
            return self.language
        return f'{self.language}-{self.variant}'


def parse_locale(locale: str) -> LanguageTag:
    matched = language_matcher.match(locale)
    if matched is None:
        raise ValueError(f'Invalid language code: {locale}')
    language, variant = matched.groups()
    return LanguageTag(language=language, variant=variant)


def compiled(pofile: Path, mofile: Path):
    """Creates or updates a mo file in the locales folder.
    """
    try:
        po_mtime = pofile.stat().st_mtime
    except (IOError, OSError):
        # please log.
        return

    if mofile.exists():
        # Update mo file?
        try:
            mo_mtime = mofile.stat().st_mtime
        except (IOError, OSError):
            # please log.
            return
    else:
        mo_mtime = 0

    if po_mtime > mo_mtime:
        try:
            po = polib.pofile(pofile)
            po.save_as_mofile(mofile)
        except (IOError, OSError) as e:
            logging.warn('Error while compiling %s (%s).' % (pofile, e))
            raise

    return mofile


def iter_translation_sources(root: Path):
    for locale in root.iterdir():
        if locale.is_dir():
            messages_dir = locale / 'LC_MESSAGES'
            for filename in messages_dir.iterdir():
                if filename.suffix == '.po':
                    yield locale.stem, filename


def iter_translation_files(root: Path, can_compile: bool = False):
    """Expects a classical gettext directory structure:
        {root}/{locale}/LC_MESSAGES/{domain}.mo
    """
    for locale, pofile in iter_translation_sources(root):
        mofile = pofile.with_suffix('.mo')
        if can_compile:
            if compiled(pofile, mofile) == mofile:
                yield locale, mofile
        elif mofile.exists():
            yield locale, mofile
        else:
            Logger.warning(
                f'File {pofile} does not have a compiled version.')
