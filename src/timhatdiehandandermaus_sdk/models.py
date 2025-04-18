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
    imdb: MovieMetadataResponse

    def telegram_markdown_v2(self) -> str:
        imdb_link = self.imdb.info_page_url
        title_link = f"[{escape_markdown(self.imdb.title)}]({imdb_link})"

        year_rating_suffix = escape_markdown(f"({self.imdb.year}) {self.imdb.rating}⭐")
        return f"{title_link} {year_rating_suffix}"


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
