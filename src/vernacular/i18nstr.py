import typing as t
from frozendict import frozendict


class i18nstr(str):

    __slots__ = ('domain', 'context', 'default', 'mapping')

    def __new__(cls,
                msgid: t.Union[str, 'i18nstr'],
                domain: t.Optional[str] = None,
                default: t.Optional[str] = None,
                mapping: t.Optional[t.Mapping] = None,
                context: t.Optional[t.Any] = None):

        inst = super().__new__(cls, str(msgid))
        if isinstance(msgid, inst.__class__):
            domain = domain or msgid.domain
            context = context or msgid.context
            default = default or msgid.default
            mapping = mapping or msgid.mapping
        inst.domain = domain
        inst.context = context
        inst.default = default or str(msgid)
        inst.mapping = mapping and frozendict(mapping) or None
        return inst

    def rebind(self, **kwargs) -> 'i18nstr':
        return self.__class__(self, **kwargs)
