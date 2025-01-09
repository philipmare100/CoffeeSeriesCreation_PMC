from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class TileHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Tile resources using the JsonApiClient.
    """
    resource_type = 'tile'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
