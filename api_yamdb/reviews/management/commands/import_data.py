import os
import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from reviews import models

# Путь до директории с csv-файлами
CSV_DIR_PATH = 'static/data/'

# Поля, которые являются внешними ключами
FOREIGN_KEY_FIELDS = ('author', 'category')

# Словарь соответствий модели и csv-файла
MODEL_AND_CSV_MATCHING = {
    models.User: 'users.csv',
    models.Genre: 'genre.csv',
    models.Category: 'category.csv',
    models.Title: 'titles.csv',
    models.GenreTitle: 'genre_title.csv',
    models.Review: 'review.csv',
    models.Comment: 'comments.csv',
}


class Command(BaseCommand):
    """Пользовательская команда Django для импорта данных из CSV в БД."""

    help = 'Import data from CSV files'

    def handle(self, *args, **kwargs):
        for model, csv_file_name in MODEL_AND_CSV_MATCHING.items():
            csv_file_path = os.path.join(CSV_DIR_PATH, csv_file_name)
            self.stdout.write(
                self.style.NOTICE(f'Starting to process file: {csv_file_path}')
            )

            deleted_count, _ = model.objects.all().delete()
            self.stdout.write(
                self.style.NOTICE(
                    f'Deleted {deleted_count} existing '
                    f'records from model {model.__name__}'
                )
            )

            try:
                with open(
                    csv_file_path, newline='', encoding='utf-8'
                ) as csv_file:
                    self.csv_serializer(csv.DictReader(csv_file), model)
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully processed file: {csv_file_path}'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing file {csv_file_path}: {e}'
                    )
                )
        self.stdout.write(
            self.style.SUCCESS('<===SUCCESSFULLY LOADED ALL DATA INTO DB===>')
        )

    def csv_serializer(self, csv_data, model):
        objects = []
        for row_number, row in enumerate(csv_data, start=1):
            row = self.check_foreign_keys(row, model, row_number)
            if row is not None:
                try:
                    objects.append(model(**row))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            'Error creating model instance '
                            f'from row {row_number}: {e}'
                        ))

        self.bulk_create_objects(model, objects)

    def check_foreign_keys(self, row, model, row_number):
        """Проверяет, существуют ли внешние ключи в строке данных."""
        for field in model._meta.fields:
            if field.name in row and field.related_model:
                related_model = field.related_model
                try:
                    row[f'{field.name}_id'] = related_model.objects.get(
                        id=row.pop(field.name)).id
                except related_model.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error: {related_model.__name__} with id '
                            f'{row[field.name]} does not '
                            f'exist (row {row_number})'
                        ))
                    return None
        return row

    def bulk_create_objects(self, model, objects):
        """Создает объекты модели в базе данных."""
        self.stdout.write(
            self.style.NOTICE(
                f'Preparing to bulk create {len(objects)} '
                f'objects for model {model.__name__}'
            ))

        try:
            with transaction.atomic():
                model.objects.bulk_create(objects)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully bulk created {len(objects)} '
                    f'objects for model {model.__name__}'
                ))
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(
                    'Integrity error bulk creating objects '
                    f'for model {model.__name__}: {e}'
                ))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    'Error bulk creating objects '
                    f'for model {model.__name__}: {e}'
                ))

        created_count = model.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'{created_count} objects now exist in the '
                f'database for model {model.__name__}'
            ))
