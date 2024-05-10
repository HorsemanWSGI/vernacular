import gettext
import typing as t
from pathlib import Path
import langcodes


class Translation(t.NamedTuple):
    domain: str
    locale: str
    mofile: Path


Language = t.Dict[str, gettext.GNUTranslations]


class Domain(t.Dict[str, Language]):

    domain: str

    def __init__(self, domain: str, *args, **kwargs):
        self.domain = domain
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Translation domain "{self.domain}">'

    def add(self, translation: Translation):
        if translation.domain != self.domain:
            raise ValueError(
                f'{self!r} can only contain translations from '
                f'domain {self.domain}. Got {translation.domain}'
            )
        try:
            tag = langcodes.Language.get(translation.locale)
        except ValueError:
            return None
        if tag.language not in self:
            language = self[tag.language] = {}
        else:
            language = self[tag.language]

        with translation.mofile.open('rb') as fp:
            catalog = gettext.GNUTranslations(fp=fp)

        if tag.territory is not None:
            if None not in language:
                # we are creating a locale in this language but we have
                # no root
                root = language[None] = gettext.GNUTranslations(fp=None)
                # there was no parse. Init the catalog
                root._catalog = {}
                root.plural = catalog.plural
            else:
                root = language[None]
            catalog.add_fallback(root)

        if tag.territory in language:
            language[tag.territory]._catalog.update(catalog._catalog)
        else:
            language[tag.territory] = catalog

    def lookup(self, entry: str, language: str):
        tag = langcodes.Language.get(language)
        if catalogs := self.get(tag.language):
            catalog = catalogs[None]
            if tag.territory:
                catalog = catalogs.get(tag.territory, catalog)
            return catalog.gettext(entry)

    def nlookup(self, singular: str, plural: str, num: int, language: str):
        tag = langcodes.Language.get(language)
        if catalogs := self.get(tag.language):
            catalog = catalogs[None]
            if tag.territory:
                catalog = catalogs.get(tag.territory, catalog)
            return catalog.ngettext(singular, plural, num)


class Translations(t.Dict[str, Domain]):

    def add(self, translation: Translation):
        if translation.domain not in self:
            self[translation.domain] = Domain(translation.domain)
        self[translation.domain].add(translation)
