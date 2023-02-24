# Generated by Django 4.1.7 on 2023-02-21 13:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_recipe_recipeingredient_recipe_ingredients_and_more'),
        ('users', '0002_alter_user_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_subscribed',
        ),
        migrations.AddField(
            model_name='user',
            name='favorite_recipes',
            field=models.ManyToManyField(help_text='Recipes followed by user', related_name='following_users', to='recipes.recipe', verbose_name='favorite_recipes'),
        ),
        migrations.AddField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(help_text='Recipes to be shopped', related_name='shopping_carts', to='recipes.recipe', verbose_name='shopping_cart'),
        ),
        migrations.AddField(
            model_name='user',
            name='users_followed',
            field=models.ManyToManyField(help_text='Users that are followed', related_name='favorite_users', to=settings.AUTH_USER_MODEL, verbose_name='users_followed'),
        ),
    ]