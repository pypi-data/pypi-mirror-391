from abc import ABC, abstractmethod
from typing import Any, Iterable

from django.db.models import QuerySet

from data_sources.contrib.django.errors import MultipleObjectsError, NotFoundObjectError
from data_sources.contrib.django.keys import QUERYSET
from data_sources.contrib.django.translations import MULTIPLE_OBJECTS_ERROR, NOT_FOUND_ERROR
from data_sources.keys import ENTITIES
from data_sources.meta import Meta
from data_sources.operations import Operation
from data_sources.operations_params import BaseOperationParam, MetaParam
from data_sources.operations_results import BaseOperationResult, StoreOperationResultInMeta


class FetchQuerySet(Operation, ABC):
    def __init__(
        self,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__()
        self._queryset_param = queryset or MetaParam(key=QUERYSET)
        self._result = result or StoreOperationResultInMeta(key=ENTITIES)

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        queryset = self._get_queryset(result=result, meta=meta)

        entities = self._fetch(queryset=queryset, meta=meta)

        result = self._store_result(
            operation_result=entities,
            data_source_result=result,
            meta=meta,
        )

        return result, meta

    def _get_queryset(self, result: Any, meta: Meta) -> QuerySet:
        return self._queryset_param.resolve(meta=meta)

    @abstractmethod
    def _fetch(self, queryset: QuerySet, meta: Meta) -> Any:
        pass

    def _store_result(self, operation_result: Any, data_source_result: Any, meta: Meta) -> Any:
        return self._result.resolve(
            operation_result=operation_result,
            data_source_result=data_source_result,
            meta=meta,
        )


class AllFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> list[Any]:
        return list(queryset)


class CountFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> int:
        return queryset.count()


class SingleFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> list[Any]:
        items = queryset[:2]
        if not items:
            raise NotFoundObjectError(NOT_FOUND_ERROR)
        elif len(items) != 1:
            raise MultipleObjectsError(MULTIPLE_OBJECTS_ERROR)
        return [items[0]]


class MultipleFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> list[Any]:
        return list(self.limit_queryset(queryset=queryset, meta=meta))

    def limit_queryset(self, queryset: QuerySet, meta: Meta) -> Iterable[Any]:
        raise NotImplementedError


class LimitedNumberFetchQuerySet(MultipleFetchQuerySet):
    def __init__(
        self,
        limit_to: BaseOperationParam[int],
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__(queryset=queryset, result=result)
        self._limit_to_param = limit_to

    def limit_queryset(self, queryset: QuerySet, meta: Meta) -> Iterable[Any]:
        limit_to = self._limit_to_param.resolve(meta=meta)
        return queryset[:limit_to]


class FirstFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> Any:
        return queryset.first()


class ExistsFetchQuerySet(FetchQuerySet):
    def _fetch(self, queryset: QuerySet, meta: Meta) -> bool:
        return queryset.exists()
