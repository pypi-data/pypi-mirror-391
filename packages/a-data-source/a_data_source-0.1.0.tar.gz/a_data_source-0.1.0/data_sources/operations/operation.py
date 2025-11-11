from abc import ABC, abstractmethod
from typing import Any

from data_sources.meta import Meta


class Operation(ABC):
    """
    Base class for operation on DataSource.
    """

    @abstractmethod
    def handle(self, result: Any, meta: Meta) -> tuple[Any, Meta]:
        pass
