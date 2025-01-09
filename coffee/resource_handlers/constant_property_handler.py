from coffee.client import JsonApiClient
from coffee.jsonapi_client.common import ResourceNameTuple
from coffee.jsonapi_client.document import Document
from coffee.resource_handlers import BaseResourceHandler


class ConstantPropertyHandler(BaseResourceHandler):
    """
    Handles CRUD operations for ConstantProperty resources using the JsonApiClient.
    """
    resource_type = 'constant_property'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_ct_name(self, component_type: str) -> Document:
        linked_resources = [ResourceNameTuple(name=component_type, type='component_type', property='component_types'),]
        return self.get_by_linked_resource_names(linked_resources)
