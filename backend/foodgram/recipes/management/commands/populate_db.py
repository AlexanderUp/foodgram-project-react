from django.conf import settings
from django.core.management.base import BaseCommand

from ._utils import process_ingredients, process_tags

PATH_TO_TAG_CSV_FILE = settings.BASE_DIR.parent.parent / "data" / "tags.csv"
PATH_TO_INGREDIENT_CSV_FILE = (
    settings.BASE_DIR.parent.parent / "data" / "ingredients.csv")


class Command(BaseCommand):
    help = "Populate db with initial data."

    def handle(self, *args, **options):
        self.stdout.write("Commence populate DB with initial data...")
        self.stdout.write("Populating DB with tags...")
        process_tags(PATH_TO_TAG_CSV_FILE)
        self.stdout.write("Tags processed!")

        self.stdout.write(
            "Populating DB with measurement units and ingredients...")
        process_ingredients(PATH_TO_INGREDIENT_CSV_FILE)
        self.stdout.write("Measurement units and ingredients processed!")

        self.stdout.write("DB successfully populated!")
