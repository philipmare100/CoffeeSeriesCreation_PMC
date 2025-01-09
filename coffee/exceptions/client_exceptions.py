class ResourceNotFoundException(Exception):
    """Exception raised when a resource is not found, by GET request."""
    pass


class InvalidResourceTypeException(Exception):
    """Exception raised when the resource type is not in the supported types list in the `relationship_model_map`."""
    pass


class NoDataReturnedException(Exception):
    """Exception raised when no data is returned."""
    pass