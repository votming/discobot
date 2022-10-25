import json

import requests

from models import ParsedMovie, Session


def set_rating(movie_uuid, guild_id, user, rating: int):
    print(f'set_rating, movie_id: {movie_uuid}, rating: {rating}, user: {user}')
    data = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_uuid, 'guild_id': guild_id, 'rating': rating}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/rate', json=json.dumps(data))
    print(response)


def set_unwatched(movie_id, guild_id, user):
    print(f'set_unwatched, movie_id: {movie_id}, user: {user}')
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/unwatched', json=json.dumps(user))
    print(response)


def set_watched(movie_id, guild_id, user):
    print(f'set_watched, movie_id: {movie_id}, user: {user}')
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/watched', json=json.dumps(user))
    print(response)

def subscribe_to_see(movie_id, guild_id, user):
    print(f'subscribe_to_see, user: {user}')
    user = {'user':{'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:8000/api/movie/subscribe_to_watch', json=json.dumps(user))
    print(response.content)

def get_movie(**kwargs):
    print(f'get_movie, id: {kwargs}')
    response = requests.post(f'http://127.0.0.1:8000/api/movie/get', json=json.dumps(kwargs))
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

def create_new_session(guild):
    print(f'create_new_session, guild: {guild}')
    response = requests.post(f'http://127.0.0.1:8000/api/session', json={'guild_id': guild.id})
    print(response.content)
    return Session(**response.json())


def join_session(session_id, user):
    print(f'join_session, session_id: {session_id}, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:8000/api/session/{session_id}/join', json=json.dumps(user))
    print(response)


def leave_session(session_id, user):
    print(f'leave_session, session_id: {session_id}, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:8000/api/session/{session_id}/leave', json=json.dumps(user))
    print(response)


def select_movie(session_id, movie_title):
    print(f'select_movie, session_id: {session_id}, user: {movie_title}')
    response = requests.post(f'http://127.0.0.1:8000/api/session/{session_id}/select_movie', json=json.dumps({'title': movie_title}))
    print(response)
    if response.status_code >= 300:
        return False
    return True


def select_random_movie(session_id):
    print(f'select_random_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:8000/api/session/{session_id}/select_random')
    print(response)


def finish_session(session_id):
    print(f'select_random_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:8000/api/session/{session_id}/finish')
    print(response)


def decline_movie(session_id):
    print(f'select_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:8000/api/session/{session_id}/decline_movie')
    print(response)


def get_session(session_id):
    print(f'get_session, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:8000/api/session/{session_id}')
    return Session(**response.json())
