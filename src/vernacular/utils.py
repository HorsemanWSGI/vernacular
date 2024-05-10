import polib
import re
import logging
import typing as t
from pathlib import Path
from langcodes import Language
from langcodes.tag_parser import LanguageTagError


Logger = logging.getLogger(__name__)


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
    for langtag in root.iterdir():
        if langtag.is_dir():
            messages_dir = langtag / 'LC_MESSAGES'
            try:
                tag = Language.get(langtag.stem).to_tag()
            except LanguageTagError:
                Logger.warning(f'{langtag.stem} is not a valid language.')
            for filename in messages_dir.iterdir():
                if filename.suffix == '.po':
                    yield tag, filename


def iter_translation_files(root: Path, can_compile: bool = False):
    """Expects a classical gettext directory structure:
        {root}/{langtag}/LC_MESSAGES/{domain}.mo
    """
    for tag, pofile in iter_translation_sources(root):
        mofile = pofile.with_suffix('.mo')
        if can_compile:
            if compiled(pofile, mofile) == mofile:
                yield tag, mofile
        elif mofile.exists():
            yield tag, mofile
        else:
            Logger.warning(
                f'File {pofile} does not have a compiled version.')
