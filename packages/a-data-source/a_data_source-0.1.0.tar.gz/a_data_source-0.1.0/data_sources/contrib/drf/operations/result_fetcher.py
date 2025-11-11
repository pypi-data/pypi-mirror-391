from typing import Any

from rest_framework.response import Response

from data_sources.contrib.drf.errors import DRFEmptyResultError
from data_sources.meta import Meta
from data_sources.operations.result_fetcher import BaseResultFetcher


class DRFResponseOperation(BaseResultFetcher):
    def __init__(self, status_code: int = 200):
        super().__init__()
        self._status_code = status_code

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        if result is None:
            raise DRFEmptyResultError('Empty `result`.')

        return Response(data=result, status=self._status_code), meta
