import csv

from recipes.models import Tag  # isort:skip


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
