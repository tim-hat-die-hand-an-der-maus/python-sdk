from thefuzz import fuzz

from timhatdiehandandermaus_sdk import models


def fuzzy_search_movie(
    movies: list[models.MovieResponse], title: str, *, threshold: int
) -> list[models.MovieResponse]:
    matches = []
    for movie in movies:
        ratio = fuzz.token_sort_ratio(title, movie.imdb.title)

        if ratio > threshold:
            matches.append((movie, ratio))

    sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
    return [match for match, _ in sorted_matches]
