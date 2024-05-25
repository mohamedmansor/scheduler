from unittest.mock import patch

import pytest
import requests

from webtask_scheduler.scheduler.tasks import send_request_to_url

pytestmark = pytest.mark.django_db


@patch("webtask_scheduler.scheduler.tasks.requests.post")
def test_send_request_to_url_success(requests_mock):
    """Test sending a request to a URL successfully."""
    # Arrange
    url = "https://webhook.com"
    expected_response = {"message": "Success"}
    requests_mock.return_value.json.return_value = expected_response

    # Act
    result = send_request_to_url(url)

    # Assert
    assert result == expected_response


@patch("webtask_scheduler.scheduler.tasks.requests.post")
@patch("logging.Logger.error")
def test_send_request_to_url_failure(mock_logger, requests_mock):
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
def test_send_request_to_url_timeout(mock_logger, requests_mock):
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
