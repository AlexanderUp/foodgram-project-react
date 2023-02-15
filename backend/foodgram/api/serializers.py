from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserCustomBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserListRetrieveSerializer(UserCustomBaseSerializer):
    class Meta(UserCustomBaseSerializer.Meta):
        fields = UserCustomBaseSerializer.Meta.fields + \
            ("is_subscribed",)  # type:ignore


class UserCreationSerializer(UserCustomBaseSerializer):
    class Meta(UserCustomBaseSerializer.Meta):
        fields = UserCustomBaseSerializer.Meta.fields + \
            ("password",)  # type:ignore
        extra_kwargs = {
            "email": {"required": True},
            "id": {"read_only": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"required": True, "write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)  # type:ignore
        user.set_password(password)
        user.save()
        return user
