from __future__ import annotations

from typing import Any, Iterator, Optional, Iterable
from uuid import UUID

import data_sources.contrib
from data_sources.contrib.django.operations.fetch_entities import (
    AllFetchQuerySet,
    SingleFetchQuerySet,
    FirstFetchQuerySet,
    ExistsFetchQuerySet,
    CountFetchQuerySet,
)
from data_sources.data_source import DataSource
from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.operations.operation import Operation
from data_sources.operations.result_fetcher import FromMetaResultFetcher, SingleEntityResultFetcher
from data_sources.operations_params import InlineParam
from data_sources.shortcuts import get_data_for_operations


def fetch_entities_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
) -> list[Any]:
    return get_data_for_operations(
        operations=[
            *operations,
            AllFetchQuerySet(),
            FromMetaResultFetcher(key=DataSourceKeys.ENTITIES),
        ],
        initial_data=initial_data,
    )


def fetch_single_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
    exception_handlers: list[ExceptionHandler] = None,
) -> Any:
    return get_data_for_operations(
        operations=[
            *operations,
            SingleFetchQuerySet(),
            FromMetaResultFetcher(key=DataSourceKeys.ENTITIES),
        ],
        initial_data=initial_data,
        exception_handlers=exception_handlers,
    )[0]


def fetch_first_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
) -> Any:
    return get_data_for_operations(
        operations=[
            *operations,
            FirstFetchQuerySet(),
            FromMetaResultFetcher(key=DataSourceKeys.ENTITIES),
        ],
        initial_data=initial_data,
    )


def get_queryset_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
) -> QuerySet:
    return get_data_for_operations(
        operations=[
            *operations,
            FromMetaResultFetcher(key=data_sources.contrib.django.keys.QUERYSET),
        ],
        initial_data=initial_data,
    )


def get_iterator_for_queryset_operations(
    operations: list[Operation],
    chunk_size: int,
    initial_data: Any = None,
) -> Iterator[Any]:
    return get_data_for_operations(
        operations=[
            *operations,
            QuerySetIterator(chunk_size=chunk_size),
            FromMetaResultFetcher(key=data_sources.contrib.django.keys.QUERYSET),
        ],
        initial_data=initial_data,
    )


def get_entity_for_operations(
    operations: list[Operation],
    id_: UUID,
    exception_handlers: list[ExceptionHandler] = None,
):
    return get_data_for_operations(
        operations=[
            *operations,
            LimitToIdsQuerySet(limit_to_ids=InlineParam([id_])),
            SingleFetchQuerySet(),
            SingleEntityResultFetcher(),
        ],
        exception_handlers=exception_handlers,
    )


def get_exists_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
    exception_handlers: list[ExceptionHandler] = None,
) -> bool:
    return get_data_for_operations(
        operations=[
            *operations,
            ExistsFetchQuerySet(result_key='_exists'),
            FromMetaResultFetcher(key='_exists'),
        ],
        initial_data=initial_data,
        exception_handlers=exception_handlers,
    )


def get_count_for_queryset_operations(
    operations: list[Operation],
    initial_data: Any = None,
) -> int:
    return get_data_for_operations(
        operations=[
            *operations,
            CountFetchQuerySet(),
            FromMetaResultFetcher(key=DataSourceKeys.ENTITIES),
        ],
        initial_data=initial_data,
    )


def apply_queryset_operations_on_queryset(
    queryset: QuerySet,
    operations: list[Operation],
    initial_data: Any = None,
    initial_params: Optional[Iterable[tuple[str, Any]]] = None,
):
    if initial_params is None:
        initial_params = ((data_sources.contrib.django.keys.QUERYSET, queryset),)

    data_source = DataSource(
        operations=[
            *operations,
            FromMetaResultFetcher(key=data_sources.contrib.django.keys.QUERYSET),
        ]
    )
    queryset, _ = data_source.get_data(initial_data=initial_data, initial_params=initial_params)
    return queryset


def apply_modify_entities_operations_on_queryset(
    entities: list[Any],
    operations: list[Operation],
    initial_data: Any = None,
    initial_params: Optional[Iterable[tuple[str, Any]]] = None,
):
    if initial_params is None:
        initial_params = ((DataSourceKeys.ENTITIES, entities),)

    data_source = DataSource(
        operations=[
            *operations,
            FromMetaResultFetcher(key=DataSourceKeys.ENTITIES),
        ]
    )
    queryset, _ = data_source.get_data(initial_data=initial_data, initial_params=initial_params)
    return queryset
