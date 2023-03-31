from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.plugins.identity.user import UserAssertion, UserData
from tests.test_apps.conftest import MessageAssertion


@pytest.mark.django_db()
def test_user_update(
    client: Client,
    login: User,
    new_user_data: UserData,
    assert_correct_user: UserAssertion,
    assert_correct_form_message: MessageAssertion,
) -> None:
    """Check that user info updated correctly."""
    response = client.post(
        reverse('identity:user_update'),
        data=new_user_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:user_update')

    response = client.get(
        reverse('identity:user_update'),
    )
    assert response.status_code == HTTPStatus.OK
    assert_correct_form_message(
        response.wsgi_request,
        ['Ваши данные сохранены'],
    )


@pytest.mark.django_db()
def test_no_messages_before_user_update(
    client: Client,
    login: User,
    assert_correct_form_message: MessageAssertion,
) -> None:
    """Check that user info updated correctly."""
    response = client.get(
        reverse('identity:user_update'),
    )
    assert response.status_code == HTTPStatus.OK
    assert_correct_form_message(response.wsgi_request, [])
