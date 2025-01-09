from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_component_constant_collation_series_export_schema():
    """JSON:API schema for component constant collation series export. Used for all CRUD operations."""
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "component_constant_collation_series_export",
        "type": "object",
        "id": "string",
        "properties": {
            "constant_property_component_type_id": {
                "type": ["string", "null"]
            },
            "constant_property_component_type": {
                "relation": "to-one",
                "resource": ["constant_property_component_type"],
            },
            "time_constant_property_id": {
                "type": ["string", "null"],
            },
            "time_constant_property": {
                "relation": "to-one",
                "resource": ["constant_property"],
                "description": "The constant property used as the timestamp for exporting to time series. Must be of "
                               "DATETIME data type."
            },
            "collation_series_id": {
                "type": ["string", "null"]
            },
            "collation_series": {
                "relation": "to-one",
                "resource": ["series"],
                "description": "The series which collates the data being exported from the selected model."
            }
        },
        "required": ["constant_property_component_type_id", "collation_series_id"],
        "additionalProperties": True
    }
