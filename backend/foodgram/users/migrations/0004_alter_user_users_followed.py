# Generated by Django 4.1.7 on 2023-02-28 09:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_user_is_subscribed_user_favorite_recipes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='users_followed',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
