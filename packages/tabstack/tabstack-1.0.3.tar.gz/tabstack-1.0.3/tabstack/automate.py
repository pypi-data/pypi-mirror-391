"""Automate operator for TABStack AI SDK."""

from typing import Any, AsyncIterator, Dict, Optional

from ._http_client import HTTPClient
from ._shared import build_automate_request, parse_sse_event
from .types import AutomateEvent
from .utils import validate_json_schema


class Automate:
    """Automate operator for AI-powered browser automation.

    The Automate operator enables complex, multi-step web automation tasks using
    natural language instructions. An AI agent navigates a real browser, performing
    actions like clicking, filling forms, and extracting data.

    Use cases include:
    - Web scraping from complex sites requiring interaction
    - Automated form filling and submission
    - Multi-step workflows (login → navigate → extract → download)
    - Tasks requiring browser state (cookies, sessions, JavaScript)

    Results stream in real-time as Server-Sent Events (SSE), allowing you to
    monitor progress and handle events as they occur.
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize Automate operator.

        Args:
            http_client: HTTP client for making API requests
        """
        self._http = http_client

    async def execute(
        self,
        task: str,
        url: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[AutomateEvent]:
        """Execute AI-powered browser automation task with streaming updates.

        This method streams real-time progress updates as Server-Sent Events (SSE).
        Use this for web scraping, form filling, navigation, and multi-step workflows.

        Args:
            task: The task description in natural language
            url: Optional starting URL for the task
            schema: Optional JSON Schema for structured data extraction

        Yields:
            AutomateEvent objects representing different stages of task execution

        Raises:
            ValueError: If schema is invalid (basic validation only)
            BadRequestError: If task is missing or parameters are invalid
            UnauthorizedError: If API key is invalid
            ServerError: If server encounters an error
            ServiceUnavailableError: If automate service is not available

        Example:
            >>> async with TABStack(api_key="your-key") as tabs:
            ...     async for event in tabs.automate.execute(
            ...         task="Find the top 3 trending repositories",
            ...         url="https://github.com/trending"
            ...     ):
            ...         if event.type == "task:completed":
            ...             print(f"Result: {event.data.final_answer}")
            ...         elif event.type == "agent:extracted":
            ...             print(f"Extracted: {event.data.extracted_data}")
            ...         elif event.type == "error":
            ...             print(f"Error: {event.data.get('error')}")

        Event Types:
            Task Events:
                - start: Task initialization
                - task:setup: Task configuration
                - task:started: Task execution begins
                - task:completed: Task finished successfully
                - task:aborted: Task was terminated
                - task:validated: Task completion validation
                - task:validation_error: Validation failed

            Agent Events:
                - agent:processing: Agent thinking/planning
                - agent:status: Status updates and plans
                - agent:step: Processing step iterations
                - agent:action: Actions being performed
                - agent:reasoned: Agent reasoning output
                - agent:extracted: Data extraction results
                - agent:waiting: Agent waiting for operations

            Browser Events:
                - browser:navigated: Page navigation events
                - browser:action_started: Browser action initiated
                - browser:action_completed: Browser action finished
                - browser:screenshot_captured: Screenshot taken

            System Events:
                - system:debug_compression: Debug compression info
                - system:debug_message: Debug messages

            Stream Control:
                - complete: End of stream with results
                - done: Stream termination
                - error: Error occurred
        """
        # Validate schema if provided
        if schema:
            validate_json_schema(schema)

        request_data = build_automate_request(task, url, schema)

        # Stream the response and parse SSE events
        current_event_type: Optional[str] = None
        current_event_data: str = ""

        async for line in self._http.post_stream("v1/automate", request_data):
            event_type, event_data, event = parse_sse_event(
                line, current_event_type, current_event_data
            )

            # Update state
            current_event_type = event_type
            current_event_data = event_data

            # Yield completed event if available
            if event:
                yield event

        # Handle any remaining event at end of stream
        if current_event_type and current_event_data:
            event_type, event_data, event = parse_sse_event(
                "", current_event_type, current_event_data
            )
            if event:
                yield event
