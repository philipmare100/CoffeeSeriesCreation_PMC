from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class EngineeringUnitHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Engineering Unit resources using the JsonApiClient.
    """
    resource_type = 'engineering_unit'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
