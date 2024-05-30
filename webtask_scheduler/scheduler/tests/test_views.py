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
    """
    Test case class for testing the GetTimerAPIView.
    """

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


class TestSetTimerAPIView:
    """
    Test case class for testing the SetTimerAPIView.
    """

    @pytest.fixture
    def api_client(self) -> APIClient:
        return APIClient()

    def test_set_timer_negative_numbers_validation(self, api_client):
        url = reverse("api:scheduler:set-timer")
        payload = {
            "hours": -1,
            "minutes": -1,
            "seconds": -1,
            "web_url": "https://example.com",
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "hours": ["Ensure this value is greater than or equal to 0."],
            "minutes": ["Ensure this value is greater than or equal to 0."],
            "seconds": ["Ensure this value is greater than or equal to 0."],
        }

    def test_set_timer_url_validation(self, api_client):
        url = reverse("api:scheduler:set-timer")
        payload = {
            "hours": 1,
            "minutes": 0,
            "seconds": 0,
            "web_url": "invalid url",
        }
        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"web_url": ["Enter a valid URL."]}

    @time_machine.travel(dt.datetime(2024, 5, 31, 1, 24, tzinfo=pytz.utc))
    def test_set_timer_create_task_successfully(self, api_client):
        url = reverse("api:scheduler:set-timer")
        payload = {
            "hours": 1,
            "minutes": 0,
            "seconds": 0,
            "web_url": "https://example.com",
        }

        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        task = PeriodicTask.objects.last()
        time_left = round((task.clocked.clocked_time - timezone.now().replace(tzinfo=pytz.utc)).total_seconds(), 1)
        assert response.json() == {"task_id": task.id, "time_left_in_seconds": int(time_left)}
        assert task.name == f"Get request to https://example.com at {task.clocked.clocked_time}"
        assert task.task == "webtask_scheduler.scheduler.tasks.send_request_to_url"
        assert task.args == '["https://example.com"]'
        assert task.one_off is True
