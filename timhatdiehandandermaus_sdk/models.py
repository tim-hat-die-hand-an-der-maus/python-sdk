from enum import Enum
from typing import Optional

from pydantic import BaseModel


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


class MovieDeleteRequest(BaseModel):
    status: MovieDeleteStatusEnum
