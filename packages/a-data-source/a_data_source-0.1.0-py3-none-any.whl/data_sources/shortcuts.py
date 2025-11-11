from __future__ import annotations

from typing import Any, Iterable

from data_sources.data_source import DataSource
from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.operations.operation import Operation


def get_data_for_operations(
    operations: list[Operation],
    initial_data: Any = None,
    initial_params: Iterable[tuple[str, Any]] | None = None,
    exception_handlers: list[ExceptionHandler] | None = None,
) -> Any:
    """
    Build DataSource and run it for the initial data.
    """
    data_source = DataSource(
        operations=operations,
        exception_handlers=exception_handlers,
    )
    data, _ = data_source.get_data(initial_data=initial_data, initial_params=initial_params)
    return data
