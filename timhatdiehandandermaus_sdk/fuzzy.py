from thefuzz import fuzz

from timhatdiehandandermaus_sdk import models


def fuzzy_search_movie(movies: list[models.MovieResponse], title: str, *, threshold: int):
    matches = []
    for movie in movies:
        if (
            fuzz.token_set_ratio(title, movie.imdb.title) > threshold
            or title.lower() in movie.imdb.title.lower()
        ):
            matches.append(movie)

    return matches
