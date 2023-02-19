from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="name",
        help_text="Tag's name",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="color",
        help_text="Tag's color",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="Tag's slug",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("pk",)

    def __str__(self):
        return self.name


class MeasurementUnit(models.Model):
    name = models.CharField(
        verbose_name="name",
        help_text="Measurement unit name",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Measurement Unit"
        verbose_name_plural = "Measurement Units"
        ordering = ("pk",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="name",
        help_text="Ingredient name",
        max_length=200,
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="measurement_unit",
        help_text="Ingredient measurement unit",
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        ordering = ("pk",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_name_measurement_unit",
            ),
        )

    def __str__(self):
        return self.name


# class ShoppingCart(models.Model):
#     # recipes
#     pass


# class Recipe(models.Model):
#     autor = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="recipes",
#         verbose_name="author",
#         help_text="Author of the recipe",
#     )
#     name = models.CharField(
#         verbose_name="name",
#         help_text="Recipe's name",
#         max_length=200,
#     )
#     text = models.CharField(
#         verbose_name="text",
#         help_text="Recipe description",
#         max_length=2000,
#     )
#     # ingredients =
#     cooking_time = models.PositiveSmallIntegerField(
#         verbose_name="cooking_time",
#         help_text="Time of recipe cooking",
#         validators=(MinValueValidator(1),)
#     )
#     # image =
#     # tags =
#     # favorited_by =
#     # shopping_cart =


# class RecipeIngredient(models.Model):
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name="recipe_ingredients",
#         verbose_name="recipe",
#         help_text="Recipe in that ingredient is used",
#     )
#     ingredient = models.ForeignKey(
#         Ingredient,
#         on_delete=models.CASCADE,
#         related_name="recipes",  # to be checked
#         verbose_name="ingredient",
#         help_text="Ingredient name",
#     )
#     amount = models.PositiveSmallIntegerField(
#         verbose_name="amount",
#         help_text="Ingredient amount",
#     )

#     class Meta:
#         verbose_name = "Recipe Ingredient"
#         verbose_name_plural = "Recipe Ingredients"
#         ordering = ("pk",)

#     def __str__(self):
#         return f"{self.recipe}-{self.ingredient}-{self.amount}"
