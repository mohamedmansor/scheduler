import logging

import requests
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_request_to_url(url):
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to send request to %s: %s", url, e)
        return {"error": str(e)}
    return response.text
