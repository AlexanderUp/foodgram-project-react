from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets

from .serializers import UserCreationSerializer, UserListRetrieveSerializer

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
