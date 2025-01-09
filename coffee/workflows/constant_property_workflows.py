import pandas as pd

from coffee.jsonapi_client.common import ResourceTuple
from coffee.jsonapi_client.resourceobject import ResourceObject
from coffee.client import JsonApiClient
from coffee.config import WorkflowConfig, logger
from coffee.utils.workflow_helpers import process_csv_generic, get_extra_kwargs
from coffee.workflows.base_workflows import BaseWorkflow
from coffee.resource_handlers import (
    ConstantPropertyComponentTypeHandler,
    ConstantPropertyEventTypeHandler,
    ConstantPropertyHandler,
    ComponentTypeHandler,
    EventTypeHandler,
)


class ConstantPropertyWorkflow(BaseWorkflow):

    def __init__(self, client: JsonApiClient, *args, **kwargs):
        super().__init__(client, *args, **kwargs)

        self.cp_main_cols = ['name', 'description', 'data_type']
        self.cp_lower_cols = ['aggregation', 'data_type']
        self.cp_expected_csv_cols = WorkflowConfig.CONSTANT_PROPERTY_EXPECTED_CSV_COLUMNS

    def create_constant_property(self,
                                 name: str,
                                 description: str,
                                 data_type: str,
                                 is_calculation: bool = False,
                                 name_formula: str = None,
                                 calculation_type: str = 'basic',
                                 time_series_conversion_method: str = 'spread_from_start_to_end',
                                 **kwargs
                                 ) -> ResourceObject | bool:
        """
        Creates a new constant property with specified attributes.

        :param name: Name of the constant property.
        :param description: Description of the constant property.
        :param data_type: Data type of the constant property (e.g., 'string', 'number').
        :param is_calculation: Indicates if the constant property is calculated. Default is False.
        :param name_formula: Formula used for calculation, applicable if is_calculation is True.
        :param calculation_type: Type of calculation ('basic' or other types).
        :param time_series_conversion_method: Method to convert time series data.
        :param kwargs: Additional keyword arguments for other properties.
        :return: A ResourceObject representing the constant property if successful, otherwise False.
        """
        # Initial ConstantProperty (CP) data
        new_constant_property_attrs = {
            'name': name,
            'description': description,
            'data_type': data_type,
        }

        # List of parameter names to ignore if they have their default value
        default_ignore_params = ['is_calculation', 'calculation_type', 'time_series_conversion_method']

        # Adding only fresh arguments to new_constant_property_data, skipping those meant to be ignored
        for key, value in kwargs.items():
            if key not in default_ignore_params and key not in new_constant_property_attrs:
                new_constant_property_attrs[key] = value

        # Include parameters only when they are explicitly set by the caller.
        if is_calculation:
            new_constant_property_attrs['is_calculation'] = is_calculation
        if name_formula:
            new_constant_property_attrs['name_formula'] = name_formula
        if calculation_type != 'basic':
            new_constant_property_attrs['calculation_type'] = calculation_type
        if time_series_conversion_method != 'spread_from_start_to_end':
            new_constant_property_attrs['time_series_conversion_method'] = time_series_conversion_method

        # Handle ConstantProperty (CP)
        cp_handler = ConstantPropertyHandler(self.client)
        cp_new = cp_handler.create(new_constant_property_attrs)
        cp_new.commit()
        logger.info(f'Successfully created a new ConstantProperty {cp_new.name}')
        return cp_new

    def patch_constant_property(self,
                                name: str,
                                new_name: str | None = None,
                                description: str | None = None,
                                data_type:  str | None = None,
                                is_calculation:  bool | None = None,
                                name_formula:  str | None = None,
                                calculation_type:  str | None = None,
                                time_series_conversion_method:  str | None = None,
                                **kwargs
                                ) -> ResourceObject | bool:
        """
        Patches constant property with specified attributes.

        :param name: Name of the constant property.
        :param new_name: New name of the constant property.
        :param description: Description of the constant property.
        :param data_type: Data type of the constant property (e.g., 'string', 'number').
        :param is_calculation: Indicates if the constant property is calculated. Default is False.
        :param name_formula: Formula used for calculation, applicable if is_calculation is True.
        :param calculation_type: Type of calculation ('basic' or other types).
        :param time_series_conversion_method: Method to convert time series data.
        :param kwargs: Additional keyword arguments for other properties.
        :return: A ResourceObject representing the constant property if successful, otherwise False.
        """
        # Include parameters only when they are explicitly set by the caller.
        patch_constant_property_attrs = {k: v for k, v in locals().items() if
                                         v is not None and k != 'self' and k != 'kwargs' and k != 'name' and k != 'new_name'}

        if new_name:
            patch_constant_property_attrs['name'] = new_name

        # Handle ConstantProperty (CP)
        cp_handler = ConstantPropertyHandler(self.client)
        cp = cp_handler.get_by_name(name).resource
        cp = cp_handler.patch(cp, patch_constant_property_attrs)
        logger.info(f'Successfully patched ConstantProperty {cp.name}')
        return cp

    def delete_constant_property(self,
                                 constant_property_name: str,
                                 **kwargs
                                 ) -> ResourceObject | bool:
        try:
            cp_handler = ConstantPropertyHandler(self.client)
            cp = cp_handler.get_by_name(constant_property_name).resource
            cp.delete()
            cp.commit()
            logger.info(f'Successfully deleted a ConstantProperty {constant_property_name}')
            return True
        except Exception as e:
            logger.info(f"Failed to deleted CP `{constant_property_name}`")
            raise

    def link_constant_property_to_component_type(self,
                                                 constant_property_name: str,
                                                 component_type_name: str,
                                                 **kwargs
                                                 ) -> ResourceObject | bool:
        """
        Links a constant property to a component type.

        :param constant_property_name: The name of the constant property to link.
        :param component_type_name: The name of the component type to link to the constant property.
        :param kwargs: Additional keyword arguments.
        :return: The linked ResourceObject if successful, otherwise False.
        """
        try:
            # Retrieve ConstantProperty (CP) resource object
            cp = ConstantPropertyHandler(self.client).get_by_name(constant_property_name).resource

            # Retrieve ComponentType (CT) resource object
            ct = ComponentTypeHandler(self.client).get_by_name(component_type_name).resource

            # Create ConstantPropertyComponentType (CPCT) link
            cpct_handler = ConstantPropertyComponentTypeHandler(self.client)
            relationships = {
                'constant_property': ResourceTuple(id=cp.id, type=cp.type),
                'component_type': ResourceTuple(id=ct.id, type=ct.type)
            }
            cpct = cpct_handler.create(relationships=relationships)
            cpct.commit()
            logger.info(f'Successfully created a new {cpct.type} with id {cpct.id}')
            return cpct
        except Exception as e:
            logger.error(f"Failed to create ConstantPropertyComponentType for CT `{component_type_name}` and CP "
                         f"`{constant_property_name}`: {e}")
            raise

    def delete_link_constant_property_to_component_type(self, constant_property_name: str, component_type_name: str):
        try:
            cpct_handler = ConstantPropertyComponentTypeHandler(self.client)
            cpct = cpct_handler.get_by_linked_cp_and_ct_names(constant_property_name, component_type_name).resource
            cpct.delete()
            cpct.commit()
            logger.info(f"Successfully deleted CTCP `{component_type_name}-{constant_property_name}`")
            return True
        except Exception as e:
            logger.info(f"Failed to deleted CTCP `{component_type_name}-{constant_property_name}`")
            raise

    def link_constant_property_to_event_type(self,
                                             constant_property_name: str,
                                             event_type_name: str,
                                             **kwargs
                                             ) -> ResourceObject | bool:
        """
        Links a constant property to an event type.

        :param constant_property_name: The name of the constant property to link.
        :param event_type_name: The name of the event type to link to the constant property.
        :param kwargs: Additional keyword arguments.
        :return: The linked ResourceObject if successful, otherwise False.
        """
        try:
            # Retrieve ConstantProperty (CP) resource object
            cp = ConstantPropertyHandler(self.client).get_by_name(constant_property_name).resource

            # Retrieve EventType (CT) resource object
            et = EventTypeHandler(self.client).get_by_name(event_type_name).resource

            # Create ConstantPropertyEventType (CPET) link
            cpet_handler = ConstantPropertyEventTypeHandler(self.client)
            relationships = {
                'constant_property': ResourceTuple(id=cp.id, type=cp.type),
                'event_type': ResourceTuple(id=et.id, type=et.type)
            }
            cpet = cpet_handler.create(relationships=relationships)
            cpet.commit()
            logger.info(f'Successfully created a new {cpet.type} with id {cpet.id}')
            return cpet
        except Exception as e:
            logger.error(f"Failed to create ConstantPropertyEventType for ET `{event_type_name}` and CP "
                         f"`{constant_property_name}`: {e}")
            raise

    def bulk_create_constant_property(self, csv_path):
        """
        Processes a CSV file to bulk create multiple constant properties from provided CSV.

        :param csv_path: Path to the CSV file containing the data for creation.
        :return: True on successful processing of all rows, False otherwise.
        """

        def create_callable(row: pd.Series):
            """Define a callable for create constant operation"""
            extra_kwargs = get_extra_kwargs(row,
                                            self.cp_main_cols,
                                            self.cp_lower_cols,
                                            self.cp_expected_csv_cols)

            self.create_constant_property(row['name'],
                                          row['description'],
                                          row['data_type'].lower(),
                                          **extra_kwargs
                                          )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CONSTANT_PROPERTY_EXPECTED_CSV_COLUMNS,
                                   create_callable,
                                   'cp_created',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_patch_constant_property(self, csv_path):
        """
        Processes a CSV file to bulk patch multiple constant properties from provided CSV.

        :param csv_path: Path to the CSV file containing the data for patch. Only include columns to be patched
        :return: True on successful processing of all rows, False otherwise.
        """

        def patch_callable(row: pd.Series):
            """Define a callable for patch constant operation"""
            extra_kwargs = get_extra_kwargs(row,
                                            ['name'],
                                            self.cp_lower_cols,
                                            self.cp_expected_csv_cols)

            self.patch_constant_property(row['name'],
                                         **extra_kwargs
                                         )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CONSTANT_PROPERTY_EXPECTED_CSV_COLUMNS,
                                   patch_callable,
                                   'cp_patched',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_constant_property(self, csv_path):
        def delete_callable(row: pd.Series):
            """Define a callable for create constant operation"""
            extra_kwargs = get_extra_kwargs(row,
                                            self.cp_main_cols,
                                            self.cp_lower_cols,
                                            self.cp_expected_csv_cols)

            self.delete_constant_property(row['name'],
                                          **extra_kwargs
                                          )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CONSTANT_PROPERTY_EXPECTED_CSV_COLUMNS,
                                   delete_callable,
                                   'cp_deleted',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_link_constant_property_to_component_type(self, csv_path: str):
        """
        Processes a CSV file to bulk link constant properties to component types from provided CSV.

        :param csv_path: Path to the CSV file containing the data for linking.
        :return: True on successful processing of all rows, False otherwise.
        """

        def link_callable(row: pd.Series):
            """Define a callable for link cp to ct operation"""
            self.link_constant_property_to_component_type(row['name'],
                                                          row['component_type'],
                                                          )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CPCT_LINKING_EXPECTED_CSV_COLUMNS,
                                   link_callable,
                                   'cpct_linking',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_delete_link_constant_property_to_component_type(self, csv_path: str):
        """
        Processes a CSV file to bulk un-link constant properties to component types from provided CSV.

        :param csv_path: Path to the CSV file containing the data for linking.
        :return: True on successful processing of all rows, False otherwise.
        """

        def delete_link_callable(row: pd.Series):
            """Define a callable for link cp to ct operation"""
            self.delete_link_constant_property_to_component_type(row['name'],
                                                                 row['component_type'],
                                                                 )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CPCT_LINKING_EXPECTED_CSV_COLUMNS,
                                   delete_link_callable,
                                   'cpct_unlinking',
                                   upload_multithreaded=self.upload_multithreaded)

    def bulk_link_constant_property_to_event_type(self, csv_path: str):
        """
        Processes a CSV file to bulk link constant properties to event types from provided CSV.

        :param csv_path: Path to the CSV file containing the data for linking.
        :return: True on successful processing of all rows, False otherwise.
        """

        def link_callable(row: pd.Series):
            """Define a callable for link cp to ct operation"""
            self.link_constant_property_to_event_type(row['name'],
                                                      row['event_type'],
                                                      )

        # Pass the callable to the generic processing method
        return process_csv_generic(csv_path,
                                   WorkflowConfig.CPET_LINKING_EXPECTED_CSV_COLUMNS,
                                   link_callable,
                                   'cpet_linking',
                                   upload_multithreaded=self.upload_multithreaded)
