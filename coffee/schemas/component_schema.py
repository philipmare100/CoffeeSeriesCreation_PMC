# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_component_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Component",
        "type": "object",
        "properties": {
            "id": {
                "type": ["string", "null"],
            },
            "revision_id": {
                "type": ["string", "null"],
            },
            "name": {
                "type": "string"
            },
            "description": {
                "type": ["string", "null"]
            },
            "component_type_id": {
                "type": ["string", "null"],
            },
            "base_type": {
                "type": "string",
                "enum": ["component", "process", "equipment", "stream", "part", "resource"],
                "default": "component",
            },
            "code": {
                "type": ["string", "null"]
            },
            "json": {
                "type": "object",
                "additionalProperties": True,
                "properties": {},
            },
            "start_time": {
                "type": ["string", "null"],
            },
            "end_time": {
                "type": ["string", "null"],
            },
            "component_type": {
                "relation": "to-one",
                "resource": "component_type"
            },
            "revision": {
                "relation": "to-one",
                "resource": "revision"
            },
            "equipment": {
                "relation": "to-many",
                "resource": ["equipment"]
            },
            "constant_components": {
                "relation": "to-many",
                "resource": ["constant_Component"]
            },
            "series_components": {
                "relation": "to-many",
                "resource": ["series_component"]
            },
            "constant_property_components": {
                "relation": "to-many",
                "resource": ["constant_property_component"]
            },
            "event_components": {
                "relation": "to-many",
                "resource": ["event_components"]
            },
            "events": {
                "relation": "to-many",
                "resource": ["event"]
            },
            "data_series": {
                "relation": "to-many",
                "resource": ["series"]
            },
            "series": {
                "relation": "to-many",
                "resource": ["series"]
            },
            "component_component": {
                "relation": "to-many",
                "resource": ["component_component"]
            }
        },
        "required": ["name", "base_type"],
        "additionalProperties": True
    }

# The actual Python schema representation might be different based on how jsonapi-client library implements or
# expects schema data.
