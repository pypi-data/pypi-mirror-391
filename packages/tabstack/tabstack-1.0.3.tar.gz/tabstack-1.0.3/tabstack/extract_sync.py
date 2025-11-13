"""Synchronous Extract operator for TABStack AI SDK."""

from typing import Any, Dict, Optional

from ._http_client_sync import HTTPClientSync
from ._shared import build_json_extract_request, build_markdown_request, build_schema_request
from .types import JsonResponse, MarkdownResponse, SchemaResponse
from .utils import validate_json_schema


class ExtractSync:
    """Synchronous Extract operator for converting and extracting web content.

    The Extract operator converts web content into structured formats without
    AI transformation. Use Extract when you want to:
    - Convert HTML to clean Markdown
    - Discover data structure automatically with schema generation
    - Extract structured data that exists in the page (no summarization/transformation)

    For AI-powered transformation of content, use the Generate operator instead.
    """

    def __init__(self, http_client: HTTPClientSync) -> None:
        """Initialize Extract operator.

        Args:
            http_client: Sync HTTP client for making API requests
        """
        self._http = http_client

    def markdown(self, url: str, metadata: bool = False, nocache: bool = False) -> MarkdownResponse:
        """Convert URL content to Markdown format.

        Extracts Open Graph and HTML meta tags from the page. When metadata=True,
        metadata is returned as a separate field (result.metadata). When metadata=False,
        metadata is embedded as YAML frontmatter at the start of the markdown content.

        Args:
            url: URL to fetch and convert to markdown
            metadata: If True, metadata is returned as a separate field. If False,
                     metadata is embedded as YAML frontmatter in the content string.
            nocache: Bypass cache and force fresh data retrieval

        Returns:
            MarkdownResponse with converted content. The metadata field is only
            populated when metadata=True.

        Raises:
            BadRequestError: If URL is missing or invalid
            UnauthorizedError: If API key is invalid
            InvalidURLError: If URL is invalid or inaccessible
            ServerError: If server encounters an error

        Example:
            >>> with TABStackSync(api_key="your-key") as tabs:
            ...     result = tabs.extract.markdown(
            ...         url="https://example.com/blog/article",
            ...         metadata=True
            ...     )
            ...     print(result.content)
            ...     print(result.metadata.title)
        """
        request_data = build_markdown_request(url, metadata, nocache)
        response = self._http.post("v1/extract/markdown", request_data)
        return MarkdownResponse.from_dict(response)

    def schema(
        self, url: str, instructions: Optional[str] = None, nocache: bool = False
    ) -> SchemaResponse:
        """Generate JSON Schema from URL content using AI.

        Analyzes the structure of content on a page and generates a JSON Schema
        that describes it. The generated schema can then be used with extract.json()
        to extract data from similar pages.

        Instructions help guide the AI to focus on specific data. Keep instructions
        under 1000 characters for best results.

        Args:
            url: URL to analyze and extract schema from
            instructions: Optional guidance for schema generation (max 1000 characters).
                         Example: "extract top stories with title, points, and author"
            nocache: Bypass cache and force fresh data retrieval

        Returns:
            SchemaResponse containing the generated JSON Schema dict

        Raises:
            BadRequestError: If URL is missing or instructions exceed 1000 characters
            UnauthorizedError: If API key is invalid
            InvalidURLError: If URL is invalid or inaccessible
            ServerError: If server encounters an error

        Example:
            >>> with TABStackSync(api_key="your-key") as tabs:
            ...     result = tabs.extract.schema(
            ...         url="https://news.ycombinator.com",
            ...         instructions="extract top stories with title, points, and author"
            ...     )
            ...     data = tabs.extract.json(
            ...         url="https://news.ycombinator.com",
            ...         schema=result.schema
            ...     )
        """
        request_data = build_schema_request(url, instructions, nocache)
        response = self._http.post("v1/extract/json/schema", request_data)
        return SchemaResponse.from_dict(response)

    def json(self, url: str, schema: Dict[str, Any], nocache: bool = False) -> JsonResponse:
        """Extract structured JSON data from URL content.

        Extracts data that exists on the page according to the provided JSON Schema.
        This method performs direct extraction without AI transformation.

        Use extract.json() when you want the data as-is from the page.
        Use generate.json() when you need AI to transform, summarize, or
        enhance the data (e.g., categorization, summarization, translation).

        Args:
            url: URL to fetch and extract data from
            schema: JSON Schema dict defining the structure of data to extract
            nocache: Bypass cache and force fresh data retrieval

        Returns:
            JsonResponse containing the extracted data matching the schema

        Raises:
            ValueError: If schema is invalid (basic validation only)
            BadRequestError: If URL or schema is missing or malformed
            UnauthorizedError: If API key is invalid
            InvalidURLError: If URL is invalid or inaccessible
            ServerError: If server encounters an error

        Example:
            >>> with TABStackSync(api_key="your-key") as tabs:
            ...     schema = {
            ...         "type": "object",
            ...         "properties": {
            ...             "stories": {
            ...                 "type": "array",
            ...                 "items": {
            ...                     "type": "object",
            ...                     "properties": {
            ...                         "title": {"type": "string"},
            ...                         "points": {"type": "number"},
            ...                         "author": {"type": "string"}
            ...                     }
            ...                 }
            ...             }
            ...         }
            ...     }
            ...     result = tabs.extract.json(
            ...         url="https://news.ycombinator.com",
            ...         schema=schema
            ...     )
            ...     print(result.data["stories"])
        """
        validate_json_schema(schema)
        request_data = build_json_extract_request(url, schema, nocache)
        # Note: API expects json_schema field
        request_data["json_schema"] = request_data.pop("schema")
        response = self._http.post("v1/extract/json", request_data)
        return JsonResponse.from_dict(response)
