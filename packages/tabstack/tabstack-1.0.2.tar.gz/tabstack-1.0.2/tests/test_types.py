"""Tests for response type classes."""

import pytest

from tabstack.types import (
    AutomateEvent,
    EventData,
    JsonResponse,
    MarkdownResponse,
    Metadata,
    SchemaResponse,
)


class TestMetadata:
    """Tests for Metadata class."""

    def test_initialization_with_all_fields(self) -> None:
        """Test Metadata initialization with all fields."""
        metadata = Metadata(
            title="Test Title",
            description="Test Description",
            author="Test Author",
            publisher="Test Publisher",
            image="https://example.com/image.jpg",
            site_name="Test Site",
            url="https://example.com",
            type="article",
        )
        assert metadata.title == "Test Title"
        assert metadata.description == "Test Description"
        assert metadata.author == "Test Author"
        assert metadata.publisher == "Test Publisher"
        assert metadata.image == "https://example.com/image.jpg"
        assert metadata.site_name == "Test Site"
        assert metadata.url == "https://example.com"
        assert metadata.type == "article"

    def test_initialization_with_no_fields(self) -> None:
        """Test Metadata initialization with no fields."""
        metadata = Metadata()
        assert metadata.title is None
        assert metadata.description is None
        assert metadata.author is None

    def test_from_dict(self) -> None:
        """Test creating Metadata from dictionary."""
        data = {
            "title": "Test",
            "description": "Description",
            "author": "Author",
        }
        metadata = Metadata.from_dict(data)
        assert metadata.title == "Test"
        assert metadata.description == "Description"
        assert metadata.author == "Author"
        assert metadata.publisher is None  # Not in dict

    def test_to_dict_with_all_fields(self) -> None:
        """Test converting Metadata to dictionary."""
        metadata = Metadata(title="Test", description="Desc", author="Auth")
        result = metadata.to_dict()
        assert result == {
            "title": "Test",
            "description": "Desc",
            "author": "Auth",
        }

    def test_to_dict_excludes_none_values(self) -> None:
        """Test to_dict excludes None values."""
        metadata = Metadata(title="Test")
        result = metadata.to_dict()
        assert result == {"title": "Test"}
        assert "description" not in result


class TestMarkdownResponse:
    """Tests for MarkdownResponse class."""

    def test_initialization_with_metadata(self) -> None:
        """Test MarkdownResponse with metadata."""
        metadata = Metadata(title="Test")
        response = MarkdownResponse(url="https://example.com", content="# Test", metadata=metadata)
        assert response.url == "https://example.com"
        assert response.content == "# Test"
        assert response.metadata == metadata

    def test_initialization_without_metadata(self) -> None:
        """Test MarkdownResponse without metadata."""
        response = MarkdownResponse(url="https://example.com", content="# Test")
        assert response.url == "https://example.com"
        assert response.content == "# Test"
        assert response.metadata is None

    def test_from_dict_with_metadata(self) -> None:
        """Test creating MarkdownResponse from dict with metadata."""
        data = {
            "url": "https://example.com",
            "content": "# Test",
            "metadata": {"title": "Test Title"},
        }
        response = MarkdownResponse.from_dict(data)
        assert response.url == "https://example.com"
        assert response.content == "# Test"
        assert response.metadata is not None
        assert response.metadata.title == "Test Title"

    def test_from_dict_without_metadata(self) -> None:
        """Test creating MarkdownResponse from dict without metadata."""
        data = {"url": "https://example.com", "content": "# Test"}
        response = MarkdownResponse.from_dict(data)
        assert response.metadata is None


class TestSchemaResponse:
    """Tests for SchemaResponse class."""

    def test_initialization(self) -> None:
        """Test SchemaResponse initialization."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        response = SchemaResponse(schema=schema)
        assert response.schema == schema

    def test_from_dict(self) -> None:
        """Test creating SchemaResponse from dict."""
        schema = {"type": "array", "items": {"type": "string"}}
        response = SchemaResponse.from_dict(schema)
        assert response.schema == schema


class TestJsonResponse:
    """Tests for JsonResponse class."""

    def test_initialization_with_dict(self) -> None:
        """Test JsonResponse with dictionary data."""
        data = {"name": "John", "age": 30}
        response = JsonResponse(data=data)
        assert response.data == data

    def test_initialization_with_list(self) -> None:
        """Test JsonResponse with list data."""
        data = [{"id": 1}, {"id": 2}]
        response = JsonResponse(data=data)
        assert response.data == data

    def test_from_dict(self) -> None:
        """Test creating JsonResponse from data."""
        data = {"items": [{"name": "Item 1"}]}
        response = JsonResponse.from_dict(data)
        assert response.data == data


class TestEventData:
    """Tests for EventData class."""

    def test_attribute_access_exact_match(self) -> None:
        """Test accessing attributes with exact key match."""
        data = {"message": "test", "status": "ok"}
        event_data = EventData(data)
        assert event_data.message == "test"
        assert event_data.status == "ok"

    def test_attribute_access_camel_case_conversion(self) -> None:
        """Test accessing attributes with snake_case to camelCase conversion."""
        data = {"finalAnswer": "done", "extractedData": {"key": "value"}}
        event_data = EventData(data)
        # Python-style snake_case access
        assert event_data.final_answer == "done"
        assert event_data.extracted_data == {"key": "value"}

    def test_attribute_not_found_raises_error(self) -> None:
        """Test accessing non-existent attribute raises AttributeError."""
        event_data = EventData({"message": "test"})
        with pytest.raises(AttributeError, match="EventData has no attribute"):
            _ = event_data.nonexistent

    def test_get_method_with_default(self) -> None:
        """Test get method with default value."""
        event_data = EventData({"message": "test"})
        assert event_data.get("message") == "test"
        assert event_data.get("missing", "default") == "default"

    def test_get_method_without_default(self) -> None:
        """Test get method without default returns None."""
        event_data = EventData({"message": "test"})
        assert event_data.get("missing") is None

    def test_raw_property(self) -> None:
        """Test accessing raw dictionary."""
        data = {"key": "value"}
        event_data = EventData(data)
        assert event_data.raw == data

    def test_repr(self) -> None:
        """Test string representation."""
        data = {"key": "value"}
        event_data = EventData(data)
        assert repr(event_data) == "EventData({'key': 'value'})"


class TestAutomateEvent:
    """Tests for AutomateEvent class."""

    def test_initialization(self) -> None:
        """Test AutomateEvent initialization."""
        data = {"message": "test", "status": "ok"}
        event = AutomateEvent(type="start", data=data)
        assert event.type == "start"
        assert isinstance(event.data, EventData)
        assert event.data.message == "test"

    def test_data_access(self) -> None:
        """Test accessing event data."""
        data = {"finalAnswer": "completed", "success": True}
        event = AutomateEvent(type="task:completed", data=data)
        # Access via attribute (with camelCase conversion)
        assert event.data.final_answer == "completed"
        # Access via get method (exact key)
        assert event.data.get("success") is True

    def test_repr(self) -> None:
        """Test string representation."""
        data = {"message": "test"}
        event = AutomateEvent(type="start", data=data)
        repr_str = repr(event)
        assert "AutomateEvent" in repr_str
        assert "type='start'" in repr_str
        assert "{'message': 'test'}" in repr_str
