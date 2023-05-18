from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

from api_yamdb.settings import EMAIL_HOST_USER
from reviews.models import User


def send_email(data):
    email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],),
            from_email=EMAIL_HOST_USER
        )
    email.send()


def send_conf_code(username):
    user = User.objects.get(username=username)
    confirmation_code = default_token_generator.make_token(user)
    email_body = (
        f'Здравствуйте, {user.username}.'
        f'\nВаш код подтверждения для API: {confirmation_code}'
    )
    data = {
            'email_subject': 'Код подтверждения для доступа к API.',
            'email_body': email_body,
            'to_email': user.email,
            }
    send_email(data)
