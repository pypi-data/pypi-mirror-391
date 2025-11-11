from django.db.models import QuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import ModifyQuerySet


class QuerySetDistinct(ModifyQuerySet):
    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        return queryset.distinct()
