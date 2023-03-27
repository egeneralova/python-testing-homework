from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.test_apps.conftest import LoginData, RegistrationData, UserAssertion


@pytest.mark.django_db()
def test_valid_registration(
    client: Client,
    registration_data: RegistrationData,
    assert_correct_user: UserAssertion,
) -> None:
    """Check user registration."""
    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:login')
    assert_correct_user(registration_data)


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

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('pictures:dashboard')
