import pandas as pd

from coffee.client import JsonApiClient
from coffee.config import logger, WorkflowConfig
from coffee.jsonapi_client.resourceobject import ResourceObject
from coffee.resource_handlers import (
    SeriesHandler,
    ProcessComponentHandler,
    SeriesComponentHandler, EngineeringUnitHandler
)
from coffee.utils.workflow_helpers import process_csv_generic, get_extra_kwargs
from coffee.workflows.base_workflows import BaseWorkflow


class SeriesWorkflow(BaseWorkflow):

    def __init__(self, client: JsonApiClient, *args, **kwargs):
        super().__init__(client, *args, **kwargs)

        self.series_main_cols = ['name', 'description']
        self.series_lower_cols = ['aggregation', 'fill_method']
        self.series_expected_csv_cols = WorkflowConfig.SERIES_EXPECTED_CSV_COLUMNS

    def create_series(self,
                      name: str,
                      description: str | None = None,
                      engineering_unit: str | None = None,
                      aggregation: str = 'mean',
                      sample_period: str | None = None,
                      fill_method: str = 'backfill',
                      name_formula: str | None = None,
                      is_calculation: bool = False,
                      specialised_function: bool = False,
                      weighted_average_series: str | None = None,
                      source_series: str = None,
                      series_type: str | None = None,
                      process: str | None = None,
                      **kwargs) -> ResourceObject | bool:
        """
        Creates a new series with specified attributes.

        :param process:
        :param specialised_function:
        :param is_calculation:
        :param name: Name of the series.
        :param description: Description of the series.
        :param fill_method:
        :param sample_period:
        :param aggregation: Aggregation method used for the series
        :param engineering_unit: Measurement unit the series.
        :param name_formula: Formula used for calculation
        :param kwargs: Additional keyword arguments for other properties.
        :param source_series:
        :param weighted_average_series: Series on which to weight the present one.
        :param series_type:
        :return: A ResourceObject representing the series if successful, otherwise False.
        """
        # Default attributes and their corresponding values
        attribute_defaults = {
            'name_formula': None,
            'is_calculation': False,
            'specialised_function': False,
            'fill_method': 'backfill',
            'aggregation': 'mean',
            'sample_period': None,
            'source_series': None,
            'series_type': None,
            'description': None
        }

        # Initial attributes setup
        new_series_attrs = {'name': name}
        new_series_attrs.update({k: v for k, v in locals().items() if k in attribute_defaults and v is not None})

        # Update with additional keyword arguments that are not predefined defaults
        new_series_attrs.update({k: v for k, v in kwargs.items() if k not in attribute_defaults})

        # Relationship mapping remains as previously described
        relationship_mapping = {
            'engineering_unit': (EngineeringUnitHandler, 'engineering_unit'),
            'weighted_average_series': (SeriesHandler, 'weighted_average_series'),
            'process': (ProcessComponentHandler, 'processes')
        }

        # Process relationships using helper function as previously described
        new_series_rels = {}
        for param, (handler, rel_name) in relationship_mapping.items():
            if locals().get(param) or kwargs.get(param):
                handler_instance = handler(self.client)
                resource = handler_instance.get_by_name(locals().get(param) or kwargs.get(param)).resource
                new_series_rels[rel_name] = [resource] if rel_name == 'processes' else resource

        # Handle Series creation
        s_handler = SeriesHandler(self.client)
        s_new = s_handler.create(new_series_attrs, new_series_rels)
        try:
            if s_new:
                s_new.commit()
                logger.info(f'Successfully created a new Series {s_new.name}')
                return s_new
            else:
                logger.error('Failed to create new series.')
                return False
        except Exception as e:
            raise

    def patch_series(self,
                     name: str,
                     new_name: str | None = None,
                     description: str | None = None,
                     engineering_unit: str | None = None,
                     aggregation: str | None = None,
                     sample_period: str | None = None,
                     fill_method: str | None = None,
                     name_formula: str | None = None,
                     is_calculation: bool | None = None,
                     specialised_function: bool | None = None,
                     weighted_average_series: str | None = None,
                     source_series: str = None,
                     series_type: str | None = None,
                     **kwargs
                     ) -> ResourceObject | bool:
        """
        Patches series with specified attributes.

        :param specialised_function:
        :param is_calculation:
        :param name: Name of the series.
        :param new_name: New name of the series.
        :param description: Description of the series.
        :param name_formula: Formula used for calculation, applicable if is_calculation is True.
        :param series_type:
        :param source_series:
        :param weighted_average_series:
        :param fill_method:
        :param sample_period:
        :param aggregation:
        :param engineering_unit:
        :param kwargs: Additional keyword arguments for other properties.
        :return: A ResourceObject representing the series if successful, otherwise False.
        """
        # Include parameters only when they are explicitly set by the caller.
        patch_series_attrs = {k: v for k, v in locals().items() if
                              v is not None and k != 'self' and k != 'kwargs' and k != 'name' and k != 'new_name'}

        if new_name:
            patch_series_attrs['name'] = new_name

        # Handle Series
        s_handler = SeriesHandler(self.client)
        s = s_handler.get_by_name(name).resource
        s = s_handler.patch(s, patch_series_attrs)
        logger.info(f'Successfully patched Series {s.name}')
        return s

    def delete_series(self, series_name: str) -> ResourceObject | bool:
        try:
            s_handler = SeriesHandler(self.client)
            s = s_handler.get_by_name(series_name).resource
            s.delete()
            s.commit()
            logger.info(f'Successfully deleted a Series {series_name}')
            return True
        except Exception as e:
            logger.info(f"Failed to delete Series `{series_name}` | Error: {e}")
            raise

    def link_series_to_component(self, series_name: str, component_name: str) -> ResourceObject | bool:
        """
        Links a series to a component.

        :param series_name: The name of the series to link.
        :param component_name: The name of the component to link to the series.
        :return: The linked ResourceObject if successful, otherwise False.
        """
        try:
            # Retrieve Series (S) resource object
            s = SeriesHandler(self.client).get_by_name(series_name).resource

            # Retrieve Component (C) resource object
            c = ProcessComponentHandler(self.client).get_by_name(component_name).resource

            # Create SeriesComponent (SC) link
            sc_handler = SeriesComponentHandler(self.client)
            from coffee.jsonapi_client.common import ResourceTuple
            relationships = {
                'series': ResourceTuple(id=s.id, type=s.type),
                'component': ResourceTuple(id=c.id, type='component')
            }
            sc = sc_handler.create(relationships=relationships)
            sc.commit()
            logger.info(f'Successfully created a new {sc.type} with id {sc.id}')
            return sc
        except Exception as e:
            logger.error(f"Failed to create SeriesComponent for Component `{component_name}` and Series "
                         f"`{series_name}`: {e}")
            raise

    def delete_link_series_to_component(self, series_name: str, component_name: str):
        """
        Deletes a link between a series and a component.

        :param series_name: The name of the series linked.
        :param component_name: The name of the component linked.
        :return: True if successful, raises an exception otherwise.
        """
        try:
            sc_handler = SeriesComponentHandler(self.client)
            sc = sc_handler.get_by_linked_series_and_component_names(series_name, component_name).resource
            sc.delete()
            sc.commit()
            logger.info(f"Successfully deleted SeriesComponent `{component_name}-{series_name}`")
            return True
        except Exception as e:
            logger.info(f"Failed to delete SeriesComponent `{component_name}-{series_name}` | Error: {e}")
            raise

    def bulk_create_series(self, csv_path):
        """
        Processes a CSV file to bulk create multiple series from provided CSV.

        :param csv_path: Path to the CSV file containing the data for creation.
        :return: True on successful processing of all rows, False otherwise.
        """

        def create_callable(row: pd.Series):
            """Define a callable for create series operation"""
            extra_kwargs = get_extra_kwargs(row,
                                            self.series_main_cols,
                                            self.series_lower_cols,
                                            self.series_expected_csv_cols)

            self.create_series(row['name'],
                               row['description'],
                               **extra_kwargs
                               )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   self.series_expected_csv_cols,
                                   create_callable,
                                   'series_created',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_patch_series(self, csv_path):
        """
        Processes a CSV file to bulk patch multiple series from provided CSV.

        :param csv_path: Path to the CSV file containing the data for patch. Only include columns to be patched
        :return: True on successful processing of all rows, False otherwise.
        """

        def patch_callable(row: pd.Series):
            """Define a callable for patch series operation"""
            extra_kwargs = get_extra_kwargs(row,
                                            self.series_main_cols,
                                            self.series_lower_cols,
                                            self.series_expected_csv_cols)

            self.patch_series(row['name'],
                              **extra_kwargs
                              )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   self.series_expected_csv_cols,
                                   patch_callable,
                                   'series_patched',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_series(self, csv_path):
        def delete_callable(row: pd.Series):
            """Define a callable for create series operation"""
            self.delete_series(row['name'])

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   self.series_expected_csv_cols,
                                   delete_callable,
                                   'series_deleted',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_link_series_to_component(self, csv_path: str):
        """
        Processes a CSV file to bulk link series to component from provided CSV.

        :param csv_path: Path to the CSV file containing the data for linking.
        :return: True on successful processing of all rows, False otherwise.
        """

        def link_callable(row: pd.Series):
            """Define a callable for link series to process component operation"""
            self.link_series_to_component(row['name'],
                                          row['process'],
                                          )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.SERIES_PROCESS_LINKING_EXPECTED_CSV_COLUMNS,
                                   link_callable,
                                   'series_process_linking',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_link_series_to_component(self, csv_path: str):
        """
        Processes a CSV file to bulk un-link series to component from provided CSV.

        :param csv_path: Path to the CSV file containing the data for linking.
        :return: True on successful processing of all rows, False otherwise.
        """

        def delete_link_callable(row: pd.Series):
            """Define a callable for link series to process component operation"""
            self.delete_link_series_to_component(row['name'],
                                                 row['process'],
                                                 )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.SERIES_PROCESS_LINKING_EXPECTED_CSV_COLUMNS,
                                   delete_link_callable,
                                   'series_process_unlinking',
                                   upload_multithreaded=self.upload_multithreaded)
