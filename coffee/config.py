import logging
from uuid import UUID

import pandera as pa
from dotenv import load_dotenv
from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()


class Settings(BaseSettings):
    API_ACCOUNT_ID: UUID
    API_TOKEN: str
    API_BASE_URL: str
    LOG_LEVEL: str = 'INFO'
    DISABLE_SSL_WARNINGS: bool = False
    CONCURRENT_REQUEST_LIMIT: int = 4

    @field_validator('API_TOKEN')
    def validate_jwt(cls, v):
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError("API_TOKEN must be a valid JWT")
        return v

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )


def get_setting_with_input(setting_name: str, settings: Settings):
    """Get setting value, asking user input if not found."""
    value = getattr(settings, setting_name, None)
    if not value:
        setattr(settings, setting_name, input(f"Enter value for {setting_name} (important): "))
    return getattr(settings, setting_name)


settings = None
try:
    settings = Settings()  # Automatically load settings from environment variables and .env file
except ValidationError as e:
    logging.error(e.json())
    # ToDo: What do we do when env vars not set?
    raise

if isinstance(settings, Settings):
    # Configure logging
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
else:
    logging.warning(f'`settings` not configured')


class WorkflowConfig:
    """
    Configuration class for specifying expected columns and Pandera data types
    for different bulk workflows.

    Each bulk workflow is represented as a dictionary within the class,
    mapping column names to their expected Pandera data types. This setup
    facilitates easy maintenance and extension of validation schemas for
    various data processing tasks.

    Example:
    ```
    COLLATION_SERIES_EXPECTED_CSV_COLUMNS = {
        "component_type": pa.String,
        "constant_property": pa.String,
        "series": pa.String,
        "account": pa.String,
    }
    ```

    Pandera DataTypes:
    - `pa.String`: Specifies that the column should be of string type.
    - `pa.Int`: Specifies that the column should be of integer type.
    - `pa.Float`: Specifies that the column should be of float type.
    - `pa.DateTime`: Specifies that the column should be a datetime object.

    These data types ensure that each column not only exists but also matches
    the expected format, enhancing data quality and consistency.
    """

    # Workflow expected columns with Pandera data types
    SERIES_EXPECTED_CSV_COLUMNS = {
        "name": pa.Column(pa.String),
        "is_calculation": pa.Column(pa.Bool, required=False),
        "new_name":pa.Column(pa.String, required=False), # Used for PATCH requests
        "description": pa.Column(pa.String, required=False),
        "fill_method": pa.Column(pa.String, required=False),
        "source_series": pa.Column(pa.String, required=False),
        "sample_period": pa.Column(pa.String, required=False),
        "weighted_average_series": pa.Column(pa.String, required=False),
        "aggregation": pa.Column(pa.String, required=False),
        "name_formula": pa.Column(pa.String, required=False, nullable=True),
        "engineering_unit": pa.Column(pa.String, required=False),
        "series_type": pa.Column(pa.String, required=False),
        "process": pa.Column(pa.String, required=False),
    }

    SERIES_PROCESS_LINKING_EXPECTED_CSV_COLUMNS = {
        "name": pa.Column(pa.String),  # Series name
        "process": pa.Column(pa.String),
    }

    COMPONENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS = {
        "component_type": pa.Column(pa.String),
        "constant_property": pa.Column(pa.String),
        "time_constant_property": pa.Column(pa.String),
        "series": pa.Column(pa.String),
    }

    EVENT_COLLATION_SERIES_EXPECTED_CSV_COLUMNS = {
        "event_type": pa.Column(pa.String),
        "constant_property": pa.Column(pa.String),
        "time_constant_property": pa.Column(pa.String),
        "series": pa.Column(pa.String),
    }

    CONSTANT_PROPERTY_EXPECTED_CSV_COLUMNS = {
        "name": pa.Column(pa.String),
        "new_name": pa.Column(pa.String, required=False),
        "description": pa.Column(pa.String, required=False),
        "data_type": pa.Column(pa.String, required=False),
        "is_drop_down_list": pa.Column(pa.Bool, required=False),
        "is_calculation": pa.Column(pa.Bool, required=False),
        "json": pa.Column(pa.Object, required=False),
        "aggregation": pa.Column(pa.String, required=False),
        "name_formula": pa.Column(pa.String, required=False, nullable=True),
    }

    CPCT_LINKING_EXPECTED_CSV_COLUMNS = {
        "name": pa.Column(pa.String),  # Constant Property name
        "component_type": pa.Column(pa.String),
    }

    CPET_LINKING_EXPECTED_CSV_COLUMNS = {
        "name": pa.Column(pa.String),  # Constant Property name
        "event_type": pa.Column(pa.String),
    }
