from .base_schema import get_base_schema
from .component_constant_collation_series_export_schema import get_component_constant_collation_series_export_schema
from .component_type_schema import get_component_type_schema
from .constant_property_component_type_schema import get_constant_property_component_type_schema
from .constant_property_event_type_schema import get_constant_property_event_type_schema
from .constant_property_schema import get_constant_property_schema
from .event_constant_collation_series_export_schema import get_event_constant_collation_series_export_schema
from .event_type_schema import get_event_type_schema
from .mapper_schema import get_mapper_schema
from .process_component_schema import get_process_component_schema
from .registry import schema_registry
from .series_component_schema import get_series_component_schema
from .series_schema import get_series_schema
from .session_state_schema import get_session_state_schema
from .tile_schema import get_tile_schema

# TODO: Move to schema_registry method
api_schema_all = {
    'base': get_base_schema(),
    'constant_property': get_constant_property_schema(),
    'component_type': get_component_type_schema(),
    'event_type': get_event_type_schema(),
    'constant_property_component_type': get_constant_property_component_type_schema(),
    'constant_property_event_type': get_constant_property_event_type_schema(),
    'component_constant_collation_series_export': get_component_constant_collation_series_export_schema(),
    'event_constant_collation_series_export': get_event_constant_collation_series_export_schema(),
    'mapper': get_mapper_schema(),
    'process': get_process_component_schema(),
    'series_component': get_series_component_schema(),
    'series': get_series_schema(),
    'session_state': get_session_state_schema(),
    'tile': get_tile_schema(),
}

# Register all schemas at the initialization phase
schema_registry.register('base', get_base_schema())
schema_registry.register('constant_property', get_constant_property_schema())
schema_registry.register('component_type', get_component_type_schema())
schema_registry.register('event_type', get_event_type_schema())
schema_registry.register('constant_property_component_type', get_constant_property_component_type_schema())
schema_registry.register('constant_property_event_type', get_constant_property_event_type_schema())
schema_registry.register('component_constant_collation_series_export', get_component_constant_collation_series_export_schema())
schema_registry.register('event_constant_collation_series_export', get_event_constant_collation_series_export_schema())
schema_registry.register('mapper', get_mapper_schema())
schema_registry.register('process', get_process_component_schema())
schema_registry.register('series_component', get_series_component_schema())
schema_registry.register('series', get_series_schema())
schema_registry.register('session_state', get_session_state_schema())
schema_registry.register('tile', get_tile_schema())
