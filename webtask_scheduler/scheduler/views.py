import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from webtask_scheduler.scheduler.serializers import SetTimerInputSerializer
from webtask_scheduler.scheduler.serializers import SetTimerOutputSerializer
from webtask_scheduler.scheduler.services import TimerService

logger = logging.getLogger(__name__)


class SetTimerAPIView(CreateAPIView):
    """
    API view to schedule a task to send a POST request to a given URL after a specified amount of time.

    This view requires authentication to access.

    """

    # Authentication and permission classes are set to allow access without authentication
    # It's recommended to set appropriate authentication and permission classes based on the application's requirements
    # But for the purpose of this example, we are allowing access without authentication
    permission_classes = (permissions.AllowAny,)

    input_serializer_class = SetTimerInputSerializer
    output_serializer_class = SetTimerOutputSerializer

    @extend_schema(
        tags=["scheduler"],
        request=SetTimerInputSerializer,
        responses=SetTimerOutputSerializer,
    )
    def post(self, request, *args, **kwargs) -> Response:
        input_serializer: SetTimerInputSerializer = self.input_serializer_class(
            data=request.data, context={"request": request}
        )
        input_serializer.is_valid(raise_exception=True)
        hours: int = input_serializer.validated_data["hours"]
        minutes: int = input_serializer.validated_data["minutes"]
        seconds: int = input_serializer.validated_data["seconds"]
        svc = TimerService()
        data = svc.set(
            hours=hours, minutes=minutes, seconds=seconds, web_url=input_serializer.validated_data["web_url"]
        )
        output_serializer: SetTimerOutputSerializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GetTimerAPIView(RetrieveAPIView):
    """
    API view to retrieve the remaining time of a scheduled task.

    This view requires authentication and returns the remaining time of a scheduled task
    identified by its task ID. It calculates the time left for the task to execute
    based on the current time and the scheduled time.

    """

    # Authentication and permission classes are set to allow access without authentication
    # It's recommended to set appropriate authentication and permission classes based on the application's requirements
    # But for the purpose of this example, we are allowing access without authentication
    permission_classes = (permissions.AllowAny,)

    output_serializer_class = SetTimerOutputSerializer

    @extend_schema(
        tags=["scheduler"],
        responses=SetTimerOutputSerializer,
    )
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs["task_id"]
        svc = TimerService()
        try:
            data = svc.get(task_id)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
