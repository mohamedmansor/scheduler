from unittest.mock import patch

import pytest
import requests

from webtask_scheduler.scheduler.tasks import send_request_to_url

pytestmark = pytest.mark.django_db


class MockResponse:
    def __init__(self, json_data: dict = {}, status_code: int = 200, reason: str = None):
        self.data = json_data
        self.status_code = status_code
        self.reason = reason or "dummy reason"

    @property
    def text(self) -> dict:
        return self.data

    def raise_for_status(self) -> None:
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Error: {self.reason}"
        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error: {self.reason}"

        if http_error_msg:
            raise requests.exceptions.HTTPError(http_error_msg, response=self)


class TestTasks:
    @patch("webtask_scheduler.scheduler.tasks.requests.post")
    def test_send_request_to_url_success(self, requests_mock: patch) -> None:
        """Test sending a request to a URL successfully."""
        # Arrange
        url = "https://webhook.com"
        requests_mock.return_value = MockResponse(json_data={"message": "Success"}, status_code=200)

        # Act
        result = send_request_to_url(url)

        # Assert
        assert result == {"message": "Success"}

    @patch("webtask_scheduler.scheduler.tasks.requests.post")
    @patch("logging.Logger.error")
    def test_send_request_to_url_failure(self, mock_logger: patch, requests_mock: patch) -> None:
        """Test sending a request to a URL that returns an error."""
        # Arrange
        url = "https://webhook.com"
        expected_error = "Internal Server Error"
        requests_mock.side_effect = requests.exceptions.HTTPError(expected_error)

        # Act
        result = send_request_to_url(url)

        # Assert
        assert result == {"error": expected_error}
        mock_logger.assert_called_once()

    @patch("webtask_scheduler.scheduler.tasks.requests.post")
    @patch("logging.Logger.error")
    def test_send_request_to_url_timeout(self, mock_logger: patch, requests_mock: patch) -> None:
        """Test sending a request to a URL that times out."""
        # Arrange
        url = "https://webhook.com"
        expected_error = "Request timed out"

        requests_mock.side_effect = requests.exceptions.Timeout(expected_error)

        # Act
        result = send_request_to_url(url)

        # Assert
        assert result == {"error": expected_error}
        mock_logger.assert_called_once()
