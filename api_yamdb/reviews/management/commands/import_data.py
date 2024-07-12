import os
import csv
import json
import logging
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from reviews import models

# Путь до директории с csv-файлами:
DIR_PATH = 'static/data'

# Файл конфигурации импорта:
CONFIG_FILE = 'json/import_data_config.json'

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


def get_instance(model, pk):
    """
    Получает экземпляр модели по первичному ключу.
    Возвращает None и логирует ошибку, если экземпляр не найден.
    """
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        logger.error(
            f'Instance of model {model.__name__} with pk {pk} does not exist.')
        return None


def transform_row_to_data(row, fields_mapping, model):
    """
    Преобразует строку CSV в словарь данных для модели.
    Обрабатывает внешние ключи, такие как `category`.
    """
    data = {}
    for key, value in row.items():
        if key in fields_mapping:
            field_name = fields_mapping[key]
            if field_name == 'category' and model == models.Title:
                data['category'] = get_instance(models.Category, value)
            elif field_name == 'genre' and model == models.Title:
                genres = [get_instance(models.Genre, genre_id)
                          for genre_id in value.split(',')]
                data['genre'] = [
                    genre for genre in genres if genre is not None
                ]
            else:
                data[field_name] = value
    return data


def process_csv_row(row, fields_mapping, model, unique_field):
    """
    Обрабатывает одну строку CSV, преобразуя её в данные модели.
    Выполняет вставку или обновление записи.
    """
    data = transform_row_to_data(row, fields_mapping, model)
    if None not in data.values() or 'genre' in data:
        try:
            instance, created = model.objects.update_or_create(
                **{unique_field: data[unique_field]},
                defaults={k: v for k, v in data.items() if k != 'genre'}
            )
            if 'genre' in data:
                instance.genre.set(data['genre'])
                instance.save()
        except IntegrityError as e:
            logger.error(f'IntegrityError importing data from CSV row: {e}')


def import_data_from_csv(file_path, model, fields_mapping):
    """
    Читает CSV-файл и обрабатывает каждую строку.
    Вызывая process_csv_row.
    """
    unique_field = fields_mapping.pop(
        'unique_field')
    try:
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                process_csv_row(row, fields_mapping, model, unique_field)
    except KeyError as e:
        logger.error(f'KeyError importing data from {file_path}: {e}')
    except Exception as e:
        logger.error(f'Error importing data from {file_path}: {e}')


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

    def handle(self, *args, **options):
        try:
            # Логирование текущей директории
            current_directory = os.getcwd()
            logger.info(f'Current working directory: {current_directory}')

            # Абсолютный путь к файлу конфигурации
            config_file_path = os.path.join(current_directory, CONFIG_FILE)
            logger.info(f'Configuration file path: {config_file_path}')

            with open(config_file_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)

            for file_name in os.listdir(DIR_PATH):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(DIR_PATH, file_name)
                    model_name = file_name.split('.')[0].lower()
                    model_data = config.get(model_name)
                    if model_data:
                        model = getattr(models, model_data['model'])
                        fields_mapping = model_data['fields_mapping']
                        import_data_from_csv(file_path, model, fields_mapping)
                    else:
                        logger.warning(
                            f'No configuration found for model {model_name}'
                        )
            self.stdout.write(self.style.SUCCESS('Data imported successfully'))
        except Exception as e:
            logger.error(f'Error during the import process: {e}')
            self.stdout.write(self.style.ERROR('Data import failed'))
