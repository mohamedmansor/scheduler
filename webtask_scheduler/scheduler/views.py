import logging

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
from webtask_scheduler.scheduler.tasks import send_request_to_url

logger = logging.getLogger(__name__)


class SetTimerAPIView(CreateAPIView):
    """
    Schedule a task to send a POST request to a given URL after a specified amount of time.
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
        run_at = timezone.datetime.now() + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        task = PeriodicTask.objects.create(
            name=f"Get request to {input_serializer.validated_data['web_url']} at {run_at}",
            task="webtask_scheduler.scheduler.tasks.send_request_to_url",
            one_off=True,
            clocked=ClockedSchedule.objects.create(clocked_time=run_at),
            args=f'["{input_serializer.validated_data["web_url"]}"]',
        )

        time_left = timezone.now() + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        data = {
            "task_uuid": task.id,
            "time_left": time_left,
        }
        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GetTimerAPIView(RetrieveAPIView):
    """
    Retrieve the status of a scheduled task.
    """

    permission_classes = (permissions.IsAuthenticated,)

    output_serializer_class = SetTimerOutputSerializer

    @extend_schema(
        tags=["scheduler"],
        responses=SetTimerOutputSerializer,
    )
    def get(self, request, *args, **kwargs):
        task_uuid = self.kwargs["task_uuid"]
        task = send_request_to_url.AsyncResult(task_uuid)
        # time_left = task.eta - timezone.now()
        data = {
            "task_uuid": task.id,
            "status": task.status,
            "time_left": 10,
        }
        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
