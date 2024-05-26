from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

API_V1 = "v1"
app_name = "api"
api_v1_urlpatterns = [
    path(
        f"{API_V1}/scheduler/",
        include("webtask_scheduler.scheduler.urls", namespace="scheduler"),
    ),
]
urlpatterns = api_v1_urlpatterns + router.urls
