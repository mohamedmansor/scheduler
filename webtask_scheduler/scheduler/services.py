import logging

import pytz
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask

logger = logging.getLogger(__name__)


class TimerService:
    def set(self, hours: int, minutes: int, seconds: int, web_url: str) -> dict:
        """
        Set a timer to send a GET request to a given URL after a specified amount of time.
        """
        logger.info(f"Setting timer for {hours} hours, {minutes} minutes, {seconds} seconds with web URL: {web_url}")

        time_now = timezone.now().replace(tzinfo=pytz.utc)
        run_at = time_now + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        task: PeriodicTask = PeriodicTask.objects.create(
            name=f"Get request to {web_url} at {run_at}",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            clocked=ClockedSchedule.objects.create(clocked_time=run_at),
            args=f'["{web_url}"]',
        )

        time_left_in_seconds: float = round((task.clocked.clocked_time - time_now).total_seconds(), 1)
        data: dict = {
            "task_id": task.id,
            "time_left_in_seconds": time_left_in_seconds,
        }
        logger.info(f"Timer set for {run_at} with task ID {task.id}")
        return data

    def get(self, task_id: int) -> dict:
        """
        Get the remaining time left for a timer to expire.
        """
        try:
            task: PeriodicTask = PeriodicTask.objects.get(id=task_id)
        except PeriodicTask.DoesNotExist:
            logger.error(f"Error occurred while retrieving task with ID {task_id}")
            raise ValueError(f"Task with ID {task_id} does not exist")

        time_now = timezone.now().replace(tzinfo=pytz.utc)
        time_left_in_seconds: float = round((task.clocked.clocked_time - time_now).total_seconds(), 1)
        if time_left_in_seconds < 0:
            time_left_in_seconds = 0

        data: dict = {
            "task_id": task.id,
            "time_left_in_seconds": time_left_in_seconds,
        }
        return data
