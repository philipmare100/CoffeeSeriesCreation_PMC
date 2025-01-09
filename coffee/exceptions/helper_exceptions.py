class UnsupportedModelTypeException(Exception):
    """Exception raised when an unsupported model type is provided for payload generation."""
    pass


class UnrecognisedRelationshipException(Exception):
    """Exception raised when an unrecognized relationship name is provided."""
    pass


class InvalidResourceObjectException(Exception):
    """Exception raised when an object is not a valid instance of `ResourceObject`."""
    pass


class InvalidCalculationGraphException(Exception):
    """Exception raised when graph does not have a start node - no item is set to calculation"""
    pass


class MultipleFormulaColumnException(Exception):
    """Exception raised when multiple formula columns are found where fewer or one was expected."""
    def __init__(self, message="Multiple formula columns found in CSV/DataFrame"):
        self.message = message
        super().__init__(self.message)
