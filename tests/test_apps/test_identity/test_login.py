from http import HTTPStatus

import pytest
from django.contrib import auth
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.plugins.identity.user import LoginData


@pytest.mark.django_db()
def test_valid_login(
    client: Client,
    create_new_user: User,
    login_data: LoginData,
) -> None:
    """Check user login."""
    response = client.post(
        reverse('identity:login'),
        data=login_data,
    )
    user = auth.get_user(client)

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('pictures:dashboard')
    assert user.is_authenticated
