from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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
        fields = (UserCustomBaseSerializer.Meta.fields
                  + ("is_subscribed",))  # type:ignore


class UserCreationSerializer(UserCustomBaseSerializer):
    class Meta(UserCustomBaseSerializer.Meta):
        fields = (UserCustomBaseSerializer.Meta.fields
                  + ("password",))  # type:ignore
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


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label="new_password",
        help_text="New password",
        style={"input_type": "password"},
        max_length=150,
    )
    current_password = serializers.CharField(
        label="current_password",
        help_text="Current password",
        style={"input_type": "password"},
        max_length=150,
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        new_password = data.get("new_password")
        current_password = data.get("current_password")
        if new_password == current_password:
            raise ValidationError(
                "You try to use current password as new password!")
        return data
