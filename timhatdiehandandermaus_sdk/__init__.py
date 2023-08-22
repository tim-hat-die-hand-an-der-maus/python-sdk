from enum import Enum

import httpx
from httpx import Response

from timhatdiehandandermaus_sdk.models import (
    MoviesResponse,
    MovieResponse,
    QueueResponse,
    MovieDeleteStatusEnum,
    MovieMetadataFieldEnum,
    MoviePostRequest,
    MovieMetadataPatchRequest,
    MovieDeleteRequest,
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
    base_url = "https://api.timhatdiehandandermaus.consulting"

    def __init__(self, auth_token: str):
        self.token = auth_token

    def request(
        self,
        *,
        method: HTTPMethod,
        path: str,
        params=None,
        headers: dict = None,
        json: dict = None,
        needs_token: bool = False,
    ) -> Response:
        _headers = {"Accept": "application/json"}
        if method != HTTPMethod.GET:
            _headers["Content-Type"] = "application/json"
        if needs_token:
            if not self.token:
                raise MissingToken(path=path, method=method)
            _headers["Authorization"] = f"Bearer {self.token}"

        if headers:
            _headers.update(headers)
        url = "/".join([self.base_url.rstrip("/"), path.lstrip("/")])

        response = httpx.request(
            method=method.value, url=url, params=params, json=json, headers=headers
        )
        response.raise_for_status()

        return response

    def get(self, path: str, params=None, headers: dict = None) -> Response:
        return self.request(
            method=HTTPMethod.GET, path=path, params=params, headers=headers
        )

    def patch(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self.request(
            method=HTTPMethod.PATCH,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def put(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self.request(
            method=HTTPMethod.PATCH,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def delete(
        self, path: str, params=None, headers: dict = None, json: dict = None
    ) -> Response:
        return self.request(
            method=HTTPMethod.PATCH,
            path=path,
            params=params,
            headers=headers,
            json=json,
            needs_token=True,
        )

    def get_movie(self, *, movie_id: str) -> MovieResponse:
        path = f"movie/{movie_id}"
        response = self.get(path=path)

        return MovieResponse.model_validate(response.json())

    def search_movie(self, *, query: str = None, status: str = None) -> MoviesResponse:
        params = {}
        if query:
            params["query"] = query
        if status:
            params["status"] = status

        response = self.get(path="movie", params=params)

        return MoviesResponse.model_validate(response.json())

    def queue(self) -> QueueResponse:
        response = self.get(path="queue")

        return QueueResponse.model_validate(response.json())

    def mark_queued_movie(
        self, *, queue_id: str, status: MovieDeleteStatusEnum
    ) -> MovieResponse:
        path = f"queue/{queue_id}"
        body = MovieDeleteRequest(status=status)
        response = self.delete(path=path, json=body.model_dump())

        return MovieResponse.model_validate(response.json())

    def mark_movie_as_deleted(self, *, queue_id: str) -> MovieResponse:
        return self.mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.DELETED
        )

    def mark_movie_as_watched(self, *, queue_id: str) -> MovieResponse:
        return self.mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.WATCHED
        )

    def add_movie(self, *, imdb_url: str) -> MovieResponse:
        body = MoviePostRequest(imdb_url=imdb_url)
        response = self.put(path="movie", json=body.model_dump())

        return MovieResponse.model_validate(response.json())

    def patch_metadata(
        self, *, movie_id: str, fields: list[MovieMetadataFieldEnum]
    ) -> Response:
        if not fields:
            raise ValueError(
                "`fields` must contain at least one `MovieMetadataFieldEnum` value"
            )

        path = f"movie/{movie_id}/metadata"
        body = MovieMetadataPatchRequest(refresh=fields)

        return self.patch(path=path, json=body.model_dump())
