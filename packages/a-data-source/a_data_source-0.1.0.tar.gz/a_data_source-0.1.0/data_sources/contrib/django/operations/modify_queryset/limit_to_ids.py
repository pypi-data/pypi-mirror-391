from typing import Iterable
from uuid import UUID

from django.db.models import QuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import ModifyQuerySet
from data_sources.operations_params import BaseOperationParam
from data_sources.operations_results import BaseOperationResult


class LimitToIdsQuerySet(ModifyQuerySet):
    def __init__(
        self,
        limit_to_ids: BaseOperationParam[Iterable[str] | QuerySet[UUID]],
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._limit_to_ids_param = limit_to_ids

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        limit_to_ids = self._limit_to_ids_param.resolve(meta=meta)

        return queryset.filter(id__in=limit_to_ids)


class ExcludeIdsFromQuerySet(ModifyQuerySet):
    def __init__(
        self,
        exclude_ids: BaseOperationParam[Iterable[str] | QuerySet[UUID]] | None,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._exclude_ids_param = exclude_ids

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        exclude_ids = self._exclude_ids_param.resolve(meta=meta)

        return queryset.exclude(id__in=exclude_ids)
