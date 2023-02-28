# Generated by Django 4.1.7 on 2023-02-28 10:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_options_recipe_publication_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(help_text='Recipe image', upload_to='recipe_images', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='publication_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Date of publication', verbose_name='Publication date'),
        ),
    ]
