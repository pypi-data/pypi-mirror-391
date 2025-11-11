from typing import Any, Iterable

from data_sources.data_source import DataSource
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_params import BaseOperationParam
from data_sources.operations_results import BaseOperationResult


class FromNestedDataSource(Operation):
    def __init__(
        self,
        operations: list[Operation],
        result: BaseOperationResult,
        initial_params: Iterable[tuple[str, BaseOperationParam]] = None,
    ):
        super().__init__()
        self._operations = operations
        self._result = result
        self._initial_params = initial_params

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        data_source = DataSource(operations=self._operations)

        initial_params = None
        if self._initial_params is not None:
            initial_params = ((key, param.resolve(meta=meta)) for key, param in self._initial_params)

        res, _ = data_source.get_data(initial_data=None, initial_params=initial_params)

        result = self._result.resolve(
            operation_result=res,
            data_source_result=result,
            meta=meta,
        )
        return result, meta
