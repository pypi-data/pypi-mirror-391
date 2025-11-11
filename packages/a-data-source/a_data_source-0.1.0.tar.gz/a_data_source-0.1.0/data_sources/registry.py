from __future__ import annotations

from copy import copy
from typing import Iterable, TypeVar, Generic


class AlreadyRegisteredError(Exception):
    pass


class KeyNotFoundError(Exception):
    pass


KeyT = TypeVar('KeyT')
ValueT = TypeVar('ValueT')


class Registry(Generic[KeyT, ValueT]):
    __slots__ = ('_registry',)

    def __init__(self):
        self._registry: dict[KeyT, ValueT] = {}

    def __copy__(self) -> Registry[KeyT, ValueT]:
        cls = self.__class__
        result = cls.__new__(cls)
        result._registry = copy(self._registry)
        return result

    def register(
        self,
        registry_key: KeyT,
        registry_value: ValueT,
        overwrite: bool = False,
    ):
        if registry_key in self._registry and not overwrite:
            raise AlreadyRegisteredError(f'Key `{registry_key}` already registered.')

        self._registry[registry_key] = registry_value

    def get_for_key(self, registry_key: KeyT) -> ValueT:
        try:
            return self._registry[registry_key]
        except KeyError:
            raise KeyNotFoundError(f'Unknown key `{registry_key}`.')

    def get_or_default(self, registry_key: KeyT, default: ValueT) -> ValueT:
        try:
            return self.get_for_key(registry_key=registry_key)
        except KeyNotFoundError:
            return default

    def have_key(self, registry_key: KeyT) -> bool:
        return True if registry_key in self._registry else False

    def __iter__(self) -> Iterable[tuple[KeyT, ValueT]]:
        return iter(self._registry.items())

    def get_keys(self) -> Iterable[KeyT]:
        return self._registry.keys()
