# Ограничитель на длину заголовка:
MAX_NAME_LENGTH = 256

# Ограничитель на длину slug:
MAX_SLUG_LENGTH = 50

# Ограничитель на кол-во выводимых символов в заголовке:
CHAR_OUTPUT_LIMIT = 20

# Роли пользователей:
USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]
