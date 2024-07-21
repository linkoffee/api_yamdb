import uuid

from django.core.mail import send_mail
# Лишняя пустая строка.
from django.conf import settings


def send_code_to_email(user):
    confirmation_code = str(uuid.uuid3(uuid.NAMESPACE_DNS, user.username))
    user.confirmation_code = confirmation_code
    send_mail(
        'Код подтвержения для завершения регистрации',
        f'Ваш код для получения JWT токена {user.confirmation_code}',
        settings.EMAIL_ADMIN,  # Для этого в settings есть специально предусмотренная константа, переопределять нужно её, а не придумывать свою.
        [user.email],
        fail_silently=False,
    )
    user.save()  # Зачем эта строка в функции отправки сообщения? Нужно разделять ответственность, если эта функция для отправки, она должна только отправлять.
