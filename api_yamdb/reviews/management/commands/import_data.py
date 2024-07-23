import os
import csv

from django.core.management.base import BaseCommand

from reviews import models

# Путь до директории с csv-файлами
CSV_DIR_PATH = 'static/data/'

# Поля, которые являются внешними ключами
FOREIGN_KEY_FIELDS = ('author', 'category')

# Словарь соответствий модели и csv-файла
MODEL_AND_CSV_MATCHING = {
    models.APIUser: 'users.csv',
    models.Genre: 'genre.csv',
    models.Category: 'category.csv',
    models.Title: 'titles.csv',
    models.Review: 'review.csv',
    models.Comment: 'comments.csv',
}


class Command(BaseCommand):
    """Пользовательская команда Django для импорта данных из CSV в БД."""

    help = 'Load data from csv file into the database'

    def handle(self, *args, **kwargs):
        error_occurred = False
        for model in MODEL_AND_CSV_MATCHING:
            csv_file_path = os.path.join(
                CSV_DIR_PATH, MODEL_AND_CSV_MATCHING[model]
            )
            self.stdout.write(
                self.style.WARNING(
                    f'Starting to process file: {csv_file_path}')
            )
            try:
                with open(
                    csv_file_path, newline='', encoding='utf-8'
                ) as csv_file:
                    self.stdout.write(
                        self.style.WARNING(f'Opened file: {csv_file_path}')
                    )
                    csv_serializer(csv.DictReader(csv_file), model, self)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Finished processing file: {csv_file_path}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing file {csv_file_path}: {e}'
                    )
                )
                error_occurred = True

        if not error_occurred:
            self.stdout.write(
                self.style.SUCCESS('<===SUCCESSFULLY LOADED DATA===>')
            )
        else:
            self.stdout.write(
                self.style.ERROR('<===FAILED TO LOAD DATA===>')
            )


def csv_serializer(csv_data, model, command):
    objs = []
    for row_number, row in enumerate(csv_data, start=1):
        for field in FOREIGN_KEY_FIELDS:
            if field in row:
                row[f'{field}_id'] = row[field]
                del row[field]
        objs.append(model(**row))
    model.objects.bulk_create(objs, ignore_conflicts=True)
    command.stdout.write(
        command.style.SUCCESS(
            f'Successfully bulk created objects for model {model.__name__}'
        )
    )
