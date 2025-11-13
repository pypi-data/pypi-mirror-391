"""Tests for utility functions."""

import pytest

from tabstack.utils import validate_json_schema


class TestValidateJsonSchema:
    """Tests for JSON Schema validation."""

    def test_valid_object_schema(self) -> None:
        """Test validation passes for valid object schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
        }
        validate_json_schema(schema)  # Should not raise

    def test_valid_array_schema(self) -> None:
        """Test validation passes for valid array schema."""
        schema = {
            "type": "array",
            "items": {"type": "string"},
        }
        validate_json_schema(schema)  # Should not raise

    def test_valid_primitive_schema(self) -> None:
        """Test validation passes for primitive type schemas."""
        for schema_type in ["string", "number", "integer", "boolean", "null"]:
            schema = {"type": schema_type}
            validate_json_schema(schema)  # Should not raise

    def test_empty_schema_raises_error(self) -> None:
        """Test empty schema raises ValueError."""
        with pytest.raises(ValueError, match="Schema cannot be empty"):
            validate_json_schema({})

    def test_non_dict_schema_raises_error(self) -> None:
        """Test non-dictionary schema raises ValueError."""
        with pytest.raises(ValueError, match="Schema must be a dictionary"):
            validate_json_schema("not a dict")  # type: ignore

    def test_missing_type_field_raises_error(self) -> None:
        """Test schema without type field raises ValueError."""
        schema = {"properties": {"name": {"type": "string"}}}
        with pytest.raises(ValueError, match="Schema must have a 'type' field"):
            validate_json_schema(schema)

    def test_invalid_type_raises_error(self) -> None:
        """Test invalid schema type raises ValueError."""
        schema = {"type": "invalid_type"}
        with pytest.raises(ValueError, match="Schema type must be one of"):
            validate_json_schema(schema)

    def test_object_properties_not_dict_raises_error(self) -> None:
        """Test object schema with non-dict properties raises ValueError."""
        schema = {"type": "object", "properties": "not a dict"}
        with pytest.raises(ValueError, match="'properties' must be a dictionary"):
            validate_json_schema(schema)

    def test_object_property_without_type_raises_error(self) -> None:
        """Test object property without type field raises ValueError."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"description": "Missing type field"},
            },
        }
        with pytest.raises(ValueError, match="Property 'name' must have a 'type' field"):
            validate_json_schema(schema)

    def test_object_property_not_dict_raises_error(self) -> None:
        """Test object property that's not a dict raises ValueError."""
        schema = {
            "type": "object",
            "properties": {
                "name": "not a dict",
            },
        }
        with pytest.raises(ValueError, match="Property 'name' must be a dictionary schema"):
            validate_json_schema(schema)

    def test_array_without_items_raises_error(self) -> None:
        """Test array schema without items field raises ValueError."""
        schema = {"type": "array"}
        with pytest.raises(ValueError, match="Array schema must have an 'items' field"):
            validate_json_schema(schema)

    def test_array_items_not_dict_raises_error(self) -> None:
        """Test array schema with non-dict items raises ValueError."""
        schema = {"type": "array", "items": "not a dict"}
        with pytest.raises(ValueError, match="Schema 'items' must be a dictionary"):
            validate_json_schema(schema)

    def test_array_items_without_type_raises_error(self) -> None:
        """Test array items without type field raises ValueError."""
        schema = {"type": "array", "items": {"description": "Missing type"}}
        with pytest.raises(ValueError, match="Schema 'items' must have a 'type' field"):
            validate_json_schema(schema)

    def test_nested_object_schema(self) -> None:
        """Test validation passes for nested object schema."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                    },
                },
            },
        }
        validate_json_schema(schema)  # Should not raise

    def test_array_of_objects_schema(self) -> None:
        """Test validation passes for array of objects schema."""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                },
            },
        }
        validate_json_schema(schema)  # Should not raise
