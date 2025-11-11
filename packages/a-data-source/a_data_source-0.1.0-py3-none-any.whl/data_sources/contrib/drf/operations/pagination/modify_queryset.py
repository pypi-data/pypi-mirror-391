from typing import Optional

from django.db.models import QuerySet

from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta
from data_sources.contrib.drf.operations.pagination.pagination_applier import PaginationApplier, PaginatorPaginationApplier
from data_sources.contrib.django.operations.queryset import ModifyQuerySet
from data_sources.operations_params import MetaParam
from data_sources.operations_params import BaseOperationParam


class LimitToIdsPaginationQuerySet(ModifyQuerySet):
    """Operation which should be used when we have issues with "big" offset."""

    def __init__(
        self,
        base_queryset: BaseOperationParam[QuerySet],
        pagination_applier: Optional[PaginationApplier] = None,
    ):
        super().__init__()
        self.pagination_applier = pagination_applier or PaginatorPaginationApplier(
            pagination_params=MetaParam(DataSourceKeys.PAGINATION_DATA),
        )
        self.base_queryset_param = base_queryset

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        queryset = queryset.values('id')

        entities_ids = self.pagination_applier.paginate(entities=queryset, meta=meta)

        base_qs = self.base_queryset_param.resolve(meta=meta)
        return base_qs.filter(id__in=[item['id'] for item in entities_ids])
