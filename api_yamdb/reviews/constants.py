from django.utils import timezone

# Ограничитель на длину заголовка:
MAX_NAME_LENGTH = 256

# Ограничитель длинны почты:
EMAIL_LENGTH = 254

# Ограничитель имён пользователей:
USERNAME_LENGTH = 150

# Ограничитель на длину slug:
MAX_SLUG_LENGTH = 50

# Ограничитель на кол-во выводимых символов в заголовке:
CHAR_OUTPUT_LIMIT = 20

# Минимальный год для успешной валидации:
MIN_YEAR = 0

# Максимальный год для успешной валидации:
CURRENT_YEAR = timezone.now().year

# Минимальная возможная оценка произведения:
MIN_SCORE = 1

# Максимальная возможная оценка произведения:
MAX_SCORE = 10

# Роли пользователей:
USER = 'user'  # падает всё почти
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = (
    (USER, USER),  # Правую часть нужно русифицировать.
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
)
