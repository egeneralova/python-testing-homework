from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from tests.test_apps.test_pictures.conftest import FavAssertion, PictureData


@pytest.mark.django_db()
def test_add_favourite_pictures(
    client: Client,
    login: User,
    picture_data_list: [PictureData],
    assert_correct_favourite_pictures: FavAssertion,
) -> None:
    """This test check adding favourite pictures functionality."""
    assert_correct_favourite_pictures(login.email, [])

    for picture in picture_data_list:
        response = client.post(
            reverse('pictures:dashboard'),
            data=picture,
        )
        assert response.status_code == HTTPStatus.FOUND
        assert response.get('Location') == reverse('pictures:dashboard')

    assert_correct_favourite_pictures(login.email, picture_data_list)
