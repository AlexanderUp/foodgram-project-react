from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import \
    validate_password as user_validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from recipes.models import Ingredient, Tag  # isort:skip

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

    def validate_password(self, value):
        user_validate_password(value)
        return value

    def validate(self, data):
        if User.objects.filter(
            email=data.get("email"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        ).exists():
            raise ValidationError(
                "User whis given credentials already exists!")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        with transaction.atomic():
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
        user_validate_password(value)
        return value

    def validate(self, data):
        new_password = data.get("new_password")
        current_password = data.get("current_password")
        if new_password == current_password:
            raise ValidationError(
                "You try to use current password as new password!")
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField()

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
