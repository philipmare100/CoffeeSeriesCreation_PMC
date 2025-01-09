import re
import time
from typing import Dict, List

import pandas as pd
import pandera as pa

from coffee.config import logger
from coffee.exceptions.client_exceptions import InvalidResourceTypeException
from coffee.exceptions.database_exceptions import UniqueViolationError, NotNullViolationError
from coffee.exceptions.helper_exceptions import InvalidResourceObjectException, UnrecognisedRelationshipException, \
    UnsupportedModelTypeException
from coffee.jsonapi_client.common import ResourceNameTuple
from coffee.jsonapi_client.resourceobject import ResourceObject


def check_csv_format(df: pd.DataFrame, expected_columns: Dict[str, pa.dtypes.DataType]) -> bool:
    """
    Validates a DataFrame against a specified schema configuration to ensure it
    contains the expected columns and data types.

    :param df: The DataFrame to validate.
    :type df: pd.DataFrame
    :param expected_columns: A dictionary mapping column names to Pandera Column
        objects, specifying the expected schema.
    :type expected_columns: dict
    :raises ValueError: If the DataFrame does not conform to the expected schema,
      detailing which columns are missing or have incorrect data types.

    This function utilises Pandera's DataFrameSchema to define and apply
    validation rules, offering a structured approach to data validation.
    """

    # Define the schema based on the workflow configuration
    pa_schema = pa.DataFrameSchema(expected_columns)

    # Validate the DataFrame against the schema
    try:
        pa_schema.validate(df, lazy=True)  # Collect all validation errors
        return True
    except pa.errors.SchemaErrors as e:
        error_messages = e.failure_cases[["column", "failure_case"]].to_string(index=False)
        raise ValueError(f"DataFrame format validation failed:\n{error_messages}")


# Define the relationship_name to model_type_name map
relationship_model_map = {
    'collation_series': 'series',
    'series': 'series',
    'constant_property_component_type': 'constant_property_component_type',
    'time_constant_property': 'constant_property',
    'constant_property': 'constant_property',
    'component_type': 'component_type',
    'event_type': 'event_type',
    'account': 'account',
    'component': 'component',
    'process': 'process'
}


def generate_jsonapi_payload(model_type: str, relationships: Dict[str, ResourceObject]):
    """
    Generates a JSONAPI payload for a POST request to create relationships between models.

    :param model_type: The model type to which the relationships are being posted.
    :type model_type: str
    :param relationships: A dictionary with keys as relationship names and values as ResourceObjects.
    :type relationships: Dict[str, ResourceObject]
    :return: A dictionary representing the JSON payload.
    """
    # Initialise the payload structure with the dynamic model type
    if model_type in relationship_model_map.values():
        payload = {
            "data": {
                "type": model_type,
                "relationships": {}
            }
        }
    else:
        msg = f"Model type `{model_type}` payload-generation not support. Check spelling and try again."
        logger.error(msg)
        raise UnsupportedModelTypeException(msg)

    # Iterate through the relationships to populate the payload
    for relationship_name, resource_object in relationships.items():
        # Use the relationship model map to get the correct model type for the relationship
        relationship_model_type = relationship_model_map.get(relationship_name)

        if isinstance(resource_object, ResourceObject):
            if relationship_model_type:
                # Construct the relationship payload assuming resource_object has an 'id' attribute
                relationship_payload = {
                    "data": {
                        "type": relationship_model_type,
                        "id": resource_object.id  # Accessing the 'id' attribute
                    }
                }

                # Update the payload with the relationship data
                payload["data"]["relationships"][relationship_name] = relationship_payload
            else:
                # Handle the case where the relationship name is not recognised
                msg = f"Warning: '{relationship_name}' is not a recognised relationship name."
                logger.error(msg)
                raise UnrecognisedRelationshipException(msg)
        else:
            msg = f"{resource_object} not an instance of `ResourceObject`."
            logger.error(msg)
            raise InvalidResourceObjectException(msg)

    return payload


def validate_linked_resource_types(linked_resources: List[ResourceNameTuple]) -> bool:
    """
    Validates that the types of the linked resources are included in the relationship model map.

    :param linked_resources: A list of ResourceNameTuple defining the resources to be validated.
    :type linked_resources: List[ResourceNameTuple]
    :return: True if all resource types are valid, False otherwise.
    :raises InvalidResourceTypeException: If any resource type is not valid according to the relationship model map.
    """
    for resource_tuple in linked_resources:
        resource_type = resource_tuple.type
        if resource_type not in relationship_model_map:
            raise InvalidResourceTypeException(f"Invalid resource type '{resource_type}'. This type is not recognised.")

    return True  # All resource types are valid


def post_request_error_parser(response_json, http_method=None, json_data=None):
    if json_data is None:
        json_data = {}

    msg = ''
    try:
        error = response_json.get('errors')[0]
    except KeyError as e:
        raise KeyError(f'Response does not contain an error: {e}')

    error_detail = error.get('detail')
    status_code = error.get('status')
    error_title = error.get('title')
    resource_type = json_data.get('data', {}).get('type')

    if 'psycopg2.errors' in error_detail:
        if 'UniqueViolation' in error_detail:
            msg = get_unique_violation_error_message(error_detail, resource_type)
            raise UniqueViolationError(msg, errors=response_json['errors'], status_code=status_code)
        if 'NotNullViolation' in error_detail:
            msg = get_not_null_violation_error_message(error_detail, resource_type)
            raise NotNullViolationError(msg, errors=response_json['errors'], status_code=status_code)
    return msg if msg else f'{error_title}: {error_detail}'


def get_unique_violation_error_message(error_detail: str, resource_type: str):
    resource_type = resource_type.replace('_', ' ').title().replace(' ', '')
    match = re.search(r"Key \((.+)\)=\((.+)\) already exists", error_detail)
    if match:
        keys, values = match.groups()
        exists_msg = f"A {resource_type} with key ({keys})=({values}) already exists."
        return exists_msg


def get_not_null_violation_error_message(error_detail: str, resource_type: str):
    # TODO: Implement full message.
    return error_detail


def exponential_backoff(retries: int) -> None:
    """
    Helper method to implement exponential backoff strategy.

    :param retries: The current number of retries.
    """
    delay = 2 ** retries  # Exponential backoff
    logger.warning(f"Retrying in {delay} seconds...")
    time.sleep(delay)