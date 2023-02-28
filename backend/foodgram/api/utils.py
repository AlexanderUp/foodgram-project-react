from recipes.models import RecipeIngredient


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
