from coffee.jsonapi_client.common import ResourceNameTuple
from coffee.jsonapi_client.document import Document
from coffee.config import logger
from coffee.client import JsonApiClient
from coffee.resource_handlers import BaseResourceHandler


class ConstantPropertyEventTypeHandler(BaseResourceHandler):
    """
    Handles CRUD operations for EventType resources using the JsonApiClient.
    """
    resource_type: str = 'constant_property_event_type'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_cp_and_et_names(self,
                                      constant_property_name: str,
                                      event_type_name: str) -> Document:
        """
        Synchronously fetches the ConstantPropertyEventType resource that is linked to the provided ConstantProperty
         and EventType names.

        :param constant_property_name: Name of the constant property (CP or const-prop) that is linked to the expected resource.
        :type constant_property_name: str
        :param event_type_name: Name of the event type (ET or event-type) that is linked to the expected resource.
        :type event_type_name: str
        :return: Fetched resource document that is linked to the provided ConstantProperty
         and EventType names.
        :rtype: list[jsonapi_client.document.Document]
        :raises RuntimeError: If the client is configured for async.
        :raises ResourceNotFoundException: If resources cannot be found.
        """
        if self.client.enable_async:
            raise RuntimeError("Client is configured for async. Use 'async_get' instead.")
        linked_resources = [
            ResourceNameTuple(type='constant_property', name=constant_property_name),
            ResourceNameTuple(type='event_type', name=event_type_name)
        ]
        logger.debug(f'ResourceType=`{self.resource_type}` expected to be `constant_property_event_type`.')
        return self.get_by_linked_resource_names(linked_resources)
