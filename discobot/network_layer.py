import json

import requests

from config import SESSIONS_PER_PAGE, BACKEND_PORT
from models import ParsedMovie, Session, History
from utils.decorators import log_api_call


@log_api_call
def set_rating(movie_uuid, guild_id, user, rating: int):
    data = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_uuid, 'guild_id': guild_id, 'rating': rating}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/rate', json=json.dumps(data))


@log_api_call
def set_unwatched(movie_id, guild_id, user):
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/unwatched', json=json.dumps(user))


@log_api_call
def set_watched(movie_id, guild_id, user):
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/watched', json=json.dumps(user))


@log_api_call
def subscribe_to_see(movie_id, guild_id, user):
    user = {'user':{'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/subscribe_to_watch', json=json.dumps(user))


@log_api_call
def get_movie(**kwargs):
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/get', json=json.dumps(kwargs))
    if response.status_code != 200:
        return None
    return ParsedMovie(**response.json())


@log_api_call
def register_movie(movie: ParsedMovie):
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie', json=movie.toJSON())
    return response.json()


@log_api_call
def update_guild(guild):
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/guild', json=guild)


@log_api_call
def get_guild_session(guild_id, members_ids=None):
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session', json={'guild_id': guild_id, 'members_ids': members_ids})
    return Session(**response.json())


@log_api_call
def join_session(session_id, user):
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/join', json=json.dumps(user))


@log_api_call
def leave_session(session_id, user):
    user = {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/leave', json=json.dumps(user))


@log_api_call
def set_dont_want_to_watch(movie_id, guild_id, user):
    user = {'user': {'id': user.id, 'name': user.name, 'avatar': user.avatar.url, 'mention': user.mention},
            'uuid': movie_id, 'guild_id': guild_id}
    return requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/movie/dont_want_to_watch', json=json.dumps(user))


@log_api_call
def select_movie(session_id, movie_title):
    response = requests.post(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/select_movie', json=json.dumps({'title': movie_title}))
    return response.status_code < 300


@log_api_call
def select_random_movie(session_id):
    return requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/select_random')


@log_api_call
def finish_session(session_id):
    return requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/finish')


@log_api_call
def decline_movie(session_id):
    return requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}/decline_movie')


@log_api_call
def get_session(session_id):
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/{session_id}')
    return Session(**response.json())


@log_api_call
def get_history(guild_id, page=0) -> History:
    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/session/by_guild/{guild_id}?limit={SESSIONS_PER_PAGE}&offset={SESSIONS_PER_PAGE*page}')
    json = response.json()
    sessions = list()
    for data in json['results']:
        sessions.append(Session(**data))
    return History(sessions=sessions, page=page+1, count=json['count'])


@log_api_call
def handshake():
    try:
        response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/handshake')
        return response and response.status_code == 200
    except Exception:
        return False
