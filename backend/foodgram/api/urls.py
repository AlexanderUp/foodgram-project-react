from django.urls import include, path
from rest_framework import routers

from .views import UserCreateListRetrieveViewSet

router = routers.DefaultRouter()
router.register(r"users", UserCreateListRetrieveViewSet)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
]
