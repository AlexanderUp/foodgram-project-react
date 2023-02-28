import csv

from recipes.models import Ingredient, MeasurementUnit, Tag


def process_tags(path_to_file):
    tags = []
    with open(path_to_file) as source:
        header = None
        reader = csv.reader(source)
        for row in reader:
            if not header:
                header = row
                continue
            tag = Tag(**dict(zip(header, row)))
            tags.append(tag)
    Tag.objects.bulk_create(tags, ignore_conflicts=True)


def process_ingredients(path_to_file):
    measurement_unit_names = set()
    raw_ingredients = []
    ingredients = []

    with open(path_to_file) as source:
        reader = csv.reader(source)
        for row in reader:
            measurement_unit_name = row[-1]
            measurement_unit_names.add(
                measurement_unit_name
            )

            raw_ingredients.append(row)

        measurement_units = [MeasurementUnit(
            name=unit_name) for unit_name in measurement_unit_names]

        MeasurementUnit.objects.bulk_create(
            measurement_units, ignore_conflicts=True)

        unit_query = MeasurementUnit.objects.all()

        for raw_ingredient in raw_ingredients:
            measurement_unit_name = raw_ingredient[-1]
            measurement_unit = unit_query.get(name=measurement_unit_name)
            ingredients.append(Ingredient(
                name=raw_ingredient[0], measurement_unit=measurement_unit))

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
