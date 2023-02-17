from django.contrib.auth import get_user_model
from djoser.views import TokenCreateView
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (PasswordChangeSerializer, UserCreationSerializer,
                          UserListRetrieveSerializer)

User = get_user_model()


class UserCreateListRetrieveViewSet(mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return UserListRetrieveSerializer
        return UserCreationSerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "create":
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]
        return [permission() for permission in permissions]

    @action(detail=False, methods=["get"], url_path="me")
    def user_profile(self, request):
        serializer = UserListRetrieveSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="set_password")
    def set_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data.get(  # type:ignore
            "current_password")
        if request.user.check_password(current_password):
            new_password = serializer.validated_data.get(  # type:ignore
                "new_password")
            request.user.set_password(new_password)
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        err_msg = {"current_password": "Wrong password."}
        return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenCreateView(TokenCreateView):

    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response
