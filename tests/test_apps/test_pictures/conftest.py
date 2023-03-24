from typing import Callable, TypeAlias, TypedDict, final

import pytest
from mimesis import Field, Schema
from mimesis.enums import Locale

from server.apps.identity.models import User
from server.apps.pictures.logic.usecases.favourites_list import FavouritesList


@final
class PictureData(TypedDict, total=False):
    """Represent the simplified picture data."""

    foreign_id: int
    url: str


@pytest.fixture()
def picture_data(faker_seed: int) -> PictureData:
    """Generate picture data."""
    mf = Field(locale=Locale.RU, seed=faker_seed)
    schema = Schema(schema=lambda: {
        'foreign_id': mf('increment'),
        'url': mf('url'),
    })
    return {
        **schema.create(iterations=1)[0],
    }


@pytest.fixture(params=[
    1,
    2,
    5,
])
def picture_data_list(request, faker_seed: int) -> [PictureData]:
    """Generate list of picture data."""
    mf = Field(locale=Locale.RU, seed=faker_seed)
    schema = Schema(schema=lambda: {
        'foreign_id': mf('increment'),
        'url': mf('url'),
    })
    return schema.create(iterations=request.param)


FavAssertion: TypeAlias = Callable[[str, [PictureData]], None]


@pytest.fixture(scope='session')
def assert_correct_favourite_pictures() -> FavAssertion:
    """Check that user has correct favourite pictures."""

    def factory(email: str, expected: [PictureData]) -> None:
        favourite = FavouritesList()(User.objects.get(email=email).id).all()
        assert len(favourite) == len(expected)
        for idx, _ in enumerate(expected):
            assert favourite[idx].url == expected[idx]['url']
            assert favourite[idx].foreign_id == expected[idx]['foreign_id']

    return factory
