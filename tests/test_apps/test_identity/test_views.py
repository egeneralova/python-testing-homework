from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db()
@pytest.mark.parametrize('page', [
    '',
    reverse('identity:registration'),
    reverse('identity:login'),
])
def test_identify_pages_unauthorized(client: Client, page: str) -> None:
    """Check that identify pages are accessible for unauthorized user."""
    response = client.get(page)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
@pytest.mark.parametrize('page', [
    reverse('pictures:dashboard'),
    reverse('pictures:favourites'),
    reverse('identity:user_update'),
])
def test_pages_redirect_unauthorized(client: Client, page: str) -> None:
    """Check that unauthorized user will be redirected to login page."""
    response = client.get(page)

    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == '{0}?next={1}'.format(
        reverse('identity:login'),
        page,
    )
