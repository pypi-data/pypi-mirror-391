from abc import ABC, abstractmethod
from typing import Any, Iterable

from data_sources.keys import ENTITIES
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_params import BaseOperationParam, MetaParam
from data_sources.operations_results import BaseOperationResult, StoreOperationResultInMeta


class ModifyEntities(Operation, ABC):
    """
    Operation that modifies entities.

    Args:
        entities: Operation parameter that returns entities to modify. By default, entities are taken from meta.
        result: Operation result that returns modified entities. By default, modified entities are added to meta.
    """
    def __init__(
        self,
        entities: BaseOperationParam[Iterable[Any]] | None = None,
        result: BaseOperationResult | None = None,
    ):
        super().__init__()
        self._entities_param = entities or MetaParam(key=ENTITIES)
        self._result = result or StoreOperationResultInMeta(key=ENTITIES, allow_modification=True)

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities: Iterable[Any] = self._entities_param.resolve(meta=meta)
        entities = self._modify_entities(entities=entities, meta=meta)

        result = self._result.resolve(
            operation_result=entities,
            data_source_result=result,
            meta=meta,
        )

        return result, meta

    @abstractmethod
    def _modify_entities(self, entities: Iterable[Any], meta: Meta) -> Iterable[Any]:
        pass


class ModifyEntity(ModifyEntities, ABC):
    def _modify_entities(self, entities: Iterable[Any], meta: Meta) -> list[Any]:
        return [self._modify_entity(entity, meta) for entity in entities]

    @abstractmethod
    def _modify_entity(self, entity: Any, meta: Meta) -> Any:
        pass
