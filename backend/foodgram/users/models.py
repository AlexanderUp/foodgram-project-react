from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_subscribed = models.BooleanField(
        verbose_name="is_subscribed",
        help_text="Is user subscribed?",
        default=False,
    )

    class Meta(AbstractUser.Meta):
        pass
