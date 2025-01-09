from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ComponentTypeHandler(BaseResourceHandler):
    """
    Handles CRUD operations for ComponentType resources using the JsonApiClient.
    """
    resource_type = 'component_type'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
