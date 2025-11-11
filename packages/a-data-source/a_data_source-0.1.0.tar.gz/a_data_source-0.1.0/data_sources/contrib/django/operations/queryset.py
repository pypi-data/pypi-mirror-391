from abc import ABC, abstractmethod
from typing import Any

from django.db.models import QuerySet

from data_sources.contrib.django.keys import QUERYSET
from data_sources.meta import Meta
from data_sources.operations import Operation
from data_sources.operations_params import BaseOperationParam, MetaParam
from data_sources.operations_results import BaseOperationResult, StoreOperationResultInMeta


class BaseQuerySetOperation(Operation, ABC):
    """
    Base operation for operations that are working with the queryset.
    """


class RootQuerySet(BaseQuerySetOperation, ABC):
    """
    Operation which responsibility is to provide root for the queryset.
    """
    def __init__(
        self,
        result: BaseOperationResult | None = None,
    ) -> None:
        super().__init__()
        # Root queryset must be a single source of queryset.
        # So, modifications are not allowed - if queryset is already present in meta
        #  - we should raise an error
        self._result = result or StoreOperationResultInMeta(key=QUERYSET, allow_modification=False)

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        queryset = self._get_queryset(meta)

        result = self._result.resolve(
            operation_result=queryset,
            data_source_result=result,
            meta=meta,
        )

        return result, meta

    @abstractmethod
    def _get_queryset(self, meta: Meta) -> QuerySet:
        pass


class ExplicitRootQuerySet(RootQuerySet):
    def __init__(self, queryset: BaseOperationParam[QuerySet], result: BaseOperationResult | None = None):
        super().__init__(result=result)
        self._queryset_param = queryset

    def _get_queryset(self, meta: Meta) -> QuerySet:
        return self._queryset_param.resolve(meta=meta)


class ModifyQuerySet(BaseQuerySetOperation, ABC):
    def __init__(
        self,
        queryset: BaseOperationParam[QuerySet] | None = None,
        result: BaseOperationResult | None = None,
    ) -> None:
        super().__init__()
        self._queryset_param = queryset or MetaParam(key=QUERYSET)
        # Result must be modifiable, because we are modifying queryset in place
        self._result = result or StoreOperationResultInMeta(key=QUERYSET, allow_modification=True)

    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        queryset = self._queryset_param.resolve(meta=meta)

        if queryset is None:
            raise RuntimeError('ModifyQuerySetOperation require queryset.')

        queryset = self._extend_queryset(queryset=queryset, meta=meta)

        result = self._result.resolve(
            operation_result=queryset,
            data_source_result=result,
            meta=meta,
        )
        return result, meta

    @abstractmethod
    def _extend_queryset(self, queryset: QuerySet, meta: Meta) -> QuerySet:
        pass
