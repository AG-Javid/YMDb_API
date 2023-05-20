import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            'Имя "me" использовать нельзя.'
        )
    match = re.match(r'^[\w@.+-]+$', username)
    if match is None or match.group() != username:
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы.'
        )
    return username
