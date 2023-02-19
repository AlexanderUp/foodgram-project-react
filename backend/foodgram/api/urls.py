from django.urls import include, path
from djoser import views as djoser_views
from rest_framework import routers

from .views import (CustomTokenCreateView, IngredientReadOnlyViewSet,
                    TagReadOnlyViewSet, UserCreateListRetrieveViewSet)

router = routers.DefaultRouter()
router.register(r"users", UserCreateListRetrieveViewSet)
router.register(r"tags", TagReadOnlyViewSet)
router.register(r"ingredients", IngredientReadOnlyViewSet)

app_name = "api"

urlpatterns = [
    path(
        "auth/token/login/",
        CustomTokenCreateView.as_view(),
        name="login"
    ),
    path(
        "auth/token/logout/",
        djoser_views.TokenDestroyView.as_view(),
        name="logout"
    ),
    path("", include(router.urls)),
]
