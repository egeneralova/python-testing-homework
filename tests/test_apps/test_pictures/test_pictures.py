from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from server.apps.pictures.intrastructure.django.forms import FavouritesForm
from server.apps.pictures.models import FavouritePicture
from tests.test_apps.test_pictures.conftest import FavAssertion, PictureData


@pytest.mark.django_db()
def test_add_favourite_pictures(
    client: Client,
    login: User,
    picture_data_list: list[PictureData],
    assert_correct_favourites: FavAssertion,
) -> None:
    """This test check adding favourite pictures functionality."""
    assert_correct_favourites(login.email, [])

    for picture in picture_data_list:
        response = client.post(
            reverse('pictures:dashboard'),
            data=picture,
        )
        assert response.status_code == HTTPStatus.FOUND
        assert response.get('Location') == reverse('pictures:dashboard')

    assert_correct_favourites(login.email, picture_data_list)


@pytest.mark.django_db()
def test_favourite_picture_list(
    client: Client,
    login: User,
    add_favourite_pictures: list[FavouritePicture],
):
    """User has correct favorites list representation."""
    response = client.get(reverse('pictures:favourites'))

    assert response.status_code == HTTPStatus.OK
    actual_pictures_list = list(
        response.context_data['object_list'],  # type: ignore[attr-defined]
    )
    assert str(actual_pictures_list) == str(add_favourite_pictures)


@pytest.mark.django_db()
def test_favourite_picture_list_delay_savings(
    client: Client,
    login: User,
    picture_data_list: list[PictureData],
    assert_correct_favourites: FavAssertion,
):
    """Check that possible to use delay saving."""
    assert_correct_favourites(login.email, [])

    for idx, pic in enumerate(picture_data_list):
        fav = FavouritesForm.save(FavouritesForm(pic, user=login), commit=False)
        assert_correct_favourites(login.email, picture_data_list[:idx])
        fav.save()
        assert_correct_favourites(login.email, picture_data_list[:idx + 1])
