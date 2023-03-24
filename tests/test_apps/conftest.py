import datetime as dt
from http import HTTPStatus
from typing import Callable, TypeAlias, TypedDict, final

import pytest
from django.test import Client
from django.urls import reverse
from mimesis import Field, Schema
from mimesis.enums import Locale

from server.apps.identity.models import User


@final
class RegistrationData(TypedDict, total=False):
    """Represent the user data that is required to create a new user."""

    email: str
    first_name: str
    last_name: str
    date_of_birth: dt.datetime
    address: str
    job_title: str
    phone: str
    phone_type: int
    # Special:
    password1: str
    password2: str


@pytest.fixture()
def registration_data(faker_seed: int) -> RegistrationData:
    """Generate registration data."""
    mf = Field(locale=Locale.RU, seed=faker_seed)
    password = mf('password')  # by default passwords are equal
    schema = Schema(schema=lambda: {
        'email': mf('person.email'),
        'first_name': mf('person.first_name'),
        'last_name': mf('person.last_name'),
        'date_of_birth': mf('datetime.date'),
        'address': mf('address.city'),
        'job_title': mf('person.occupation'),
        'phone': mf('person.telephone'),
    })
    return {
        **schema.create(iterations=1)[0],  # type: ignore[misc]
        **{'password1': password, 'password2': password},
    }


@final
class UserData(TypedDict, total=False):
    """Represent the user data that is required to create a new user."""

    email: str
    first_name: str
    last_name: str
    date_of_birth: dt.datetime
    address: str
    job_title: str
    phone: str


@pytest.fixture()
def new_user_data(faker_seed: int, user_data: UserData) -> UserData:
    """Create user data for update."""
    mf = Field(locale=Locale.RU, seed=faker_seed)
    schema = Schema(schema=lambda: {
        'email': user_data['email'],
        'first_name': mf('person.first_name'),
        'last_name': mf('person.last_name'),
        'date_of_birth': mf('datetime.date'),
        'address': mf('address.city'),
        'job_title': mf('person.occupation'),
        'phone': mf('person.telephone'),
    })
    return {
        **schema.create(iterations=1)[0],
    }


@final
class LoginData(TypedDict, total=False):
    """Represent the simplified login data."""

    username: str
    password: str


@pytest.fixture()
def login_data(registration_data) -> LoginData:
    """Login data from``registration_data``."""
    return {
        'username': registration_data['email'],
        'password': registration_data['password1'],
    }


@pytest.fixture()
def user_data(registration_data) -> UserData:
    """We need to simplify registration data to drop passwords."""
    return {  # type: ignore[return-value]
        key_name: value_part
        for key_name, value_part in registration_data.items()
        if not key_name.startswith('password')
    }


UserAssertion: TypeAlias = Callable[[str, UserData], None]


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    """Check that user created correctly."""

    def factory(email: str, expected: UserData) -> None:
        user = User.objects.get(email=email)
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            assert getattr(user, field_name) == data_value

    return factory


@pytest.mark.django_db()
@pytest.fixture()
def create_new_user(
    client: Client,
    registration_data: RegistrationData,
    user_data: UserData,
    assert_correct_user: UserAssertion,
) -> RegistrationData:
    """Create new user."""
    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:login')

    assert_correct_user(registration_data['email'], user_data)

    return registration_data


@pytest.mark.django_db()
@pytest.fixture()
def login(
    client: Client,
    create_new_user: RegistrationData,
    login_data: LoginData,
) -> RegistrationData:
    """Login as valid user."""
    response = client.post(
        reverse('identity:login'),
        data=login_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('pictures:dashboard')

    return create_new_user
