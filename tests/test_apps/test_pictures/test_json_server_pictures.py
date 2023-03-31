import json
from contextlib import contextmanager
from http import HTTPStatus
from typing import Callable, Iterator
from urllib.parse import urljoin

import httpretty
import pytest
import requests
from django.test import Client
from django.urls import reverse

from server.apps.identity.models import User
from server.apps.pictures.container import container
from server.common.django.types import Settings


@pytest.fixture()
def settings() -> Settings:
    """Get Django settings."""
    return container.resolve(Settings)


@pytest.fixture()
def mock_pictures_fetch_api(
    settings: Settings,
    json_server_photos,
) -> Callable[[], None]:
    """Route placeholder API endpoint to json-server."""

    @contextmanager
    def factory() -> Iterator[None]:
        with httpretty.httprettized():
            httpretty.register_uri(
                httpretty.GET,
                urljoin(settings.PLACEHOLDER_API_URL, 'photos'),
                body=json.dumps(json_server_photos),
                content_type='application/json',
            )
            yield
            assert httpretty.has_request()

    return factory  # type: ignore[return-value]


@pytest.fixture()
def json_server_photos():
    """Get photos from json_server."""
    return requests.get(
        'http://python-testing-homework_json_server_1/photos',
        timeout=1,
    ).json()


@pytest.mark.django_db()
def test_pictures_dashboard_content(
    login: User,
    client: Client,
    mock_pictures_fetch_api,
    json_server_photos,
) -> None:
    """Check dashboard content."""
    with mock_pictures_fetch_api():
        response = client.get(reverse('pictures:dashboard'))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['pictures']) == len(json_server_photos)
        assert response.context['pictures'] == json_server_photos
