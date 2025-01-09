from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ParserConfigTemplateHandler(BaseResourceHandler):
    """
    Handles CRUD operations for ParserConfigTemplate resources using the JsonApiClient.
    """
    resource_type = 'parser_config_template'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)
