import pytest

from tests.test_apps.conftest import RegistrationData


@pytest.mark.django_db()
def test_valid_registration(
    create_new_user: RegistrationData,
) -> None:
    """Check user registration."""


@pytest.mark.django_db()
def test_valid_login(
    login: RegistrationData,
) -> None:
    """Check user login."""
