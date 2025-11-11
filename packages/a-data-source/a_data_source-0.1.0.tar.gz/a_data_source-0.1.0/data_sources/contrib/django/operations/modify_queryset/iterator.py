from django.db.models import QuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import ModifyQuerySet
from data_sources.operations_params import BaseOperationParam
from data_sources.operations_results import BaseOperationResult


class QuerySetIterator(ModifyQuerySet):
    def __init__(
        self,
        chunk_size: int,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._chunk_size = chunk_size

    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        return queryset.iterator(chunk_size=self._chunk_size)
