from __future__ import annotations

from typing import Any, Optional, Type

from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.meta import Meta


class ExceptionCatcherHandler(ExceptionHandler):
    def __init__(self):
        super().__init__()
        self._storage = []

    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        self._storage.append(exception)
        return 0  # we need to return not-None object in order to break error handling pipe

    def raised(self, exception_class: Type[Exception]) -> bool:
        for exc in self._storage:
            if isinstance(exc, exception_class):
                return True

        return False
