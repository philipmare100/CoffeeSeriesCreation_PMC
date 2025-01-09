from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_constant_property_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "constant_property",
        "type": "object",
        "id": "string",
        "properties": {
            "name": {
                "type": "string"
            },
            "description": {
                "type": ["string", "null"]
            },
            "alias": {
                "type": ["string", "null"]
            },
            "is_calculation": {
                "type": "boolean",
                "default": False
            },
            "formula": {
                "type": ["string", "null"]
            },
            "name_formula": {
                "type": ["string", "null"]
            },
            "variables": {
                "type": ["array", "null"],
                "items": {
                    "type": "string"
                }
            },
            "variable_ids": {
                "type": ["array", "null"],
                "items": {
                    "type": "string"
                }
            },
            "aggregation": {
                "type": ["string", "null"],
                # "enum": ["total", "mean", "count"],
                # "default": "mean"
            },
            "is_drop_down_list": {
                "type": ["boolean", "null"],
                "default": False
            },
            "data_type": {
                "type": "string",
                "enum": ["float", "string", "datetime", "file"],
                "default": "float"
            },
            "file_type": {
                "type": ["string", "null"]
            },
            "calculation_type": {
                "type": ["string", "null"],
                # "enum": ["basic", "advanced"],
                "default": "basic"
            },
            "json": {
                "type": "object",
                "properties": {}
            },
            "time_series_conversion_method": {
                "type": ["string", "null"],
                # "enum": ["spread_from_start_to_end", "allocate_to_end", "allocate_to_start"],
                "default": "spread_from_start_to_end"
            },
            # "property_categories": {
            #     "type": "array",
            #     "items": {"type": "string"}
            # },
            "event_types": {
                "relation": "to-many",
                "resource": ["event_type"],
            },
            "component_types": {
                "relation": "to-many",
                "resource": ["component_type"],
            },
            # "ore_body_types": {
            #     "type": "array",
            #     "items": {"type": "string"}
            # },
            "weighted_by_id": {
                "type": ["string", "null"]
            },
            "positive_variance": {
                "type": ["boolean", "null"]
            }
        },
        "required": ["name", "is_calculation", "data_type"],
        "additionalProperties": True,
    }
