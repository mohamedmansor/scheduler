import logging

import requests
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_request_to_url(url: str) -> str | dict:
    """
    Sends a POST request to the specified URL and returns the response text.

    Args:
        url (str): The URL to send the request to.

    Returns:
        Union[str, dict]: The response text or an error dictionary.

    Raises:
        requests.exceptions.RequestException: If an error occurs while sending the request.

    """
    logger.info("Sending request to %s", url)
    try:
        response = requests.post(url, timeout=10)

        logger.info("Received response with status code %s for url %s", response.status_code, url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to send request to %s: %s", url, e)
        return {"error": str(e)}
    return response.text
