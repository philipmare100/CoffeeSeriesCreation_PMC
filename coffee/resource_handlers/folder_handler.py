from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class FolderHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Folder resources using the JsonApiClient.
    """
    resource_type = 'folder'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
