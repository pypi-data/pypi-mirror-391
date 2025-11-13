"""Shared utilities for sync and async implementations.

Contains all pure business logic that can be reused between sync and async versions.
"""

import json
from typing import Any, Dict, Optional, Tuple

from .types import AutomateEvent


def build_markdown_request(
    url: str, metadata: bool = False, nocache: bool = False
) -> Dict[str, Any]:
    """Build request data for markdown extraction.

    Args:
        url: URL to fetch and convert
        metadata: Whether to return metadata as separate field
        nocache: Whether to bypass cache

    Returns:
        Request data dictionary
    """
    request_data: Dict[str, Any] = {"url": url}
    if metadata:
        request_data["metadata"] = metadata
    if nocache:
        request_data["nocache"] = nocache
    return request_data


def build_schema_request(
    url: str, instructions: Optional[str] = None, nocache: bool = False
) -> Dict[str, Any]:
    """Build request data for schema generation.

    Args:
        url: URL to analyze
        instructions: Optional instructions for schema generation
        nocache: Whether to bypass cache

    Returns:
        Request data dictionary
    """
    request_data: Dict[str, Any] = {"url": url}
    if instructions:
        request_data["instructions"] = instructions
    if nocache:
        request_data["nocache"] = nocache
    return request_data


def build_json_extract_request(
    url: str, schema: Dict[str, Any], nocache: bool = False
) -> Dict[str, Any]:
    """Build request data for JSON extraction.

    Args:
        url: URL to extract from
        schema: JSON Schema defining structure
        nocache: Whether to bypass cache

    Returns:
        Request data dictionary
    """
    request_data: Dict[str, Any] = {"url": url, "schema": schema}
    if nocache:
        request_data["nocache"] = nocache
    return request_data


def build_json_generate_request(
    url: str, schema: Dict[str, Any], instructions: str, nocache: bool = False
) -> Dict[str, Any]:
    """Build request data for JSON generation.

    Args:
        url: URL to fetch content from
        schema: JSON Schema for output structure
        instructions: AI instructions for transformation
        nocache: Whether to bypass cache

    Returns:
        Request data dictionary
    """
    request_data: Dict[str, Any] = {
        "url": url,
        "json_schema": schema,
        "instructions": instructions,
    }
    if nocache:
        request_data["nocache"] = nocache
    return request_data


def build_automate_request(
    task: str,
    url: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build request data for automation task.

    Args:
        task: Task description in natural language
        url: Optional starting URL
        schema: Optional JSON Schema for structured output

    Returns:
        Request data dictionary
    """
    request_data: Dict[str, Any] = {"task": task}
    if url:
        request_data["url"] = url
    if schema:
        request_data["schema"] = schema
    return request_data


def get_http_headers(api_key: str, content_type: str = "application/json") -> Dict[str, str]:
    """Get HTTP headers for requests.

    Args:
        api_key: API key for authentication
        content_type: Content type for the request

    Returns:
        Dictionary of headers
    """
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": content_type,
        "Accept": "application/json",
        "User-Agent": "tabstack-ai-python/1.0.0",
    }


def handle_error_response(status: int, body: bytes) -> None:
    """Handle error responses and raise appropriate exceptions.

    Args:
        status: HTTP status code
        body: Response body

    Raises:
        TABStackError: Appropriate exception based on status code
    """
    from .exceptions import (
        APIError,
        BadRequestError,
        InvalidURLError,
        ServerError,
        ServiceUnavailableError,
        UnauthorizedError,
    )

    # Try to parse JSON error response, fall back to raw text if not JSON
    try:
        error_data = json.loads(body.decode("utf-8"))
        error_message = error_data.get("error", "Unknown error")
    except (json.JSONDecodeError, UnicodeDecodeError):
        error_message = body.decode("utf-8", errors="replace") if body else "Unknown error"

    # Map HTTP status codes to specific exception types
    if status == 400:
        raise BadRequestError(error_message)
    elif status == 401:
        raise UnauthorizedError(error_message)
    elif status == 422:
        raise InvalidURLError(error_message)
    elif status == 500:
        raise ServerError(error_message)
    elif status == 503:
        raise ServiceUnavailableError(error_message)
    else:
        raise APIError(error_message, status)


def parse_sse_event(
    line: str, current_event_type: Optional[str], current_event_data: str
) -> Tuple[Optional[str], str, Optional[AutomateEvent]]:
    """Parse Server-Sent Events (SSE) line.

    Args:
        line: Current line from SSE stream
        current_event_type: Current event type being accumulated
        current_event_data: Current event data being accumulated

    Returns:
        Tuple of (updated_event_type, updated_event_data, completed_event)
        where completed_event is None if no event is complete yet
    """
    # SSE format: "event: <type>" or "data: <json>"
    if line.startswith("event:"):
        # If we have a pending event, complete it
        if current_event_type and current_event_data:
            try:
                data_dict = json.loads(current_event_data)
                event = AutomateEvent(type=current_event_type, data=data_dict)
                # Extract new event type and reset data
                new_event_type = line[6:].strip()
                return new_event_type, "", event
            except json.JSONDecodeError:
                # If JSON is invalid, skip and start new event
                new_event_type = line[6:].strip()
                return new_event_type, "", None

        # Extract event type and continue accumulating
        new_event_type = line[6:].strip()
        return new_event_type, current_event_data, None

    elif line.startswith("data:"):
        # Accumulate event data (can be multiline)
        data_line = line[5:].strip()
        if current_event_data:
            updated_data = current_event_data + "\n" + data_line
        else:
            updated_data = data_line
        return current_event_type, updated_data, None

    elif line == "":
        # Empty line completes an event
        if current_event_type and current_event_data:
            try:
                data_dict = json.loads(current_event_data)
                event = AutomateEvent(type=current_event_type, data=data_dict)
                # Reset for next event
                return None, "", event
            except json.JSONDecodeError:
                # If JSON is invalid, skip event
                return None, "", None

    # Line doesn't match SSE format, ignore it
    return current_event_type, current_event_data, None
