from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from data_sources.data_source import DataSource
from data_sources.exception_handlers.exception_handler import ExceptionHandler
from data_sources.contrib.drf.error_handlers import MultipleObjectsHandler, NotFoundObjectHandler
from data_sources.exception_handlers.filter_order import NotEnumMemberHandler
from data_sources.exception_handlers.paginator import PaginationParamsErrorHandler
from data_sources.keys import DataSourceKeys
from data_sources.contrib.drf.operations.fetch_params import FetchRequestOperation
from data_sources.operations.drf.filter_order import RequestFilterOrderOperation
from data_sources.contrib.drf.operations.result_fetcher import DRFResponseOperation
from data_sources.contrib.drf.operations.serialization import DRFSerializationOperation
from data_sources.contrib.django.operations.fetch_entities import SingleFetchQuerySet, AllFetchQuerySet
from data_sources.operations.filter_order import ApplyFilterOrderOperation, ApplyOnlyOrderOperation
from data_sources.operations.modifiers import ProvideCountQuerySetOperation
from data_sources.operations.modify_entity.set_entity import SetEntityOperation
from data_sources.operations.operation import Operation
from data_sources.contrib.drf.operations.pagination.fetch_entities import PaginateFetchQuerySetOperation
from data_sources.contrib.drf.operations.pagination.fetch_params import FetchPaginationParamsFromRequestOperation
from data_sources.contrib.drf.operations.pagination.modify_queryset import LimitToIdsPaginationQuerySet
from data_sources.contrib.drf.operations.pagination.result_fetcher import (
    PageNumberPaginateOperation,
    StaticEntitiesCountProvider,
)
from data_sources.contrib.django.operations.queryset import LookupQuerySetOperation
from data_sources.operations.nested_data_source import QuerySetFromDataSourceOperation
from data_sources.operations.result_fetcher import SingleEntityResultFetcher
from data_sources.operations_params import InlineParam, MetaParam
from data_sources.operations_results import StoreOperationResultInMeta
from utils.helper.fields_handler import FilterOrderManager
from utils.rest.generics import ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView


