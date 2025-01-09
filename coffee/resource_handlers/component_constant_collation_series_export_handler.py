from coffee.client import JsonApiClient
from coffee.config import logger
from coffee.jsonapi_client.filter import Filter
from coffee.jsonapi_client.document import Document
from coffee.resource_handlers.base_resource_handler import BaseResourceHandler
from coffee.resource_handlers.constant_property_component_type_handler import ConstantPropertyComponentTypeHandler
from coffee.resource_handlers.series_handler import SeriesHandler


class ComponentConstantCollationSeriesExportHandler(BaseResourceHandler):
    """
    Handles CRUD operations for ComponentConstantCollationSeriesExport resources using the JsonApiClient.
    """
    resource_type = 'component_constant_collation_series_export'

    def __init__(self, client: JsonApiClient):
        super().__init__(client)

    def get_by_linked_ct_cp_and_series_names(self,
                                             series_name: str,
                                             constant_property_name: str,
                                             component_type_name: str,
                                             ) -> Document:
        """Retrieve a component_constant_collation_series_export resource based on the given component_type name,
         constant_property name, and a collation series name.

        :param series_name: Name of the collation series
        :type series_name: str
        :param constant_property_name: Name of the collation constant property
        :type constant_property_name: str
        :param component_type_name: Name of the component type to which the collation constant property belongs
        :type component_type_name: str"""

        cpct_handler = ConstantPropertyComponentTypeHandler(self.client)
        cpct = cpct_handler.get_by_linked_cp_and_ct_names(constant_property_name, component_type_name).resource
        series = SeriesHandler(self.client).get_by_name(series_name).resource
        linked_resources = {
            'constant_property_component_type__id': cpct.id,
            'collation_series__id': series.id,
        }
        cccse_doc = self.get(filter_obj=Filter(**linked_resources))
        logger.info(f'Found CCCSE with collation_series {series_name} and cp {constant_property_name} (belonging to ct '
                    f'{component_type_name})')
        return cccse_doc

