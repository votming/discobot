from dataclasses import dataclass
from typing import Optional
from models import ParsedMovie

import requests



class MovieParser:
    url = "https://imdb8.p.rapidapi.com/auto-complete"
    querystring = {"q": "Дракула"}
    headers = {
        "X-RapidAPI-Key": "0cd4346526msh767fedcf9d81d21p157f18jsn068f9afb1dbf",
        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
    }
    obj = {'d': [{'i': {'height': 1184, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg', 'width': 800}, 'id': 'tt0848228', 'l': 'The Avengers', 'q': 'feature', 'qid': 'movie', 'rank': 1062, 's': 'Robert Downey Jr., Chris Evans', 'y': 2012}, {'i': {'height': 2048, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_.jpg', 'width': 1382}, 'id': 'tt4154796', 'l': 'Avengers: Endgame', 'q': 'feature', 'qid': 'movie', 'rank': 385, 's': 'Robert Downey Jr., Chris Evans', 'y': 2019}, {'i': {'height': 2048, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BMjMxNjY2MDU1OV5BMl5BanBnXkFtZTgwNzY1MTUwNTM@._V1_.jpg', 'width': 1382}, 'id': 'tt4154756', 'l': 'Avengers: Infinity War', 'q': 'feature', 'qid': 'movie', 'rank': 745, 's': 'Robert Downey Jr., Chris Hemsworth', 'y': 2018}, {'i': {'height': 2883, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BZWE0MjkyNGQtMjgwMS00NGIwLTg5YmEtYThlOTQ1NTZmNWFmXkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_.jpg', 'width': 1920}, 'id': 'tt21361444', 'l': 'Avengers: Secret Wars', 'q': 'feature', 'qid': 'movie', 'rank': 917, 's': 'Jonathan Majors, Chris Hemsworth', 'y': 2026}, {'i': {'height': 582, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BZWQwZTdjMDUtNTY1YS00MDI0LWFkNjYtZDA4MDdmZjdlMDRlXkEyXkFqcGdeQXVyNjUwNzk3NDc@._V1_.jpg', 'width': 427}, 'id': 'tt0054518', 'l': 'The Avengers', 'q': 'TV series', 'qid': 'tvSeries', 'rank': 4677, 's': 'Patrick Macnee, Diana Rigg', 'y': 1961, 'yr': '1961-1969'}, {'i': {'height': 2883, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BMTMyMTMwYTctMjExYi00NTc3LWEwYjAtZWJmODVkZDU1NTZiXkEyXkFqcGdeQXVyMTEzMTI1Mjk3._V1_.jpg', 'width': 1920}, 'id': 'tt21357150', 'l': 'Avengers: The Kang Dynasty', 'q': 'feature', 'qid': 'movie', 'rank': 1869, 's': 'Jonathan Majors', 'y': 2025}, {'i': {'height': 1280, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BMTM4OGJmNWMtOTM4Ni00NTE3LTg3MDItZmQxYjc4N2JhNmUxXkEyXkFqcGdeQXVyNTgzMDMzMTg@._V1_.jpg', 'width': 864}, 'id': 'tt2395427', 'l': 'Avengers: Age of Ultron', 'q': 'feature', 'qid': 'movie', 'rank': 1792, 's': 'Robert Downey Jr., Chris Evans', 'y': 2015}, {'i': {'height': 742, 'imageUrl': 'https://m.media-amazon.com/images/M/MV5BYWE1NTdjOWQtYTQ2Ny00Nzc5LWExYzMtNmRlOThmOTE2N2I4XkEyXkFqcGdeQXVyNjUwNzk3NDc@._V1_.jpg', 'width': 493}, 'id': 'tt0118661', 'l': 'The Avengers', 'q': 'feature', 'qid': 'movie', 'rank': 9609, 's': 'Ralph Fiennes, Uma Thurman', 'y': 1998}], 'q': '%D0%BC%D1%81%D1%82%D0%B8%D1%82%D0%B5%D0%BB%D0%B8', 'v': 1}

    @classmethod
    def get_movie(cls, name) -> ParsedMovie:
        # response = requests.request("GET", cls.url, headers=cls.headers, params=cls.querystring)
        # movie = response.json()['d'][0]
        json = cls.obj['d'][0]
        movie = ParsedMovie(id=json['id'], name=json['l'], rank=json['rank'], image=json['i']['imageUrl'], year=json['y'])
        movie.id = json['id']
        movie.name = f"{json['l']} ({json['y']})"
        movie.rank = json['rank']
        movie.image = json['i']['imageUrl']
        movie.year = json['y']

        return movie


movie = MovieParser.get_movie('Мстители')
print(movie.name)
