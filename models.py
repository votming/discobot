import json
from datetime import datetime
from dataclasses import dataclass

import discord


@dataclass
class ParsedMovie:
    id: int
    name: str
    rank: int = None
    image: str = None
    year: int = None
    already_seen: list = None
    want_to_see: list = None
    guild: str = None
    created_at: datetime = None
    updated_at: datetime = None

    def toJSON(self):
        return self.__dict__

