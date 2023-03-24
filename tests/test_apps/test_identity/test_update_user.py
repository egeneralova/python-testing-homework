from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from tests.test_apps.conftest import RegistrationData, UserAssertion, UserData


@pytest.mark.django_db()
def test_user_update(
    client: Client,
    login: RegistrationData,
    new_user_data: UserData,
    assert_correct_user: UserAssertion,
) -> None:
    """Check that user info updated correctly."""
    response = client.post(
        reverse('identity:user_update'),
        data=new_user_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:user_update')

    assert_correct_user(login['email'], new_user_data)
