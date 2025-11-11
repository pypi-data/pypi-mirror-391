from typing import Collection

from django.db.models import QuerySet
from django.db.models.query import EmptyQuerySet

from data_sources.meta import Meta
from data_sources.contrib.django.operations.queryset import RootQuerySet
from data_sources.operations_params import BaseOperationParam


class BaseCombineQuerySet(RootQuerySet):
    def __init__(self, querysets: Collection[BaseOperationParam]):
        super().__init__()

        if len(querysets) < 2:
            raise Exception('More than one queryset for combination expected')

        self._queryset_params = querysets

    def combine(self, queryset: QuerySet, rest_querysets: list[QuerySet], meta: Meta) -> QuerySet:
        raise NotImplementedError

    def _get_queryset(self, meta: Meta) -> QuerySet:
        querysets = [queryset_param.resolve(meta=meta) for queryset_param in self._queryset_params]

        not_empty_querysets = list(filter(lambda qs: not isinstance(qs, EmptyQuerySet), querysets))

        if not len(not_empty_querysets):
            return querysets[0]

        if len(not_empty_querysets) == 1:
            return not_empty_querysets[0]

        queryset, *rest = not_empty_querysets

        return self.combine(queryset, rest, meta)


class UnionQuerySetOperation(BaseCombineQuerySet):
    def __init__(self, querysets: Collection[BaseOperationParam], union_all: bool = True):
        super().__init__(querysets=querysets)
        self.union_all = union_all

    def combine(self, queryset: QuerySet, rest_querysets: list[QuerySet], meta: Meta) -> QuerySet:
        return queryset.union(*rest_querysets, all=self.union_all)


class IntersectQuerySetOperation(BaseCombineQuerySet):
    def combine(self, queryset: QuerySet, rest_querysets: list[QuerySet], meta: Meta) -> QuerySet:
        return queryset.intersection(*rest_querysets)


class DifferenceQuerySetOperation(BaseCombineQuerySet):
    def combine(self, queryset: QuerySet, rest_querysets: list[QuerySet], meta: Meta) -> QuerySet:
        return queryset.difference(*rest_querysets)
