from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class SeriesTypeHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Series Type resources using the JsonApiClient.
    """
    resource_type = 'series_type'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
