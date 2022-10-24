import json

import requests

from models import ParsedMovie


def set_watched(movie_id, user):
    print(f'set_watched, movie_id: {movie_id}, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/{movie_id}/watched', json=json.dumps(user))
    print(response)

def subscribe_to_see(movie_id, user):
    print(f'subscribe_to_see, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/{movie_id}/subscribe_to_watch', json=json.dumps(user))
    print(response.content)

def get_movie(id):
    print(f'get_movie, id: {id}')
    response = requests.get(f'http://127.0.0.1:8000/api/movie/{id}')
    if response.status_code!=200:
        return None
    print(response)
    return ParsedMovie(**response.json())

def get_movie_by_name(name) -> ParsedMovie:
    print(f'get_movie_by_name, id: {name}')
    response = requests.get(f'http://127.0.0.1:8000/api/movie/by_name/{name}')
    if response.status_code!=200:
        return None
    print(response)
    return ParsedMovie(**response.json())

def register_movie(movie: ParsedMovie):
    print(f'register_movie, movie: {movie}')
    response = requests.post(f'http://127.0.0.1:8000/api/movie', json=movie.toJSON())
    print(response.content)
    return response.json()

def update_guild(guild):
    print(f'update_guild, guild: {guild}')
    response = requests.post(f'http://127.0.0.1:8000/api/guild', json=guild)
    print(response.content)

def set_rating(movie_id, user, rating):
    print(f'set_rating, movie_id: {movie_id}, user: {user}, rating: {rating}')
    pass