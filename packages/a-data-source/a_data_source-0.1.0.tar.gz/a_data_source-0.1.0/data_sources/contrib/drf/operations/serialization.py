from typing import Any, Type

from rest_framework.serializers import Serializer

from data_sources.meta import Meta

from data_sources.operations.modify_entity.base import ModifyEntitiesOperation


class DRFSerializationOperation(ModifyEntitiesOperation):
    def __init__(
        self,
        serializer_class: Type[Serializer],
        serializer_kwargs: dict[str, Any],
    ):
        super().__init__()
        self.serializer_class = serializer_class
        self.serializer_kwargs = serializer_kwargs

    def _modify_entities(self, entities: list[Any], meta: Meta) -> list[Any]:
        self.serializer_kwargs['many'] = True
        serializer = self.serializer_class(instance=entities, **self.serializer_kwargs)

        return serializer.data
