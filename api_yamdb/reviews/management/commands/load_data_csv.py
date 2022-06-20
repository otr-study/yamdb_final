import csv
from os import path

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from reviews.models import (Categories, Comment, Genres, Review, Title,
                            TitlesGenres, User)

PRESET = (
    ('users.csv', User,),
    ('genre.csv', Genres,),
    ('category.csv', Categories,),
    ('titles.csv', Title,),
    ('genre_title.csv', TitlesGenres,),
    ('review.csv', Review,),
    ('comments.csv', Comment,),
)

FIELDS_TO_CONVERT_NAME = {
    'author': 'author_id',
    'category': 'category_id',
}


class Command(BaseCommand):
    help = "Loads data from CSV files."

    def add_arguments(self, parser):
        parser.add_argument("catalog_path", type=str)

    def handle(self, *args, **options):
        catalog_path = options["catalog_path"]
        for filename, cls in PRESET:
            ids = [elem['id'] for elem in cls.objects.all().values('id')]
            with open(path.join(catalog_path, filename), 'r') as csv_file:
                data = csv.reader(csv_file, delimiter=",")
                objects = []
                header = data.__next__()
                for row in data:
                    if int(row[0]) in ids:
                        continue
                    param = self.get_model_params(header, row)
                    objects.append(cls(**param))
                if objects:
                    cls.objects.bulk_create(objects)

    def get_model_params(self, header, values):
        keys = [self.convert_key(key) for key in header]
        return {
            key: self.convert_value(key, value) for key, value in zip(
                keys,
                values
            )
        }

    def convert_key(self, key):
        if key in FIELDS_TO_CONVERT_NAME:
            return FIELDS_TO_CONVERT_NAME[key]
        return key

    def convert_value(self, key, value):
        if key == 'pub_date':
            return parse_datetime(value)
        return value
