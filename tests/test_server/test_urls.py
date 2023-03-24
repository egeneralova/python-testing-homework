from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db()
def test_health_check(client: Client) -> None:
    """This test ensures that health check is accessible."""
    response = client.get('/health/')

    assert response.status_code == HTTPStatus.OK


def test_admin_unauthorized(client: Client) -> None:
    """This test ensures that admin panel requires auth."""
    response = client.get('/admin/')

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
def test_admin_authorized(admin_client: Client) -> None:
    """This test ensures that admin panel is accessible."""
    response = admin_client.get('/admin/')

    assert response.status_code == HTTPStatus.OK


def test_admin_docs_unauthorized(client: Client) -> None:
    """This test ensures that admin panel docs requires auth."""
    response = client.get('/admin/doc/')

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
def test_admin_docs_authorized(admin_client: Client) -> None:
    """This test ensures that admin panel docs are accessible."""
    response = admin_client.get('/admin/doc/')

    assert response.status_code == HTTPStatus.OK
    assert b'docutils' not in response.content


@pytest.mark.parametrize('page', [
    '/robots.txt',
    '/humans.txt',
])
def test_specials_txt(client: Client, page: str) -> None:
    """This test ensures that special `txt` files are accessible."""
    response = client.get(page)

    assert response.status_code == HTTPStatus.OK
    assert response.get('Content-Type') == 'text/plain'


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
    assert response.get('Location') == '/identity/login?next={0}'.format(page)
