# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_session_state_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "session_state",
        "type": "object",
        "id": "string",
        "properties": {
            "id": {
                "type": ["string", "null"],
                "format": "uuid"
            },
            "user_id": {
                "type": ["string", "null"],
                "format": "uuid"
            },
            "json": {
                "type": ["object", "null"]
            },
            "report": {
                "type": "string",
            },
            "name": {
                "type": "string",
            },
            "code": {
                "type": ["string", "null"]
            },
            "is_default": {
                "type": ["boolean", "null"]
            },
            "range": {
                "type": ["string", "null"]
            },
            "download_url": {
                "type": ["string", "null"],
                "format": "uri"
            },
            "visibility": {
                "type": ["string", "null"]
            },
            "default_folder_id": {
                "type": ["string", "null"],
                "format": "uuid"
            },
            "user": {
                "relation": "to-one",
                "resource": "users"
            },
            "default_folder": {
                "relation": "to-one",
                "resource": "folder"
            },
            "folders": {
                "relation": "to-many",
                "resource": ["folder"]
            },
            "tiles": {
                "relation": "to-many",
                "resource": ["tile"]
            },
            "groups": {
                "relation": "to-many",
                "resource": ["group"]
            },
        },
        "additionalProperties": True,
        "required": ["report", "name"],
    }
