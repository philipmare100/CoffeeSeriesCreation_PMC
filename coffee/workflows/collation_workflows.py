from coffee.jsonapi_client.common import ResourceTuple
from coffee.jsonapi_client.resourceobject import ResourceObject
from coffee.client import JsonApiClient
from coffee.config import WorkflowConfig, logger
from coffee.utils.workflow_helpers import process_csv_generic
from coffee.workflows.base_workflows import BaseWorkflow
from coffee.resource_handlers import (
    ConstantPropertyComponentTypeHandler,
    ComponentConstantCollationSeriesExportHandler,
    SeriesHandler, EventConstantCollationSeriesExportHandler, ConstantPropertyEventTypeHandler, ConstantPropertyHandler
)


class ComponentCollationWorkflow(BaseWorkflow):
    """
    Defines a workflow for creating and deleting collation series exports linking constant properties,
    component types, and series in the context of the coffee framework.

    Attributes:
        client (JsonApiClient): An instance of JsonApiClient to interact with the coffee API.
    """
    # ToDo: Add custom Time Constant Property capability

    def create_collation_series_export(self,
                                       series_name: str,
                                       constant_property_name: str,
                                       time_constant_property_name: str,
                                       component_type_name: str) -> ResourceObject | bool:
        """
        Creates a ComponentConstantCollationSeriesExport (CCCSE) to link a series with a constant property and
        component type.

        :param series_name: The name of the series to collate to.
        :param constant_property_name: The name of the constant property to collate from.
        :param time_constant_property_name: The name of the time constant property to collate with.
        :param component_type_name: The name of the component type to collate from.
        :return: The created CCCSE ResourceObject on success, or False on failure.
        """
        try:
            # Retrieve Series resource object to collate to
            series = SeriesHandler(self.client).get_by_name(series_name).resource

            # Retrieve ConstantPropertyComponentType (CPCT) resource object to collate from
            cpct_handler = ConstantPropertyComponentTypeHandler(self.client)
            cpct_document = cpct_handler.get_by_linked_cp_and_ct_names(constant_property_name, component_type_name)
            cpct = cpct_document.resource

            # Retrieve time Constant Property (CP) resource object to collate to
            time_cp = ConstantPropertyHandler(self.client).get_by_name(time_constant_property_name).resource

            # Create ComponentConstantCollationSeriesExport (CCCSE)
            cccse_handler = ComponentConstantCollationSeriesExportHandler(self.client)
            relationships = {
                'constant_property_component_type': ResourceTuple(id=cpct.id, type=cpct.type),
                'collation_series': ResourceTuple(id=series.id, type=series.type),
                'time_constant_property': ResourceTuple(id=time_cp.id, type=time_cp.type)
            }
            cccse = cccse_handler.create(relationships=relationships)
            cccse.commit()
            return cccse
        except Exception as e:
            logger.error(f"Failed to create collation series export {series_name}: {e}")
            raise

    def delete_collation_series_export(self, series_name: str, constant_property_name: str, component_type_name: str):
        """
        Deletes a previously created ComponentConstantCollationSeriesExport (CCCSE) linking a series with
        a constant property and component type.

        :param series_name: The name of the series linked to the CCCSE.
        :param constant_property_name: The name of the constant property linked to the CCCSE.
        :param component_type_name: The name of the component type linked to the CCCSE.
        :return: True on successful deletion, raises an exception on failure.
        """
        try:
            cccse_handler = ComponentConstantCollationSeriesExportHandler(self.client)
            cccse = cccse_handler.get_by_linked_ct_cp_and_series_names(series_name,
                                                                       constant_property_name,
                                                                       component_type_name).resource
            cccse.delete()
            cccse.commit()
            logger.info(f"Successfully deleted CCCSE for CTCP `{component_type_name}-{constant_property_name}` and "
                        f"collation series `{series_name}`")
            return True
        except Exception as e:
            logger.info(f"Failed to deleted CCCSE for CTCP `{component_type_name}-{constant_property_name}` and "
                        f"collation series `{series_name}`")
            raise

    def bulk_create_collation_series_export(self, csv_path):
        """
        Processes a CSV file to bulk create collation series exports for multiple series, constant properties,
        and component types.

        :param csv_path: Path to the CSV file containing the data for creation.
        :return: True on successful processing of all rows, False otherwise.
        """
        def create_callable(row):
            """Define a callable for create operation"""
            self.create_collation_series_export(row['series'],
                                                row['constant_property'],
                                                row['time_constant_property'],
                                                row['component_type'])

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path, WorkflowConfig.COMPONENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS, create_callable, upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_collation_series_export(self, csv_path):
        """
        Processes a CSV file to bulk delete ComponentConstantCollationSeriesExports (CCCSE) for multiple series,
        constant properties, and component types.

        This method reads from a provided CSV file, each row containing the data necessary to identify and delete
        a CCCSE. It uses the `delete_collation_series_export` method for each row to attempt deletion of the CCCSE.

        :param csv_path: Path to the CSV file containing data for deletion. The CSV is expected to have columns
                         for 'component_type', 'constant_property', and 'series', which correspond to the
                         identifiers used to find and delete the CCCSEs.
        :return: True if all CCCSEs referenced in the CSV file are successfully processed (regardless of whether
                 the deletion was successful for each), raises an exception if unable to process the CSV file.
        """

        def delete_callable(row):
            """Define a callable for delete operation"""
            self.delete_collation_series_export(row['series'],
                                                row['constant_property'],
                                                row['component_type'])

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path, WorkflowConfig.COMPONENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS, delete_callable, upload_multithreaded=self.upload_multithreaded)


