import pytest

from timhatdiehandandermaus_sdk import MovieResponse, fuzzy
from timhatdiehandandermaus_sdk.models import (
    CoverMetadataResponse,
    MovieMetadataResponse,
    MovieStatusResponseEnum,
)


def create_movie_response_with_title(title: str):
    return MovieResponse.model_validate(
        {
            "id": "",
            "status": MovieStatusResponseEnum.QUEUED,
            "imdb": MovieMetadataResponse.model_validate(
                {
                    "id": "",
                    "title": title,
                    "year": None,
                    "rating": None,
                    "cover": CoverMetadataResponse.model_validate(
                        {"url": "", "ratio": None}
                    ),
                }
            ),
        }
    )


@pytest.mark.parametrize(
    "query,db_titles,expected_length,threshold",
    [
        ("Pacific", ["Pacific Rim", "Pacific Rim Uprising"], 2, 50),
        ("pacific", ["Pacific Rim", "Pacific Rim: Uprising"], 2, 50),
        ("Pacific Rim", ["Pacific Rim", "Pacific Rim: Uprising"], 2, 70),
        ("Pacific Rim: Uprising", ["Pacific Rim", "Pacific Rim: Uprising"], 2, 70),
        ("Pcific Rm", ["Pacific Rim", "Pacific Rim: Uprising"], 1, 70),
    ],
)
def test_fuzzy_search(
    query: str, db_titles: list[str], expected_length: int, threshold: int
):
    try:
        movie_responses = [
            create_movie_response_with_title(db_title) for db_title in db_titles
        ]
        assert (
            len(fuzzy.fuzzy_search_movie(movie_responses, query, threshold=threshold))
            == expected_length
        )
    except (AttributeError, TypeError):
        assert query is None
