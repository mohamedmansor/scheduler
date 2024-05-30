from django.urls import path

from webtask_scheduler.scheduler import views

app_name = "scheduler"
urlpatterns = [
    path(
        "timer/",
        view=views.SetTimerAPIView.as_view(),
        name="timer",
    ),
    path(
        "timer/<str:task_id>/",
        view=views.GetTimerAPIView.as_view(),
        name="timer",
    ),
]
