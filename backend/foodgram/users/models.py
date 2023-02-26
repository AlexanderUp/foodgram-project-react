from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe  # isort:skip


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="email",
        help_text="User's email",
        unique=True,
    )
    favorite_recipes = models.ManyToManyField(
        to=Recipe,
        related_name="following_users",
        verbose_name="favorite_recipes",
        help_text="Recipes followed by user",
    )
    users_followed = models.ManyToManyField(
        to="self",
        symmetrical=False,
    )
    shopping_cart = models.ManyToManyField(
        to=Recipe,
        related_name="shopping_carts",
        verbose_name="shopping_cart",
        help_text="Recipes to be shopped",
    )

    class Meta(AbstractUser.Meta):
        ordering = ("pk",)
