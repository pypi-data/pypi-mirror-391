from typing import Optional, Any

from data_sources.keys import DataSourceKeys
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.contrib.drf.operations.pagination.pagination_applier import PaginationApplier, PaginatorPaginationApplier
from data_sources.operations_params import BaseOperationParam, MetaParam
from data_sources.operations_results import BaseOperationResult


class PaginateEntitiesOperation(Operation):
    def __init__(
        self,
        entities: BaseOperationParam,
        result: BaseOperationResult,
        pagination_applier: Optional[PaginationApplier] = None,
    ):
        super().__init__()
        self._result = result
        self._entities_param = entities
        self._pagination_applier = pagination_applier or PaginatorPaginationApplier(
            pagination_params=MetaParam(DataSourceKeys.PAGINATION_DATA),
        )

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities = self._entities_param.resolve(meta=meta)
        paginated_entities = self._pagination_applier.paginate(entities=entities, meta=meta)

        result = self._result.resolve(
            operation_result=paginated_entities,
            data_source_result=result,
            meta=meta,
        )
        return result, meta
