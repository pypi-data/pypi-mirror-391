# TABStack AI Python SDK

[![PyPI version](https://badge.fury.io/py/tabstack.svg)](https://badge.fury.io/py/tabstack)
[![Python Versions](https://img.shields.io/pypi/pyversions/tabstack.svg)](https://pypi.org/project/tabstack/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/tabstack/tabs-python/workflows/Tests/badge.svg)](https://github.com/tabstack/tabs-python/actions)
[![codecov](https://codecov.io/gh/tabstack/tabs-python/branch/main/graph/badge.svg)](https://codecov.io/gh/tabstack/tabs-python)

Python SDK for [TABStack AI](https://tabstack.ai) - Extract, Generate, and Automate web content using AI.

## Features

- **🔍 Extract**: Convert web content to markdown or structured JSON
- **✨ Generate**: Transform and enhance web data with AI
- **🤖 Automate**: Execute complex web automation tasks using natural language
- **⚡ Async/Await**: Modern async Python API for efficient concurrent operations
- **🔄 Connection Pooling**: Configurable HTTP connection pooling for optimal performance
- **📘 Fully Typed**: Complete type hints for better IDE support and type safety
- **🔒 JSON Schema**: Use standard JSON Schema for structured data extraction
- **🛡️ Error Handling**: Comprehensive custom exceptions for all API errors

## Installation

### Using uv (recommended)
```bash
uv pip install tabstack
```

Or add to your project:
```bash
uv add tabstack
```

### Using pip
```bash
pip install tabstack
```

### Using poetry
```bash
poetry add tabstack
```

### Using pipenv
```bash
pipenv install tabstack
```

### From Source
```bash
git clone https://github.com/tabstack/tabs-python.git
cd tabs-python
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
import os
from tabstack import TABStack

async def main():
    # Initialize the client with connection pooling
    async with TABStack(
        api_key=os.getenv('TABSTACK_API_KEY'),
        max_connections=100,
        max_keepalive_connections=20
    ) as tabs:
        # Extract markdown from a URL
        result = await tabs.extract.markdown(
            url="https://news.ycombinator.com",
            metadata=True
        )
        print(result.content)
        print(result.metadata.title)

        # Extract structured JSON data
        schema = {
            "type": "object",
            "properties": {
                "stories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "points": {"type": "number"},
                            "author": {"type": "string"}
                        }
                    }
                }
            }
        }

        data = await tabs.extract.json(
            url="https://news.ycombinator.com",
            schema=schema
        )

        # Generate transformed content with AI
        summary_schema = {
            "type": "object",
            "properties": {
                "summaries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "category": {"type": "string"},
                            "summary": {"type": "string"}
                        }
                    }
                }
            }
        }

        # First extract the markdown
        markdown_result = await tabs.extract.markdown(url="https://news.ycombinator.com")

        # Then transform it with AI
        summaries = await tabs.generate.json(
            markdown=markdown_result.content,
            schema=summary_schema,
            instructions="For each story, categorize it and write a one-sentence summary"
        )

        # Automate web tasks (streaming)
        async for event in tabs.automate.execute(
            task="Find the top 3 trending repositories and extract their details",
            url="https://github.com/trending"
        ):
            if event.type == "task:completed":
                print(f"Result: {event.data.final_answer}")
            elif event.type == "agent:extracted":
                print(f"Extracted: {event.data.extracted_data}")

# Run the async function
asyncio.run(main())
```

## API Reference

All methods are async and should be awaited. The client supports async context manager for automatic connection cleanup.

### Client Initialization

```python
from tabstack import TABStack

async with TABStack(
    api_key="your-api-key",
    base_url="https://api.tabstack.ai/",  # optional
    max_connections=100,  # optional
    max_keepalive_connections=20,  # optional
    keepalive_expiry=30.0,  # optional, in seconds
    timeout=60.0  # optional, in seconds
) as tabs:
    # Your code here
    pass
```

**Parameters:**
- `api_key` (str, required): Your TABStack API key
- `base_url` (str, optional): API base URL. Default: `https://api.tabstack.ai/`
- `max_connections` (int, optional): Maximum concurrent connections. Default: `100`
- `max_keepalive_connections` (int, optional): Maximum idle connections to keep alive. Default: `20`
- `keepalive_expiry` (float, optional): Seconds to keep idle connections alive. Default: `30.0`
- `timeout` (float, optional): Request timeout in seconds. Default: `60.0`

### Extract Operator

The Extract operator converts web content into structured formats without AI transformation.

#### `extract.markdown(url, metadata=False, nocache=False)`

Convert URL content to Markdown format.

**Parameters:**
- `url` (str): URL to convert
- `metadata` (bool): If True, return metadata as separate field. If False, embed as YAML frontmatter. Default: `False`
- `nocache` (bool): Bypass cache and force fresh retrieval. Default: `False`

**Returns:** `MarkdownResponse` with `url`, `content`, and optional `metadata` fields

**Example:**
```python
result = await tabs.extract.markdown(
    url="https://example.com",
    metadata=True
)
print(result.content)
print(result.metadata.title)
```

#### `extract.schema(url, instructions, nocache=False)`

Generate a JSON Schema by analyzing the structure of a webpage.

**Parameters:**
- `url` (str): URL to analyze
- `instructions` (str): Instructions for what data to extract (max 1000 characters)
- `nocache` (bool): Bypass cache. Default: `False`

**Returns:** `SchemaResponse` with generated `schema` dict

**Example:**
```python
result = await tabs.extract.schema(
    url="https://example.com/products",
    instructions="Extract product listings with name, price, and availability"
)
# Use the schema for extraction
data = await tabs.extract.json(url="https://example.com/products", schema=result.schema)
```

#### `extract.json(url, schema, nocache=False)`

Extract structured JSON data from a URL using a schema.

**Parameters:**
- `url` (str): URL to extract from
- `schema` (dict): JSON Schema defining the structure
- `nocache` (bool): Bypass cache. Default: `False`

**Returns:** `JsonResponse` with extracted `data`

**Example:**
```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"}
    }
}
result = await tabs.extract.json(url="https://example.com", schema=schema)
print(result.data)
```

### Generate Operator

The Generate operator uses AI to transform and enhance web content.

#### `generate.json(markdown, instructions, schema)`

Transform markdown content into structured JSON using AI.

**Parameters:**
- `markdown` (str): Markdown content to transform
- `instructions` (str): AI instructions for transformation
- `schema` (dict): JSON Schema for output structure

**Returns:** `JsonResponse` with generated `data`

**Example:**
```python
# First extract markdown
md = await tabs.extract.markdown(url="https://news.ycombinator.com")

# Then transform with AI
schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}}
    }
}
result = await tabs.generate.json(
    markdown=md.content,
    instructions="Summarize the content and extract main topics",
    schema=schema
)
```

### Automate Operator

The Automate operator executes complex web automation tasks using natural language.

#### `automate.execute(task, url=None, schema=None)`

Execute an AI-powered browser automation task (returns async iterator for Server-Sent Events).

**Parameters:**
- `task` (str): Natural language description of the task
- `url` (str, optional): Starting URL for the task
- `schema` (dict, optional): JSON Schema for structured data extraction

**Yields:** `AutomateEvent` objects with `type` and `data` fields

**Event Types:**
- `start`: Automation started
- `agent:navigating`: Agent is navigating to a URL
- `agent:thinking`: Agent is analyzing the page
- `agent:action`: Agent performed an action (click, scroll, etc.)
- `agent:extracted`: Agent extracted structured data
- `task:completed`: Task finished successfully

**Example:**
```python
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "stars": {"type": "number"}
        }
    }
}

async for event in tabs.automate.execute(
    task="Find trending repositories and extract their names and star counts",
    url="https://github.com/trending",
    schema=schema
):
    if event.type == "agent:extracted":
        print(f"Extracted: {event.data.extracted_data}")
    elif event.type == "task:completed":
        print(f"Final answer: {event.data.final_answer}")
```

## Working with JSON Schemas

TABStack uses standard JSON Schema for defining data structures. Here are common patterns:

### Basic Object
```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"},
        "in_stock": {"type": "boolean"}
    }
}
```

### Array of Objects
```python
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "number"},
            "name": {"type": "string"}
        }
    }
}
```

### Nested Objects
```python
schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "details": {
                    "type": "object",
                    "properties": {
                        "weight": {"type": "number"},
                        "dimensions": {"type": "string"}
                    }
                }
            }
        }
    }
}
```

### Array of Primitives
```python
schema = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
```

For more information on JSON Schema, see [json-schema.org](https://json-schema.org/).

## Error Handling

The SDK provides specific exception classes for different error scenarios:

| Exception | Status Code | Description | Retryable |
|-----------|-------------|-------------|-----------|
| `BadRequestError` | 400 | Invalid request parameters | No |
| `UnauthorizedError` | 401 | Invalid or missing API key | No |
| `InvalidURLError` | 422 | URL is invalid or inaccessible | No |
| `ServerError` | 500 | Internal server error | Yes (with backoff) |
| `ServiceUnavailableError` | 503 | Service temporarily unavailable | Yes (after delay) |
| `APIError` | Other | Generic API error | Depends on status |

### Example Error Handling

```python
import asyncio
from tabstack import TABStack
from tabstack.exceptions import (
    BadRequestError,
    UnauthorizedError,
    InvalidURLError,
    ServerError,
    ServiceUnavailableError,
)

async def main():
    async with TABStack(api_key="your-api-key") as tabs:
        try:
            result = await tabs.extract.markdown(url="https://example.com")
        except UnauthorizedError:
            print("Error: Invalid API key")
        except InvalidURLError as e:
            print(f"Error: URL is invalid or inaccessible - {e.message}")
        except BadRequestError as e:
            print(f"Error: Bad request - {e.message}")
        except ServerError as e:
            print(f"Server error (retryable): {e.message}")
            # Implement retry logic with exponential backoff
        except ServiceUnavailableError as e:
            print(f"Service unavailable (retryable): {e.message}")
            # Wait and retry

asyncio.run(main())
```

## Development & Testing

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/tabstack/tabs-python.git
cd tabs-python

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tabstack --cov-report=html

# Run specific test file
pytest tests/test_extract.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .

# Type checking
mypy tabstack/
```

### Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── test_client.py           # TABStack client tests
├── test_extract.py          # Extract operator tests
├── test_generate.py         # Generate operator tests
├── test_automate.py         # Automate operator tests
├── test_http_client.py      # HTTP client tests
├── test_types.py            # Response type tests
├── test_exceptions.py       # Exception tests
├── test_utils.py            # Utility function tests
└── test_integration.py      # End-to-end integration tests
```

All tests use mocked HTTP responses - no real API calls are made during testing.

## Contributing

Contributions are welcome! Here's a quick checklist:

- [ ] Fork the repository and create a feature branch
- [ ] Write tests for new functionality
- [ ] Ensure all tests pass (`pytest`)
- [ ] Format code with ruff (`ruff format .`)
- [ ] Ensure linting passes (`ruff check .`)
- [ ] Update documentation as needed
- [ ] Submit a pull request with clear description

## Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13, 3.14)
- httpx >= 0.27.0

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Links

- **Homepage**: [https://tabstack.ai](https://tabstack.ai)
- **Documentation**: [https://docs.tabstack.ai](https://docs.tabstack.ai)
- **PyPI**: [https://pypi.org/project/tabstack/](https://pypi.org/project/tabstack/)
- **Repository**: [https://github.com/tabstack/tabs-python](https://github.com/tabstack/tabs-python)
- **Issues**: [https://github.com/tabstack/tabs-python/issues](https://github.com/tabstack/tabs-python/issues)

## Support

- **Email**: support@tabstack.ai
- **Discord**: [Join our community](https://discord.gg/tabstack)
- **Documentation**: [docs.tabstack.ai](https://docs.tabstack.ai)
