from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_series_component_schema():
    """JSON:API schema for series component. Used for all CRUD operations."""
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "series_component",
        "type": "object",
        "id": "string",
        "properties": {
            "id": {
                "type": ["string", "null"]
            },
            "component": {
                "relation": "to-one",
                "resource": ["component"],
            },
            "component_id": {
                "type": ["string", "null"]
            },
            "series": {
                "relation": "to-one",
                "resource": ["series"],
            },
            "series_id": {
                "type": ["string", "null"],
            },
            "series_property_id": {
                "type": ["string", "null"],
            },
            "series_property": {
                "relation": "to-one",
                "resource": ["series_property"],
            },
            "can_edit": {
                "type": "boolean",
                "default": False,
            },
            "report_group": {
                "type": ["string", "null"]
            },
            "view_on_flowchart": {
                "type": "boolean",
                "default": False,
            },
            "view_on_parent_flowchart": {
                "type": "boolean",
                "default": False,
            },
            "series_order": {
                "type": ["number", "null"]
            },
            "json": {
                "type": "object",
                "properties": {}
            },
        },
        "required": ["component_id", "series_id"],
        "additionalProperties": True,
        "description": "Mapping between Constant Property and Component Type, ensuring a unique constraint on "
                       "event type and constant property."
    }
