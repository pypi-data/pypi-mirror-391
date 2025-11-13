"""Tests for ExtractSync operator."""

from typing import Any

import pytest

from tabstack.extract_sync import ExtractSync
from tabstack.types import JsonResponse, MarkdownResponse, SchemaResponse


class TestExtractSyncMarkdown:
    """Tests for markdown extraction."""

    def test_markdown_without_metadata(
        self, mocker: Any, mock_markdown_response: dict[str, Any]
    ) -> None:
        """Test markdown extraction without metadata field."""
        mock_http = mocker.Mock()
        # Return response with metadata embedded in content
        response_data = {
            "url": "https://example.com",
            "content": "---\ntitle: Test\n---\n# Content",
        }
        mock_http.post.return_value = response_data

        extract = ExtractSync(mock_http)
        result = extract.markdown(url="https://example.com", metadata=False)

        assert isinstance(result, MarkdownResponse)
        assert result.url == "https://example.com"
        assert "# Content" in result.content
        assert result.metadata is None
        mock_http.post.assert_called_once_with(
            "v1/extract/markdown",
            {"url": "https://example.com"},
        )

    def test_markdown_with_metadata(
        self, mocker: Any, mock_markdown_response: dict[str, Any]
    ) -> None:
        """Test markdown extraction with separate metadata field."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = mock_markdown_response

        extract = ExtractSync(mock_http)
        result = extract.markdown(url="https://example.com", metadata=True)

        assert isinstance(result, MarkdownResponse)
        assert result.url == "https://example.com"
        assert result.metadata is not None
        assert result.metadata.title == "Example Page"
        assert result.metadata.description == "An example page"

    def test_markdown_with_nocache(self, mocker: Any) -> None:
        """Test markdown extraction with nocache flag."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = {
            "url": "https://example.com",
            "content": "# Test",
        }

        extract = ExtractSync(mock_http)
        extract.markdown(url="https://example.com", nocache=True)

        mock_http.post.assert_called_once_with(
            "v1/extract/markdown",
            {"url": "https://example.com", "nocache": True},
        )


class TestExtractSyncSchema:
    """Tests for schema generation."""

    def test_schema_generation(self, mocker: Any, mock_schema_response: dict[str, Any]) -> None:
        """Test schema generation from URL."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = mock_schema_response

        extract = ExtractSync(mock_http)
        result = extract.schema(url="https://example.com", instructions="Extract products")

        assert isinstance(result, SchemaResponse)
        assert result.schema == mock_schema_response
        assert "properties" in result.schema
        mock_http.post.assert_called_once_with(
            "v1/extract/json/schema",
            {
                "url": "https://example.com",
                "instructions": "Extract products",
            },
        )

    def test_schema_with_nocache(self, mocker: Any) -> None:
        """Test schema generation with nocache flag."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = {"type": "object", "properties": {}}

        extract = ExtractSync(mock_http)
        extract.schema(url="https://example.com", instructions="Test", nocache=True)

        call_args = mock_http.post.call_args
        assert call_args[0][1]["nocache"] is True


class TestExtractSyncJson:
    """Tests for JSON extraction."""

    def test_json_extraction_with_dict_schema(
        self, mocker: Any, mock_json_response: dict[str, Any], json_schema: dict[str, Any]
    ) -> None:
        """Test JSON extraction with dictionary schema."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = mock_json_response

        extract = ExtractSync(mock_http)
        result = extract.json(url="https://example.com", schema=json_schema)

        assert isinstance(result, JsonResponse)
        assert result.data == mock_json_response
        assert "items" in result.data
        mock_http.post.assert_called_once_with(
            "v1/extract/json",
            {
                "url": "https://example.com",
                "json_schema": json_schema,
            },
        )

    def test_json_extraction_validates_schema(
        self, mocker: Any, json_schema: dict[str, Any]
    ) -> None:
        """Test JSON extraction validates schema before sending."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = {"data": "test"}

        extract = ExtractSync(mock_http)

        # Valid schema should work
        extract.json(url="https://example.com", schema=json_schema)

        # Invalid schema should raise ValueError
        invalid_schema = {"invalid": "schema"}
        with pytest.raises(ValueError, match="Schema must have a 'type' field"):
            extract.json(url="https://example.com", schema=invalid_schema)

    def test_json_extraction_with_nocache(self, mocker: Any, json_schema: dict[str, Any]) -> None:
        """Test JSON extraction with nocache flag."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = {"result": "data"}

        extract = ExtractSync(mock_http)
        extract.json(url="https://example.com", schema=json_schema, nocache=True)

        call_args = mock_http.post.call_args
        assert call_args[0][1]["nocache"] is True

    def test_json_extraction_with_array_schema(self, mocker: Any) -> None:
        """Test JSON extraction with array schema."""
        mock_http = mocker.Mock()
        mock_http.post.return_value = [{"id": 1}, {"id": 2}]

        array_schema = {"type": "array", "items": {"type": "object"}}

        extract = ExtractSync(mock_http)
        result = extract.json(url="https://example.com", schema=array_schema)

        assert isinstance(result, JsonResponse)
        assert isinstance(result.data, list)
        assert len(result.data) == 2
