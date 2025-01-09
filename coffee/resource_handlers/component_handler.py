from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ComponentHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Component resources using the JsonApiClient.
    """
    resource_type = 'component'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
