from __future__ import annotations

from abc import ABC, abstractmethod

from data_sources.contrib.drf.errors import PaginationParamsError
from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta
from data_sources.operations.store_in_meta import StoreInMeta
from data_sources.operations_params import BaseOperationParam, MetaParam
from utils.rest.pagination.constants import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_MAX_PAGE_SIZE,
    DEFAULT_PAGE_QUERY_PARAM,
    DEFAULT_PAGE_SIZE_QUERY_PARAM,
)
from utils.rest.pagination.descriptors import PaginationParams
from utils.rest.pagination.parse_params import (
    parse_pagination_params_from_request,
    parse_pagination_params_from_data,
)
from utils.rest.pagination.translations import INVALID_PAGE_SIZE_GREATER_ZERO


class FetchPaginationParamsOperation(StoreInMeta, ABC):
    def __init__(self, default_page_size: int = DEFAULT_PAGE_SIZE, max_page_size: int = DEFAULT_MAX_PAGE_SIZE):
        super().__init__()
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size

    def _get_meta_key(self, meta: Meta) -> str:
        return DataSourceKeys.PAGINATION_DATA

    @abstractmethod
    def _get_value(self, meta: Meta) -> PaginationParams:
        pass


class FetchPaginationFromParamsOperation(FetchPaginationParamsOperation):
    def __init__(
        self,
        param: BaseOperationParam = None,
        page_query_param: str = DEFAULT_PAGE_QUERY_PARAM,
        page_size_query_param: str = DEFAULT_PAGE_SIZE_QUERY_PARAM,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.page_query_param = page_query_param
        self.page_size_query_param = page_size_query_param
        self._param = param or MetaParam(key=DataSourceKeys.QUERY_PARAMS)

    def _get_value(self, meta: Meta) -> PaginationParams:
        params_data = self._param.resolve(meta=meta)

        parser = self._get_parser()

        pagination_params = parser(
            params_data,
            page_size_query_param=self.page_size_query_param,
            page_query_param=self.page_query_param,
            default_page_size=self.default_page_size,
            default_max_page_size=self.max_page_size,
        )

        self._validate_page_size_lower_limit(page_size=pagination_params.page_size)

        return pagination_params

    def _get_parser(self):
        return parse_pagination_params_from_data

    def _validate_page_size_lower_limit(self, page_size: int):
        # TODO: move to validation service?
        if page_size < 1:
            raise PaginationParamsError(message=INVALID_PAGE_SIZE_GREATER_ZERO)


class FetchPaginationParamsFromRequestOperation(FetchPaginationFromParamsOperation):
    def __init__(self, **kwargs):
        super().__init__(param=MetaParam(key=DataSourceKeys.REQUEST), **kwargs)

    def _get_parser(self):
        return parse_pagination_params_from_request
