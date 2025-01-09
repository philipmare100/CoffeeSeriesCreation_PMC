from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ResourceComponentHandler(BaseResourceHandler):
    """
    Handles CRUD operations for resource type Component resources using the JsonApiClient.
    """
    resource_type = 'resource'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
