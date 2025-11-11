from __future__ import annotations

from rest_framework.exceptions import ValidationError, NotFound

from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.contrib.drf.errors import DRFEmptyResultError, PaginationParamsError


class DRFEmptyResultHandler(ExceptionHandler):
    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        if isinstance(exception, DRFEmptyResultError):
            return NotFound()


from typing import Any, Optional

from rest_framework.exceptions import NotFound

from api.error_codes import PAGE_OUT_OF_RANGE
from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.meta import Meta


class PaginationParamsErrorHandler(ExceptionHandler):
    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        if isinstance(exception, PaginationParamsError):
            return NotFound(exception.message, code=PAGE_OUT_OF_RANGE)
