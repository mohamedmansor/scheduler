import logging

import requests
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_request_to_url(url):
    """
    Sends a POST request to the specified URL and returns the response text.

    Args:
        url (str): The URL to send the request to.

    Returns:
        str: The response text.

    Raises:
        requests.exceptions.RequestException: If an error occurs while sending the request.

    """
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to send request to %s: %s", url, e)
        return {"error": str(e)}
    return response.text
