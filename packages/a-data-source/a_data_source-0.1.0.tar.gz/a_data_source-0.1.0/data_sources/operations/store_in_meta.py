from abc import ABC, abstractmethod
from typing import Any, Iterable

from data_sources.keys import DataSourceKey
from data_sources.meta import Meta
from data_sources.operations.operation import Operation


class StoreInMeta(Operation, ABC):
    """
    Operation which responsibility is to add values to the meta.
    """

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        meta.add(self._get_meta_key(meta=meta), self._get_value(meta=meta))

        return result, meta

    @abstractmethod
    def _get_meta_key(self, meta: Meta) -> DataSourceKey:
        pass

    @abstractmethod
    def _get_value(self, meta: Meta) -> Any:
        pass


class StoreInMetaMultipleParams(Operation, ABC):
    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        for k, v in self.get_params(meta):
            meta.add(k, v)

        return result, meta

    @abstractmethod
    def get_params(self, meta: Meta) -> Iterable[tuple[DataSourceKey, Any]]:
        pass


class ImplicitStoreInMetaParams(StoreInMetaMultipleParams):
    def __init__(self, params: Iterable[tuple[DataSourceKey, Any]]):
        self.params = params

    def get_params(self, meta: Meta) -> Iterable[tuple[DataSourceKey, Any]]:
        return self.params
