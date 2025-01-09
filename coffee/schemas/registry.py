class SchemaRegistry:
    def __init__(self):
        # Store schemas in the expected format (resource_type: schema)
        self.schemas = {}

    def register(self, resource_type, schema):
        """Register a schema by resource type."""
        self.schemas[resource_type] = schema

    def get_schema(self, resource_type):
        """Retrieve a schema by resource type."""
        return self.schemas.get(resource_type)

    def get_all_schemas(self):
        """Return all schemas as a dictionary of resource_type: schema."""
        return self.schemas

    def get_relationship_type(self, resource_type, attribute_name):
        """Get the relationship type for a specific attribute in a schema."""
        schema = self.get_schema(resource_type)
        if schema and 'properties' in schema:
            attribute = schema['properties'].get(attribute_name)
            if attribute and 'relation' in attribute:
                return attribute['relation']  # Return 'to-one' or 'to-many'
        return None

# Instantiate the schema registry globally
schema_registry = SchemaRegistry()