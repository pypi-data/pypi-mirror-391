from typing import Any

from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_results import BaseOperationResult


class StoreOperation(Operation):
    def __init__(self, result: BaseOperationResult, data: Any):
        self._result = result
        self._data = data

    def handle(self, result: BaseOperationResult, meta: Meta) -> tuple[BaseOperationResult, Meta]:
        result = self._result.resolve(
            operation_result=self._data,
            data_source_result=result,
            meta=meta,
        )
        return result, meta
