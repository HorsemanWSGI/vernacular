import gettext
import typing as t
from pathlib import Path
from vernacular.utils import parse_locale


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
        tag = parse_locale(translation.locale)
        if tag.language not in self:
            language = self[tag.language] = {}
        else:
            language = self[tag.language]

        with translation.mofile.open('rb') as fp:
            catalog = gettext.GNUTranslations(fp=fp)

        if tag.variant is not None:
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

        if tag.variant in language:
            language[tag.variant]._catalog.update(catalog._catalog)
        else:
            language[tag.variant] = catalog

    def lookup(self, entry: str, language: str):
        tag = parse_locale(language)
        if catalogs := self.get(tag.language):
            catalog = catalogs[None]
            if tag.variant:
                catalog = catalogs.get(tag.variant, catalog)
            return catalog.gettext(entry)

    def nlookup(self, singular: str, plural: str, num: int, language: str):
        tag = parse_locale(language)
        if catalogs := self.get(tag.language):
            catalog = catalogs[None]
            if tag.variant:
                catalog = catalogs.get(tag.variant, catalog)
            return catalog.ngettext(singular, plural, num)


class Translations(t.Dict[str, Domain]):

    def add(self, translation: Translation):
        if translation.domain not in self:
            self[translation.domain] = Domain(translation.domain)
        self[translation.domain].add(translation)
