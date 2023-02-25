import base64
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import \
    validate_password as validate_user_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers

from .utils import add_ingredients_to_recipe  # isort:skip
from recipes.models import (Ingredient, Tag, Recipe,  # isort:skip
                            RecipeIngredient)  # isort:skip

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
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserCustomBaseSerializer.Meta):
        fields = (
            *UserCustomBaseSerializer.Meta.fields,
            "is_subscribed",
        )  # type:ignore

    def get_is_subscribed(self, obj):
        return False


class UserCreationSerializer(UserCustomBaseSerializer):
    class Meta(UserCustomBaseSerializer.Meta):
        fields = (
            *UserCustomBaseSerializer.Meta.fields,
            "password",
        )  # type:ignore
        extra_kwargs = {
            "email": {"required": True},
            "id": {"read_only": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"required": True, "write_only": True},
        }

    def validate_password(self, value):
        validate_user_password(value)
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
        return User.objects.create_user(**validated_data)  # type:ignore


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
    current_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_new_password(self, value):
        validate_user_password(value)
        return value

    def validate(self, data):
        new_password = data.get("new_password")
        current_password = data.get("current_password")
        current_user = data.get("current_user")
        if new_password == current_password:
            raise ValidationError(
                "You try to use current password as new password!")
        if not current_user.check_password(current_password):
            raise ValidationError("Wrong password!")
        return data


class Base64EncodedImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, datastr = data.split(";base64,")
            ext = format.split("/")[-1]
            img = base64.b64decode(datastr)
            name = os.urandom(8).hex()
            data = ContentFile(img, name=f"{name}." + ext)
        return super().to_internal_value(data)


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


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit.name")

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount"
        )


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(validators=[MinValueValidator(1),])


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserListRetrieveSerializer()
    ingredients = RecipeIngredientReadSerializer(
        source="recipe_ingredients", many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        pass

    def get_is_in_shopping_cart(self, obj):
        pass


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64EncodedImageField()

    class Meta:
        model = Recipe
        fields = (
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        ingredient_data = validated_data.pop("ingredients")
        tag_ids = validated_data.pop("tags")

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tag_ids)
            add_ingredients_to_recipe(recipe, ingredient_data)
            return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data["image"]
        instance.name = validated_data["name"]
        instance.text = validated_data["text"]
        instance.cooking_time = validated_data["cooking_time"]

        tag_ids = validated_data["tags"]
        ingredient_data = validated_data["ingredients"]

        with transaction.atomic():
            instance.save()
            instance.tags.set(tag_ids, clear=True)

            for ingredient in instance.recipe_ingredients.all():
                ingredient.delete()

            add_ingredients_to_recipe(instance, ingredient_data)
        return instance


class FavoriteRecipeSerializer(RecipeReadSerializer):
    image = serializers.SerializerMethodField()

    class Meta(RecipeReadSerializer.Meta):
        fields = (  # type:ignore
            "id",
            "name",
            "image",
            "cooking_time",
        )

    def get_image(self, obj):
        return obj.image.url


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = FavoriteRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return False

    def get_recipe_count(self, obj):
        return obj.recipes.count()
