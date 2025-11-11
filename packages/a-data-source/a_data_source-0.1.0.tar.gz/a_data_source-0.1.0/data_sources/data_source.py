from typing import Any, Iterable

from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.meta import Meta
from data_sources.keys import INITIAL_DATA
from data_sources.operations.operation import Operation


class DataSource:
    """
    DataSource provides a centralized data fetching and processing pipeline.

    It allows to define a sequence of operations to be applied to the data.
    However, operations results are not just passed to the next operation.
    Instead, operations results are stored in the Meta object.
    This allows to access the results of any previous operation in the current operation.
    Alternatively, results of operations could also be piped from one another.
    Both approaches are supported.
    """
    def __init__(self, operations: list[Operation], exception_handlers: list[ExceptionHandler] | None = None):
        self.operations: list[Operation] = operations
        self.exception_handlers: list[ExceptionHandler] = exception_handlers or []

    def get_data(
        self,
        initial_data: Any,
        initial_params: Iterable[tuple[str, Any]] | None = None,
    ) -> tuple[Any, Meta]:
        result, meta = self._initialize(initial_data, initial_params=initial_params)
        result, meta = self._run_operations(result, meta)
        return result, meta

    def _initialize(self, initial_data: Any, initial_params: Iterable[tuple[str, Any]] = None) -> tuple[None, Meta]:
        meta = Meta()
        meta.add(INITIAL_DATA, initial_data)
        if initial_params is not None:
            for key, value in initial_params:
                meta.add(key=key, value=value)
        return None, meta

    def _run_operations(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        for operation in self.operations:
            try:
                result, meta = operation.handle(result=result, meta=meta)
            except Exception as exc:
                return self._handle_exception(exception=exc, result=result, meta=meta)

        return result, meta

    def _handle_exception(self, exception: Exception, result: Any, meta: Meta) -> tuple[Any, Meta]:
        for handler in self.exception_handlers:
            handling_result = handler.handle(exception=exception, result=result, meta=meta)
            if handling_result is not None:
                if isinstance(handling_result, Exception):
                    raise handling_result
                else:
                    return handling_result, meta

        raise exception
