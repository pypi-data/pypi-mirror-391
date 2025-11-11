from typing import Optional, Iterable, Any

from django.db.models import QuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.fetch_entities import MultipleFetchQuerySet
from data_sources.contrib.drf.operations.pagination.pagination_applier import PaginationApplier, PaginatorPaginationApplier
from data_sources.operations_params import BaseOperationParam
from utils.rest.pagination.descriptors import PaginationParams


class PaginateFetchQuerySetOperation(MultipleFetchQuerySet):
    def __init__(
        self,
        pagination_params: BaseOperationParam[PaginationParams],
        pagination_applier: Optional[PaginationApplier] = None,
    ):
        super().__init__()
        self._pagination_applier = pagination_applier or PaginatorPaginationApplier(
            pagination_params=pagination_params,
        )

    def limit_queryset(self, queryset: QuerySet, meta: Meta) -> Iterable[Any]:
        return self._pagination_applier.paginate(entities=queryset, meta=meta)