class DataSourceListAPIViewMixin(ListAPIView):
    filter_order_manager: FilterOrderManager = None

    def get_default_fetch_params_operations(self) -> list[Operation]:
        ops = [FetchRequestOperation(), ProvideCountQuerySetOperation(), FetchPaginationParamsFromRequestOperation()]

        return ops

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_filter_order_operations(self) -> list[Operation]:
        if self.filter_order_manager is None:
            return []

        return [
            RequestFilterOrderOperation(filter_order_manager=self.filter_order_manager),
        ]

    def get_filter_order_apply_operations(self) -> list[Operation]:
        if self.filter_order_manager is None:
            return []
        return [
            ApplyFilterOrderOperation(),
        ]

    def get_querysets_operations(self) -> list[Operation]:
        return []

    def get_fetch_entities_operations(self) -> list[Operation]:
        return [
            PaginateFetchQuerySetOperation(pagination_params=MetaParam(DataSourceKeys.PAGINATION_DATA)),
        ]

    def get_entities_modifiers_operations(self) -> list[Operation]:
        return []

    def get_serialization_operations(self) -> list[Operation]:
        return [
            DRFSerializationOperation(
                serializer_class=self.get_serializer_class(),
                serializer_kwargs={'context': self.get_serializer_context()},
            ),
        ]

    def get_result_fetching_operations(self) -> list[Operation]:
        return [
            PageNumberPaginateOperation(),
            DRFResponseOperation(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        return [NotEnumMemberHandler(), PaginationParamsErrorHandler()]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def get_datasource_operations(self) -> list[Operation]:
        return [
            *self.get_default_fetch_params_operations(),
            *self.get_custom_fetch_params_operations(),
            *self.get_filter_order_operations(),
            *self.get_querysets_operations(),
            *self.get_filter_order_apply_operations(),
            *self.get_fetch_entities_operations(),
            *self.get_entities_modifiers_operations(),
            *self.get_serialization_operations(),
            *self.get_result_fetching_operations(),
        ]

    def list(self, request, *args, **kwargs):
        data_source = DataSource(
            operations=self.get_datasource_operations(),
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )
        data, _ = data_source.get_data(self)
        return data


class DataSourceStaticListAPIViewMixin(ListAPIView):
    def get_default_fetch_params_operations(self) -> list[Operation]:
        ops = [FetchRequestOperation(), FetchPaginationParamsFromRequestOperation()]

        return ops

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_static_entities_operations(self) -> list[Operation]:
        return []

    def get_serialization_operations(self) -> list[Operation]:
        return [
            DRFSerializationOperation(
                serializer_class=self.get_serializer_class(),
                serializer_kwargs={'context': self.get_serializer_context()},
            ),
        ]

    def get_result_fetching_operations(self) -> list[Operation]:
        return [
            PageNumberPaginateOperation(count_provider=StaticEntitiesCountProvider()),
            DRFResponseOperation(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        return [NotEnumMemberHandler(), PaginationParamsErrorHandler()]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def get_additional_queryset_entities_operations(self):
        return []

    def list(self, request, *args, **kwargs):
        data_source = DataSource(
            operations=[
                *self.get_default_fetch_params_operations(),
                *self.get_custom_fetch_params_operations(),
                *self.get_additional_queryset_entities_operations(),
                *self.get_static_entities_operations(),
                *self.get_serialization_operations(),
                *self.get_result_fetching_operations(),
            ],
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )
        data, _ = data_source.get_data(self)
        return data


class DataSourceListLimitedToIDsAPIViewMixin(ListAPIView):
    filter_order_manager: FilterOrderManager = None

    def get_default_fetch_params_operations(self) -> list[Operation]:
        ops = [FetchRequestOperation(), ProvideCountQuerySetOperation(), FetchPaginationParamsFromRequestOperation()]

        return ops

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_filter_order_operations(self) -> list[Operation]:
        if self.filter_order_manager is None:
            return []

        return [
            RequestFilterOrderOperation(filter_order_manager=self.filter_order_manager),
        ]

    def get_filter_order_apply_operations(self) -> list[Operation]:
        if self.filter_order_manager is None:
            return []
        return [
            ApplyFilterOrderOperation(),
        ]

    def get_entities_modifiers_operations(self) -> list[Operation]:
        return []

    def get_serialization_operations(self) -> list[Operation]:
        return [
            DRFSerializationOperation(
                serializer_class=self.get_serializer_class(),
                serializer_kwargs={'context': self.get_serializer_context()},
            ),
        ]

    def get_result_fetching_operations(self) -> list[Operation]:
        return [
            PageNumberPaginateOperation(),
            DRFResponseOperation(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        return [NotEnumMemberHandler(), PaginationParamsErrorHandler()]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def get_root_queryset_operation(self) -> Operation:
        raise NotImplementedError

    def get_filtration_operations(self) -> list[Operation]:
        raise NotImplementedError

    def get_annotation_operations(self) -> list[Operation]:
        raise NotImplementedError

    def get_datasource_operations(self) -> list[Operation]:
        return [
            *self.get_default_fetch_params_operations(),
            *self.get_custom_fetch_params_operations(),
            self.get_root_queryset_operation(),
            *self.get_filter_order_operations(),
            *self.get_filtration_operations(),
            *self.get_filter_order_apply_operations(),
            QuerySetFromDataSourceOperation(
                operations=[self.get_root_queryset_operation()], result=StoreOperationResultInMeta('_root_queryset')
            ),
            LimitToIdsPaginationQuerySet(base_queryset=MetaParam('_root_queryset')),
            *self.get_annotation_operations(),
            ApplyOnlyOrderOperation(),
            AllFetchQuerySet(),
            *self.get_entities_modifiers_operations(),
            *self.get_serialization_operations(),
            *self.get_result_fetching_operations(),
        ]

    def list(self, request, *args, **kwargs):
        data_source = DataSource(
            operations=self.get_datasource_operations(),
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )
        data, _ = data_source.get_data(self)
        return data


class DataSourceRetrieveAPIViewMixin(RetrieveAPIView):
    def get_default_fetch_params_operations(self) -> list[Operation]:
        return [
            FetchRequestOperation(),
        ]

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_querysets_operations(self) -> list[Operation]:
        return []

    def get_lookup_queryset_operations(self) -> list[Operation]:
        lookup_name = self.lookup_url_kwarg or self.lookup_field
        assert lookup_name in self.kwargs, (
            f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
            f'named {lookup_name}. Fix your URL conf, or set the `.lookup_field` '
            f'attribute on the view correctly.'
        )

        return [
            LookupQuerySetOperation(lookup_field=self.lookup_field, lookup_value=InlineParam(self.kwargs[lookup_name])),
        ]

    def get_fetch_entities_operations(self) -> list[Operation]:
        return [SingleFetchQuerySet()]

    def get_entities_modifiers_operations(self) -> list[Operation]:
        return []

    def get_serialization_operations(self) -> list[Operation]:
        return [
            DRFSerializationOperation(
                serializer_class=self.get_serializer_class(),
                serializer_kwargs={'context': self.get_serializer_context()},
            ),
        ]

    def get_result_fetching_operations(self) -> list[Operation]:
        return [
            SingleEntityResultFetcher(),
            DRFResponseOperation(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        return [
            NotEnumMemberHandler(),
            MultipleObjectsHandler(),
            NotFoundObjectHandler(),
        ]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def retrieve(self, request, *args, **kwargs):
        data_source = DataSource(
            operations=[
                *self.get_default_fetch_params_operations(),
                *self.get_custom_fetch_params_operations(),
                *self.get_querysets_operations(),
                *self.get_lookup_queryset_operations(),
                *self.get_fetch_entities_operations(),
                *self.get_entities_modifiers_operations(),
                *self.get_serialization_operations(),
                *self.get_result_fetching_operations(),
            ],
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )
        data, _ = data_source.get_data(self)
        return data


class DataSourceDestroyAPIViewMixin(DestroyAPIView):
    def get_default_fetch_params_operations(self) -> list[Operation]:
        return [
            FetchRequestOperation(),
        ]

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_querysets_operations(self) -> list[Operation]:
        return []

    def get_lookup_queryset_operations(self) -> list[Operation]:
        lookup_name = self.lookup_url_kwarg or self.lookup_field
        assert lookup_name in self.kwargs, (
            f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
            f'named {lookup_name}. Fix your URL conf, or set the `.lookup_field` '
            f'attribute on the view correctly.'
        )

        return [
            LookupQuerySetOperation(lookup_field=self.lookup_field, lookup_value=InlineParam(self.kwargs[lookup_name])),
        ]

    def get_fetch_entities_operations(self) -> list[Operation]:
        return [SingleFetchQuerySet()]

    def get_single_entity_operations(self) -> list[Operation]:
        return [
            SingleEntityResultFetcher(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        # todo we should move common methods to separate class and rename some of the methods
        return [
            NotEnumMemberHandler(),
            MultipleObjectsHandler(),
            NotFoundObjectHandler(),
        ]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def delete(self, request, *args, **kwargs):
        data_source = DataSource(
            operations=[
                *self.get_default_fetch_params_operations(),
                *self.get_custom_fetch_params_operations(),
                *self.get_querysets_operations(),
                *self.get_lookup_queryset_operations(),
                *self.get_fetch_entities_operations(),
                *self.get_single_entity_operations(),
            ],
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )
        instance, _ = data_source.get_data(self)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DataSourceUpdateAPIViewMixin(UpdateAPIView):
    def get_default_fetch_params_operations(self) -> list[Operation]:
        return [
            FetchRequestOperation(),
        ]

    def get_custom_fetch_params_operations(self) -> list[Operation]:
        return []

    def get_querysets_operations(self) -> list[Operation]:
        return []

    def get_lookup_queryset_operations(self) -> list[Operation]:
        lookup_name = self.lookup_url_kwarg or self.lookup_field
        assert lookup_name in self.kwargs, (
            f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
            f'named {lookup_name}. Fix your URL conf, or set the `.lookup_field` '
            f'attribute on the view correctly.'
        )

        return [
            LookupQuerySetOperation(lookup_field=self.lookup_field, lookup_value=InlineParam(self.kwargs[lookup_name])),
        ]

    def get_fetch_entities_operations(self) -> list[Operation]:
        return [SingleFetchQuerySet()]

    def get_single_entity_operations(self) -> list[Operation]:
        return [
            SingleEntityResultFetcher(),
        ]

    def get_default_exception_handlers(self) -> list[ExceptionHandler]:
        return [
            MultipleObjectsHandler(),
            NotFoundObjectHandler(),
        ]

    def get_custom_exception_handlers(self) -> list[ExceptionHandler]:
        return []

    def get_serialization_operations(self) -> list[Operation]:
        return [
            DRFSerializationOperation(
                serializer_class=self.get_serializer_class(),
                serializer_kwargs={'context': self.get_serializer_context()},
            ),
        ]

    def get_result_fetching_operations(self) -> list[Operation]:
        return [
            SingleEntityResultFetcher(),
            DRFResponseOperation(),
        ]

    def get_entity_after_update_operations(self, instance: object) -> list[Operation]:
        return [SetEntityOperation(instance=instance)]

    def get_before_update_entity_modifiers_operations(self) -> list[Operation]:
        return []

    def get_entities_modifiers_operations(self) -> list[Operation]:
        return []

    def update(self, request, *args, **kwargs):
        data_source_before_update = self._get_data_source_before_update()
        instance, meta = data_source_before_update.get_data(initial_data=self)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer=serializer)
        self.clean_prefetch_cache(instance=instance)

        data_source_after_update = self._get_data_source_after_update(instance=instance)
        data, _ = data_source_after_update.get_data(initial_data=self)
        return data

    def perform_update(self, serializer: Serializer) -> object:
        raise NotImplementedError

    def _get_data_source_before_update(self) -> DataSource:
        return DataSource(
            operations=[
                *self.get_default_fetch_params_operations(),
                *self.get_custom_fetch_params_operations(),
                *self.get_querysets_operations(),
                *self.get_lookup_queryset_operations(),
                *self.get_fetch_entities_operations(),
                *self.get_before_update_entity_modifiers_operations(),
                *self.get_single_entity_operations(),
            ],
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )

    def _get_data_source_after_update(self, instance: object) -> DataSource:
        return DataSource(
            operations=[
                *self.get_entity_after_update_operations(instance=instance),
                *self.get_entities_modifiers_operations(),
                *self.get_serialization_operations(),
                *self.get_result_fetching_operations(),
            ],
            exception_handlers=[
                *self.get_default_exception_handlers(),
                *self.get_custom_exception_handlers(),
            ],
        )


class DataSourceRUDAPIViewMixin(
    DataSourceRetrieveAPIViewMixin, DataSourceUpdateAPIViewMixin, DataSourceDestroyAPIViewMixin
):
    pass
