from django.urls import include, path
from djoser import views as djoser_views
from rest_framework import routers

from .views import (CustomTokenCreateView, IngredientReadOnlyViewSet,
                    RecipeModelViewSet, TagReadOnlyViewSet,
                    UserCreateListRetrieveViewSet)

router = routers.DefaultRouter()
router.register(r"users", UserCreateListRetrieveViewSet, basename="User")
router.register(r"tags", TagReadOnlyViewSet)
router.register(r"ingredients", IngredientReadOnlyViewSet)
router.register(r"recipes", RecipeModelViewSet, basename="Recipe")


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
