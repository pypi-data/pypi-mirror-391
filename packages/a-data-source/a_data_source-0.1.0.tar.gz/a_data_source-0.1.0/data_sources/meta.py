from __future__ import annotations

from copy import copy
from typing import Any, Iterable

from data_sources.keys import DataSourceKey
from data_sources.registry import AlreadyRegisteredError, Registry, KeyNotFoundError


class NotPresentInMeta(Exception):
    pass


class AlreadyPresentInMeta(Exception):
    pass


class Meta:
    """
    Container for metadata of all operations.

    Each operation could read or write metadata.
    """
    def __init__(self) -> None:
        self._container = Registry[DataSourceKey, Any]()

    def __copy__(self) -> Meta:
        cls = self.__class__
        result = cls.__new__(cls)
        result._container = copy(self._container)
        return result

    def add(self, key: DataSourceKey, value: Any) -> None:
        try:
            self._container.register(key, value)
        except AlreadyRegisteredError:
            raise AlreadyPresentInMeta()

    def add_or_modify(self, key: DataSourceKey, value: Any) -> None:
        self._container.register(key, value, overwrite=True)

    def get(self, key: DataSourceKey) -> Any:
        try:
            return self._container.get_for_key(key)
        except KeyNotFoundError:
            raise NotPresentInMeta(key)

    def keys(self) -> Iterable[DataSourceKey]:
        return self._container.get_keys()
