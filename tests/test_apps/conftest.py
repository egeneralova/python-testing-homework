from typing import Callable

import pytest
from django.contrib.messages import get_messages
from django.core.handlers.wsgi import WSGIRequest
from django.test import Client
from mimesis import Field, Schema
from mimesis.enums import Locale
from typing_extensions import TypeAlias

from server.apps.identity.models import User
from server.apps.pictures.models import FavouritePicture
from tests.plugins.identity.user import LoginData, UserAssertion, UserData
from tests.test_apps.test_pictures.conftest import PictureData


@pytest.fixture()
def picture_factory():
    """Generate picture data."""

    def factory(faker_seed, count) -> list[PictureData]:
        mf = Field(locale=Locale.RU, seed=faker_seed)
        schema = Schema(schema=lambda: {
            'foreign_id': mf('increment'),
            'url': mf('url'),
        })
        return schema.create(iterations=count)  # type: ignore[return-value]

    return factory


@pytest.fixture()
def user_factory():
    """Generate registration data."""

    def factory(faker_seed, **fields) -> UserData:
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
            **fields,
        }

    return factory


@pytest.fixture()
def registration_data(user_factory, faker_seed):
    """Random user data from factory."""
    return user_factory(faker_seed)


@pytest.fixture()
def user_data(registration_data: UserData):
    """User data."""
    return {
        **{
            key_name: value_part
            for key_name, value_part in registration_data.items()
            if not key_name.startswith('password')
        },
        **{'password': registration_data['password1']},
    }


@pytest.fixture()
def login_data(registration_data: UserData) -> LoginData:
    """Login data from``registration_data``."""
    return {
        'username': registration_data['email'],
        'password': registration_data['password1'],
    }


@pytest.fixture()
def new_user_data(user_factory, registration_data: UserData):
    """New user data from factory."""
    test = user_factory(1)
    test['email'] = registration_data['email']
    return test


@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    """Check that user created correctly."""

    def factory(expected: UserData) -> None:
        user = User.objects.get(email=expected['email'])
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            if not field_name.startswith('password'):
                actual = getattr(user, field_name)
                if not actual:
                    actual = ''
                assert actual == data_value
    return factory


@pytest.mark.django_db()
@pytest.fixture()
def create_new_user(user_data: UserData) -> User:
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


@pytest.mark.django_db()
@pytest.fixture(params=[
    1,
    2,
    5,
])
def add_favourite_pictures(
    create_new_user: User,
    picture_factory,
    faker_seed,
    request,
) -> list[FavouritePicture]:
    """Add favourite pictures to user."""
    favorites = [
        FavouritePicture(**fav) for fav in picture_factory(
            faker_seed,
            request.param,
        )
    ]
    for fav in favorites:
        fav.user = create_new_user
        fav.save()

    return favorites


MessageAssertion: TypeAlias = Callable[[WSGIRequest, list[str]], None]


@pytest.fixture(scope='session')
def assert_correct_form_message() -> MessageAssertion:
    """Check that user created correctly."""

    def factory(wsgi_request, expected: list[str]) -> None:
        messages = list(get_messages(wsgi_request))
        assert len(messages) == len(expected)
        for idx, message in enumerate(messages):
            assert str(message) == expected[idx]

    return factory
