from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class CollectorHandler(BaseResourceHandler):
    """
    Handles CRUD operations for mapper resources using the JsonApiClient.
    """
    resource_type = 'collector'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
