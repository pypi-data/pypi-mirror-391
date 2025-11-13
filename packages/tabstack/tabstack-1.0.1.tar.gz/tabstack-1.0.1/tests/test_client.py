"""Tests for main TABStack client."""

from typing import Any

import pytest

from tabstack import TABStack
from tabstack.automate import Automate
from tabstack.extract import Extract
from tabstack.generate import Generate


class TestTABStackInitialization:
    """Tests for TABStack client initialization."""

    def test_initialization_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = TABStack(api_key="test_key_123")
        assert client._http_client.api_key == "test_key_123"

    def test_initialization_with_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = TABStack(api_key="test_key", base_url="https://custom.api.com")
        assert client._http_client.base_url == "https://custom.api.com"

    def test_initialization_missing_api_key(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(TypeError):
            TABStack()  # type: ignore

    def test_operators_are_initialized(self) -> None:
        """Test all operators are properly initialized."""
        client = TABStack(api_key="test_key")
        assert isinstance(client.extract, Extract)
        assert isinstance(client.generate, Generate)
        assert isinstance(client.automate, Automate)

    def test_operators_share_http_client(self) -> None:
        """Test all operators share the same HTTP client."""
        client = TABStack(api_key="test_key")
        # All operators should use the same HTTP client instance
        assert client.extract._http is client._http_client
        assert client.generate._http is client._http_client
        assert client.automate._http is client._http_client


class TestTABStackContextManager:
    """Tests for async context manager support."""

    async def test_context_manager_usage(self) -> None:
        """Test using TABStack as async context manager."""
        async with TABStack(api_key="test_key") as client:
            assert isinstance(client, TABStack)
            assert isinstance(client.extract, Extract)

        # Client should be closed after context

    async def test_context_manager_closes_http_client(self, mocker: Any) -> None:
        """Test context manager closes HTTP client."""
        client = TABStack(api_key="test_key")

        # Mock the close method
        mock_close = mocker.AsyncMock()
        client._http_client.close = mock_close

        async with client:
            pass

        mock_close.assert_called_once()

    async def test_manual_close(self, mocker: Any) -> None:
        """Test manually closing the client."""
        client = TABStack(api_key="test_key")

        mock_close = mocker.AsyncMock()
        client._http_client.close = mock_close

        await client.close()

        mock_close.assert_called_once()


class TestTABStackIntegration:
    """Integration tests using TABStack client."""

    async def test_extract_markdown_integration(self, mocker: Any) -> None:
        """Test complete flow for extracting markdown."""
        # Mock HTTP response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"url": "https://example.com", "content": "# Test"}'
        mock_response.json.return_value = {
            "url": "https://example.com",
            "content": "# Test",
        }

        mock_httpx_client = mocker.AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        client = TABStack(api_key="test_key")
        client._http_client._client = mock_httpx_client

        result = await client.extract.markdown(url="https://example.com")

        assert result.url == "https://example.com"
        assert result.content == "# Test"
        mock_httpx_client.post.assert_called_once()

    async def test_generate_json_integration(self, mocker: Any) -> None:
        """Test complete flow for generating JSON."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"summary": "Test summary"}'
        mock_response.json.return_value = {"summary": "Test summary"}

        mock_httpx_client = mocker.AsyncMock()
        mock_httpx_client.post.return_value = mock_response

        client = TABStack(api_key="test_key")
        client._http_client._client = mock_httpx_client

        schema = {"type": "object", "properties": {"summary": {"type": "string"}}}
        result = await client.generate.json(
            url="https://example.com/article", schema=schema, instructions="Summarize"
        )

        assert result.data["summary"] == "Test summary"
        mock_httpx_client.post.assert_called_once()

    async def test_automate_streaming_integration(self, mocker: Any) -> None:
        """Test complete flow for automate streaming."""
        mock_response = mocker.AsyncMock()
        mock_response.status_code = 200

        async def mock_aiter_bytes(chunk_size: int):  # type: ignore
            yield b'event: start\ndata: {"message": "Starting"}\n\n'
            yield b'event: task:completed\ndata: {"finalAnswer": "Done"}\n\n'

        mock_response.aiter_bytes = mock_aiter_bytes

        # Create proper async context manager mock
        mock_stream_cm = mocker.MagicMock()
        mock_stream_cm.__aenter__ = mocker.AsyncMock(return_value=mock_response)
        mock_stream_cm.__aexit__ = mocker.AsyncMock(return_value=None)

        mock_httpx_client = mocker.AsyncMock()
        mock_httpx_client.stream = mocker.MagicMock(return_value=mock_stream_cm)

        client = TABStack(api_key="test_key")
        client._http_client._client = mock_httpx_client

        events = []
        async for event in client.automate.execute(task="Test", url="https://example.com"):
            events.append(event)

        assert len(events) >= 1
        mock_httpx_client.stream.assert_called_once()
