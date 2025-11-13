"""Main client for TABStack AI SDK."""

from typing import Any

from ._http_client import HTTPClient
from .automate import Automate
from .extract import Extract
from .generate import Generate


class TABStack:
    """TABStack AI async client for web content extraction, generation, and automation.

    This is the main entry point for the TABStack AI SDK. Initialize it with your
    API key to access the extract, generate, and automate operators. All operations
    are async and support connection pooling for efficient resource usage.

    Example:
        >>> import asyncio
        >>> import os
        >>> from tabstack import TABStack
        >>>
        >>> async def main():
        ...     async with TABStack(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
        ...         result = await tabs.extract.markdown(url="https://example.com")
        ...         print(result.content)
        >>>
        >>> asyncio.run(main())
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
        """Initialize TABStack async client with connection pooling.

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
            >>> async with TABStack(
            ...     api_key="your-api-key-here",
            ...     max_connections=50,
            ...     max_keepalive_connections=10
            ... ) as tabs:
            ...     result = await tabs.extract.markdown(url="https://example.com")
        """
        if not api_key:
            raise ValueError("api_key is required")

        # HTTPClient uses httpx which is thread-safe for async operations
        self._http_client = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            timeout=timeout,
        )

        # Initialize operators (each shares the same HTTP client for connection reuse)
        self.extract = Extract(self._http_client)
        self.generate = Generate(self._http_client)
        self.automate = Automate(self._http_client)

    async def close(self) -> None:
        """Close the HTTP client and release all connections.

        Example:
            >>> tabs = TABStack(api_key="your-key")
            >>> try:
            ...     result = await tabs.extract.markdown(url="https://example.com")
            ... finally:
            ...     await tabs.close()
        """
        await self._http_client.close()

    async def __aenter__(self) -> "TABStack":
        """Async context manager entry.

        Example:
            >>> async with TABStack(api_key="your-key") as tabs:
            ...     result = await tabs.extract.markdown(url="https://example.com")
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"TABStack(base_url='{self._http_client.base_url}')"
