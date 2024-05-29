import logging

import pytz
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import PeriodicTask
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from webtask_scheduler.scheduler.serializers import SetTimerInputSerializer
from webtask_scheduler.scheduler.serializers import SetTimerOutputSerializer

logger = logging.getLogger(__name__)


class SetTimerAPIView(CreateAPIView):
    """
    API view to schedule a task to send a POST request to a given URL after a specified amount of time.

    This view requires authentication to access.

    """

    permission_classes = (permissions.IsAuthenticated,)

    input_serializer_class = SetTimerInputSerializer
    output_serializer_class = SetTimerOutputSerializer

    @extend_schema(
        tags=["scheduler"],
        request=SetTimerInputSerializer,
        responses=SetTimerOutputSerializer,
    )
    def post(self, request, *args, **kwargs):
        input_serializer = self.input_serializer_class(data=request.data, context={"request": request})
        input_serializer.is_valid(raise_exception=True)
        hours = input_serializer.validated_data["hours"]
        minutes = input_serializer.validated_data["minutes"]
        seconds = input_serializer.validated_data["seconds"]
        time_now = timezone.now().replace(tzinfo=pytz.utc)
        run_at = time_now + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        task = PeriodicTask.objects.create(
            name=f"Get request to {input_serializer.validated_data['web_url']} at {run_at}",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            clocked=ClockedSchedule.objects.create(clocked_time=run_at),
            args=f'["{input_serializer.validated_data["web_url"]}"]',
        )

        time_left_in_seconds = round((task.clocked.clocked_time - time_now).total_seconds(), 1)
        data = {
            "task_id": task.id,
            "time_left_in_seconds": time_left_in_seconds,
        }
        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GetTimerAPIView(RetrieveAPIView):
    """
    API view to retrieve the remaining time of a scheduled task.

    This view requires authentication and returns the remaining time of a scheduled task
    identified by its task ID. It calculates the time left for the task to execute
    based on the current time and the scheduled time.

    """

    permission_classes = (permissions.IsAuthenticated,)

    output_serializer_class = SetTimerOutputSerializer

    @extend_schema(
        tags=["scheduler"],
        responses=SetTimerOutputSerializer,
    )
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs["task_id"]
        try:
            task = PeriodicTask.objects.get(id=task_id)
        except PeriodicTask.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        time_now = timezone.now().replace(tzinfo=pytz.utc)
        time_left_in_seconds = round((task.clocked.clocked_time - time_now).total_seconds(), 1)
        if time_left_in_seconds < 0:
            time_left_in_seconds = 0
        data = {
            "task_id": task.id,
            "time_left_in_seconds": time_left_in_seconds,
        }
        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
