from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class EventTypeHandler(BaseResourceHandler):
    """
    Handles CRUD operations for EventType resources using the JsonApiClient.
    """
    resource_type = 'event_type'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
