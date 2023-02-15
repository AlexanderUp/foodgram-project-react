from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
