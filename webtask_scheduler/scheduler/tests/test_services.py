import datetime as dt
from unittest.mock import patch

import pytest
import pytz
import time_machine
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask

from webtask_scheduler.scheduler.services import TimerService

pytestmark = pytest.mark.django_db


class TestTimerService:
    """
    Test case class for testing the TimerService.
    """

    @time_machine.travel(dt.datetime(2024, 5, 31, 1, 24, tzinfo=pytz.utc))
    @patch("logging.Logger.info")
    def test_set_timer(self, mock_logger) -> None:
        service: TimerService = TimerService()
        data: dict = service.set(hours=0, minutes=1, seconds=0, web_url="https://example.com")

        assert data["time_left_in_seconds"] == 60
        assert mock_logger.call_count == 2
        PeriodicTask.objects.count() == 1
        PeriodicTask.objects.last().id == data["task_id"]

    @time_machine.travel(dt.datetime(2024, 5, 31, 1, 24, tzinfo=pytz.utc))
    @patch("logging.Logger.info")
    def test_get_timer(self, mock_logger) -> None:
        time_now: dt.datetime = timezone.now().replace(tzinfo=pytz.utc)
        run_at: dt.datetime = time_now + timezone.timedelta(hours=0, minutes=1, seconds=0)
        task: PeriodicTask = PeriodicTask.objects.create(
            clocked=ClockedSchedule.objects.create(clocked_time=run_at),
            name="Get request to https://example.com at 2022-01-01 00:00:00",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            args='["https://example.com"]',
        )
        service: TimerService = TimerService()
        data: dict = service.get(task_id=task.id)

        assert data["time_left_in_seconds"] == 60
        assert data["task_id"] == task.id
        assert mock_logger.call_count == 1

    @patch("logging.Logger.error")
    def test_get_timer_id_not_found(self, mock_logger) -> None:
        service: TimerService = TimerService()
        with pytest.raises(ValueError):
            service.get(task_id=999999)

        assert mock_logger.call_count == 1
