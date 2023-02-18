from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="name",
        help_text="Tag's name",
        max_length=20,
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
        max_length=20,
        unique=True,
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("pk",)

    def __str__(self):
        return self.name
