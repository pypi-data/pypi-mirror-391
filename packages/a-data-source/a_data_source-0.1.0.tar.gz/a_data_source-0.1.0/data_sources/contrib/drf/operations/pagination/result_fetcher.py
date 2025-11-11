from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from django.db.models import QuerySet

import data_sources.contrib.django.keys
from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta, NotPresentInMeta
from data_sources.operations.result_fetcher import BaseResultFetcher
from data_sources.operations_params import BaseOperationParam, MetaParam
from utils.rest.pagination.base import generate_links
from utils.rest.pagination.descriptors import PaginationParams


class FetchCountFrom(str, Enum):
    QUERYSET = 'queryset'
    COUNT_QUERYSET = 'count_queryset'
    COUNT_ENTITIES = 'count_entities'


class BaseCountProvider(ABC):
    def __init__(self, fetch_from: FetchCountFrom = None):
        self._fetch_from = fetch_from

    @abstractmethod
    def get_entities_count(self, meta: Meta) -> tuple[int, FetchCountFrom]:
        pass


class ImplicitCountProvider(BaseCountProvider):
    def __init__(self, count: int):
        super().__init__(fetch_from=FetchCountFrom.COUNT_ENTITIES)
        self._count = count

    def get_entities_count(self, meta: Meta) -> tuple[int, FetchCountFrom]:
        return self._count, FetchCountFrom.COUNT_ENTITIES


class EntitiesCountProvider(BaseCountProvider):
    def get_entities_count(self, meta: Meta) -> tuple[int, FetchCountFrom]:
        fetch_from = self._get_fetch_from(meta)

        if fetch_from == FetchCountFrom.COUNT_QUERYSET:
            count = self._get_from_count_queryset(meta)
        elif fetch_from == FetchCountFrom.QUERYSET:
            count = self._get_from_queryset(meta)
        else:
            raise Exception

        return count, fetch_from

    def _get_fetch_from(self, meta: Meta) -> FetchCountFrom:
        if self._fetch_from is not None:
            return self._fetch_from

        if self._should_use_count_queryset(meta):
            return FetchCountFrom.COUNT_QUERYSET
        else:
            return FetchCountFrom.QUERYSET

    def _should_use_count_queryset(self, meta: Meta) -> bool:
        try:
            return (
                meta.get(DataSourceKeys.PROVIDE_COUNT_QUERYSET) and meta.get(DataSourceKeys.COUNT_QUERYSET) is not None
            )
        except NotPresentInMeta:
            return False

    def get_queryset_meta_key(self, meta: Meta) -> str:
        return data_sources.contrib.django.keys.QUERYSET

    def get_count_queryset_meta_key(self, meta: Meta) -> str:
        return DataSourceKeys.COUNT_QUERYSET

    def _get_from_queryset(self, meta: Meta) -> int:
        queryset_key = self.get_queryset_meta_key(meta)
        queryset = meta.get(queryset_key)
        if queryset is None:
            raise Exception('Queryset is missing.')

        return queryset.count()

    def _get_from_count_queryset(self, meta: Meta) -> int:
        count_queryset_key = self.get_count_queryset_meta_key(meta)
        count_queryset = meta.get(count_queryset_key)
        if count_queryset is None:
            raise Exception('Count queryset is missing.')

        return count_queryset.count()


class EntitiesCountLenProvider(EntitiesCountProvider):
    def _get_from_count_queryset(self, meta: Meta) -> int:
        count_queryset_key = self.get_count_queryset_meta_key(meta)
        count_queryset = meta.get(count_queryset_key)
        if count_queryset is None:
            raise Exception('Count queryset is missing.')

        if isinstance(count_queryset, QuerySet):
            return count_queryset.count()
        elif isinstance(count_queryset, list):
            return len(count_queryset)
        raise Exception(f'{type(count_queryset)} type of count_queryset - is unknown instance type.')


class SQLCountProvider(EntitiesCountProvider):
    def _get_from_count_queryset(self, meta: Meta) -> int:
        count_queryset_key = self.get_count_queryset_meta_key(meta)
        count_queryset = meta.get(count_queryset_key)
        if count_queryset is None:
            raise Exception('Count queryset is missing.')
        if isinstance(count_queryset, int):
            return count_queryset
        raise Exception(f'{type(count_queryset)} type of count_queryset - is unknown instance type.')


class StaticEntitiesCountProvider(BaseCountProvider):
    def __init__(self, entities: BaseOperationParam = None):
        super().__init__(fetch_from=FetchCountFrom.COUNT_ENTITIES)
        self._entities_param = entities or MetaParam(DataSourceKeys.ENTITIES)

    def get_entities_count(self, meta: Meta) -> tuple[int, FetchCountFrom]:
        entities = self._entities_param.resolve(meta=meta)
        return len(entities), self._fetch_from


class PageNumberPaginateOperation(BaseResultFetcher):
    def __init__(self, page_query_param: str = 'page', count_provider: BaseCountProvider = None, **kwargs):
        super().__init__(**kwargs)

        self.page_query_param = page_query_param
        self._count_provider = count_provider or EntitiesCountProvider()

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        request = meta.get(DataSourceKeys.REQUEST)
        entities: list[Any] = self.get_entities(meta)
        pagination_params: PaginationParams = self._get_pagination_params(meta)

        count = self._get_entities_count(meta)

        has_next = (pagination_params.page_size * pagination_params.page) < count
        has_prev = pagination_params.page > 1

        prev_link, next_link = generate_links(
            request=request,
            generate_prev=has_prev,
            generate_next=has_next,
            page=pagination_params.page,
            page_query_param=self.page_query_param,
        )

        result = self._paginate(
            entities=entities,
            prev_link=prev_link,
            next_link=next_link,
            count=count,
        )

        return result, meta

    def _paginate(
        self,
        entities: list[Any],
        next_link: Optional[str],
        prev_link: Optional[str],
        count: int,
    ) -> dict:
        return {
            'count': count,
            'next': next_link,
            'previous': prev_link,
            'results': entities,
        }

    def _get_pagination_params(self, meta: Meta) -> PaginationParams:
        key = self.get_pagination_data_meta_key(meta=meta)
        return meta.get(key)

    def _get_entities_count(self, meta: Meta) -> int:
        count, _ = self._count_provider.get_entities_count(meta)
        return count

    def get_pagination_data_meta_key(self, meta: Meta) -> str:
        return DataSourceKeys.PAGINATION_DATA
