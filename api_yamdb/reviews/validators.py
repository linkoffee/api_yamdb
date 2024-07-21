import re

from django.core.exceptions import ValidationError


def username_validator(value):
    # Проверка на запрещенные слова
    forbidden_values = ('me',)
    if value.lower() in forbidden_values:
        raise ValidationError(f'Недопустимое имя пользователя: {value}')

    # Проверка на запрещенные символы
    forbidden_chars = re.sub(r'^[\w.@+-]+\Z', '', value)
    if forbidden_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {forbidden_chars}')  # Запрещенный символ может повторятся несколько раз в имени, писать его несколько раз не нужно, нужно использовать set и join.

    return value
