import datetime as dt
from typing import Callable, Optional, TypedDict, final

import pytest
from django.test import Client
from mimesis import Field, Schema
from mimesis.enums import Locale
from typing_extensions import TypeAlias

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
    password: str
    password1: Optional[str]
    password2: Optional[str]


@final
class LoginData(TypedDict, total=False):
    """Represent the simplified login data."""

    username: str
    password: str


@pytest.fixture()
def user_factory():
    """Generate registration data."""

    def factory(faker_seed, **fields) -> RegistrationData:
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
            **{'password': password},
            **fields,
        }

    return factory


@pytest.fixture()
def user_data(user_factory, faker_seed):
    """Random user data from factory."""
    return user_factory(faker_seed)


@pytest.fixture()
def registration_data(user_data: RegistrationData) -> RegistrationData:
    """User data."""
    user_data['password1'] = user_data['password']
    user_data['password2'] = user_data['password']

    return user_data


@pytest.fixture()
def login_data(user_data: RegistrationData) -> LoginData:
    """Login data from``registration_data``."""
    return {
        'username': user_data['email'],
        'password': user_data['password'],
    }


@pytest.fixture()
def new_user_data(user_factory, registration_data: RegistrationData):
    """New user data from factory."""
    test = user_factory(1)
    test['email'] = registration_data['email']
    return test


UserAssertion: TypeAlias = Callable[[RegistrationData], None]


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    """Check that user created correctly."""

    def factory(expected: RegistrationData) -> None:
        user = User.objects.get(email=expected['email'])
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            if not field_name.startswith('password'):
                assert getattr(user, field_name) == data_value

    return factory


@pytest.mark.django_db()
@pytest.fixture()
def create_new_user(user_data: RegistrationData) -> User:
    """Create new user."""
    user = User(**user_data)
    user.set_password(user_data['password'])
    user.save()

    return user


@pytest.mark.django_db()
@pytest.fixture()
def login(client: Client, create_new_user: User) -> User:
    """Login as valid user."""
    client.force_login(create_new_user)

    return create_new_user
