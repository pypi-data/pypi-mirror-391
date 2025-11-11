from typing import Any

from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_results import BaseOperationResult


class FetchQueryParamsOperation(Operation):
    def __init__(self, query_param: str, result: BaseOperationResult, allow_multiple: bool = False):
        self._query_param = query_param
        self._result = result
        self._allow_multiple = allow_multiple

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        query_param_data = meta.get(DataSourceKeys.REQUEST).GET

        if self._allow_multiple:
            values = query_param_data.getlist(self._query_param)
        else:
            values = query_param_data.get(self._query_param)

        result = self._result.resolve(
            operation_result=values,
            data_source_result=result,
            meta=meta,
        )

        return result, meta
