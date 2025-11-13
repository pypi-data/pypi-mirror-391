"""Synchronous Generate operator for TABStack AI SDK."""

from typing import Any, Dict

from ._http_client_sync import HTTPClientSync
from ._shared import build_json_generate_request
from .types import JsonResponse
from .utils import validate_json_schema


class GenerateSync:
    """Synchronous Generate operator for AI-powered content transformation.

    The Generate operator uses AI to transform, enhance, and create new content
    from web pages based on custom instructions. Unlike Extract (which retrieves
    data as-is), Generate can:
    - Summarize and condense content
    - Categorize and classify information
    - Translate or rewrite content
    - Create new insights from existing data
    - Restructure data into different formats

    Use Generate when you need AI to interpret and transform content, not just extract it.
    """

    def __init__(self, http_client: HTTPClientSync) -> None:
        """Initialize Generate operator.

        Args:
            http_client: Sync HTTP client for making API requests
        """
        self._http = http_client

    def json(
        self, url: str, schema: Dict[str, Any], instructions: str, nocache: bool = False
    ) -> JsonResponse:
        """Generate AI-transformed JSON from URL content.

        Fetches content from a URL and uses AI to transform it according to your
        instructions. The AI can summarize, categorize, translate, or create new
        insights from the original content.

        The instructions parameter tells the AI how to transform the data. Be specific
        about what transformations you want (e.g., "summarize in one sentence",
        "categorize as tech/business/science", "translate to Spanish").

        Args:
            url: URL to fetch content from
            schema: JSON Schema dict defining the structure of the transformed output
            instructions: Natural language instructions for how to transform the data.
                         Be specific about the transformation you want.
            nocache: Bypass cache and force fresh data retrieval

        Returns:
            JsonResponse containing the AI-transformed data matching the schema

        Raises:
            ValueError: If schema is invalid (basic validation only)
            BadRequestError: If URL, schema, or instructions are missing or malformed
            UnauthorizedError: If API key is invalid
            InvalidURLError: If URL is invalid or inaccessible
            ServerError: If server encounters an error

        Example:
            >>> with TABStackSync(api_key="your-key") as tabs:
            ...     schema = {
            ...         "type": "object",
            ...         "properties": {
            ...             "summaries": {
            ...                 "type": "array",
            ...                 "items": {
            ...                     "type": "object",
            ...                     "properties": {
            ...                         "title": {"type": "string"},
            ...                         "category": {"type": "string"},
            ...                         "summary": {"type": "string"}
            ...                     }
            ...                 }
            ...             }
            ...         }
            ...     }
            ...     result = tabs.generate.json(
            ...         url="https://news.ycombinator.com",
            ...         schema=schema,
            ...         instructions="Categorize each story and write a one-sentence summary"
            ...     )
            ...     print(result.data["summaries"])
        """
        validate_json_schema(schema)
        request_data = build_json_generate_request(url, schema, instructions, nocache)
        response = self._http.post("v1/generate/json", request_data)
        return JsonResponse.from_dict(response)
