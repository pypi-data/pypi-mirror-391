from __future__ import annotations

from typing import Any, Optional

from rest_framework.exceptions import ValidationError, NotFound

from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.contrib.django.errors import MultipleObjectsError, NotFoundObjectError
from data_sources.meta import Meta


class MultipleObjectsHandler(ExceptionHandler):
    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        if isinstance(exception, MultipleObjectsError):
            return ValidationError(exception.message)

        return None


class NotFoundObjectHandler(ExceptionHandler):
    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        if isinstance(exception, NotFoundObjectError):
            return NotFound(exception.message)

        return None
