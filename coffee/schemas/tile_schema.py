from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_tile_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "tile",
        "type": "object",
        "id": "string",
        "properties": {
            "id": {
                "type": ["string", "null"],
                "format": "uuid"
            },
            "content": {
                "type": "string"
            },
            "title": {
                "type": ["string", "null"]
            },
            "category": {
                "type": ["object", "null"]
            },
            "custom_dtp": {
                "type": ["boolean", "null"]
            },
            "relative_dtp": {
                "type": ["string", "null"]
            },
            "show_header": {
                "type": ["boolean", "null"]
            },
            "hide_edit": {
                "type": ["boolean", "null"]
            },
            "hide_scroll": {
                "type": ["boolean", "null"],
                "default": True
            },
            "range": {
                "type": ["string", "null"],
            },
            "sample_period": {
                "type": ["string", "null"],
                "default": "hour"
            },
            "start": {
                "type": ["string", "null"],
                "format": "date-time"
            },
            "end": {
                "type": ["string", "null"],
                "format": "date-time"
            },
            "calendar": {
                "type": "string",
                "default": "default"
            },
            "parameters": {
                "type": ["object", "null"]
            },
            "session_states": {
                "relation": "to-many",
                "resource": ["session_state"]
            },
        },
        "required": ["id", "content"],
        "additionalProperties": True
    }
