import typing as t
from string import Template
from vernacular.i18nstr import i18nstr
from vernacular.store import Translations


class Translator:

    __slots__ = ('translations', 'default_domain', 'default_language')

    def __init__(self,
                 translations: Translations,
                 default_domain: str = 'messages',
                 default_language: str = 'en_US'):
        self.translations = translations
        self.default_domain = default_domain
        self.default_language = default_language

    def translate(self,
                  phrase: t.Union[i18nstr, str],
                  domain=None,
                  mapping=None,
                  context=None,
                  default=None,
                  target_language=None):
        if not isinstance(phrase, i18nstr):
            phrase = i18nstr(
                phrase,
                domain=domain or self.default_domain,
                mapping=mapping,
                context=context,
                default=default
            )
        else:
            phrase = phrase.replace(
                domain=domain or phrase.domain or self.default_domain,
                mapping=mapping,
                context=context,
                default=default
            )

        target_language = target_language or self.default_language
        translated = None
        if trdomain := self.translations.get(phrase.domain):
            translated = trdomain.lookup(phrase, target_language)
        if translated is None:
            translated = phrase.default
        if translated and '$' in translated and phrase.mapping:
            return Template(translated).safe_substitute(phrase.mapping)

        return translated

    def pluralize(self,
                  singular: str, plural: str, num: int,
                  domain=None,
                  mapping=None,
                  context=None,
                  target_language=None):
        domain = domain or self.default_domain
        target_language = target_language or self.default_language
        translated = None
        if trdomain := self.translations.get(domain):
            translated = trdomain.nlookup(
                singular, plural, num, target_language)
        if translated and '$' in translated and mapping:
            return Template(translated).safe_substitute(mapping)
        return translated
