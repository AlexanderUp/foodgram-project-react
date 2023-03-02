from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient  # isort:skip


def add_ingredients_to_recipe(recipe, ingredient_data):
    recipe_ingredients = []
    for ingredient_dict in ingredient_data:
        ingredient = ingredient_dict["id"]
        amount = ingredient_dict["amount"]
        recipe_ingredient = RecipeIngredient(
            recipe=recipe, ingredient=ingredient, amount=amount
        )
        recipe_ingredients.append(recipe_ingredient)
    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def get_annotated_recipe_instance(serializer, request):
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    instance.author.is_subscribed = request.user.users_followed.filter(
        pk=instance.author.pk).exists()
    instance.is_favorited = request.user.favorite_recipes.filter(
        pk=instance.pk).exists()
    instance.is_in_shopping_cart = request.user.shopping_cart.filter(
        pk=instance.pk).exists()
    return instance


def get_shopping_cart_ingredient_list_string(ingredients):
    strings = []
    strings.append("Ingredient, amount")
    strings.append("------------------")

    for ingredient in ingredients:
        name = ingredient.get("ingredient_name")
        amount = ingredient.get("total_amount")
        line = f"{name.capitalize()}, {amount}"  # type:ignore
        strings.append(line)
    return "\n".join(strings)


def process_recipe_for_favorite(pk, request, serializer_class):
    recipe = get_object_or_404(Recipe, pk=pk)
    err_msg = {}

    if request.method == "post":
        if not request.user.shopping_cart.filter(pk=recipe.pk).exists():
            request.user.shopping_cart.add(recipe)
            serializer = serializer_class(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        err_msg.update({"errors": "Recipe already in shopping_cart."})

    if request.method == "delete":
        if request.user.shopping_cart.filter(pk=recipe.pk).exists():
            request.user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        err_msg.update({"errors": "No such recipe in shopping cart."})

    return Response(err_msg, status=status.HTTP_400_BAD_REQUEST)
