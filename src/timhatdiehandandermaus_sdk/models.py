from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from timhatdiehandandermaus_sdk.utils import escape_markdown

# see https://tim-api.bembel.party/docs/swagger/ for api models


class ResponseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
    )


class MovieMetadataFieldEnum(Enum):
    COVER = "cover"
    RATING = "rating"


class CoverMetadataResponse(ResponseModel):
    url: str
    ratio: float | None


class MovieStatusResponseEnum(Enum):
    QUEUED = "Queued"
    WATCHED = "Watched"
    DELETED = "Deleted"


class MovieStatusSearchRequestEnum(Enum):
    QUEUED = "Queued"
    WATCHED = "Watched"
    DELETED = "Deleted"


class MovieMetadataResponse(ResponseModel):
    id: str
    title: str
    year: int | None
    rating: str | None
    cover: CoverMetadataResponse | None
    info_page_url: str


class MovieResponse(ResponseModel):
    id: str
    status: MovieStatusResponseEnum
    imdb: MovieMetadataResponse | None
    tmdb: MovieMetadataResponse | None

    @property
    def metadata(self) -> MovieMetadataResponse:
        result = self.tmdb or self.imdb
        if result is None:
            raise ValueError("Movie has no metadata")
        return result

    def telegram_markdown_v2(self) -> str:
        links = []

        if tmdb := self.tmdb:
            if rating := tmdb.rating:
                text = f"TMDB {escape_markdown(rating)}⭐"
            else:
                text = "TMDB"
            links.append(f"[{text}]({tmdb.info_page_url})")

        if imdb := self.imdb:
            if rating := imdb.rating:
                text = f"IMDb {escape_markdown(rating)}⭐"
            else:
                text = "IMDb"
            links.append(f"[{text}]({imdb.info_page_url})")

        meta = self.metadata
        title = escape_markdown(meta.title)
        year = meta.year

        year_suffix = "" if year is None else escape_markdown(f" ({year})")

        return rf"{title}{year_suffix} \- {', '.join(links)}"


class MoviesResponse(ResponseModel):
    movies: list[MovieResponse]


class QueueItemResponse(ResponseModel):
    id: str


class QueueResponse(BaseModel):
    queue: list[QueueItemResponse]


class MovieDeleteStatusEnum(Enum):
    DELETED = "Deleted"
    WATCHED = "Watched"


class MoviePostRequest(BaseModel):
    imdbUrl: str


class MovieMetadataPatchRequest(BaseModel):
    refresh: list[MovieMetadataFieldEnum]
