from typing import Iterable

from django.db.models import QuerySet, Expression

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import ModifyQuerySet
from data_sources.operations_params import BaseOperationParam, force_to_param
from data_sources.operations_results import BaseOperationResult


class QuerySetValues(ModifyQuerySet):
    def __init__(
        self,
        fields: BaseOperationParam[Iterable[str | Expression]] | Iterable[str | Expression],
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._fields_param = force_to_param(fields)

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        fields = self._fields_param.resolve(meta=meta)
        return queryset.values(*fields)


class QuerySetValuesList(ModifyQuerySet):
    def __init__(
        self,
        fields: BaseOperationParam[Iterable[str]] | Iterable[str],
        flat: BaseOperationParam[bool] | bool = False,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)

        self._fields_param = force_to_param(fields)
        self._flat_param = force_to_param(flat)

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        fields = self._fields_param.resolve(meta=meta)
        flat = self._flat_param.resolve(meta=meta)
        return queryset.values_list(*fields, flat=flat)
