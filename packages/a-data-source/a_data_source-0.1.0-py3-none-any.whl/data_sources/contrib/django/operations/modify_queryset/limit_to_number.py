from django.db.models import QuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import ModifyQuerySet
from data_sources.operations_params import BaseOperationParam, force_to_param
from data_sources.operations_results import BaseOperationResult


class LimitToNumberQuerySet(ModifyQuerySet):
    def __init__(
        self,
        limit_to: BaseOperationParam[int] | int,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._limit_to_param = force_to_param(limit_to)

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        limit_to: int = self._limit_to_param.resolve(meta=meta)
        return queryset[: limit_to]
