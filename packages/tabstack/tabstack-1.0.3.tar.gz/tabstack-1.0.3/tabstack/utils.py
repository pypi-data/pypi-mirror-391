"""Utility functions for TabStack AI SDK."""

from typing import Any, Dict


def validate_json_schema(schema: Dict[str, Any]) -> None:
    """Validate that a dictionary is a basic JSON Schema.

    Performs lightweight validation to catch common schema errors before
    sending to the API. This is NOT a full JSON Schema validator - it only
    checks basic structure (type field, properties format, items format).

    The API performs complete validation and will return detailed errors
    for complex schema issues.

    Args:
        schema: Dictionary representing a JSON Schema

    Raises:
        ValueError: If the schema has basic structural problems

    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "name": {"type": "string"},
        ...         "age": {"type": "number"}
        ...     }
        ... }
        >>> validate_json_schema(schema)  # Passes validation
    """
    # Basic validation only - full validation happens at the API for better error messages
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dictionary")

    if not schema:
        raise ValueError("Schema cannot be empty")

    if "type" not in schema:
        raise ValueError("Schema must have a 'type' field")

    schema_type = schema["type"]
    valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]

    if schema_type not in valid_types:
        raise ValueError(f"Schema type must be one of {valid_types}, got '{schema_type}'")

    # For object types, validate properties structure
    if schema_type == "object":
        if "properties" in schema:
            properties = schema["properties"]
            if not isinstance(properties, dict):
                raise ValueError("Schema 'properties' must be a dictionary")

            # Validate each property is a valid schema
            for prop_name, prop_schema in properties.items():
                if not isinstance(prop_schema, dict):
                    raise ValueError(f"Property '{prop_name}' must be a dictionary schema")
                if "type" not in prop_schema:
                    raise ValueError(f"Property '{prop_name}' must have a 'type' field")

    # For array types, validate items structure
    elif schema_type == "array":
        if "items" not in schema:
            raise ValueError("Array schema must have an 'items' field")

        items = schema["items"]
        if not isinstance(items, dict):
            raise ValueError("Schema 'items' must be a dictionary")
        if "type" not in items:
            raise ValueError("Schema 'items' must have a 'type' field")
