"""Tests for AutomateSync operator."""

from typing import Any

import pytest

from tabstack.automate_sync import AutomateSync
from tabstack.types import AutomateEvent


class TestAutomateSyncExecute:
    """Tests for automate execution."""

    def test_execute_streaming(self, mocker: Any, mock_automate_events: list[str]) -> None:
        """Test automate execute with streaming events."""
        mock_http = mocker.Mock()

        # Mock the streaming response
        def mock_stream(path, data):  # type: ignore
            for event_line in mock_automate_events:
                yield event_line

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(task="Extract data", url="https://example.com"):
            events.append(event)

        # Should have received all events
        assert len(events) == 4
        assert all(isinstance(e, AutomateEvent) for e in events)

        # Check event types
        assert events[0].type == "start"
        assert events[1].type == "agent:navigating"
        assert events[2].type == "agent:extracted"
        assert events[3].type == "task:completed"

        # Verify API was called correctly
        mock_http.post_stream.assert_called_once_with(
            "v1/automate",
            {
                "task": "Extract data",
                "url": "https://example.com",
            },
        )

    def test_execute_with_schema(self, mocker: Any, json_schema: dict[str, Any]) -> None:
        """Test automate execute with JSON schema."""
        mock_http = mocker.Mock()

        def mock_stream(path, data):  # type: ignore
            yield "event: task:completed"
            yield 'data: {"finalAnswer": "Done", "success": true}'
            yield ""  # Empty line completes the event

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(
            task="Extract data", url="https://example.com", schema=json_schema
        ):
            events.append(event)

        # Verify schema was passed
        assert len(events) > 0
        call_args = mock_http.post_stream.call_args
        assert call_args[0][1]["schema"] == json_schema

    def test_execute_validates_schema(self, mocker: Any) -> None:
        """Test automate validates schema before sending."""
        mock_http = mocker.Mock()
        automate = AutomateSync(mock_http)

        # Invalid schema should raise ValueError
        invalid_schema = {"missing": "type"}
        with pytest.raises(ValueError, match="Schema must have a 'type' field"):
            for _ in automate.execute(
                task="Test", url="https://example.com", schema=invalid_schema
            ):
                pass

    def test_execute_parses_event_data(self, mocker: Any) -> None:
        """Test automate correctly parses event data."""
        mock_http = mocker.Mock()

        def mock_stream(path, data):  # type: ignore
            yield "event: agent:extracted"
            yield 'data: {"extractedData": {"title": "Test Title", "count": 42}}'
            yield ""  # Empty line completes the event

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(task="Test", url="https://example.com"):
            events.append(event)

        assert len(events) == 1
        event = events[0]
        assert event.type == "agent:extracted"
        # Access via snake_case (converted from camelCase)
        assert event.data.extracted_data["title"] == "Test Title"
        assert event.data.extracted_data["count"] == 42

    def test_execute_handles_malformed_sse(self, mocker: Any) -> None:
        """Test automate handles malformed SSE gracefully."""
        mock_http = mocker.Mock()

        def mock_stream(path, data):  # type: ignore
            yield "event: start"  # Event without data
            yield ""  # Complete the event (will have no data)
            yield "data: not-json"  # Data without event (invalid)
            yield "event: valid"  # Valid event
            yield 'data: {"message": "ok"}'
            yield ""  # Complete the event

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(task="Test", url="https://example.com"):
            events.append(event)

        # Should have at least parsed the valid event
        # (implementation may vary on how it handles malformed events)
        assert len(events) >= 1

    def test_execute_with_empty_task(self, mocker: Any) -> None:
        """Test automate with empty task string."""
        mock_http = mocker.Mock()

        def mock_stream(path, data):  # type: ignore
            yield "event: task:completed"
            yield 'data: {"finalAnswer": "Done"}'
            yield ""  # Empty line completes the event

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(task="", url="https://example.com"):
            events.append(event)

        # Should still call API (API will validate)
        mock_http.post_stream.assert_called_once()

    def test_execute_event_types(self, mocker: Any) -> None:
        """Test various event types are parsed correctly."""
        mock_http = mocker.Mock()

        def mock_stream(path, data):  # type: ignore
            # Various event types from the API
            yield "event: start"
            yield 'data: {"message": "Starting"}'
            yield ""
            yield "event: agent:navigating"
            yield 'data: {"url": "https://test.com"}'
            yield ""
            yield "event: agent:thinking"
            yield 'data: {"thought": "Analyzing page"}'
            yield ""
            yield "event: agent:extracted"
            yield 'data: {"extractedData": {}}'
            yield ""
            yield "event: agent:action"
            yield 'data: {"action": "click", "selector": "button"}'
            yield ""
            yield "event: task:completed"
            yield 'data: {"finalAnswer": "Done", "success": true}'
            yield ""

        # Use Mock instead of AsyncMock for post_stream
        mock_http.post_stream = mocker.Mock(side_effect=mock_stream)

        automate = AutomateSync(mock_http)
        events = []
        for event in automate.execute(task="Test", url="https://example.com"):
            events.append(event)

        assert len(events) == 6
        event_types = [e.type for e in events]
        assert "start" in event_types
        assert "agent:navigating" in event_types
        assert "agent:thinking" in event_types
        assert "agent:extracted" in event_types
        assert "agent:action" in event_types
        assert "task:completed" in event_types
