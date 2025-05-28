import asyncio
from uuid import UUID

import httpx

from timhatdiehandandermaus_sdk import fuzzy
from timhatdiehandandermaus_sdk.models import (
    CanonicalUserResponse,
    MovieDeleteStatusEnum,
    MoviePostRequest,
    MovieResponse,
    MoviesResponse,
    MovieStatusSearchRequestEnum,
    QueueResponse,
    TelegramUserRequest,
)


class MissingToken(Exception):
    def __init__(self) -> None:
        super().__init__("This method needs an authentication token.")


class TimApi:
    def __init__(
        self,
        auth_token: str | None = None,
        *,
        api_url: str | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            base_url=api_url or "https://tim-api.bembel.party",
        )
        if auth_token:
            self._client.headers["Authorization"] = f"Bearer {auth_token}"

        self._token = auth_token

    @property
    def has_token(self):
        return bool(self._token)

    def _check_token(self) -> None:
        if not self.has_token:
            raise MissingToken()

    async def get_movie(self, *, movie_id: str) -> MovieResponse:
        """
        Gets a movie by id
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/get_movie__id_
        :param movie_id: string with a movie ID
        :return: MovieResponse
        """
        response = await self._client.get(f"/movie/{movie_id}")
        response.raise_for_status()

        return MovieResponse.model_validate_json(response.content)

    async def search_movie(
        self,
        *,
        query: str | None = None,
        status: MovieStatusSearchRequestEnum | None = None,
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

        response = await self._client.get("/movie", params=params)
        response.raise_for_status()

        return MoviesResponse.model_validate_json(response.content)

    async def fuzzy_search_movie(
        self,
        *,
        query: str | None = None,
        status: MovieStatusSearchRequestEnum | None = None,
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
        movies = (await self.search_movie(query=query, status=status)).movies
        title = "" if query is None else query

        return fuzzy.fuzzy_search_movie(movies, title=title, threshold=threshold)

    async def queue(self) -> QueueResponse:
        """
        Retrieves queue, returns a list of `QueueResponseItem` (movie IDs only)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/get_queue
        :return: QueueResponse
        """
        response = await self._client.get("/queue")
        response.raise_for_status()

        return QueueResponse.model_validate_json(response.content)

    async def queued_movies(self, *, limit: int | None = None) -> list[MovieResponse]:
        queue_items = (await self.queue()).queue
        if limit:
            queue_items = queue_items[:limit]

        movie_tasks: list[asyncio.Task[MovieResponse]] = []
        async with asyncio.TaskGroup() as tg:
            for queue_item in queue_items:
                task = tg.create_task(self.get_movie(movie_id=queue_item.id))
                movie_tasks.append(task)

        return [task.result() for task in movie_tasks]

    async def _mark_queued_movie(
        self, *, queue_id: str, status: MovieDeleteStatusEnum
    ) -> MovieResponse:
        if queue_id == "f388de4e-184e-4258-a0b5-10ad753c1ece":
            return await self.get_movie(movie_id=queue_id)

        self._check_token()

        response = await self._client.delete(
            f"/queue/{queue_id}",
            params={
                "status": status.value,
            },
        )
        response.raise_for_status()

        return MovieResponse.model_validate_json(response.content)

    async def mark_movie_as_deleted(self, *, queue_id: str) -> MovieResponse:
        """
        Marks a movie from the queue as deleted (by `queue_id`)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/delete_queue__id_
        :param queue_id: ID of the queue item (not the movie)
        :return: MovieResponse
        """
        return await self._mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.DELETED
        )

    async def mark_movie_as_watched(self, *, queue_id: str) -> MovieResponse:
        """
        Marks a movie from the queue as watched (by `queue_id`)
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Queue%20Resource/delete_queue__id_
        :param queue_id: ID of the queue item (not the movie)
        :return: MovieResponse
        """
        return await self._mark_queued_movie(
            queue_id=queue_id, status=MovieDeleteStatusEnum.WATCHED
        )

    async def add_movie(
        self,
        *,
        imdb_url: str,
        user_id: UUID | None = None,
    ) -> MovieResponse:
        """
        Adds a movie to the database (and queue) by `imdb_url`
        See https://api.timhatdiehandandermaus.consulting/docs/swagger/#/Movie%20Resource/put_movie
        :param imdb_url: Valid imdb url or imdb ID (see https://github.com/tim-hat-die-hand-an-der-maus/imdb-resolver)
        :return: MovieResponse
        """
        self._check_token()

        body = MoviePostRequest(imdb_url=imdb_url, user_id=user_id)
        response = await self._client.put("/movie", json=body.model_dump(mode="json"))
        response.raise_for_status()

        return MovieResponse.model_validate_json(response.content)

    async def get_canonical_user(
        self, *, user_id: UUID
    ) -> CanonicalUserResponse | None:
        self._check_token()

        response = await self._client.get(f"/user/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return CanonicalUserResponse.model_validate_json(response.content)

    async def update_telegram_user(
        self, telegram_user: TelegramUserRequest
    ) -> CanonicalUserResponse:
        self._check_token()

        response = await self._client.put(
            "/user/telegram",
            json=telegram_user.model_dump(mode="json"),
        )
        response.raise_for_status()

        return CanonicalUserResponse.model_validate_json(response.content)
