from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.test_apps.conftest import RegistrationData, UserAssertion


@pytest.mark.django_db()
def test_user_update(
    client: Client,
    login: User,
    new_user_data: RegistrationData,
    assert_correct_user: UserAssertion,
) -> None:
    """Check that user info updated correctly."""
    response = client.post(
        reverse('identity:user_update'),
        data=new_user_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:user_update')

    assert_correct_user(new_user_data)
