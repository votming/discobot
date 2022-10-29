import json

import requests

from config import SESSIONS_PER_PAGE, BACKEND_PORT
from models import ParsedMovie, Session, History


def set_rating(movie_uuid, guild_id, user, rating: int):
    print(f'set_rating, movie_id: {movie_uuid}, rating: {rating}, user: {user}')
    data = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_uuid, 'guild_id': guild_id, 'rating': rating}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/rate', json=json.dumps(data))
    print(response)


def set_unwatched(movie_id, guild_id, user):
    print(f'set_unwatched, movie_id: {movie_id}, user: {user}')
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/unwatched', json=json.dumps(user))
    print(response)


def set_watched(movie_id, guild_id, user):
    print(f'set_watched, movie_id: {movie_id}, user: {user}')
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/watched', json=json.dumps(user))
    print(response)


def subscribe_to_see(movie_id, guild_id, user):
    print(f'subscribe_to_see, user: {user}')
    user = {'user':{'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/subscribe_to_watch', json=json.dumps(user))
    print(response.content)


def get_movie(**kwargs):
    print(f'get_movie, id: {kwargs}')
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/get', json=json.dumps(kwargs))
    if response.status_code!=200:
        return None
    print(response)
    return ParsedMovie(**response.json())


def register_movie(movie: ParsedMovie):
    print(f'register_movie, movie: {movie}')
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie', json=movie.toJSON())
    print(response.content)
    return response.json()


def update_guild(guild):
    print(f'update_guild, guild: {guild}')
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/guild', json=guild)
    print(response.content)


def get_guild_session(guild_id):
    print(f'get_guild_session, guild: {guild_id}')
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session', json={'guild_id': guild_id})
    print(response.content)
    return Session(**response.json())


def join_session(session_id, user):
    print(f'join_session, session_id: {session_id}, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/join', json=json.dumps(user))
    print(response)


def leave_session(session_id, user):
    print(f'leave_session, session_id: {session_id}, user: {user}')
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/leave', json=json.dumps(user))
    print(response)


def select_movie(session_id, movie_title):
    print(f'select_movie, session_id: {session_id}, user: {movie_title}')
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/select_movie', json=json.dumps({'title': movie_title}))
    print(response)
    if response.status_code >= 300:
        return False
    return True


def select_random_movie(session_id):
    print(f'select_random_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/select_random')
    print(response)


def finish_session(session_id):
    print(f'select_random_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/finish')
    print(response)


def decline_movie(session_id):
    print(f'select_movie, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/decline_movie')
    print(response)


def get_session(session_id):
    print(f'get_session, session_id: {session_id}')
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}')
    return Session(**response.json())


def get_history(guild_id, page=0) -> History:
    print(f'get_all_history, guild_id: {guild_id}')
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/by_guild/{guild_id}?limit={SESSIONS_PER_PAGE}&offset={SESSIONS_PER_PAGE*page}')
    json = response.json()
    sessions = list()
    for data in json['results']:
        sessions.append(Session(**data))
    return History(sessions=sessions, page=page+1, count=json['count'])

def handshake():
    print(f'handshake')
    try:
        response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/handshake')
        return response and response.status_code == 200
    except Exception:
        return False
