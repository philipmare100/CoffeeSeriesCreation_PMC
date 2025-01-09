# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_component_type_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "component_type",
        "type": "object",
        "id": "string",
        "properties": {
            "name": {
                "type": "string"
            },
            "description": {
                "type": ["string", "null"]
            },
            # "json": {
            #     "type": "object",
            #     "properties": "null"
            # },
            "base_type": {
                "type": "string",
                "enum": ["component", "process", "equipment", "stream", "part", "resource"]
            },
            "component_category_id": {
                "type": ["string", "null"],
                "format": "uuid"
            },
            "constant_properties": {
                "relation": "to-many",
                "resource": ["constant_property"]
            },
            "series_properties": {
                "relation": "to-many",
                "resource": ["series_property"]
            },
            "components": {
                "relation": "to-many",
                "resource": ["component"]
            },
            "component_type_constants": {
                "relation": "to-many",
                "resource": ["component_type_constant"]
            },
            "property_categories": {
                "relation": "to-many",
                "resource": ["property_category"]
            },
            "event_types": {
                "relation": "to-many",
                "resource": ["event_type"]
            },
            "component_type_component_type": {
                "relation": "to-many",
                "resource": ["component_type_component_type"]
            },
        },
        "required": ["name", "base_type"],
        "additionalProperties": True
    }

# The actual Python schema representation might be different based on how jsonapi-client library implements or
# expects schema data.
