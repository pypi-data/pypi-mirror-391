from typing import Iterable, Any, Optional, Type, Sequence

from django.core.paginator import Paginator, InvalidPage

from data_sources.contrib.drf.errors import PaginationParamsError
from data_sources.meta import Meta
from data_sources.operations_params import BaseOperationParam
from utils.rest.pagination.base import SmartPaginator
from utils.rest.pagination.descriptors import PaginationParams


class PaginationApplier:
    def paginate(self, entities: Iterable, meta: Meta) -> list[Any]:
        raise NotImplementedError


class PaginatorPaginationApplier(PaginationApplier):
    def __init__(
        self,
        pagination_params: BaseOperationParam[PaginationParams],
        paginator_class: Optional[Type[Paginator]] = None,
    ):
        super().__init__()
        self._paginator_class = paginator_class or SmartPaginator
        self._pagination_params = pagination_params

    def paginate(self, entities: Sequence, meta: Meta) -> list[Any]:
        pagination_params = self._pagination_params.resolve(meta=meta)

        paginator = self._paginator_class(entities, per_page=pagination_params.page_size, allow_empty_first_page=True)

        try:
            page = paginator.page(pagination_params.page)
        except InvalidPage as ex:
            raise PaginationParamsError(ex.args)

        return list(page)
