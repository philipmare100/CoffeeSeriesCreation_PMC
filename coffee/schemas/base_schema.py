def get_base_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "base",
        "type": "object",
        "id": "string",
        "properties": {
            "created_on": {
                "type": ["string", "null"]
            },
            "changed_on": {
                "type": ["string", "null"]
            },
            "created_by_name": {
                "type": ["string", "null"]
            },
            "created_by_lastname": {
                "type": ["string", "null"]
            },
            "changed_by_name": {
                "type": ["string", "null"]
            },
            "changed_by_lastname": {
                "type": ["string", "null"]
            },
            "account_name": {
                "type": ["string", "null"]
            },
            "account": {
                "relation": "to-one",
                "resource": ["account"]
            },
            "created_by": {
                "relation": "to-one",
                "resource": ["users"]
            },
            "changed_by": {
                "relation": "to-one",
                "resource": ["users"]
            },
        },
        "additionalProperties": True,
    }


def with_base_properties(schema_func):
    """Decorator to add audit properties to a schema function."""

    def wrapper(*args, **kwargs):
        schema = schema_func(*args, **kwargs)
        audit_schema = get_base_schema()
        schema["properties"].update(audit_schema["properties"])
        return schema

    return wrapper
