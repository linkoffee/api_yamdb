import os
import csv
import logging
from django.core.management.base import BaseCommand

from reviews import models

# Путь до директории с csv-файлами:
CSV_DIR_PATH = 'static/data/'

# Поля, которые являются внешними ключами.
FOREIGN_KEY_FIELDS = ('author', 'category')

# Словарь соответствий модели и csv-файла:
MODEL_AND_CSV_MATCHING = {
    models.Category: 'category.csv',
    models.Comment: 'comments.csv',
    models.Genre: 'genre.csv',
    models.Review: 'review.csv',
    models.Title: 'titles.csv',
    models.User: 'users.csv'
}

# Настройка логирования:
log_file_path = os.path.join(os.path.dirname(__file__), 'import_data.log')

logging.basicConfig(
    level=logging.INFO,
    format=(
        '[%(asctime)s][%(levelname)s][%(message)s][%(filename)s][%(lineno)s]'
    ),
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Пользовательская команда Django.
    --------------------------------
    [1] Перебирает все файлы с расширением .csv в указанной директории.
    [2] Для каждого CSV-файла определяет соответствующую модель.
    [3] Выполняет сопоставление полей из json файла.
    [4] Вызывает функцию import_data_from_csv для импорта данных
    из CSV-файла в соответствующую модель.
    """

    help = 'Import data from CSV files'

    def handle(self, *args, **kwargs):
        for model, csv_file_name in MODEL_AND_CSV_MATCHING.items():
            csv_file_name = CSV_DIR_PATH + csv_file_name
            logger.info(f'Starting to process file: {csv_file_name}')
            try:
                with open(
                    csv_file_name, newline='', encoding='utf-8'
                ) as csv_file:
                    self.csv_serializer(csv.DictReader(csv_file), model)
            except Exception as e:
                logger.error(f'Error processing file {csv_file_name}: {e}')
                self.stdout.write(self.style.ERROR('DATA IMPORT FAILED'))
            logger.info(f'Successfully processed file: {csv_file_name}')
        logger.info('Successfully loaded all data into database')
        self.stdout.write(self.style.SUCCESS('DATA IMPORTED SUCCESSFULLY'))

    def csv_serializer(self, csv_data, model):
        objects = []
        for row_number, row in enumerate(csv_data, start=1):
            for field in model._meta.fields:
                if field.name in row and field.related_model:
                    row[f'{field.name}_id'] = row.pop(field.name)

            try:
                objects.append(model(**row))
            except Exception as e:
                logger.error(
                    'Error creating model instance '
                    f'from row {row_number}: {e}'
                )
        try:
            model.objects.bulk_create(objects)
            logger.info(
                f'Successfully bulk created {len(objects)} '
                f'objects for model {model.__name__}'
            )
        except Exception as e:
            logger.error(
                f'Error bulk creating objects for model {model.__name__}: {e}'
            )
