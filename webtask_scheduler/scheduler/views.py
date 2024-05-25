import logging

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from webtask_scheduler.scheduler.serializers import SetTimerInputSerializer
from webtask_scheduler.scheduler.serializers import SetTimerOutputSerializer

from .tasks import send_request_to_url

logger = logging.getLogger(__name__)


class SetTimerAPIView(CreateAPIView):
    """ """

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
        # TODO invoke task
        eta = timezone.now() + timezone.timedelta(
            hours=input_serializer.validated_data["hours"],
            minutes=input_serializer.validated_data["minutes"],
            seconds=input_serializer.validated_data["seconds"],
        )
        task = send_request_to_url.apply_async(
            args=[input_serializer.validated_data["web_url"]],
            eta=eta,
        )
        data = {
            "task_id": task.id,
            "status": task.status,
            "time_left": task.time_left,
        }
        output_serializer = self.output_serializer_class(data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
