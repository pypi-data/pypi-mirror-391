from ..clients.data import (
    ApiClient,
    Configuration,
    DatasetServiceApi,
    DataTableServiceApi,
)
from .common import BaseElevateClient, BaseElevateService


class DataClient(BaseElevateClient, ApiClient):
    _route = "/api/data"
    _conf_class = Configuration


class DataTableService(BaseElevateService, DataTableServiceApi):
    _client_class = DataClient


class DatasetService(BaseElevateService, DatasetServiceApi):
    _client_class = DataClient
