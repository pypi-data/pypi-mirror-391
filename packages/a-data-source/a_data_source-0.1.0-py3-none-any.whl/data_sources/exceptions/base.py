from typing import Optional


class DataSourceError(Exception):
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code


class InitializationError(Exception):
    pass
