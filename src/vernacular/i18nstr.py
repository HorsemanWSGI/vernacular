import typing as t
from frozendict import frozendict


class i18nstr(str):

    __slots__ = ('domain', 'context', 'default', 'mapping')

    def __new__(self,
                msgid: t.Union[str, 'i18nstr'],
                domain: t.Optional[str] = None,
                default: t.Optional[str] = None,
                mapping: t.Optional[t.Mapping] = None,
                context: t.Optional[t.Any] = None):

        self = super().__new__(self, str(msgid))
        if isinstance(msgid, self.__class__):
            domain = domain or msgid.domain
            context = context or msgid.context
            default = default or msgid.default
            mapping = mapping or msgid.mapping
        self.domain = domain
        self.context = context
        self.default = default or str(msgid)
        self.mapping = mapping and frozendict(mapping) or None
        return self

    def replace(self, **kwargs) -> 'i18nstr':
        return self.__class__(self, **kwargs)
