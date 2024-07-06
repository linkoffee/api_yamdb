import os
import csv
import json

from reviews import models


# Путь до директории с csv-файлами:
DIR_PATH = 'api_yamdb/static/data'

# Файл конфигурации импорта:
CONFIG_FILE = 'api_yamdb/json/import_data_config.json'


def import_data_from_csv(file_path, model, fields_mapping):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data = {
                fields_mapping[index]: value for index, value in enumerate(row)
            }
            model.objects.create(**data)


def main():
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)

    for file_name in os.listdir(DIR_PATH):
        if file_name.endswith('.csv'):
            file_path = os.path.join(DIR_PATH, file_name)
            model_name = file_name.split('.')[0]
            model_data = config.get(model_name)
            if model_data:
                model = getattr(models, model_data['model'])
                fields_mapping = model_data['fields_mapping']
                import_data_from_csv(file_path, model, fields_mapping)


if __name__ == '__main__':
    main()
