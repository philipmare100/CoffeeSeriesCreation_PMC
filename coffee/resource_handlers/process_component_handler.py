from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ProcessComponentHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Process Component resources using the JsonApiClient.
    """
    resource_type = 'process'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
