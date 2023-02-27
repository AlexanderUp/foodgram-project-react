from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Prefetch, Q, Value
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import CustomOrderedIngredientSearchFilter
from .pagination_classes import CustomPageSizeLimitPaginationClass
from .permissions import RecipeOwnerPermission
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          PasswordChangeSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, SubscriptionSerializer,
                          TagSerializer, UserCreationSerializer,
                          UserListRetrieveSerializer)

from recipes.models import (Ingredient, Recipe, RecipeIngredient,  # isort:skip
                            Tag)

User = get_user_model()


class UserCreateListRetrieveViewSet(mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    pagination_class = CustomPageSizeLimitPaginationClass

    def get_queryset(self):
        queryset = User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.users_followed.filter(  # type:ignore
                    pk=OuterRef("pk")
                )
            ))
        # Ensure queryset is re-evaluated on each request.
        queryset = queryset.all()
        return queryset

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
    def subscriptions(self, request):
        queryset = request.user.users_followed.all()
        # all users in queryset are followed, no need to annotate with explicit query
        queryset = queryset.annotate(is_subscribed=Value(True))
        paginated_queryset = self.paginate_queryset(queryset)

        recipes_limit = self.request.query_params.get(  # type:ignore
            "recipes_limit")
        context = {}
        if recipes_limit:
            context.update({"recipes_limit": int(recipes_limit)})

        serializer = SubscriptionSerializer(
            paginated_queryset, many=True, context=context
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk):
        user_to_subscribe = get_object_or_404(User, pk=pk)
        err_msg = {}

        if user_to_subscribe == request.user:
            err_msg = {"errors": "Can't subscribe to yourself."}

        if request.user.users_followed.filter(pk=user_to_subscribe.pk).exists():
            err_msg = {"errors": "This user is followed already."}

        if err_msg:
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)

        request.user.users_followed.add(user_to_subscribe)
        # need to refresh annotated field through calling 'self.get_queryset()'
        user_to_subscribe = self.get_object()

        recipes_limit = self.request.query_params.get(  # type:ignore
            "recipes_limit")
        context = {}
        if recipes_limit:
            context.update({"recipes_limit": int(recipes_limit)})
        serializer = SubscriptionSerializer(user_to_subscribe, context=context)
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
    pagination_class = CustomPageSizeLimitPaginationClass
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ("author",)

    def get_queryset(self):
        prefetch_ingredients = Prefetch(
            "recipe_ingredients",
            queryset=RecipeIngredient.objects.select_related(
                "ingredient__measurement_unit").all()
        )

        if self.request.user.is_anonymous:
            authors = User.objects.annotate(is_subscribed=Value(False))
        else:
            authors = User.objects.annotate(
                is_subscribed=Exists(
                    self.request.user.users_followed.filter(  # type:ignore
                        pk=OuterRef("pk")
                    )
                ))
        prefetch_authors = Prefetch("author", queryset=authors)
        query = (
            Recipe.objects
                  .prefetch_related("tags")
                  .prefetch_related(prefetch_authors)
                  .prefetch_related(prefetch_ingredients)
        )

        if self.request.user.is_anonymous:
            query = query.annotate(is_favorited=Value(False))
        else:
            query = query.annotate(
                is_favorited=Exists(
                    self.request.user.favorite_recipes.filter(  # type:ignore
                        pk=OuterRef("pk")
                    ))
            )

        if self.request.user.is_anonymous:
            query = query.annotate(is_in_shopping_cart=Value(False))
        else:
            query = query.annotate(
                is_in_shopping_cart=Exists(
                    self.request.user.shopping_cart.filter(  # type:ignore
                        pk=OuterRef("pk")
                    ))
            )

        tag_slugs = self.request.query_params.getlist("tags")  # type:ignore
        q_object = Q()
        for tag_slug in tag_slugs:
            q_object |= Q(tags__slug=tag_slug)

        is_favorited_param = self.request.query_params.get(  # type:ignore
            "is_favorited", 0)
        is_favorited_param = bool(int(is_favorited_param))
        if is_favorited_param:
            q_object &= Q(is_favorited=is_favorited_param)

        is_in_shopping_cart_param = self.request.query_params.get(  # type:ignore
            "is_in_shopping_cart", 0)
        is_in_shopping_cart_param = bool(int(is_in_shopping_cart_param))
        if is_in_shopping_cart_param:
            q_object &= Q(is_in_shopping_cart=is_in_shopping_cart_param)

        query = query.filter(q_object)
        return query

    def get_permissions(self):
        action_list = ("list", "retrieve",)
        if self.action in action_list:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, RecipeOwnerPermission]
        return [permission() for permission in permissions]

    def get_serializer_class(self):
        read_actions = ("list", "retrieve",)
        write_actions = ("create", "partial_update",)
        if self.action in read_actions:
            return RecipeReadSerializer
        if self.action in write_actions:
            return RecipeWriteSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = RecipeReadSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response_serializer = RecipeReadSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="favorite")
    def favorite_list(self, request):
        serializer = FavoriteRecipeSerializer(
            request.user.favorite_recipes.all(), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        err_msg = {}
        if request.user.favorite_recipes.filter(pk=recipe.pk).exists():
            err_msg.update({"errors": "Recipe already in favorites."})
        if err_msg:
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.favorite_recipes.add(recipe)
        serializer = FavoriteRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        err_msg = {}
        if not request.user.favorite_recipes.filter(pk=recipe.pk).exists():
            err_msg.update({"errors": "No such recipe in favorites."})
        if err_msg:
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.favorite_recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="show_shopping_cart")
    def show_shopping_cart(self, request):
        queryset = request.user.shopping_cart.all()
        serializer = FavoriteRecipeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        pass

    @action(detail=True, methods=["post"])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        err_msg = {}
        if request.user.shopping_cart.filter(pk=recipe.pk).exists():
            err_msg.update({"errors": "Recipe already in shopping_cart."})
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.shopping_cart.add(recipe)
        serializer = FavoriteRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        err_msg = {}
        if not request.user.shopping_cart.filter(pk=recipe.pk).exists():
            err_msg.update({"errors": "No such recipe in shopping cart."})
            return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)
        request.user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
