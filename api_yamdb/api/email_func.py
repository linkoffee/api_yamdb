import uuid

from django.core.mail import send_mail
from django.conf import settings


def send_code_to_email(user):
    confirmation_code = str(uuid.uuid3(uuid.NAMESPACE_DNS, user.username))
    user.confirmation_code = confirmation_code
    send_mail(
        'Код подтвержения для завершения регистрации',
        f'Ваш код для получения JWT токена {user.confirmation_code}',
        settings.EMAIL,
        [user.email],
        fail_silently=False,
    )
