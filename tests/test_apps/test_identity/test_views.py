from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from server.apps.identity.models import User
from server.apps.pictures.models import FavouritePicture


@pytest.mark.django_db()
@pytest.mark.parametrize(('page', 'template'), [
    ('', 'common/_base.html'),
    (reverse('identity:registration'), 'identity/pages/registration.html'),
    (reverse('identity:login'), 'identity/pages/login.html'),
])
def test_identify_pages_unauthorized(
    client: Client,
    page: str,
    template: str,
) -> None:
    """Check that identify pages are accessible for unauthorized user."""
    response = client.get(page)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, template)  # type: ignore[arg-type]


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


@pytest.mark.django_db()
@pytest.mark.parametrize(('page', 'template'), [
    (reverse('pictures:dashboard'), 'pictures/pages/dashboard.html'),
    (reverse('pictures:favourites'), 'pictures/pages/favourites.html'),
    (reverse('identity:user_update'), 'identity/pages/user_update.html'),
])
def test_pages_authorized(
    login: User,
    client: Client,
    page: str,
    template: str,
) -> None:
    """Check that unauthorized user will be redirected to login page."""
    response = client.get(page)

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, template)  # type: ignore[arg-type]


@pytest.mark.django_db()
def test_non_empty_favourites_page_authorized(
    login: User,
    add_favourite_pictures: list[FavouritePicture],
    client: Client,
) -> None:
    """Check that unauthorized user will be redirected to login page."""
    response = client.get(reverse('pictures:favourites'))

    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(
        response, 'pictures/pages/favourites.html',  # type: ignore[arg-type]
    )
