from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


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
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name="tags",
        help_text="Recipe's tags",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Author",
        help_text="Author of the recipe",
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through="RecipeIngredient",
        # related_name="ingredient_recipes",
        verbose_name="ingredients",
        help_text="Ingredients used",
    )
    name = models.CharField(
        verbose_name="Name",
        help_text="Recipe's name",
        max_length=200,
    )
    image = models.FileField(
        upload_to="recipe_images",
        verbose_name="image",
        help_text="Recipe image",
    )
    text = models.TextField(
        verbose_name="Text",
        help_text="Recipe description",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Cooking time",
        help_text="Time of recipe cooking",
        validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-pk",)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="recipe",
        help_text="Recipe, using this ingredient",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="ingredient",
        help_text="Ingredient, used in recipe",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="amount",
        help_text="Ingredient amount used",
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = "RecipeIngredient"
        verbose_name_plural = "RecipeIngredients"
        ordering = ("pk",)

    def __str__(self):
        return f"{self.recipe}-({self.ingredient})-({self.amount})"
