from typing import Iterable, Any, Callable

from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_params import BaseOperationParam
from data_sources.operations_results import BaseOperationResult


class Sort(Operation):
    def __init__(
        self,
        entities: BaseOperationParam[Iterable[Any]],
        result: BaseOperationResult,
        sort_key: Callable[[Any], Any] = None,
        reverse: bool = False,
    ):
        super().__init__()
        self._entities_param = entities
        self._result = result

        self._sort_key = sort_key
        self._reverse = reverse

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities = self._entities_param.resolve(meta=meta)

        sorted_entities = sorted(entities, key=self._sort_key, reverse=self._reverse)

        result = self._result.resolve(
            operation_result=sorted_entities,
            data_source_result=result,
            meta=meta,
        )

        return result, meta
