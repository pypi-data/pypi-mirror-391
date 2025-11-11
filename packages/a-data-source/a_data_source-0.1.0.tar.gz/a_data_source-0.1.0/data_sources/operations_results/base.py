from typing import Any

from data_sources.keys import DataSourceKey
from data_sources.meta import Meta


class BaseOperationResult:
    """
    Base class for operation result.

    This class can be used to allow the caller to specify how the operation should work,
    when it's unclear what should be done with the result of an operation.
    For example, store it to the meta (and if so - under which key) or return it as a result of the data source.
    """
    def resolve(self, operation_result: Any, data_source_result: Any, meta: Meta) -> Any:
        raise NotImplementedError


class StoreOperationResultInMeta(BaseOperationResult):
    """
    Stores operation result to the meta.
    """
    def __init__(self, key: DataSourceKey, allow_modification: bool = False):
        super().__init__()
        self._allow_modification = allow_modification
        self._key = key

    def resolve(self, operation_result: Any, data_source_result: Any, meta: Meta) -> Any:
        if self._allow_modification:
            meta.add_or_modify(key=self._key, value=operation_result)
        else:
            meta.add(key=self._key, value=operation_result)

        return data_source_result


class ReturnAsOperationResult(BaseOperationResult):
    """
    Returns operation result as a result of the data source.
    """
    def resolve(self, operation_result: Any, data_source_result: Any, meta: Meta) -> Any:
        return operation_result
