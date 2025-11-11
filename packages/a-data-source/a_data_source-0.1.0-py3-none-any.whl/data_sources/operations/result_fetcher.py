from abc import ABC
from typing import Any, TypeVar, Generic

from data_sources.errors import NotSingleEntityError
from data_sources.keys import ENTITIES, DataSourceKey
from data_sources.meta import Meta
from data_sources.operations.operation import Operation
from data_sources.operations_params import BaseOperationParam, MetaParam


class BaseResultFetcher(Operation, ABC):
    def __init__(self, entities: BaseOperationParam[list[Any]] | None = None):
        super().__init__()
        self._entities_param = entities or MetaParam(key=ENTITIES)


class SingleEntityResultFetcher(BaseResultFetcher):
    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities: list[Any] = self._entities_param.resolve(meta=meta)

        if len(entities) != 1:
            raise NotSingleEntityError(f'Not a single entity. {len(entities)}')

        return entities[0], meta


EntityIDT = TypeVar('EntityIDT')


class SpecificEntityResultFetcher(BaseResultFetcher, Generic[EntityIDT]):
    def __init__(self, entity_id: EntityIDT, entities: BaseOperationParam[list[Any]] | None = None):
        super().__init__(entities=entities)
        self._entity_id = entity_id

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities: list[Any] = self._entities_param.resolve(meta=meta)

        entity = next((entity for entity in entities if self.get_entity_id(entity) == self._entity_id), None)

        return entity, meta

    def get_entity_id(self, entity: Any) -> EntityIDT:
        return entity['id'] if isinstance(entity, dict) else entity.id


class AllEntitiesResultFetcher(BaseResultFetcher):
    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        entities: list[Any] = self._entities_param.resolve(meta=meta)
        return entities, meta


class FromMetaResultFetcher(Operation):
    def __init__(self, key: DataSourceKey) -> None:
        self._key = key

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        return meta.get(self._key), meta
