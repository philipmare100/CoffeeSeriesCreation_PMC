# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_event_type_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "event_type",
        "type": "object",
        "id": "string",
        "properties": {
            "name": {
                "type": "string"
            },
            "description": {
                "type": ["string", "null"]
            },
            "severity": {
                "type": ["integer", "null"]
            },
            "icon": {
                "type": ["string", "null"]
            },
            "base_type": {
                "type": "string",
                "enum": ["event", "comment", "correction_factor", "downtime"]
            },
            "behaviour": {
                "type": ["string", "null"]
            },
            "component_types": {
                "relation": "to-many",
                "resource": ["component_type"]
            },
            "events": {
                "relation": "to-many",
                "resource": ["event"]
            },
            "constant_properties": {
                "relation": "to-many",
                "resource": ["constant_property"]
            },
        },
        "required": ["name", "base_type"],
        "additionalProperties": True
    }
