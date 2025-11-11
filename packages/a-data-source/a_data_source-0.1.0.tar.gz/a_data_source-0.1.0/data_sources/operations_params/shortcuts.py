from typing import Any

from data_sources.operations_params import BaseOperationParam, InlineParam


def force_to_param(value: BaseOperationParam[Any] | Any) -> BaseOperationParam[Any]:
    if not isinstance(value, BaseOperationParam):
        return InlineParam(value)

    return value
