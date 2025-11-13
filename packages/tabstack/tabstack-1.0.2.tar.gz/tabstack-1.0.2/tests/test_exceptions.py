"""Tests for exception classes."""

from tabstack.exceptions import (
    APIError,
    BadRequestError,
    InvalidURLError,
    ServerError,
    ServiceUnavailableError,
    TABStackError,
    UnauthorizedError,
)


class TestTABStackError:
    """Tests for base TABStackError."""

    def test_error_with_message_and_status(self) -> None:
        """Test error initialization with message and status code."""
        error = TABStackError("Test error", status_code=418)
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code == 418

    def test_error_with_message_only(self) -> None:
        """Test error initialization with message only."""
        error = TABStackError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None


class TestBadRequestError:
    """Tests for BadRequestError."""

    def test_error_initialization(self) -> None:
        """Test BadRequestError has correct status code."""
        error = BadRequestError("Invalid request")
        assert str(error) == "Invalid request"
        assert error.message == "Invalid request"
        assert error.status_code == 400

    def test_inherits_from_tabstack_error(self) -> None:
        """Test BadRequestError inherits from TABStackError."""
        error = BadRequestError("Test")
        assert isinstance(error, TABStackError)


class TestUnauthorizedError:
    """Tests for UnauthorizedError."""

    def test_error_with_custom_message(self) -> None:
        """Test UnauthorizedError with custom message."""
        error = UnauthorizedError("Custom auth error")
        assert str(error) == "Custom auth error"
        assert error.status_code == 401

    def test_error_with_default_message(self) -> None:
        """Test UnauthorizedError with default message."""
        error = UnauthorizedError()
        assert "Invalid or missing API key" in str(error)
        assert error.status_code == 401

    def test_inherits_from_tabstack_error(self) -> None:
        """Test UnauthorizedError inherits from TABStackError."""
        error = UnauthorizedError()
        assert isinstance(error, TABStackError)


class TestInvalidURLError:
    """Tests for InvalidURLError."""

    def test_error_with_custom_message(self) -> None:
        """Test InvalidURLError with custom message."""
        error = InvalidURLError("URL not found")
        assert str(error) == "URL not found"
        assert error.status_code == 422

    def test_error_with_default_message(self) -> None:
        """Test InvalidURLError with default message."""
        error = InvalidURLError()
        assert "Invalid or inaccessible URL" in str(error)
        assert error.status_code == 422

    def test_inherits_from_tabstack_error(self) -> None:
        """Test InvalidURLError inherits from TABStackError."""
        error = InvalidURLError()
        assert isinstance(error, TABStackError)


class TestServerError:
    """Tests for ServerError."""

    def test_error_with_custom_message(self) -> None:
        """Test ServerError with custom message."""
        error = ServerError("Database connection failed")
        assert str(error) == "Database connection failed"
        assert error.status_code == 500

    def test_error_with_default_message(self) -> None:
        """Test ServerError with default message."""
        error = ServerError()
        assert "Internal server error" in str(error)
        assert error.status_code == 500

    def test_inherits_from_tabstack_error(self) -> None:
        """Test ServerError inherits from TABStackError."""
        error = ServerError()
        assert isinstance(error, TABStackError)


class TestServiceUnavailableError:
    """Tests for ServiceUnavailableError."""

    def test_error_with_custom_message(self) -> None:
        """Test ServiceUnavailableError with custom message."""
        error = ServiceUnavailableError("Automate service is down")
        assert str(error) == "Automate service is down"
        assert error.status_code == 503

    def test_error_with_default_message(self) -> None:
        """Test ServiceUnavailableError with default message."""
        error = ServiceUnavailableError()
        assert "Service unavailable" in str(error)
        assert error.status_code == 503

    def test_inherits_from_tabstack_error(self) -> None:
        """Test ServiceUnavailableError inherits from TABStackError."""
        error = ServiceUnavailableError()
        assert isinstance(error, TABStackError)


class TestAPIError:
    """Tests for generic APIError."""

    def test_error_with_custom_status(self) -> None:
        """Test APIError with custom status code."""
        error = APIError("Rate limit exceeded", status_code=429)
        assert str(error) == "Rate limit exceeded"
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429

    def test_inherits_from_tabstack_error(self) -> None:
        """Test APIError inherits from TABStackError."""
        error = APIError("Test", 418)
        assert isinstance(error, TABStackError)
