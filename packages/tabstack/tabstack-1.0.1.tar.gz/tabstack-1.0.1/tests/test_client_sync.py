"""Tests for TABStackSync client."""

from typing import Any

import pytest

from tabstack import TABStackSync
from tabstack.automate_sync import AutomateSync
from tabstack.extract_sync import ExtractSync
from tabstack.generate_sync import GenerateSync


class TestTABStackSyncInitialization:
    """Tests for TABStackSync client initialization."""

    def test_initialization_with_api_key(self) -> None:
        """Test client initialization with API key."""
        client = TABStackSync(api_key="test_key_123")
        assert client._http_client.api_key == "test_key_123"

    def test_initialization_with_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = TABStackSync(api_key="test_key", base_url="https://custom.api.com")
        assert client._http_client.base_url == "https://custom.api.com"

    def test_initialization_missing_api_key(self) -> None:
        """Test initialization without API key raises error."""
        with pytest.raises(TypeError):
            TABStackSync()  # type: ignore

    def test_operators_are_initialized(self) -> None:
        """Test all operators are properly initialized."""
        client = TABStackSync(api_key="test_key")
        assert isinstance(client.extract, ExtractSync)
        assert isinstance(client.generate, GenerateSync)
        assert isinstance(client.automate, AutomateSync)

    def test_operators_share_http_client(self) -> None:
        """Test all operators share the same HTTP client."""
        client = TABStackSync(api_key="test_key")
        # All operators should use the same HTTP client instance
        assert client.extract._http is client._http_client
        assert client.generate._http is client._http_client
        assert client.automate._http is client._http_client


class TestTABStackSyncContextManager:
    """Tests for sync context manager support."""

    def test_context_manager_usage(self) -> None:
        """Test using TABStackSync as context manager."""
        with TABStackSync(api_key="test_key") as client:
            assert isinstance(client, TABStackSync)
            assert isinstance(client.extract, ExtractSync)

    def test_context_manager_closes_http_client(self, mocker: Any) -> None:
        """Test context manager closes HTTP client."""
        client = TABStackSync(api_key="test_key")

        # Mock the close method
        mock_close = mocker.Mock()
        client._http_client.close = mock_close

        with client:
            pass

        mock_close.assert_called_once()

    def test_manual_close(self, mocker: Any) -> None:
        """Test manually closing the client."""
        client = TABStackSync(api_key="test_key")

        mock_close = mocker.Mock()
        client._http_client.close = mock_close

        client.close()

        mock_close.assert_called_once()
