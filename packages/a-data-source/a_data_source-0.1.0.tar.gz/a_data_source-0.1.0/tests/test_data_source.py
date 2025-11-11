from typing import Any

from data_sources.data_source import DataSource
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations.result_fetcher import FromMetaResultFetcher
from data_sources.operations.store_operation import StoreOperation
from data_sources.operations_results import StoreOperationResultInMeta


class _PipeOperation(Operation):
    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        return result, meta


class TestDataSource:
    def test_pipe_result_and_meta(self):
        data_source = DataSource(
            operations=[
                StoreOperation(result=StoreOperationResultInMeta(key='v'), data=1),
                FromMetaResultFetcher(key='v'),
                _PipeOperation(),
            ]
        )

        res, meta = data_source.get_data(None)
        assert res == 1
