import pytest
from django.utils import timezone
from django_celery_beat.tests import ClockedScheduleFactory
from django_celery_beat.tests import PeriodicTaskFactory
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestGetTimerAPIView:
    @pytest.fixture
    def api_client(self) -> APIClient:
        return APIClient()

    @pytest.fixture
    def test_data(self):
        # Set up test data
        task = PeriodicTaskFactory.create(
            clocked=ClockedScheduleFactory.create(),
            name="Get request to https://example.com at 2022-01-01 00:00:00",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            args='["https://example.com"]',
            expires=timezone.now() + timezone.timedelta(hours=1),
        )

        return task

    def test_get_timer_details_successfully(self, api_client, test_data):
        task = test_data
        response = api_client.get("/api/v1/scheduler/", HTTP_AUTHORIZATION="Bearer generate_jwe_token(user)")

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "task_id": task.id,
            "time_left_in_seconds": task.expires.seconds,
        }