class EventCollationWorkflow(BaseWorkflow):
    """
    Defines a workflow for creating and deleting collation series exports linking constant properties,
    component types, and series in the context of the coffee framework.

    Attributes:
        client (JsonApiClient): An instance of JsonApiClient to interact with the coffee API.
    """
    # ToDo: Add custom Time Constant Property capability

    def create_collation_series_export(self,
                                       series_name: str,
                                       constant_property_name: str,
                                       event_type_name: str) -> ResourceObject | bool:
        """
        Creates a EventConstantCollationSeriesExport (CCCSE) to link a series with a constant property and
        event type.

        :param series_name: The name of the series to collate to.
        :param constant_property_name: The name of the constant property to collate from.
        :param event_type_name: The name of the event type to collate from.
        :return: The created CCCSE ResourceObject on success, or False on failure.
        """
        try:
            # Retrieve Series resource object to collate to
            series = SeriesHandler(self.client).get_by_name(series_name).resource

            # Retrieve ConstantPropertyEventType (CPCT) resource object to collate from
            cpet_handler = ConstantPropertyEventTypeHandler(self.client)
            cpet_document = cpet_handler.get_by_linked_cp_and_et_names(constant_property_name, event_type_name)
            cpet = cpet_document.resource

            # Create EventConstantCollationSeriesExport (CCCSE)
            cccse_handler = EventConstantCollationSeriesExportHandler(self.client)
            relationships = {
                'constant_property_event_type': ResourceTuple(id=cpet.id, type=cpet.type),
                'collation_series': ResourceTuple(id=series.id, type=series.type)
            }
            cccse = cccse_handler.create(relationships=relationships)
            cccse.commit()
            return cccse
        except Exception as e:
            logger.error(f"Failed to create collation series export {series_name}: {e}")
            raise

    def delete_collation_series_export(self, series_name: str, constant_property_name: str, event_type_name: str):
        """
        Deletes a previously created EventConstantCollationSeriesExport (CCCSE) linking a series with
        a constant property and event type.

        :param series_name: The name of the series linked to the CCCSE.
        :param constant_property_name: The name of the constant property linked to the CCCSE.
        :param event_type_name: The name of the event type linked to the CCCSE.
        :return: True on successful deletion, raises an exception on failure.
        """
        try:
            cccse_handler = EventConstantCollationSeriesExportHandler(self.client)
            cccse = cccse_handler.get_by_linked_et_cp_and_series_names(series_name,
                                                                       constant_property_name,
                                                                       event_type_name).resource
            cccse.delete()
            cccse.commit()
            logger.info(f"Successfully deleted CCCSE for CTCP `{event_type_name}-{constant_property_name}` and "
                        f"collation series `{series_name}`")
            return True
        except Exception as e:
            logger.info(f"Failed to deleted CCCSE for CTCP `{event_type_name}-{constant_property_name}` and "
                        f"collation series `{series_name}`")
            raise

    def bulk_create_collation_series_export(self, csv_path):
        """
        Processes a CSV file to bulk create collation series exports for multiple series, constant properties,
        and event types.

        :param csv_path: Path to the CSV file containing the data for creation.
        :return: True on successful processing of all rows, False otherwise.
        """
        def create_callable(row):
            """Define a callable for create operation"""
            self.create_collation_series_export(row['series'],
                                                row['constant_property'],
                                                row['event_type'])

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.EVENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS,
                                   create_callable,
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_collation_series_export(self, csv_path):
        """
        Processes a CSV file to bulk delete EventConstantCollationSeriesExports (CCCSE) for multiple series,
        constant properties, and event types.

        This method reads from a provided CSV file, each row containing the data necessary to identify and delete
        a CCCSE. It uses the `delete_collation_series_export` method for each row to attempt deletion of the CCCSE.

        :param csv_path: Path to the CSV file containing data for deletion. The CSV is expected to have columns
                         for 'event_type', 'constant_property', and 'series', which correspond to the
                         identifiers used to find and delete the CCCSEs.
        :return: True if all CCCSEs referenced in the CSV file are successfully processed (regardless of whether
                 the deletion was successful for each), raises an exception if unable to process the CSV file.
        """

        def delete_callable(row):
            """Define a callable for delete operation"""
            self.delete_collation_series_export(row['series'],
                                                row['constant_property'],
                                                row['event_type'])

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path, WorkflowConfig.COMPONENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS, delete_callable, upload_multithreaded=self.upload_multithreaded)
