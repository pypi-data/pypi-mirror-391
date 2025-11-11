from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from data_sources.meta import Meta


class ExceptionHandler(ABC):
    """
    Base class for exceptions handlers raised in DataSource.
    """

    @abstractmethod
    def handle(self, exception: Exception, result: Any, meta: Meta) -> Optional[Exception | Any]:
        return None
