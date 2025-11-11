from typing import Iterable

from data_sources.contrib.django.keys import QUERYSET
from data_sources.operations import Operation,  FromNestedDataSource,  FromMetaResultFetcher
from data_sources.operations_params import BaseOperationParam
from data_sources.operations_results import BaseOperationResult


class QuerySetFromNestedDataSource(FromNestedDataSource):
    def __init__(
        self,
        operations: list[Operation],
        result: BaseOperationResult,
        initial_params: Iterable[tuple[str, BaseOperationParam]] = None,
    ):
        super().__init__(
            operations=[*operations, FromMetaResultFetcher(key=QUERYSET)],
            initial_params=initial_params,
            result=result,
        )
