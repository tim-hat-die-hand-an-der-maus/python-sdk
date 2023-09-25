from enum import Enum
from typing import Optional

from pydantic import BaseModel

from timhatdiehandandermaus_sdk.utils import escape_markdown


# see https://api.timhatdiehandandermaus.consulting/docs/swagger/ for api models


class MovieMetadataFieldEnum(Enum):
    COVER = "cover"
    RATING = "rating"


class CoverMetadataResponse(BaseModel):
    url: str
    ratio: Optional[float]


class MovieStatusResponseEnum(Enum):
    QUEUED = "Queued"
    WATCHED = "Watched"
    DELETED = "Deleted"


class MovieStatusSearchRequestEnum(Enum):
    QUEUED = "Queued"
    WATCHED = "Watched"
    DELETED = "Deleted"


class MovieMetadataResponse(BaseModel):
    id: str
    title: str
    year: Optional[int]
    rating: Optional[str]
    cover: CoverMetadataResponse


class MovieResponse(BaseModel):
    id: str
    status: MovieStatusResponseEnum
    imdb: MovieMetadataResponse

    def telegram_markdown_v2(self) -> str:
        imdb_link = f"https://www.imdb.com/title/tt{self.imdb.id}"
        title_link = f"[{escape_markdown(self.imdb.title)}]({imdb_link})"

        year_rating_suffix = escape_markdown(f"({self.imdb.year}) {self.imdb.rating}⭐")
        return f"{title_link} {year_rating_suffix}"


class MoviesResponse(BaseModel):
    movies: list[MovieResponse]


class QueueItemResponse(BaseModel):
    id: str


class QueueResponse(BaseModel):
    queue: list[QueueItemResponse]


class MovieDeleteStatusEnum(Enum):
    DELETED = "Deleted"
    WATCHED = "Watched"


class MoviePostRequest(BaseModel):
    imbdUrl: str


class MovieMetadataPatchRequest(BaseModel):
    refresh: list[MovieMetadataFieldEnum]
