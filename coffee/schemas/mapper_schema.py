# This schema definition assumes the use of JSON Schema for validation within the jsonapi-client library.
from coffee.schemas.base_schema import with_base_properties


@with_base_properties
def get_mapper_schema():
    return {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "mapper",
        "type": "object",
        "id": "string",
        "properties": {
            "source_name": {
                "type": ["string", "null"]
            },
            "pre_process": {
                "type": ["string", "null"]
            },
            "series_id": {
                "type": ["string", "null"]
            },
            "series": {
                "relation": "to-one",
                "resource": ["series"]
            },
            "collector_id": {
                "type": ["string", "null"]
            },
            "collector": {
                "relation": "to-one",
                "resource": ["collector"]
            },
            "downtime_last_updated": {
                "type": ["string", "null"],
            },
            "invert_signal": {
                "type": ["boolean", "null"]
            },
            "create_events": {
                "type": ["boolean", "null"]
            },
            "save_opsdata": {
                "type": ["boolean", "null"]
            },
            "interpolated": {
                "type": ["boolean", "null"]
            },
            "import_client_historian": {
                "type": ["boolean", "null"]
            },
            "send_alerts": {
                "type": ["boolean", "null"]
            },
            "aggregation_method": {
                "type": ["string", "null"],
                # "enum": ["mean", "total", "difference", "mean_excluding_zeros", "mean_excluding_negatives", "latest_value", "time_weighted_average"],
                # "default": "mean",
            },
            "high_frequency_collection": {
                "type": ["boolean", "null"]
            },
            "priority": {
                "type": ["string", "null"]
            },
            "data_last_updated": {
                "type": ["string", "null"],
                "format": "date-time"
            },


        },
        "required": ["source_name", "aggregation_method"],
        "additionalProperties": True
    }
