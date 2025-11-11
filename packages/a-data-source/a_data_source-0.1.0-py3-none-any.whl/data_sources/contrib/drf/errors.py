from data_sources.exceptions.base import DataSourceError


class DRFEmptyResultError(DataSourceError):
    pass


class PaginationError(DataSourceError):
    pass


class PaginationParamsError(PaginationError):
    pass
