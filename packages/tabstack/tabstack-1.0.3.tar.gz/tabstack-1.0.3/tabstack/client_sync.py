"""Synchronous main client for TABStack AI SDK."""

from typing import Any

from ._http_client_sync import HTTPClientSync
from .automate_sync import AutomateSync
from .extract_sync import ExtractSync
from .generate_sync import GenerateSync


class TABStackSync:
    """TABStack AI synchronous client for web content extraction, generation, and automation.

    This is the synchronous version of the TABStack AI SDK. Use this when you don't need
    async/await support. For async support, use the `TABStack` class instead.

    All operations are synchronous and support connection pooling for efficient resource usage.

    Example:
        >>> import os
        >>> from tabstack import TABStackSync
        >>>
        >>> with TABStackSync(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
        ...     result = tabs.extract.markdown(url="https://example.com")
        ...     print(result.content)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tabstack.ai/",
        max_connections: int = 100,  # Allows high concurrency for batch processing
        max_keepalive_connections: int = 20,  # Balance between reuse and memory
        keepalive_expiry: float = 30.0,  # API's connection timeout is ~30s
        timeout: float = 60.0,  # Web scraping/AI operations can take time
    ) -> None:
        """Initialize TABStack synchronous client with connection pooling.

        Args:
            api_key: Your TABStack API key for authentication
            base_url: Base URL for the TABStack API (default: https://api.tabstack.ai/)
            max_connections: Maximum number of connections in the pool (default: 100)
            max_keepalive_connections: Maximum idle connections to keep alive (default: 20)
            keepalive_expiry: Time in seconds to keep idle connections alive (default: 30.0)
            timeout: Default timeout for requests in seconds (default: 60.0)

        Raises:
            ValueError: If api_key is empty or None

        Example:
            >>> with TABStackSync(
            ...     api_key="your-api-key-here",
            ...     max_connections=50,
            ...     max_keepalive_connections=10
            ... ) as tabs:
            ...     result = tabs.extract.markdown(url="https://example.com")
        """
        if not api_key:
            raise ValueError("api_key is required")

        # HTTPClientSync uses httpx.Client which is thread-safe
        self._http_client = HTTPClientSync(
            api_key=api_key,
            base_url=base_url,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            timeout=timeout,
        )

        # Initialize operators (each shares the same HTTP client for connection reuse)
        self.extract = ExtractSync(self._http_client)
        self.generate = GenerateSync(self._http_client)
        self.automate = AutomateSync(self._http_client)

    def close(self) -> None:
        """Close the HTTP client and release all connections.

        Example:
            >>> tabs = TABStackSync(api_key="your-key")
            >>> try:
            ...     result = tabs.extract.markdown(url="https://example.com")
            ... finally:
            ...     tabs.close()
        """
        self._http_client.close()

    def __enter__(self) -> "TABStackSync":
        """Sync context manager entry.

        Example:
            >>> with TABStackSync(api_key="your-key") as tabs:
            ...     result = tabs.extract.markdown(url="https://example.com")
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sync context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"TABStackSync(base_url='{self._http_client.base_url}')"
