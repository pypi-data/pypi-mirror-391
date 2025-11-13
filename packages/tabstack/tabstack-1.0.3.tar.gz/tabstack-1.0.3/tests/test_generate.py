"""Tests for Generate operator."""

from typing import Any

import pytest

from tabstack.generate import Generate
from tabstack.types import JsonResponse


class TestGenerateJson:
    """Tests for JSON generation."""

    async def test_json_generation_with_markdown(
        self, mocker: Any, json_schema: dict[str, Any]
    ) -> None:
        """Test JSON generation from markdown content."""
        mock_http = mocker.AsyncMock()
        mock_http.post.return_value = {"summary": "Test summary", "keywords": ["test"]}

        generate = Generate(mock_http)
        result = await generate.json(
            url="https://example.com/article",
            schema=json_schema,
            instructions="Summarize this article",
        )

        assert isinstance(result, JsonResponse)
        assert "summary" in result.data
        mock_http.post.assert_called_once_with(
            "v1/generate/json",
            {
                "url": "https://example.com/article",
                "json_schema": json_schema,
                "instructions": "Summarize this article",
            },
        )

    async def test_json_generation_validates_schema(self, mocker: Any) -> None:
        """Test JSON generation validates schema before sending."""
        mock_http = mocker.AsyncMock()
        mock_http.post.return_value = {"data": "test"}

        generate = Generate(mock_http)

        # Valid schema should work
        valid_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        await generate.json(url="https://example.com", schema=valid_schema, instructions="Extract")

        # Invalid schema should raise ValueError
        invalid_schema = {}
        with pytest.raises(ValueError, match="Schema cannot be empty"):
            await generate.json(
                url="https://example.com", schema=invalid_schema, instructions="Extract"
            )

    async def test_json_generation_with_complex_schema(self, mocker: Any) -> None:
        """Test JSON generation with nested schema."""
        mock_http = mocker.AsyncMock()
        mock_response = {
            "article": {
                "title": "Test",
                "author": {"name": "John", "email": "john@example.com"},
            }
        }
        mock_http.post.return_value = mock_response

        complex_schema = {
            "type": "object",
            "properties": {
                "article": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "author": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                            },
                        },
                    },
                }
            },
        }

        generate = Generate(mock_http)
        result = await generate.json(
            url="https://example.com/article",
            schema=complex_schema,
            instructions="Extract article metadata",
        )

        assert isinstance(result, JsonResponse)
        assert result.data == mock_response
        assert result.data["article"]["author"]["name"] == "John"

    async def test_json_generation_with_array_output(self, mocker: Any) -> None:
        """Test JSON generation that returns an array."""
        mock_http = mocker.AsyncMock()
        mock_http.post.return_value = [
            {"name": "Item 1", "score": 95},
            {"name": "Item 2", "score": 87},
        ]

        array_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "score": {"type": "number"},
                },
            },
        }

        generate = Generate(mock_http)
        result = await generate.json(
            url="https://example.com/rankings",
            schema=array_schema,
            instructions="Extract rankings",
        )

        assert isinstance(result, JsonResponse)
        assert isinstance(result.data, list)
        assert len(result.data) == 2
        assert result.data[0]["name"] == "Item 1"

    async def test_json_generation_empty_markdown(
        self, mocker: Any, json_schema: dict[str, Any]
    ) -> None:
        """Test JSON generation with empty markdown."""
        mock_http = mocker.AsyncMock()
        mock_http.post.return_value = {}

        generate = Generate(mock_http)
        result = await generate.json(
            url="https://example.com", schema=json_schema, instructions="Extract data"
        )

        assert isinstance(result, JsonResponse)
        # Empty markdown should still call API
        mock_http.post.assert_called_once()
