from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Recipe


@receiver(pre_delete, sender=Recipe)
def delete_recipe_image(sender, instance, **kwargs):
    instance.image.delete()
