"""TABStack AI Python SDK.

This SDK provides a Python interface to the TABStack AI API for web content
extraction, AI-powered content generation, and browser automation.

The SDK provides three main operators:

- **Extract**: Convert web content to markdown or extract structured data
- **Generate**: Transform and enhance web data using AI
- **Automate**: Execute complex browser automation tasks with natural language

The SDK supports both async (TABStack) and sync (TABStackSync) clients:

Async Example:
    >>> import asyncio
    >>> import os
    >>> from tabstack import TABStack
    >>>
    >>> async def main():
    ...     async with TABStack(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
    ...         # Extract markdown from a URL
    ...         result = await tabs.extract.markdown(url="https://example.com")
    ...         print(result.content)
    >>>
    >>> asyncio.run(main())

Sync Example:
    >>> import os
    >>> from tabstack import TABStackSync
    >>>
    >>> with TABStackSync(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
    ...     # Extract markdown from a URL (no async/await needed)
    ...     result = tabs.extract.markdown(url="https://example.com")
    ...     print(result.content)

Workflow: Schema Generation → Data Extraction
    >>> async def extract_with_generated_schema():
    ...     async with TABStack(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
    ...         # First, generate a schema from the content
    ...         schema_result = await tabs.extract.schema(
    ...             url="https://news.ycombinator.com",
    ...             instructions="extract top stories with title, points, and author"
    ...         )
    ...
    ...         # Then use the generated schema to extract structured data
    ...         data = await tabs.extract.json(
    ...             url="https://news.ycombinator.com",
    ...             schema=schema_result.schema
    ...         )
    ...         print(data.data)

Workflow: Extract → Transform
    >>> async def extract_and_transform():
    ...     async with TABStack(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
    ...         # Define schema for transformed output
    ...         summary_schema = {
    ...             "type": "object",
    ...             "properties": {
    ...                 "summaries": {
    ...                     "type": "array",
    ...                     "items": {
    ...                         "type": "object",
    ...                         "properties": {
    ...                             "title": {"type": "string"},
    ...                             "category": {"type": "string"},
    ...                             "summary": {"type": "string"}
    ...                         }
    ...                     }
    ...                 }
    ...             }
    ...         }
    ...
    ...         # Generate transformed content with AI
    ...         result = await tabs.generate.json(
    ...             url="https://news.ycombinator.com",
    ...             schema=summary_schema,
    ...             instructions="Categorize each story and write a brief summary"
    ...         )
    ...         print(result.data)

Workflow: Browser Automation
    >>> async def automate_task():
    ...     async with TABStack(api_key=os.getenv('TABSTACK_API_KEY')) as tabs:
    ...         # Execute complex web automation tasks
    ...         async for event in tabs.automate.execute(
    ...             task="Extract the top 5 trending repositories",
    ...             url="https://github.com/trending",
    ...             guardrails="browse and extract only, do not click stars or forks"
    ...         ):
    ...             if event.type == "task:completed":
    ...                 print(f"Task complete: {event.data.get('finalAnswer')}")
"""

from .automate import Automate
from .automate_sync import AutomateSync
from .client import TABStack
from .client_sync import TABStackSync
from .exceptions import (
    APIError,
    BadRequestError,
    InvalidURLError,
    ServerError,
    ServiceUnavailableError,
    TABStackError,
    UnauthorizedError,
)
from .extract import Extract
from .extract_sync import ExtractSync
from .generate import Generate
from .generate_sync import GenerateSync
from .types import (
    AutomateEvent,
    EventData,
    JsonResponse,
    MarkdownResponse,
    Metadata,
    SchemaResponse,
)

__version__ = "1.0.3"
__all__ = [
    # Main clients
    "TABStack",  # Async client
    "TABStackSync",  # Sync client
    # Async operators
    "Extract",
    "Generate",
    "Automate",
    # Sync operators
    "ExtractSync",
    "GenerateSync",
    "AutomateSync",
    # Response types
    "MarkdownResponse",
    "SchemaResponse",
    "JsonResponse",
    "Metadata",
    "AutomateEvent",
    "EventData",
    # Exceptions
    "TABStackError",
    "BadRequestError",
    "UnauthorizedError",
    "InvalidURLError",
    "ServerError",
    "ServiceUnavailableError",
    "APIError",
]
