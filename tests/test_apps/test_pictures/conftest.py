from typing import Callable, TypedDict, final

import pytest
from typing_extensions import TypeAlias

from server.apps.identity.models import User
from server.apps.pictures.logic.usecases.favourites_list import FavouritesList


@final
class PictureData(TypedDict, total=False):
    """Represent the simplified picture data."""

    foreign_id: int
    url: str


@pytest.fixture(params=[
    1,
    2,
    5,
])
def picture_data_list(request, faker_seed: int, picture_factory):
    """Generate list of picture data."""
    return picture_factory(faker_seed, request.param)


FavAssertion: TypeAlias = Callable[[str, list[PictureData]], None]


@pytest.fixture(scope='session')
def assert_correct_favourites() -> FavAssertion:
    """Check that user has correct favourite pictures."""

    def factory(email: str, expected: list[PictureData]) -> None:
        favourite = FavouritesList()(User.objects.get(email=email).id).all()
        assert len(favourite) == len(expected)
        for idx, _ in enumerate(expected):
            assert favourite[idx].url == expected[idx]['url']
            assert favourite[idx].foreign_id == expected[idx]['foreign_id']

    return factory
