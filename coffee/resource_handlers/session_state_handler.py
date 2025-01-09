from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class SessionStateHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Session State (Page) resources using the JsonApiClient.
    """
    resource_type = 'session_state'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
