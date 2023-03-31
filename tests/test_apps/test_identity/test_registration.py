from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.plugins.identity.user import UserAssertion, UserData


@pytest.mark.django_db()
def test_valid_registration(
    client: Client,
    registration_data: UserData,
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


@pytest.mark.parametrize('field', User.OPTIONAL)
@pytest.mark.django_db()
def test_empty_optional_field_registration(
    client: Client,
    user_factory,
    faker_seed,
    field: str,
    assert_correct_user: UserAssertion,
) -> None:
    """Check user registration with empty optional fields."""
    registration_data = user_factory(faker_seed, **{field: ''})

    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:login')
    assert_correct_user(registration_data)


@pytest.mark.django_db()
@pytest.mark.parametrize('field', User.REQUIRED_FIELDS + [User.USERNAME_FIELD])
def test_empty_required_field_registration(
    client: Client,
    user_factory,
    faker_seed,
    field: str,
) -> None:
    """Check required field for user registration."""
    registration_data = user_factory(faker_seed, **{field: ''})

    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors == {field: ['Обязательное поле.']}
    assert not User.objects.filter(email=registration_data['email'])


@pytest.mark.django_db()
def test_create_user_without_email() -> None:
    """Check that user should have email."""
    with pytest.raises(ValueError, match='Users must have an email address'):
        User.objects.create_user('', '')
