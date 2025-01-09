from coffee.jsonapi_client.common import ResourceNameTuple
from coffee.jsonapi_client.document import Document
from coffee.config import logger
from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ConstantPropertyComponentTypeHandler(BaseResourceHandler):
    """
    Handles CRUD operations for ComponentType resources using the JsonApiClient.
    """
    resource_type: str = 'constant_property_component_type'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_cp_and_ct_names(self,
                                      constant_property_name: str,
                                      component_type_name: str) -> Document:
        """
        Synchronously fetches the ConstantPropertyComponentType resource that is linked to the provided ConstantProperty
         and ComponentType names.

        :param constant_property_name: Name of the constant property (CP or const-prop) that is linked to the expected resource.
        :type constant_property_name: str
        :param component_type_name: Name of the component type (CT or comp-type) that is linked to the expected resource.
        :type component_type_name: str
        :return: Fetched resource document that is linked to the provided ConstantProperty
         and ComponentType names.
        :rtype: list[jsonapi_client.document.Document]
        :raises RuntimeError: If the client is configured for async.
        :raises ResourceNotFoundException: If resources cannot be found.
        """
        if self.client.enable_async:
            raise RuntimeError("Client is configured for async. Use 'async_get' instead.")
        linked_resources = [
            ResourceNameTuple(type='constant_property', name=constant_property_name),
            ResourceNameTuple(type='component_type', name=component_type_name)
        ]
        logger.debug(f'ResourceType=`{self.resource_type}` expected to be `constant_property_component_type`.')
        return self.get_by_linked_resource_names(linked_resources)
