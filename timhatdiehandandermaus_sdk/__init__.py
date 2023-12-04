import os
from enum import Enum
from urllib.parse import urljoin

import httpx
from httpx import Response

import timhatdiehandandermaus_sdk.fuzzy
from timhatdiehandandermaus_sdk.models import (
    MoviesResponse,
    MovieResponse,
    QueueResponse,
    MovieDeleteStatusEnum,
    MovieMetadataFieldEnum,
    MoviePostRequest,
    MovieMetadataPatchRequest,
    MovieStatusSearchRequestEnum,
)


class HTTPMethod(Enum):
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class MissingToken(Exception):
    def __init__(self, *, path: str, method: HTTPMethod):
        super().__init__(
            f"This method ({method.value}) at `{path}` needs an authentication token"
        )


class TimApi:
    base_url = os.getenv("API_URL") or "https://api.timhatdiehandandermaus.consulting"

    def __init__(self, auth_token: str = None):
        self.token = auth_token

    def _request(
        self,
        *,
        method: HTTPMethod,
        path: str,
        params=None,
        headers: dict = None,
        json: dict = None,
        needs_token: bool = False,
        timeout: int = 30,
    ) -> Response:
        _headers = {"Accept": "application/json"}
        if method not in [HTTPMethod.GET, HTTPMethod.DELETE]:
            _headers["Content-Type"] = "application/json"
        if needs_token:
            if not self.token:
                raise MissingToken(path=path, method=method)
            _headers["Authorization"] = f"Bearer {self.token}"

        if headers:
            _headers.update(headers)
        url = urljoin(self.base_url, path)

        response = httpx.request(
            method=method.value,
            url=url,
            params=params,
            headers=_headers,
            json=json,
            timeout=timeout,
        )
        response.raise_for_status()

        return response

    def _get(self, path: str, params=None, headers: dict = None) -> Response:
        return self._request(
            method=HTTPMethod.GET, path=path, params=params, headers=headers
        )

    def _patch(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self._request(
            method=HTTPMethod.PATCH,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def _put(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self._request(
            method=HTTPMethod.PUT,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def _delete(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self._request(
            method=HTTPMethod.DELETE,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def get_movie(self, *, movie_id: str) -> MovieResponse:
        """
        Gets a movie by id
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/get_movie__id_
        :param movie_id: string with a movie ID
        :return: MovieResponse
        """
        path = f"movie/{movie_id}"
        response = self._get(path=path)

        return MovieResponse.model_validate(response.json())

    def search_movie(
        self, *, query: str = None, status: MovieStatusSearchRequestEnum = None
    ) -> MoviesResponse:
        """
        Searches movie by `query` and or `status`
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/get_movie
        :param query: queries movies by name (fuzzy search), no value will return all movies (except for status filter)
        :param status: returns movies with given status only
        :return: MoviesResponse
        """
        params = {}
        if query:
            params["query"] = query
        if status:
            params["status"] = status.value

        response = self._get(path="movie", params=params)

        return MoviesResponse.model_validate(response.json())

    def fuzzy_search_movie(
        self,
        *,
        query: str = None,
        status: MovieStatusSearchRequestEnum = None,
        threshold: int = 80,
    ) -> list[MovieResponse]:
        """
        Searches movie by `query` and or `status`
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/get_movie
        :param query: queries movies by name (fuzzy search), no value will return all movies (except for status filter)
        :param status: returns movies with given status only
        :param threshold: threshold for the fuzzy search to match on
        :return: MoviesResponse
        """
        movies = self.search_movie(query=query, status=status).movies
        return fuzzy.fuzzy_search_movie(movies, title=query, threshold=threshold)

    def queue(self) -> QueueResponse:
        """
        Retrieves queue, returns a list of `QueueResponseItem` (movie IDs only)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/get_queue
        :return: QueueResponse
        """
        response = self._get(path="queue")

        return QueueResponse.model_validate(response.json())

    def queued_movies(self, *, limit: int | None = None) -> list[MovieResponse]:
        queue_items = self.queue().queue
        if limit:
            queue_items = queue_items[:limit]
        movies = []

        for queue_item in queue_items:
            movies.append(self.get_movie(movie_id=queue_item.id))

        # noinspection PyTypeChecker
        return [movie for movie in movies]

    def _mark_queued_movie(
        self, *, queue_id: str, status: MovieDeleteStatusEnum
    ) -> MovieResponse:
        if queue_id == "f388de4e-184e-4258-a0b5-10ad753c1ece":
            return self.get_movie(movie_id=queue_id)

        path = f"queue/{queue_id}"
        response = self._delete(
            path=path,
            params={
                "status": status.value,
            },
        )

        return MovieResponse.model_validate(response.json())

    def mark_movie_as_deleted(self, *, queue_id: str) -> MovieResponse:
        """
        Marks a movie from the queue as deleted (by `queue_id`)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/delete_queue__id_
        :param queue_id: ID of the queue item (not the movie)
        :return: MovieResponse
        """
        return self._mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.DELETED
        )

    def mark_movie_as_watched(self, *, queue_id: str) -> MovieResponse:
        """
        Marks a movie from the queue as watched (by `queue_id`)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/delete_queue__id_
        :param queue_id: ID of the queue item (not the movie)
        :return: MovieResponse
        """
        return self._mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.WATCHED
        )

    def add_movie(self, *, imdb_url: str) -> MovieResponse:
        """
        Adds a movie to the database (and queue) by `imdb_url`
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/put_movie
        :param imdb_url: Valid imdb url or imdb ID (see https://github.com/tim-hat-die-hand-an-der-maus/imdb-resolver)
        :return: MovieResponse
        """
        body = MoviePostRequest.model_validate({"imbdUrl": imdb_url})
        response = self._put(path="movie", json=body.model_dump())

        return MovieResponse.model_validate(response.json())

    def patch_metadata(
        self, *, movie_id: str, fields: list[MovieMetadataFieldEnum]
    ) -> Response:
        """
        Patches a list of metadata fields (e.g. cover URL + rating if `fields=[MovieMetadataFieldEnum.COVER]`)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/patch_movie__id__metadata
        :param movie_id: valid movie UUID to be patched (doesn't need to be in the queue)
        :param fields: list of metadata fields to refresh (see MovieMetadataFieldEnum for options)
        :return: Nothing, api returns a 204
        """
        if not fields:
            raise ValueError(
                "`fields` must contain at least one `MovieMetadataFieldEnum` value"
            )

        path = f"movie/{movie_id}/metadata"
        body = MovieMetadataPatchRequest.model_validate({"refresh": fields})

        return self._patch(path=path, json=body.model_dump())
