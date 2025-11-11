from typing import Any

from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta
from data_sources.operations.store_in_meta import StoreInMeta


class FetchRequestOperation(StoreInMeta):
    def _get_meta_key(self, meta: Meta) -> str:
        return DataSourceKeys.REQUEST

    def _get_value(self, meta: Meta) -> Any:
        initial = meta.get(DataSourceKeys.INITIAL_DATA)
        return initial.request
