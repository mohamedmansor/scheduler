import datetime as dt

import pytest
import pytz
import time_machine
from django.shortcuts import reverse
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestGetTimerAPIView:
    @pytest.fixture
    def api_client(self) -> APIClient:
        return APIClient()

    @time_machine.travel(dt.datetime(2024, 5, 30, 1, 24, tzinfo=pytz.utc))
    @pytest.fixture
    def test_data(self):
        time_now = timezone.now().replace(tzinfo=pytz.utc)
        run_at = time_now + timezone.timedelta(hours=0, minutes=1, seconds=0)
        task = PeriodicTask.objects.create(
            clocked=ClockedSchedule.objects.create(clocked_time=run_at),
            name="Get request to https://example.com at 2022-01-01 00:00:00",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            args='["https://example.com"]',
        )
        return task

    def test_get_timer_id_not_found(self, api_client, test_data):
        url = reverse("api:scheduler:get-timer", kwargs={"task_id": 999999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Task not found."}

    @time_machine.travel(dt.datetime(2024, 5, 31, 1, 24, tzinfo=pytz.utc))
    def test_get_expired_timer_returns_zero(self, api_client, test_data):
        url = reverse("api:scheduler:get-timer", kwargs={"task_id": test_data.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "task_id": test_data.id,
            "time_left_in_seconds": 0,
        }

    def test_get_timer_successfully(self, api_client, test_data):
        url = reverse("api:scheduler:get-timer", kwargs={"task_id": test_data.id})
        response = api_client.get(url)
        time_left = round((test_data.clocked.clocked_time - timezone.now().replace(tzinfo=pytz.utc)).total_seconds(), 1)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"task_id": test_data.id, "time_left_in_seconds": int(time_left)}


# TODO Add tests for SetTimerAPIView
