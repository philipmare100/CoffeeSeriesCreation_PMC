from coffee.client import JsonApiClient
from coffee.config import logger
from coffee.jsonapi_client.filter import Filter
from coffee.jsonapi_client.document import Document
from coffee.resource_handlers.base_resource_handler import BaseResourceHandler
from coffee.resource_handlers.constant_property_event_type_handler import ConstantPropertyEventTypeHandler
from coffee.resource_handlers.series_handler import SeriesHandler


class EventConstantCollationSeriesExportHandler(BaseResourceHandler):
    """
    Handles CRUD operations for EventConstantCollationSeriesExport resources using the JsonApiClient.
    """
    resource_type = 'event_constant_collation_series_export'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_et_cp_and_series_names(self,
                                             series_name: str,
                                             constant_property_name: str,
                                             event_type_name: str,
                                             ) -> Document:
        """Retrieve an event_constant_collation_series_export resource based on the given event_type name,
         constant_property name, and a collation series name.

        :param series_name: Name of the collation series
        :type series_name: str
        :param constant_property_name: Name of the collation constant property
        :type constant_property_name: str
        :param event_type_name: Name of the event type to which the collation constant property belongs
        :type event_type_name: str"""

        cpet_handler = ConstantPropertyEventTypeHandler(self.client)
        cpet = cpet_handler.get_by_linked_cp_and_et_names(constant_property_name, event_type_name).resource
        series = SeriesHandler(self.client).get_by_name(series_name).resource
        linked_resources = {
            'constant_property_event_type__id': cpet.id,
            'collation_series__id': series.id,
        }
        ec_cse_doc = self.get(filter_obj=Filter(**linked_resources))
        logger.info(f'Found ECCSE with collation_series {series_name} and cp {constant_property_name} (belonging to et '
                    f'{event_type_name})')
        return ec_cse_doc
