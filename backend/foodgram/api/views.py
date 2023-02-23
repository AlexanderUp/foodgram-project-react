from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import CustomOrderedIngredientSearchFilter
from .serializers import (IngredientSerializer, PasswordChangeSerializer,
                          RecipeSerializer, RecipeWriteSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserCreationSerializer, UserListRetrieveSerializer)

from recipes.models import (Ingredient, MeasurementUnit, Recipe,  # isort:skip
                            RecipeIngredient, Tag)

User = get_user_model()


class UserCreateListRetrieveViewSet(mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        action_list = ("list", "retrieve", "me",)
        if self.action in action_list:
            return UserListRetrieveSerializer
        return UserCreationSerializer

    def get_permissions(self):
        action_list = ("list", "create",)
        if self.action in action_list:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def set_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get(  # type:ignore
            "new_password")
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def subcriptions(self, request):
        queryset = request.user.users_followed.all()
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk):
        user_to_subscribe = get_object_or_404(User, pk=pk)
        err_msg = {}

        if user_to_subscribe is request.user:
            err_msg = {"errors": "Can't subscribe to yourself."}

        if request.user.users_followed.filter(pk=user_to_subscribe.pk).exists():
            err_msg = {"errors": "This user is followed already."}

        if err_msg:
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)

        request.user.users_followed.add(user_to_subscribe)
        serializer = SubscriptionSerializer(user_to_subscribe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        user_to_unsubscribe = get_object_or_404(User, pk=pk)
        err_msg = {}

        if not request.user.users_followed.filter(pk=user_to_unsubscribe.pk).exists():
            err_msg = {
                "errors": "Can't unsubscribe from user that is not following."}

        if err_msg:
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)

        request.user.users_followed.remove(user_to_unsubscribe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class TagReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related("measurement_unit").all()
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,
                       CustomOrderedIngredientSearchFilter)
    filterset_fields = ("name",)
    search_fields = ("name",)


class RecipeModelViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete',]

    def get_queryset(self):
        prefetch_ingredients = Prefetch(
            "recipe_ingredients",
            queryset=RecipeIngredient.objects.select_related(
                "ingredient__measurement_unit").all()
        )
        query = (
            Recipe.objects
                  .select_related("author")
                  .prefetch_related("tags")
                  .prefetch_related(prefetch_ingredients)
        )
        return query

    def get_permissions(self):
        action_list = ("list", "retrieve",)
        if self.action in action_list:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        read_actions = ("list", "retrieve",)
        write_actions = ("post", "patch",)
        if self.action in read_actions:
            return RecipeSerializer
        if self.action in write_actions:
            return RecipeWriteSerializer
        return super().get_serializer_class()
