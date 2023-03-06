from datetime import datetime
from dataclasses import dataclass


@dataclass
class ParsedMovie:
    uuid: int
    name: str
    rank: int = None
    rankings: list = None
    image: str = None
    year: int = None
    average_rating: int = None
    already_seen: list = None
    want_to_see: list = None
    dont_want_to_watch: list = None
    sessions: list = None
    guild: str = None
    actors: str = None
    created_at: datetime = None
    updated_at: datetime = None
    id: int = None

    def toJSON(self):
        return self.__dict__


@dataclass
class Session:
    id: int
    guild: str
    audience: list
    available_movies: list = None
    club_has_seen: list = None
    audience_want_to_see_movies: list = None
    seen_at: datetime = None
    movie: dict = None
    created_at: datetime = None
    updated_at: datetime = None

    def toJSON(self):
        return self.__dict__


@dataclass
class Channel:
    id: int
    guild: str
    config: dict

@dataclass
class History:
    sessions: list
    count: int
    page: int

