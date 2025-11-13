"""Tests for HTTPClientSync class."""

import json
from typing import Any

import httpx
import pytest

from tabstack._http_client_sync import HTTPClientSync
from tabstack._shared import get_http_headers, handle_error_response
from tabstack.exceptions import (
    APIError,
    BadRequestError,
    InvalidURLError,
    ServerError,
    ServiceUnavailableError,
    UnauthorizedError,
)


class TestHTTPClientSyncInitialization:
    """Tests for HTTPClientSync initialization."""

    def test_initialization_with_defaults(self) -> None:
        """Test HTTPClientSync initialization with default values."""
        client = HTTPClientSync(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.tabstack.ai"

    def test_initialization_with_custom_values(self) -> None:
        """Test HTTPClientSync initialization with custom values."""
        client = HTTPClientSync(
            api_key="test_key",
            base_url="https://custom.api.com/",
            max_connections=50,
            timeout=120.0,
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.com"
        assert client._timeout == 120.0

    def test_base_url_trailing_slash_removed(self) -> None:
        """Test trailing slash is removed from base_url."""
        client = HTTPClientSync(api_key="test_key", base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"


class TestHTTPClientSyncHeaders:
    """Tests for HTTP headers generation."""

    def test_get_headers_default(self) -> None:
        """Test default headers."""
        headers = get_http_headers("test_key_123")
        assert headers["Authorization"] == "Bearer test_key_123"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "tabstack-ai-python" in headers["User-Agent"]

    def test_get_headers_custom_content_type(self) -> None:
        """Test headers with custom content type."""
        headers = get_http_headers("test_key", content_type="text/plain")
        assert headers["Content-Type"] == "text/plain"


class TestHTTPClientSyncErrorHandling:
    """Tests for error response handling."""

    def test_handle_error_400_bad_request(self) -> None:
        """Test 400 error raises BadRequestError."""
        error_body = json.dumps({"error": "Invalid schema"}).encode()
        with pytest.raises(BadRequestError, match="Invalid schema"):
            handle_error_response(400, error_body)

    def test_handle_error_401_unauthorized(self) -> None:
        """Test 401 error raises UnauthorizedError."""
        error_body = json.dumps({"error": "Invalid API key"}).encode()
        with pytest.raises(UnauthorizedError, match="Invalid API key"):
            handle_error_response(401, error_body)

    def test_handle_error_422_invalid_url(self) -> None:
        """Test 422 error raises InvalidURLError."""
        error_body = json.dumps({"error": "URL not found"}).encode()
        with pytest.raises(InvalidURLError, match="URL not found"):
            handle_error_response(422, error_body)

    def test_handle_error_500_server_error(self) -> None:
        """Test 500 error raises ServerError."""
        error_body = json.dumps({"error": "Internal error"}).encode()
        with pytest.raises(ServerError, match="Internal error"):
            handle_error_response(500, error_body)

    def test_handle_error_503_service_unavailable(self) -> None:
        """Test 503 error raises ServiceUnavailableError."""
        error_body = json.dumps({"error": "Service down"}).encode()
        with pytest.raises(ServiceUnavailableError, match="Service down"):
            handle_error_response(503, error_body)

    def test_handle_error_generic_status(self) -> None:
        """Test other status codes raise generic APIError."""
        error_body = json.dumps({"error": "Rate limited"}).encode()
        with pytest.raises(APIError, match="Rate limited") as exc_info:
            handle_error_response(429, error_body)
        assert exc_info.value.status_code == 429

    def test_handle_error_non_json_response(self) -> None:
        """Test error handling with non-JSON response."""
        error_body = b"Plain text error"
        with pytest.raises(BadRequestError, match="Plain text error"):
            handle_error_response(400, error_body)

    def test_handle_error_empty_response(self) -> None:
        """Test error handling with empty response."""
        with pytest.raises(BadRequestError, match="Unknown error"):
            handle_error_response(400, b"")


class TestHTTPClientSyncPost:
    """Tests for POST requests."""

    def test_post_success(self, mocker: Any) -> None:
        """Test successful POST request."""
        client = HTTPClientSync(api_key="test_key")

        # Mock the httpx response
        mock_response = mocker.Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{"result": "success"}'
        mock_response.json.return_value = {"result": "success"}

        # Mock the httpx client
        mock_httpx_client = mocker.Mock(spec=httpx.Client)
        mock_httpx_client.post.return_value = mock_response

        # Inject mock client
        client._client = mock_httpx_client

        # Make request
        result = client.post("/test", data={"key": "value"})

        assert result == {"result": "success"}
        mock_httpx_client.post.assert_called_once()

    def test_post_error_response(self, mocker: Any) -> None:
        """Test POST request with error response."""
        client = HTTPClientSync(api_key="test_key")

        # Mock error response
        mock_response = mocker.Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.content = b'{"error": "Bad request"}'

        mock_httpx_client = mocker.Mock(spec=httpx.Client)
        mock_httpx_client.post.return_value = mock_response

        client._client = mock_httpx_client

        with pytest.raises(BadRequestError):
            client.post("/test", data={"key": "value"})

    def test_post_empty_response(self, mocker: Any) -> None:
        """Test POST request with empty response body."""
        client = HTTPClientSync(api_key="test_key")

        mock_response = mocker.Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b""

        mock_httpx_client = mocker.Mock(spec=httpx.Client)
        mock_httpx_client.post.return_value = mock_response

        client._client = mock_httpx_client

        result = client.post("/test")
        assert result == {}


class TestHTTPClientSyncStreaming:
    """Tests for streaming POST requests."""

    def test_post_stream_success(self, mocker: Any) -> None:
        """Test successful streaming POST request."""
        client = HTTPClientSync(api_key="test_key")

        # Mock streaming response
        mock_response = mocker.Mock()
        mock_response.status_code = 200

        # Simulate SSE data chunks
        def mock_iter_bytes(chunk_size: int):  # type: ignore
            yield b"event: start\n"
            yield b'data: {"message": "Starting"}\n\n'
            yield b"event: complete\n"
            yield b'data: {"message": "Done"}\n\n'

        mock_response.iter_bytes = mock_iter_bytes

        # Create proper context manager mock
        mock_stream_cm = mocker.MagicMock()
        mock_stream_cm.__enter__ = mocker.Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = mocker.Mock(return_value=None)

        mock_httpx_client = mocker.Mock(spec=httpx.Client)
        mock_httpx_client.stream = mocker.MagicMock(return_value=mock_stream_cm)

        client._client = mock_httpx_client

        # Collect streamed lines
        lines = []
        for line in client.post_stream("/automate", data={"task": "test"}):
            lines.append(line)

        assert len(lines) > 0
        assert any("start" in line for line in lines)

    def test_post_stream_error_response(self, mocker: Any) -> None:
        """Test streaming POST request with error."""
        client = HTTPClientSync(api_key="test_key")

        mock_response = mocker.Mock()
        mock_response.status_code = 503
        mock_response.iter_bytes.return_value = iter([b'{"error": "Service unavailable"}'])

        # Create proper context manager mock
        mock_stream_cm = mocker.MagicMock()
        mock_stream_cm.__enter__ = mocker.Mock(return_value=mock_response)
        mock_stream_cm.__exit__ = mocker.Mock(return_value=None)

        mock_httpx_client = mocker.Mock(spec=httpx.Client)
        mock_httpx_client.stream = mocker.MagicMock(return_value=mock_stream_cm)

        client._client = mock_httpx_client

        with pytest.raises(ServiceUnavailableError):
            for _ in client.post_stream("/automate", data={"task": "test"}):
                pass


class TestHTTPClientSyncContextManager:
    """Tests for context manager support."""

    def test_context_manager_close(self, mocker: Any) -> None:
        """Test context manager properly closes client."""
        with HTTPClientSync(api_key="test_key") as client:
            # Create a mock client
            mock_httpx_client = mocker.Mock(spec=httpx.Client)
            client._client = mock_httpx_client

        # Client should be closed
        mock_httpx_client.close.assert_called_once()

    def test_close_when_no_client(self) -> None:
        """Test close when httpx client was never created."""
        client = HTTPClientSync(api_key="test_key")
        client.close()  # Should not raise
        assert client._client is None
