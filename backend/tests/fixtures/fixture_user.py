import pytest


@pytest.fixture
def password():
    return 'securepassword'


@pytest.fixture
def user(django_user_model, password):
    return django_user_model.object.create_user(
        email='user@example.com',
        username='exampleuser',
        first_name='John',
        last_name='Doe',
        password=password,
    )


@pytest.fixture
def user_token(user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def user_client(user, token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client
