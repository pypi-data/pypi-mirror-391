from data_sources.exceptions.base import DataSourceError


class MultipleObjectsError(DataSourceError):
    pass


class NotFoundObjectError(DataSourceError):
    pass
