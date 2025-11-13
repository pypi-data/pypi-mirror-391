"""Shared pytest fixtures for TABStack SDK tests.

Provides fixtures for mocking HTTP responses and creating test clients.
"""

from typing import Any, Dict, List

import httpx
import pytest


@pytest.fixture
def api_key() -> str:
    """Return test API key."""
    return "test_api_key_12345"


@pytest.fixture
def base_url() -> str:
    """Return test base URL."""
    return "https://api.tabstack.ai/"


@pytest.fixture
def mock_markdown_response() -> Dict[str, Any]:
    """Return mock markdown extraction response."""
    return {
        "url": "https://example.com",
        "content": "# Example Page\n\nThis is example content.",
        "metadata": {
            "title": "Example Page",
            "description": "An example page",
            "author": "Test Author",
            "publisher": "Test Publisher",
            "image": "https://example.com/image.jpg",
            "site_name": "Example Site",
            "url": "https://example.com",
            "type": "article",
        },
    }


@pytest.fixture
def mock_schema_response() -> Dict[str, Any]:
    """Return mock schema generation response."""
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                    },
                },
            },
        },
    }


@pytest.fixture
def mock_json_response() -> Dict[str, Any]:
    """Return mock JSON extraction response."""
    return {
        "title": "Example Products",
        "items": [
            {"name": "Product 1", "price": 19.99},
            {"name": "Product 2", "price": 29.99},
        ],
    }


@pytest.fixture
def mock_automate_events() -> List[str]:
    """Return mock SSE events from automate endpoint."""
    return [
        "event: start",
        'data: {"message": "Starting automation"}',
        "",
        "event: agent:navigating",
        'data: {"url": "https://example.com"}',
        "",
        "event: agent:extracted",
        'data: {"extractedData": {"title": "Test"}}',
        "",
        "event: task:completed",
        'data: {"finalAnswer": "Task completed", "success": true}',
        "",
    ]


@pytest.fixture
def json_schema() -> Dict[str, Any]:
    """Return valid JSON Schema for testing."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name"],
    }


@pytest.fixture
def mock_httpx_client(mocker: Any) -> Any:
    """Return mocked httpx.AsyncClient."""
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.aclose = mocker.AsyncMock()
    return mock_client


@pytest.fixture
def mock_successful_response(mocker: Any) -> Any:
    """Return mock successful HTTP response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.content = b'{"data": "success"}'
    mock_response.json.return_value = {"data": "success"}
    return mock_response


@pytest.fixture
def mock_error_response(mocker: Any) -> Any:
    """Return mock error HTTP response."""
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 400
    mock_response.content = b'{"error": "Bad request"}'
    return mock_response
