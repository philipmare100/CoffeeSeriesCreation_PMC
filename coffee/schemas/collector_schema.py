# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_component_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "collector",
        "type": "object",
        "properties": {
            "id": {
                "type": ["string", "null"],
            },
            "name": {
                "type": ["string", "null"],
            },
            "description": {
                "type": ["string", "null"],
            },
            "parser_config": {
                "type": "object",
                "properties": {}
            },
            "connection_string": {
                "type": ["string", "null"],
            },
            "frequency": {
                "type": ["number", "null"]
            },
            "timezone": {
                "type": ["number", "null"]
            },
            "last_imported": {
                "type": ["string", "null"],
                "format": "date-time"
            },
            "max_hours_to_import": {
                "type": ["number", "null"]
            },
            "series_column": {
                "type": ["string", "null"],
            },
            "timestamp_column": {
                "type": ["string", "null"],
            },
            "value_column": {
                "type": ["string", "null"],
            },
            "query_function": {
                "type": ["string", "null"],
            },
            "table": {
                "type": ["string", "null"],
            },
            "schema": {
                "type": ["string", "null"],
            },
            "email_settings": {
                "type": "object",
                "properties": {}
            },
            "email_address": {
                "type": ["string", "null"],
            },
            "allowed_emails": {
                "type": ["string", "null"],
            },
            "external_allowed_emails": {
                "type": "object",
                "properties": {}
            },
            "attachment_type": {
                "type": ["string", "null"],
            },
            "expected_data_frequency": {
                "type": ["number", "null"]
            },
            "json": {
                "type": "object",
                "properties": {}
            },
            "mappers": {
                "relation": "to-many",
                "resource": ["mapper"]
            },
            "users": {
                "relation": "to-many",
                "resource": ["users"]
            },
            "collector_alerts_users": {
                "relation": "to-many",
                "resource": ["users"]
            }
        },
        "required": ["name"],
        "additionalProperties": True
    }

# The actual Python schema representation might be different based on how jsonapi-client library implements or
# expects schema data.
