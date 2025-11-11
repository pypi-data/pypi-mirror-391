from typing import Generic, TypeVar

from data_sources.keys import DataSourceKey
from data_sources.meta import Meta


ParamT = TypeVar('ParamT')


class BaseOperationParam(Generic[ParamT]):
    """
    Base class for operation parameters.

    Operation parameter is a value that is used by an operation to perform its task.
    Params to operations could be passed in two ways:
    1. Using regular python syntax
    ```python
    >>> class FetchUser(Operation):
    >>>     def __init__(self, user_id: int):
    >>>         self.user_id = user_id
    >>>
    >>>     def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
    >>>         return User.objects.get(id=self.user_id), meta
    >>>
    >>> fetch_user = FetchUser(user_id=1)
    ```
    2. Using `BaseOperationParam` subclasses.
    ```python
    >>> class FetchUser(Operation):
    >>>     def __init__(self, user_id: BaseOperationParam[int]):
    >>>         self.user_id = user_id
    >>>
    >>>     def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
    >>>         user_id = self.user_id.resolve(meta)
    >>>         return User.objects.get(id=user_id), meta
    >>>
    >>> fetch_user = FetchUser(user_id=InlineParam(1))
    ```

    Usage of `BaseOperationParam` subclasses is a more complex way of passing params,
    but it provides possibility of interacting with the data source meta.

    So, if you need to pass a simple value to an operation, use regular python syntax.
    If you need to pass a value that depends on the data source meta, use `BaseOperationParam` subclasses.
    """
    def resolve(self, meta: Meta) -> ParamT:
        raise NotImplementedError


class InlineParam(BaseOperationParam[ParamT]):
    """
    Inline (static) parameter value. Resolved to the same value every time.
    """
    def __init__(self, value: ParamT) -> None:
        self.value = value

    def resolve(self, meta: Meta) -> ParamT:
        return self.value


class MetaParam(BaseOperationParam[ParamT]):
    """
    Meta parameter value. Resolved to the value from the data source meta.
    """
    def __init__(self, key: DataSourceKey) -> None:
        self.key = key

    def resolve(self, meta: Meta) -> ParamT:
        return meta.get(self.key)
