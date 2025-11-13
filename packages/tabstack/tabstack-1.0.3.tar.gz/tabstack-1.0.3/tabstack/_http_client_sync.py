"""Synchronous HTTP client for TABStack AI SDK."""

from typing import Any, Dict, Iterator, Optional

import httpx

from ._shared import get_http_headers, handle_error_response


class HTTPClientSync:
    """Synchronous HTTP client for TABStack API requests.

    Handles HTTP communication with the TABStack API, including:
    - Connection pooling and keepalive for performance
    - Request authentication with API keys
    - Error response parsing and exception mapping
    - Server-Sent Events (SSE) streaming for automate endpoint

    This is an internal class. Users should use the TABStackSync client instead.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tabstack.ai/",
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        timeout: float = 60.0,
    ) -> None:
        """Initialize sync HTTP client with connection pooling.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            max_connections: Maximum number of connections in the pool
            max_keepalive_connections: Maximum number of idle connections to keep alive
            keepalive_expiry: Time in seconds to keep idle connections alive
            timeout: Default timeout for requests in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

        # Configure connection pooling limits
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
        )

        # Create sync client with connection pooling
        self._client: Optional[httpx.Client] = None
        self._limits = limits
        self._timeout = timeout

    def _get_client(self) -> httpx.Client:
        """Get or create the sync HTTP client.

        Returns:
            Configured sync HTTP client
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                limits=self._limits,
                timeout=self._timeout,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client and release connections."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "HTTPClientSync":
        """Sync context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sync context manager exit."""
        self.close()

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a sync POST request.

        Args:
            path: API endpoint path
            data: Request body data

        Returns:
            Response data as dictionary

        Raises:
            TABStackError: On API errors
        """
        client = self._get_client()
        headers = get_http_headers(self.api_key)

        # Make the request
        response = client.post(
            path,
            json=data,
            headers=headers,
        )

        # Handle errors
        if response.status_code >= 400:
            handle_error_response(response.status_code, response.content)

        # Parse successful response
        if response.content:
            return response.json()
        else:
            return {}

    def post_stream(self, path: str, data: Optional[Dict[str, Any]] = None) -> Iterator[str]:
        """Make a sync POST request with streaming response (Server-Sent Events).

        Args:
            path: API endpoint path
            data: Request body data

        Yields:
            Lines from the streaming response

        Raises:
            TABStackError: On API errors
        """
        client = self._get_client()
        headers = get_http_headers(self.api_key)
        headers["Accept"] = "text/event-stream"

        # Make streaming request
        with client.stream("POST", path, json=data, headers=headers) as response:
            # Check for errors first
            if response.status_code >= 400:
                error_body = b"".join(response.iter_bytes())
                handle_error_response(response.status_code, error_body)

            # SSE streams are line-based; buffer bytes until we have complete lines
            buffer = b""
            for chunk in response.iter_bytes(chunk_size=1024):
                buffer += chunk
                # Process complete lines
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    line = line_bytes.decode("utf-8", errors="replace").rstrip("\r")
                    if line:  # Skip empty lines
                        yield line

            # Process any remaining data
            if buffer:
                line = buffer.decode("utf-8", errors="replace").rstrip("\r\n")
                if line:
                    yield line
