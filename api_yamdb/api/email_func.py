from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_code_to_email(user):
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтвержения для завершения регистрации',
        f'Ваш код для получения JWT токена {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        (user.email,),
        fail_silently=False,
    )
