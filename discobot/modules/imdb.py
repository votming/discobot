from dataclasses import dataclass
from typing import Optional

from config import RAPID_API_X_KEY
from models import ParsedMovie

import requests


class MovieParser:
    url = "https://imdb8.p.rapidapi.com/auto-complete"
    headers = {"X-RapidAPI-Key": RAPID_API_X_KEY, "X-RapidAPI-Host": "imdb8.p.rapidapi.com"}

    @classmethod
    def get_movie(cls, name) -> ParsedMovie:
        querystring = {"q": name}
        response = requests.request("GET", cls.url, headers=cls.headers, params=querystring)
        json = response.json()['d'][0]
        movie = ParsedMovie(uuid=json['id'], name=f"{json['l']} ({json['y']})", rank=json['rank'], year=json['y'],
                            image=json['i']['imageUrl'],  actors=json['s'])
        return movie
