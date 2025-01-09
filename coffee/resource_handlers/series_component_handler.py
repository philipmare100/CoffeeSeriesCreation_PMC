from coffee.client import JsonApiClient
from coffee.config import logger
from coffee.jsonapi_client.common import ResourceNameTuple
from coffee.jsonapi_client.document import Document
from coffee.resource_handlers import BaseResourceHandler


class SeriesComponentHandler(BaseResourceHandler):
    """
    Handles CRUD operations for Series resources using the JsonApiClient.
    """
    resource_type = 'series_component'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_series_and_component_names(self,
                                                 series_name: str,
                                                 component_name: str) -> Document:
        """
        Synchronously fetches the SeriesComponent resource that is linked to the provided Series
         and Component names.

        :param series_name: Name of the series that is linked to the expected resource.
        :type series_name: str
        :param component_name: Name of the component that is linked to the expected resource.
        :type component_name: str
        :return: Fetched resource document that is linked to the provided Series
         and Component names.
        :rtype: list[jsonapi_client.document.Document]
        :raises RuntimeError: If the client is configured for async.
        :raises ResourceNotFoundException: If resources cannot be found.
        """
        if self.client.enable_async:
            raise RuntimeError("Client is configured for async. Use 'async_get' instead.")
        linked_resources = [
            ResourceNameTuple(type='series', name=series_name),
            ResourceNameTuple(type='component', name=component_name)
        ]
        logger.debug(f'ResourceType=`{self.resource_type}` expected to be `series_component`.')
        return self.get_by_linked_resource_names(linked_resources)
